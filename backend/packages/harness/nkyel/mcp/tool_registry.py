"""Unified MCP & Native Tool Registry for Ñkyel Studio (50 Verified Tools)."""

from __future__ import annotations

from typing import Any, Literal

ToolStatus = Literal["VERIFIED", "FAILED", "UNAVAILABLE", "NOT_TESTED"]

TOOL_REGISTRY: dict[str, dict[str, Any]] = {
    # ─── 1. GOOGLE DRIVE MCP (8 TOOLS) ───────────────────────────────────────────
    "gdrive_search_files": {"category": "drive", "server": "google-drive", "status": "VERIFIED", "description": "Search for Drive files using structured queries"},
    "gdrive_list_recent_files": {"category": "drive", "server": "google-drive", "status": "VERIFIED", "description": "List recently accessed or modified Drive files"},
    "gdrive_get_file_metadata": {"category": "drive", "server": "google-drive", "status": "VERIFIED", "description": "Retrieve comprehensive metadata for a Drive file"},
    "gdrive_read_file_content": {"category": "drive", "server": "google-drive", "status": "VERIFIED", "description": "Read file text and structured content from Drive"},
    "gdrive_download_file_content": {"category": "drive", "server": "google-drive", "status": "VERIFIED", "description": "Download raw Drive file content as base64"},
    "gdrive_create_file": {"category": "drive", "server": "google-drive", "status": "VERIFIED", "description": "Upload or create a new file in Google Drive"},
    "gdrive_copy_file": {"category": "drive", "server": "google-drive", "status": "VERIFIED", "description": "Create a copy of an existing Drive file"},
    "gdrive_get_file_permissions": {"category": "drive", "server": "google-drive", "status": "VERIFIED", "description": "List access permissions of a Drive document"},

    # ─── 2. GMAIL MCP & SEND ADAPTER (19 TOOLS) ──────────────────────────────────
    "gmail_create_draft": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Create email draft in authenticated Gmail"},
    "gmail_list_drafts": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "List all active Gmail drafts"},
    "gmail_get_draft": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Retrieve content of a specific Gmail draft"},
    "gmail_get_thread": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Retrieve email thread with all messages"},
    "gmail_get_message": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Retrieve single message details"},
    "gmail_search_threads": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Search email threads by query"},
    "gmail_label_thread": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Apply labels to an email thread"},
    "gmail_unlabel_thread": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Remove labels from an email thread"},
    "gmail_trash_thread": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Move thread to Gmail trash"},
    "gmail_untrash_thread": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Restore thread from trash"},
    "gmail_mark_thread_spam": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Mark thread as spam"},
    "gmail_unmark_thread_spam": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Remove spam flag from thread"},
    "gmail_list_labels": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "List all labels on account"},
    "gmail_label_message": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Apply label to specific message"},
    "gmail_update_message_labels": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Add or remove labels atomically"},
    "gmail_unlabel_message": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Remove label from message"},
    "gmail_create_label": {"category": "email", "server": "gmail", "status": "VERIFIED", "description": "Create a new Gmail label"},
    "gmail_prepare_draft_with_attachment": {"category": "email", "server": "gmail_adapter", "status": "VERIFIED", "description": "Prepare structured draft with PDF/DOCX and generate approval token"},
    "gmail_send_with_approval": {"category": "email", "server": "gmail_adapter", "status": "VERIFIED", "description": "Send email with attachments after explicit human consent"},

    # ─── 3. TAVILY RESEARCH MCP (5 TOOLS) ────────────────────────────────────────
    "tavily_search": {"category": "research", "server": "tavily", "status": "VERIFIED", "description": "Real-time web search with domain filters"},
    "tavily_extract": {"category": "research", "server": "tavily", "status": "VERIFIED", "description": "Extract clean markdown from web pages"},
    "tavily_crawl": {"category": "research", "server": "tavily", "status": "VERIFIED", "description": "Crawl domain subpages recursively"},
    "tavily_map": {"category": "research", "server": "tavily", "status": "VERIFIED", "description": "Discover sitemap and URL hierarchy"},
    "tavily_research": {"category": "research", "server": "tavily", "status": "VERIFIED", "description": "Autonomous comprehensive research report"},

    # ─── 4. E2B LIVE VISUAL COMPUTER (7 TOOLS) ───────────────────────────────────
    "computer_launch_session": {"category": "browser", "server": "e2b_desktop", "status": "VERIFIED", "description": "Launch Chrome desktop sandbox with live stream"},
    "computer_navigate": {"category": "browser", "server": "e2b_desktop", "status": "VERIFIED", "description": "Navigate to URL in streamed Chrome"},
    "computer_click": {"category": "browser", "server": "e2b_desktop", "status": "VERIFIED", "description": "Click coordinate (x,y) with left/right/double click"},
    "computer_scroll": {"category": "browser", "server": "e2b_desktop", "status": "VERIFIED", "description": "Scroll browser view up or down"},
    "computer_type_text": {"category": "browser", "server": "e2b_desktop", "status": "VERIFIED", "description": "Type text into focused form element"},
    "computer_take_screenshot": {"category": "browser", "server": "e2b_desktop", "status": "VERIFIED", "description": "Capture current desktop screenshot"},
    "computer_close_session": {"category": "browser", "server": "e2b_desktop", "status": "VERIFIED", "description": "Clean up and terminate cloud sandbox"},

    # ─── 5. ARTIFACT ENGINEERING DELIVERABLES (4 TOOLS) ──────────────────────────
    "render_pdf_deliverable": {"category": "artifact", "server": "artifact_engineer", "status": "VERIFIED", "description": "Compile high-typography PDF with Typst 0.15"},
    "render_docx_deliverable": {"category": "artifact", "server": "artifact_engineer", "status": "VERIFIED", "description": "Generate 100% editable Microsoft Word document"},
    "render_pptx_deliverable": {"category": "artifact", "server": "artifact_engineer", "status": "VERIFIED", "description": "Generate 100% editable 16:9 PowerPoint deck"},
    "render_xlsx_deliverable": {"category": "artifact", "server": "artifact_engineer", "status": "VERIFIED", "description": "Build Excel workbook with calculation formulas"},

    # ─── 6. WEB KNOWLEDGE & DOCUMENTATION MCP (7 TOOLS) ──────────────────────────
    "duckduckgo_search": {"category": "search", "server": "duckduckgo", "status": "VERIFIED", "description": "Fast web search via DuckDuckGo"},
    "fetch_webpage": {"category": "search", "server": "fetch", "status": "VERIFIED", "description": "Convert HTML page to clean Markdown"},
    "wikipedia_search": {"category": "knowledge", "server": "wikipedia", "status": "VERIFIED", "description": "Search encyclopedia articles"},
    "wikipedia_summary": {"category": "knowledge", "server": "wikipedia", "status": "VERIFIED", "description": "Fetch summary of an encyclopedia page"},
    "wikipedia_page": {"category": "knowledge", "server": "wikipedia", "status": "VERIFIED", "description": "Fetch full text and sections of article"},
    "arxiv_search": {"category": "academic", "server": "arxiv", "status": "VERIFIED", "description": "Search arXiv scientific papers"},
    "arxiv_download": {"category": "academic", "server": "arxiv", "status": "VERIFIED", "description": "Download research paper PDF metadata"}
}


def get_verified_tools_count() -> int:
    return len(TOOL_REGISTRY)


def get_tools_for_mission(categories: list[str]) -> list[dict[str, Any]]:
    """Return tool schemas relevant to the current mission without prompt bloat."""
    return [
        {"name": k, **v} for k, v in TOOL_REGISTRY.items()
        if v["category"] in categories
    ]
