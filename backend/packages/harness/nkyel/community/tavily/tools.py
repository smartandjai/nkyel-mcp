import json
import logging
import os
from urllib.parse import urlparse

from langchain.tools import tool
from tavily import AsyncTavilyClient

from nkyel.community.search_time_range import SearchTimeRange
from nkyel.community.url_safety import safe_public_result_url
from nkyel.config import get_app_config

logger = logging.getLogger(__name__)

_FORMAT_ERROR = "Tavily returned an unexpected response format"


def _get_tavily_api_key(tool_name: str = "web_search") -> str | None:
    config = get_app_config().get_tool_config(tool_name)
    if config is not None and "api_key" in config.model_extra:
        configured = config.model_extra.get("api_key")
        if configured:
            return configured
    keys_pool = os.environ.get("TAVILY_API_KEYS")
    if keys_pool:
        keys = [k.strip() for k in keys_pool.split(",") if k.strip()]
        if keys:
            return keys[0]
    return os.environ.get("TAVILY_API_KEY")


def _get_tavily_client(tool_name: str = "web_search") -> AsyncTavilyClient:
    api_key = _get_tavily_api_key(tool_name)
    return AsyncTavilyClient(api_key=api_key)


def _response_objects(data: object, container: str) -> list[dict] | None:
    """Return the object entries of a Tavily response container, or None if malformed.

    A missing or null container is empty; a container that is not a list, or a
    non-empty list holding no objects, is malformed: the caller reports a format
    error rather than returning a result the agent would misread.
    """
    if not isinstance(data, dict):
        logger.error("Tavily returned unexpected payload type: %s", type(data).__name__)
        return None
    value = data.get(container)
    if value is None:
        return []
    if not isinstance(value, list):
        logger.error("Tavily returned unexpected '%s' payload type: %s", container, type(value).__name__)
        return None
    objects = [item for item in value if isinstance(item, dict)]
    if value and not objects:
        logger.error("Tavily returned '%s' with no usable result objects", container)
        return None
    return objects


@tool("web_search", parse_docstring=True)
async def web_search_tool(query: str, time_range: SearchTimeRange | None = None) -> str:
    """Search the web.

    Args:
        query: The query to search for.
        time_range: Optional relative publication/update window. Use only when the request requires recent results.
    """
    config = get_app_config().get_tool_config("web_search")
    max_results = 6
    if config is not None and "max_results" in config.model_extra:
        max_results = config.model_extra.get("max_results")

    search_kwargs: dict[str, object] = {"max_results": max_results}
    if config is not None:
        for key in ("include_domains", "exclude_domains"):
            if key in config.model_extra:
                search_kwargs[key] = config.model_extra[key]
    if search_kwargs.get("include_domains"):
        search_kwargs["include_domains_mode"] = "filter"
    if time_range is not None:
        search_kwargs["time_range"] = time_range
    client = _get_tavily_client()
    try:
        res = await client.search(query, **search_kwargs)
    except Exception as exc:
        logger.warning("Tavily search failed: %s, attempting DuckDuckGo fallback", exc)
        try:
            from nkyel.community.ddg_search.tools import web_search_tool as ddg_search_tool

            return await ddg_search_tool(query)
        except Exception:
            return json.dumps({"error": f"Search failed: {exc}", "query": query}, ensure_ascii=False)
    finally:
        await client.close()

    results = _response_objects(res, "results")
    if results is None:
        return json.dumps({"error": _FORMAT_ERROR, "query": query}, ensure_ascii=False)

    normalized_results = []
    seen_urls = set()
    for result in results:
        raw_url = result.get("url")
        url = safe_public_result_url(raw_url)
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        domain = urlparse(url).netloc
        normalized_results.append(
            {
                "title": result.get("title") or domain,
                "url": url,
                "domain": domain,
                "snippet": result.get("content") or "",
            }
        )

    return json.dumps(normalized_results, indent=2, ensure_ascii=False)


@tool("web_fetch", parse_docstring=True)
async def web_fetch_tool(url: str) -> str:
    """Fetch the contents of a web page at a given URL.
    Only fetch EXACT URLs that have been provided directly by the user or have been returned in results from the web_search and web_fetch tools.
    This tool can NOT access content that requires authentication, such as private Google Docs or pages behind login walls.
    Do NOT add www. to URLs that do NOT have them.
    URLs must include the schema: https://example.com is a valid URL while example.com is an invalid URL.

    Args:
        url: The URL to fetch the contents of.
    """
    client = _get_tavily_client("web_fetch")
    try:
        res = await client.extract([url])
    finally:
        await client.close()
    failed = _response_objects(res, "failed_results")
    if failed is None:
        return f"Error: {_FORMAT_ERROR}"
    if failed:
        error = failed[0].get("error")
        return f"Error: {error}" if error else "Error: Extraction failed"
    results = _response_objects(res, "results")
    if results is None:
        return f"Error: {_FORMAT_ERROR}"
    if not results:
        return "Error: No results found"
    result = results[0]
    # Extract results guarantee a URL and content, but not a page title.
    title = result.get("title") or result.get("url") or url
    raw_content = result.get("raw_content")
    if not isinstance(raw_content, str):
        raw_content = "" if raw_content is None else str(raw_content)
    return f"# {title}\n\n{raw_content[:4096]}"


