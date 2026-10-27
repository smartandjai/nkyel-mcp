#!/usr/bin/env python3
"""Generate the Ñkyel MCP catalog into extensions_config.json.

Usage:  python scripts/nkyel_mcp_catalog.py [path/to/extensions_config.json]

- Servers that need no credential, or whose credential is present in the
  environment, are enabled.
- Servers whose credential is missing are written disabled with a French
  description saying which variable/OAuth is required, so the Connexions UI
  lists them honestly instead of showing broken tools.
- Existing non-MCP keys (skills, middlewares, ...) are preserved.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NPX = "npx"
UVX = "uvx"


def stdio(cmd, args, desc, env=None, needs=None, timeout=120):
    return {"type": "stdio", "command": cmd, "args": args, "env": env or {}, "description": desc, "_needs": needs or [], "session_init_timeout": timeout, "tool_call_timeout": 180}


def http(url, desc, headers=None, needs=None, oauth=False):
    return {"type": "http", "url": url, "headers": headers or {}, "description": desc, "_needs": needs or [], "_oauth": oauth, "session_init_timeout": 60}


CATALOG: dict[str, dict] = {
    # ── Ñkyel Research ────────────────────────────────────────────────────
    "tavily": http("https://mcp.tavily.com/mcp/", "Ñkyel Recherche — Tavily officiel : search, extract, map, crawl, research", {"Authorization": "$TAVILY_MCP_AUTH"}, ["TAVILY_MCP_AUTH"]),
    "exa": http("https://mcp.exa.ai/mcp", "Recherche web neuronale Exa (code, entreprises, articles)"),
    "parallel-search": http("https://search.parallel.ai/mcp", "Recherche web et lecture de pages Parallel", {"User-Agent": "nkyel"}),
    "duckduckgo": stdio(UVX, ["duckduckgo-mcp-server"], "Recherche DuckDuckGo et lecture de pages"),
    "fetch": stdio(UVX, ["mcp-server-fetch"], "Récupère une URL et la convertit en Markdown"),
    "wikipedia": stdio(UVX, ["wikipedia-mcp"], "Articles, résumés et sections Wikipédia"),
    "arxiv": stdio(UVX, ["arxiv-mcp-server", "--storage-path", "$NKYEL_MCP_WORKSPACE"], "Recherche et lecture d'articles scientifiques arXiv"),
    "youtube-transcript": stdio(NPX, ["-y", "@kimtaeyoon83/mcp-server-youtube-transcript"], "Transcriptions de vidéos YouTube"),
    "deepwiki": http("https://mcp.deepwiki.com/mcp", "Documentation générée des dépôts GitHub publics (DeepWiki)"),
    "context7": http("https://mcp.context7.com/mcp", "Documentation à jour des bibliothèques logicielles (Context7)"),
    "gitmcp": http("https://gitmcp.io/docs", "Documentation de n'importe quel dépôt GitHub (GitMCP)"),
    "microsoft-learn": http("https://learn.microsoft.com/api/mcp", "Documentation officielle Microsoft Learn"),
    "aws-knowledge": http("https://knowledge-mcp.global.api.aws", "Documentation officielle AWS"),
    "cloudflare-docs": http("https://docs.mcp.cloudflare.com/mcp", "Documentation officielle Cloudflare"),
    # ── Ñkyel Computer ────────────────────────────────────────────────────
    "e2b": stdio("node" if os.getenv("NKYEL_E2B_MCP_ENTRY") else NPX, [os.getenv("NKYEL_E2B_MCP_ENTRY")] if os.getenv("NKYEL_E2B_MCP_ENTRY") else ["-y", "@e2b/mcp-server"], "Ñkyel Ordinateur — exécution de code dans un bac à sable cloud E2B", {"E2B_API_KEY": "$E2B_API_KEY"}, ["E2B_API_KEY"], 180),
    "filesystem": stdio(NPX, ["-y", "@modelcontextprotocol/server-filesystem", "$NKYEL_MCP_WORKSPACE"], "Lecture/écriture de fichiers dans l'espace de travail Ñkyel", needs=["NKYEL_MCP_WORKSPACE"]),
    "git": stdio(UVX, ["mcp-server-git", "--repository", "$NKYEL_MCP_GIT_REPO"], "Historique, diff et statut d'un dépôt Git", needs=["NKYEL_MCP_GIT_REPO"]),
    "sqlite": stdio(UVX, ["mcp-server-sqlite", "--db-path", "$NKYEL_MCP_SQLITE"], "Base SQLite locale pour analyses de données", needs=["NKYEL_MCP_SQLITE"]),
    # ── Ñkyel Studio / office ─────────────────────────────────────────────
    "markitdown": stdio(UVX, ["markitdown-mcp"], "Convertit PDF, DOCX, PPTX, XLSX, images en Markdown (Microsoft)"),
    "excel": stdio(UVX, ["excel-mcp-server", "stdio"], "Création et édition de classeurs Excel", {"EXCEL_FILES_PATH": "$NKYEL_MCP_WORKSPACE"}),
    # ── Raisonnement / utilitaires ────────────────────────────────────────
    "sequential-thinking": stdio(NPX, ["-y", "@modelcontextprotocol/server-sequential-thinking"], "Raisonnement structuré étape par étape"),
    "memory": stdio(NPX, ["-y", "@modelcontextprotocol/server-memory"], "Graphe de connaissances persistant"),
    "time": stdio(UVX, ["mcp-server-time", "--local-timezone", "Africa/Libreville"], "Heure et conversions de fuseaux horaires"),
    "calculator": stdio(UVX, ["mcp-server-calculator"], "Calculs mathématiques exacts"),
    "everything": stdio(NPX, ["-y", "@modelcontextprotocol/server-everything"], "Serveur de référence MCP : outils, ressources, prompts, sampling"),
    "airbnb": stdio(NPX, ["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"], "Recherche d'hébergements Airbnb"),
    "qdrant": stdio(UVX, ["mcp-server-qdrant"], "Mémoire vectorielle sémantique (collection démo isolée)", {"QDRANT_URL": "$QDRANT_URL", "QDRANT_API_KEY": "$QDRANT_API_KEY", "COLLECTION_NAME": "nkyel_demo_mcp"}, ["QDRANT_URL", "QDRANT_API_KEY"]),
    # ── Productivité (identifiants requis) ────────────────────────────────
    "github": http("https://api.githubcopilot.com/mcp/", "GitHub : dépôts, issues, pull requests, code", {"Authorization": "$GITHUB_MCP_AUTH"}, ["GITHUB_MCP_AUTH"]),
    "gmail": stdio(NPX, ["-y", "@gongrzhe/server-gmail-autoauth-mcp"], "Gmail : lire, chercher, envoyer des e-mails", needs=["GMAIL_OAUTH_PATH"], env={"GMAIL_OAUTH_PATH": "$GMAIL_OAUTH_PATH", "GMAIL_CREDENTIALS_PATH": "$GMAIL_CREDENTIALS_PATH"}),
    "google-drive": stdio(NPX, ["-y", "@modelcontextprotocol/server-gdrive"], "Google Drive : chercher et lire des documents", {"GDRIVE_CREDENTIALS_PATH": "$GDRIVE_CREDENTIALS_PATH"}, ["GDRIVE_CREDENTIALS_PATH"]),
    "google-maps": stdio(NPX, ["-y", "@modelcontextprotocol/server-google-maps"], "Google Maps : lieux, itinéraires, géocodage", {"GOOGLE_MAPS_API_KEY": "$GOOGLE_MAPS_API_KEY"}, ["GOOGLE_MAPS_API_KEY"]),
    "resend": stdio(NPX, ["-y", "resend-mcp"], "Envoi d'e-mails transactionnels (Resend)", {"RESEND_API_KEY": "$RESEND_API_KEY"}, ["RESEND_API_KEY"]),
    "slack": stdio(NPX, ["-y", "@modelcontextprotocol/server-slack"], "Slack : canaux, messages, réponses", {"SLACK_BOT_TOKEN": "$SLACK_BOT_TOKEN", "SLACK_TEAM_ID": "$SLACK_TEAM_ID"}, ["SLACK_BOT_TOKEN", "SLACK_TEAM_ID"]),
    "notion": stdio(NPX, ["-y", "@notionhq/notion-mcp-server"], "Notion : pages et bases de données", {"NOTION_TOKEN": "$NOTION_TOKEN"}, ["NOTION_TOKEN"]),
    "brave-search": stdio(NPX, ["-y", "@brave/brave-search-mcp-server"], "Recherche web Brave", {"BRAVE_API_KEY": "$BRAVE_API_KEY"}, ["BRAVE_API_KEY"]),
    "firecrawl": stdio(NPX, ["-y", "firecrawl-mcp"], "Scraping et crawl web Firecrawl", {"FIRECRAWL_API_KEY": "$FIRECRAWL_API_KEY"}, ["FIRECRAWL_API_KEY"]),
    "airtable": stdio(NPX, ["-y", "airtable-mcp-server"], "Airtable : bases et enregistrements", {"AIRTABLE_API_KEY": "$AIRTABLE_API_KEY"}, ["AIRTABLE_API_KEY"]),
    "todoist": stdio(NPX, ["-y", "@abhiz123/todoist-mcp-server"], "Todoist : tâches et projets", {"TODOIST_API_TOKEN": "$TODOIST_API_TOKEN"}, ["TODOIST_API_TOKEN"]),
    "elevenlabs": stdio(UVX, ["elevenlabs-mcp"], "Synthèse vocale ElevenLabs", {"ELEVENLABS_API_KEY": "$ELEVENLABS_API_KEY"}, ["ELEVENLABS_API_KEY"]),
    "perplexity": stdio(NPX, ["-y", "server-perplexity-ask"], "Recherche Perplexity Sonar", {"PERPLEXITY_API_KEY": "$PERPLEXITY_API_KEY"}, ["PERPLEXITY_API_KEY"]),
    "stripe": http("https://mcp.stripe.com", "Stripe : paiements, clients, factures", {"Authorization": "$STRIPE_MCP_AUTH"}, ["STRIPE_MCP_AUTH"]),
    "postgres-neon": stdio(NPX, ["-y", "@modelcontextprotocol/server-postgres", "$NKYEL_MCP_POSTGRES_URL"], "PostgreSQL en lecture seule (base démo dédiée)", needs=["NKYEL_MCP_POSTGRES_URL"]),
    # ── OAuth (connexion utilisateur via Paramètres → Connexions) ─────────
    "linear": http("https://mcp.linear.app/mcp", "Linear : issues et projets", oauth=True),
    "notion-remote": http("https://mcp.notion.com/mcp", "Notion (OAuth officiel)", oauth=True),
    "atlassian": http("https://mcp.atlassian.com/v1/sse", "Jira et Confluence", oauth=True),
    "asana": http("https://mcp.asana.com/sse", "Asana : tâches et projets", oauth=True),
    "sentry": http("https://mcp.sentry.dev/mcp", "Sentry : erreurs et performances", oauth=True),
    "cloudflare-bindings": http("https://bindings.mcp.cloudflare.com/mcp", "Cloudflare Workers, KV, R2, D1", oauth=True),
    "neon": http("https://mcp.neon.tech/mcp", "Neon : projets et branches PostgreSQL", oauth=True),
    "vercel": http("https://mcp.vercel.com", "Vercel : déploiements et projets", oauth=True),
    "figma": http("https://mcp.figma.com/mcp", "Figma : fichiers de design", oauth=True),
    "hubspot": http("https://mcp.hubspot.com/anthropic", "HubSpot CRM", oauth=True),
    "paypal": http("https://mcp.paypal.com/mcp", "PayPal : transactions et factures", oauth=True),
    "intercom": http("https://mcp.intercom.com/mcp", "Intercom : conversations clients", oauth=True),
    "zapier": http("https://mcp.zapier.com/api/mcp/mcp", "Zapier : 8000+ applications", oauth=True),
}


def main() -> None:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "extensions_config.json"
    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / "backend" / ".env")
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    data = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
    data.setdefault("middlewares", [])
    data["mcpInterceptors"] = [i for i in data.get("mcpInterceptors", []) if not i.startswith("my_package.")]
    servers = {}
    enabled = []
    for name, spec in CATALOG.items():
        spec = dict(spec)
        needs = spec.pop("_needs")
        oauth = spec.pop("_oauth", False)
        missing = [v for v in needs if not os.getenv(v)]
        on = not missing and not oauth
        if missing:
            spec["description"] += f" — requiert {', '.join(missing)}"
        if oauth:
            spec["description"] += " — connexion OAuth requise"
        if spec["type"] != "stdio":
            spec.pop("tool_call_timeout", None)
        spec["enabled"] = on
        spec["tool_name_prefix"] = True
        servers[name] = spec
        if on:
            enabled.append(name)
    data["mcpServers"] = servers
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(servers)} MCP servers written, {len(enabled)} enabled:")
    print("  " + ", ".join(enabled))


if __name__ == "__main__":
    main()
