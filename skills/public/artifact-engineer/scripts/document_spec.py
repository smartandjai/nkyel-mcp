"""DocumentSpec: Validated, versioned structured intermediate representation for Ñkyel Studio deliverables."""

from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class ThemeTokens(BaseModel):
    primary_color: str = "#1e293b"      # Slate 800
    secondary_color: str = "#3b82f6"    # Blue 500
    accent_color: str = "#0ea5e9"       # Sky 500
    bg_color: str = "#ffffff"
    text_color: str = "#0f172a"          # Slate 900
    muted_color: str = "#64748b"         # Slate 500
    font_family_headline: str = "Helvetica"
    font_family_body: str = "Helvetica"
    margin_cm: float = 2.0


class TableColumn(BaseModel):
    header: str
    key: str
    width_ratio: float = 1.0
    alignment: Literal["left", "center", "right"] = "left"


class TableData(BaseModel):
    id: str
    title: str = ""
    caption: str = ""
    columns: list[TableColumn] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)


class Citation(BaseModel):
    id: str
    url: str | None = None
    title: str
    authors: str = ""
    access_date: str = ""
    notes: str = ""


class ParagraphBlock(BaseModel):
    text: str
    style: Literal["normal", "lead", "callout", "quote", "bullet", "numbered"] = "normal"
    bold_prefix: str = ""


class DocumentSection(BaseModel):
    id: str
    title: str
    level: int = 1
    page_break_before: bool = False
    paragraphs: list[ParagraphBlock] = Field(default_factory=list)
    tables: list[TableData] = Field(default_factory=list)
    key_metrics: list[dict[str, str]] = Field(default_factory=list)


class SlideContent(BaseModel):
    slide_number: int
    layout: Literal["title", "content", "two_column", "metric_highlight", "table"] = "content"
    title: str
    subtitle: str = ""
    bullets: list[str] = Field(default_factory=list)
    metrics: list[dict[str, str]] = Field(default_factory=list)
    table: TableData | None = None
    speaker_notes: str = ""


class SheetColumn(BaseModel):
    header: str
    key: str
    width: int = 15
    number_format: str = "@"  # Text, Currency, Percentage, Integer, Float


class SheetData(BaseModel):
    name: str
    columns: list[SheetColumn] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    freeze_panes: str = "A2"
    has_total_row: bool = False


class DocumentSpec(BaseModel):
    version: str = "2.0"
    document_id: str
    document_type: Literal["report", "policy_brief", "presentation", "workbook", "letter"]
    title: str
    subtitle: str = ""
    author: str = "Ñkyel Studio"
    organization: str = "SmartANDJ AI Technologies"
    date: str = "2026-10-27"
    language: str = "fr"
    audience: str = "Executive & Technical Stakeholders"
    purpose: str = "Competitive Benchmark & Sovereign Deliverable"
    style_preset: Literal[
        "executive_report",
        "policy_brief",
        "corporate_report",
        "academic_report",
        "consulting_presentation",
        "investor_deck",
        "data_workbook"
    ] = "executive_report"
    theme: ThemeTokens = Field(default_factory=ThemeTokens)
    
    # Document content
    executive_summary: str = ""
    sections: list[DocumentSection] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    
    # Presentation content (PPTX)
    slides: list[SlideContent] = Field(default_factory=list)
    
    # Workbook content (XLSX)
    sheets: list[SheetData] = Field(default_factory=list)