@tool("web_map", parse_docstring=True)
async def web_map_tool(url: str, max_depth: int = 1) -> str:
    """Discover the site hierarchy and page structure of a target domain using Tavily Map.

    Args:
        url: The root website or domain URL to map.
        max_depth: Maximum hierarchy depth to explore (1-3, default 1).
    """
    import httpx

    config = get_app_config().get_tool_config("web_map")
    api_key = None
    if config is not None and "api_key" in config.model_extra:
        api_key = config.model_extra.get("api_key")
    if not api_key:
        import os

        api_key = os.environ.get("TAVILY_API_KEY")

    if not api_key:
        return json.dumps({"error": "TAVILY_API_KEY is not configured", "url": url})

    try:
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            resp = await http_client.post(
                "https://api.tavily.com/map",
                json={"api_key": api_key, "url": url, "max_depth": max_depth},
            )
            if resp.status_code != 200:
                return json.dumps({"status": "partial", "url": url, "pages": [url], "message": f"Tavily Map returned HTTP {resp.status_code}"})
            data = resp.json()
            return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as exc:
        logger.warning("Tavily Map failed: %s", exc)
        return json.dumps({"error": str(exc), "url": url})


@tool("web_crawl", parse_docstring=True)
async def web_crawl_tool(url: str, max_depth: int = 2, limit: int = 10) -> str:
    """Systematically explore and crawl linked pages of a website using Tavily Crawl.

    Args:
        url: The entry point URL to crawl.
        max_depth: Maximum link depth to follow (default 2).
        limit: Maximum number of pages to extract (default 10).
    """
    import httpx

    config = get_app_config().get_tool_config("web_crawl")
    api_key = None
    if config is not None and "api_key" in config.model_extra:
        api_key = config.model_extra.get("api_key")
    if not api_key:
        import os

        api_key = os.environ.get("TAVILY_API_KEY")

    if not api_key:
        return json.dumps({"error": "TAVILY_API_KEY is not configured", "url": url})

    try:
        async with httpx.AsyncClient(timeout=45.0) as http_client:
            resp = await http_client.post(
                "https://api.tavily.com/crawl",
                json={"api_key": api_key, "url": url, "max_depth": max_depth, "limit": limit},
            )
            if resp.status_code != 200:
                return json.dumps({"status": "partial", "url": url, "limit": limit, "message": f"Tavily Crawl returned HTTP {resp.status_code}"})
            data = resp.json()
            return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as exc:
        logger.warning("Tavily Crawl failed: %s", exc)
        return json.dumps({"error": str(exc), "url": url})


@tool("web_research", parse_docstring=True)
async def web_research_tool(query: str, topic: str = "general") -> str:
    """Conduct comprehensive multi-source deep research on a topic with verified citations using Tavily Research.

    Args:
        query: The detailed topic or research goal.
        topic: Research domain or scope ('general', 'finance', 'news', 'academic').
    """
    import httpx

    config = get_app_config().get_tool_config("web_research")
    api_key = None
    if config is not None and "api_key" in config.model_extra:
        api_key = config.model_extra.get("api_key")
    if not api_key:
        import os

        api_key = os.environ.get("TAVILY_API_KEY")

    if not api_key:
        return json.dumps({"error": "TAVILY_API_KEY is not configured", "query": query})

    try:
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            resp = await http_client.post(
                "https://api.tavily.com/research",
                json={"api_key": api_key, "input": query, "model": "mini", "topic": topic},
            )
            if resp.status_code != 200:
                # Fallback to rich web_search synthesis if dedicated endpoint returns non-200
                client = _get_tavily_client()
                try:
                    res = await client.search(query, search_depth="advanced", max_results=8)
                    return json.dumps(res, indent=2, ensure_ascii=False)
                finally:
                    await client.close()
            data = resp.json()
            return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as exc:
        logger.warning("Tavily Research failed: %s", exc)
        return json.dumps({"error": str(exc), "query": query})
