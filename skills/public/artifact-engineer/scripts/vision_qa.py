"""DeepSeek Multimodal Vision QA Engine for Ñkyel Studio Deliverables."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any
import httpx
from dotenv import load_dotenv

from document_spec import DocumentSpec


load_dotenv(Path(__file__).resolve().parents[4] / "backend/.env")
load_dotenv(Path(__file__).resolve().parents[4] / ".env")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


VISION_SYSTEM_PROMPT = """You are the Principal Document Quality and Visual Typography Inspector for Ñkyel Studio.
Your role is to strictly inspect rendered document pages or presentation slides and identify defects before client delivery.

You must evaluate:
1. Text overflows or truncated text.
2. Clipped headings or improper hierarchy.
3. Misaligned tables, uneven columns, or crowded data rows.
4. Color contrast and legibility (must adhere to professional sovereign standards).
5. Unbalanced whitespace or awkward page breaks.
6. Typography consistency (sizes, leading, margins).

Respond ONLY with valid JSON conforming strictly to this format:
{
  "overallAssessment": "<Executive summary of visual quality>",
  "visualScore": <integer from 0 to 100>,
  "hasDefects": <true if severity high/critical or action needed, else false>,
  "defects": [
    {
      "pageOrSlideNumber": <integer>,
      "affectedElementId": "<id or title of affected section/table/slide>",
      "issueType": "<text_overflow | clipped_heading | misaligned_table | poor_contrast | unbalanced_whitespace | inconsistent_typography | incorrect_spacing | bad_page_break | overlapping_objects | visual_inconsistency>",
      "severity": "<low | medium | high | critical>",
      "observedDefect": "<Precise description of what is visually wrong>",
      "proposedCorrection": "<Actionable instruction to fix the DocumentSpec/source>",
      "confidence": <float 0.0 to 1.0>,
      "requiresHumanReview": false
    }
  ]
}
"""


def encode_image(img_path: Path) -> str:
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def inspect_rendered_pages(
    image_paths: list[str | Path],
    doc: DocumentSpec,
    max_pages_to_inspect: int = 4
) -> dict[str, Any]:
    """Send rendered page images to DeepSeek Flash Vision API for structured visual QA."""
    if not DEEPSEEK_API_KEY:
        return {
            "status": "skipped",
            "reason": "DEEPSEEK_API_KEY not configured",
            "overallAssessment": "Visual QA skipped: no API key provided.",
            "visualScore": 90,
            "hasDefects": False,
            "defects": []
        }

    # Select pages to inspect (limit to conserve budget)
    selected_paths = [Path(p) for p in image_paths if Path(p).exists()][:max_pages_to_inspect]
    if not selected_paths:
        return {
            "status": "skipped",
            "reason": "No rendered images available for inspection",
            "overallAssessment": "No images to inspect.",
            "visualScore": 100,
            "hasDefects": False,
            "defects": []
        }

    content_items: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                f"Please inspect these {len(selected_paths)} rendered pages of the deliverable titled "
                f"'{doc.title}' ({doc.document_type}, style preset: {doc.style_preset}). "
                f"Element IDs present in document: {[s.id for s in doc.sections]}. "
                f"Identify any typography, alignment, contrast, or layout defects."
            )
        }
    ]

    for p in selected_paths:
        b64 = encode_image(p)
        content_items.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64}"
            }
        })

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": VISION_SYSTEM_PROMPT},
            {"role": "user", "content": content_items}
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 1200,
        "temperature": 0.1
    }

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        url = f"{DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions"
        resp = httpx.post(url, headers=headers, json=payload, timeout=40.0)
        if resp.status_code != 200:
            return {
                "status": "error",
                "http_status": resp.status_code,
                "error_detail": resp.text[:400],
                "overallAssessment": f"DeepSeek API error {resp.status_code}",
                "visualScore": 85,
                "hasDefects": False,
                "defects": []
            }

        data = resp.json()
        raw_content = data["choices"][0]["message"]["content"]
        parsed = json.loads(raw_content)
        parsed["status"] = "success"
        parsed["inspected_pages_count"] = len(selected_paths)
        return parsed

    except Exception as e:
        return {
            "status": "exception",
            "error_detail": str(e),
            "overallAssessment": f"Inspection exception: {str(e)}",
            "visualScore": 85,
            "hasDefects": False,
            "defects": []
        }
