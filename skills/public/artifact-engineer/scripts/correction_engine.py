"""Automated Targeted Correction Engine for Ñkyel Studio Deliverables."""

from __future__ import annotations

import copy
from typing import Any

from document_spec import DocumentSpec, DocumentSection, TableData


def apply_targeted_corrections(
    doc: DocumentSpec,
    defects: list[dict[str, Any]]
) -> tuple[DocumentSpec, list[str]]:
    """Apply targeted modifications to DocumentSpec based on vision QA findings."""
    new_doc = doc.model_copy(deep=True)
    applied_corrections: list[str] = []

    for defect in defects:
        issue_type = defect.get("issueType", "").lower()
        target_id = str(defect.get("affectedElementId", "")).strip().lower()
        page_num = defect.get("pageOrSlideNumber", 1)

        # 1. Text Overflow or Bad Page Break
        if "overflow" in issue_type or "break" in issue_type or "page" in issue_type:
            # Check if we should insert a page break on sections
            corrected = False
            for sec in new_doc.sections:
                if sec.id.lower() == target_id or target_id in sec.title.lower():
                    sec.page_break_before = True
                    applied_corrections.append(f"Added page break before section '{sec.title}' (ID: {sec.id}) to resolve overflow.")
                    corrected = True
                    break
            
            # If no specific section matched, gently optimize document margin
            if not corrected and new_doc.theme.margin_cm > 1.6:
                new_doc.theme.margin_cm = max(1.6, round(new_doc.theme.margin_cm - 0.2, 1))
                applied_corrections.append(f"Adjusted page margin to {new_doc.theme.margin_cm}cm to eliminate text clipping/overflow.")

        # 2. Table Misalignment or Crowding
        elif "table" in issue_type or "misalign" in issue_type or "column" in issue_type:
            found_table = False
            for sec in new_doc.sections:
                for table in sec.tables:
                    if table.id.lower() == target_id or target_id in table.title.lower():
                        # Equalize and balance column ratios
                        for col in table.columns:
                            col.width_ratio = 1.0
                        applied_corrections.append(f"Rebalanced column widths and alignment for table '{table.title or table.id}'.")
                        found_table = True
                        break
                if found_table:
                    break
            
            if not found_table and new_doc.sections:
                # Apply table balance across any tables found
                for sec in new_doc.sections:
                    for table in sec.tables:
                        for col in table.columns:
                            col.width_ratio = 1.0
                        applied_corrections.append(f"Standardized column ratios on table '{table.id}'.")

        # 3. Poor Contrast
        elif "contrast" in issue_type or "color" in issue_type:
            new_doc.theme.primary_color = "#0f172a"    # Slate 900 (ultra high contrast)
            new_doc.theme.text_color = "#020617"       # Slate 950
            new_doc.theme.secondary_color = "#1d4ed8"  # High-contrast Royal Blue
            applied_corrections.append("Upgraded palette tokens to high-contrast sovereign standard (Slate 950 / Royal Blue).")

        # 4. Spacing / Typography Hierarchy
        elif "spacing" in issue_type or "typography" in issue_type or "heading" in issue_type:
            for sec in new_doc.sections:
                if sec.level > 2:
                    sec.level = 2
            applied_corrections.append("Normalized heading hierarchy to level 1 and 2.")

        # 5. Slide Balance (for PPTX)
        elif "slide" in issue_type and new_doc.slides:
            for slide in new_doc.slides:
                if slide.slide_number == page_num or str(slide.slide_number) == target_id:
                    if len(slide.bullets) > 4:
                        slide.bullets = slide.bullets[:4]
                        applied_corrections.append(f"Trimmed bullet points on slide {slide.slide_number} to prevent visual crowding.")

    return new_doc, applied_corrections
