"""Preset design systems and templates for Ñkyel Studio deliverables."""

from __future__ import annotations
from document_spec import ThemeTokens

PRESET_THEMES: dict[str, ThemeTokens] = {
    "executive_report": ThemeTokens(
        primary_color="#0f172a",     # Deep Slate
        secondary_color="#2563eb",   # Vibrant Blue
        accent_color="#0ea5e9",      # Cyan
        bg_color="#ffffff",
        text_color="#1e293b",
        muted_color="#64748b",
        font_family_headline="Helvetica",
        font_family_body="Helvetica",
        margin_cm=2.2,
    ),
    "policy_brief": ThemeTokens(
        primary_color="#1e3a5f",     # Deep Navy
        secondary_color="#b45309",   # Amber Gold
        accent_color="#0284c7",
        bg_color="#ffffff",
        text_color="#0f172a",
        muted_color="#475569",
        font_family_headline="Helvetica",
        font_family_body="Helvetica",
        margin_cm=2.5,
    ),
    "corporate_report": ThemeTokens(
        primary_color="#111827",     # Charcoal
        secondary_color="#059669",   # Emerald
        accent_color="#10b981",
        bg_color="#ffffff",
        text_color="#1f2937",
        muted_color="#6b7280",
        font_family_headline="Helvetica",
        font_family_body="Helvetica",
        margin_cm=2.0,
    ),
    "academic_report": ThemeTokens(
        primary_color="#18181b",     # Zinc Black
        secondary_color="#4f46e5",   # Indigo
        accent_color="#6366f1",
        bg_color="#ffffff",
        text_color="#27272a",
        muted_color="#71717a",
        font_family_headline="Helvetica",
        font_family_body="Helvetica",
        margin_cm=2.5,
    ),
    "consulting_presentation": ThemeTokens(
        primary_color="#0a192f",     # Midnight Navy
        secondary_color="#00b4d8",   # Tech Cyan
        accent_color="#90e0ef",
        bg_color="#f8fafc",
        text_color="#0f172a",
        muted_color="#64748b",
        font_family_headline="Helvetica",
        font_family_body="Helvetica",
        margin_cm=1.5,
    ),
    "investor_deck": ThemeTokens(
        primary_color="#030712",     # True Black
        secondary_color="#10b981",   # Sovereign Green
        accent_color="#34d399",
        bg_color="#ffffff",
        text_color="#111827",
        muted_color="#4b5563",
        font_family_headline="Helvetica",
        font_family_body="Helvetica",
        margin_cm=1.2,
    ),
    "data_workbook": ThemeTokens(
        primary_color="#134e4a",     # Teal Dark
        secondary_color="#0d9488",   # Teal Light
        accent_color="#14b8a6",
        bg_color="#ffffff",
        text_color="#042f2e",
        muted_color="#5eead4",
        font_family_headline="Helvetica",
        font_family_body="Helvetica",
        margin_cm=1.0,
    ),
}

def get_theme_for_preset(preset_name: str) -> ThemeTokens:
    return PRESET_THEMES.get(preset_name, PRESET_THEMES["executive_report"])


TEMPLATE_PRESETS = PRESET_THEMES
