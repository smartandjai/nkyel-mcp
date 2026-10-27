---
name: artifact-engineer
description: Produce genuinely professional, publication-grade PDF, DOCX, PPTX, and XLSX deliverables using native open-source compilation engines (Typst, python-docx, python-pptx, openpyxl) with DeepSeek Multimodal Vision QA and automated targeted defect correction.
---

# Ñkyel Studio — Professional Artifact Engineering Skill

## Overview

This skill replaces unstructured Markdown-to-file exports with a sovereign, production-grade document and presentation publishing pipeline.

Instead of writing raw unformatted files or relying on screenshots, this skill executes a verified, multi-stage engineering workflow:
1. **Content Intelligence & Provenance**: Gathers verified factual findings, metrics, and citations without hallucinating data.
2. **DocumentSpec (Intermediate Representation)**: Generates a structured, validated JSON intermediate specification.
3. **Template Token System**: Applies typographic hierarchy, color tokens, and margin rules from high-end presets (`executive_report`, `policy_brief`, `corporate_report`, `consulting_presentation`, `investor_deck`, `data_workbook`).
4. **Specialized Open-Source Compilers**:
   - **PDF**: Compiled with the Rust-based Typst engine (vector typography, dynamic headers/footers, math, tables, callouts).
   - **DOCX**: Generated with `python-docx` (true Word headings, editable tables, standard XML container).
   - **PPTX**: Built with `python-pptx` (genuine 16:9 widescreen slides, editable text boxes, metric cards, styled tables).
   - **XLSX**: Built with `openpyxl` (real Excel formulas like `=SUM()`, freeze panes `A2`, auto-fit columns, styled headers).
5. **Deterministic Pre-flight Validation**: Verifies container integrity, magic bytes, non-empty text, and formula syntax before vision analysis.
6. **DeepSeek Multimodal Vision QA**: Renders page/slide PNG images and submits them to DeepSeek Flash multimodal vision for defect analysis (text overflow, contrast, misalignment, typography).
7. **Automated Targeted Correction**: Executes up to 2 repair iterations adjusting real DocumentSpec parameters before final delivery.
8. **Cloud Storage & Delivery**: Publishes artifacts to Cloudflare R2 (`nkyel-artifacts-prod`) and records metadata in Neon PostgreSQL.

---

## Supported Deliverable Presets

| Preset | Format Targets | Key Characteristics |
|---|---|---|
| `executive_report` | PDF + DOCX | Slate 800 & Blue palette, executive summary card, metric highlights, data tables, page numbering, citations. |
| `policy_brief` | PDF + DOCX | Navy & Amber palette, high-density two-column layout, callouts, strict provenance tracking. |
| `corporate_report` | PDF + DOCX | Dark Zinc & Emerald, modern sans-serif, KPI cards, corporate governance styling. |
| `consulting_presentation` | PPTX | 16:9 widescreen, 4-card metric layouts, structured tables, editable bullet points, speaker notes. |
| `investor_deck` | PPTX | High-contrast dark or crisp white, valuation/traction tables, financial metric callouts. |
| `data_workbook` | XLSX | Styled table headers, frozen top row (`A2`), auto-fit widths, formula totals (`=SUM`, `=AVERAGE`). |

---

## How to Execute the Pipeline

When generating deliverables, the agent writes a `DocumentSpec` JSON file and runs the orchestrator script:

```bash
# In backend virtualenv or sandbox
python skills/public/artifact-engineer/scripts/artifact_pipeline.py \
  --spec /path/to/spec.json \
  --output-dir /mnt/user-data/workspace/output \
  --formats pdf docx pptx xlsx
```

### DocumentSpec Structure Example

```json
{
  "document_id": "rapport_souverainete_2026",
  "document_type": "report",
  "title": "Rapport Stratégique de Souveraineté Numérique",
  "subtitle": "Benchmarks comparatifs & Infrastructure Souveraine Ñkyel",
  "author": "Ñkyel Studio",
  "organization": "SmartANDJ AI Technologies",
  "date": "2026-10-27",
  "language": "fr",
  "style_preset": "executive_report",
  "executive_summary": "Synthèse des performances et de la résilience du socle agentique souverain...",
  "sections": [
    {
      "id": "sec_benchmarks",
      "title": "Banc d'Essai Comparatif des Moteurs",
      "level": 1,
      "page_break_before": false,
      "paragraphs": [
        {
          "text": "L'intégration du compilateur Typst offre un gain de vitesse de 8x par rapport aux moteurs LaTeX traditionnels.",
          "style": "normal"
        }
      ],
      "tables": [
        {
          "id": "tbl_latence",
          "title": "Indicateurs de Performance Documentaire",
          "columns": [
            {"header": "Moteur", "key": "engine", "width_ratio": 1.2, "alignment": "left"},
            {"header": "Temps de Compilation", "key": "time", "width_ratio": 1.0, "alignment": "right"},
            {"header": "Score Qualité Visuelle", "key": "score", "width_ratio": 1.0, "alignment": "center"}
          ],
          "rows": [
            {"engine": "Typst Native (Ñkyel)", "time": "85 ms", "score": "98 / 100"},
            {"engine": "Chromium Headless", "time": "640 ms", "score": "84 / 100"}
          ]
        }
      ]
    }
  ],
  "citations": [
    {
      "id": "cit_1",
      "title": "Spécification Typst 0.15 — High Performance Document Compilation",
      "url": "https://typst.app/docs",
      "access_date": "2026-10-27"
    }
  ]
}
```

---

## Editability Rules

1. **DOCX and PPTX deliverables MUST contain real, native text and objects**.
2. Never substitute flattened slide screenshots for real PPTX presentations when editability is requested.
3. Spreadsheets MUST contain real calculation formulas (`=SUM`, `=AVERAGE`), not hardcoded calculated numbers.
4. Always inspect page renderings with DeepSeek Vision before delivering final assets to the client.
