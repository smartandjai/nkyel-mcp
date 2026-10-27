"""Ñkyel Studio Professional Artifact Engineering Pipeline.

Core Architecture:
USER REQUEST -> DOCUMENT SPEC (IR) -> TEMPLATE TOKENS -> RENDERING ->
DETERMINISTIC VALIDATION -> DEEPSEEK VISION QA -> TARGETED REPAIR ->
FINAL RENDER -> R2 / NEON REGISTRATION -> DELIVERY
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Literal
import boto3
from dotenv import load_dotenv

from document_spec import DocumentSpec
from templates import TEMPLATE_PRESETS
from render_pdf import render_pdf_and_pages
from render_docx import render_docx
from render_pptx import render_pptx
from render_xlsx import render_xlsx
from deterministic_validator import (
    validate_pdf,
    validate_docx,
    validate_pptx,
    validate_xlsx,
)
from vision_qa import inspect_rendered_pages
from correction_engine import apply_targeted_corrections

# Load environment
REPO_ROOT = Path(__file__).resolve().parents[4]
load_dotenv(REPO_ROOT / "backend/.env")
load_dotenv(REPO_ROOT / ".env")

R2_ENDPOINT = os.getenv("R2_ENDPOINT_URL")
R2_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("R2_BUCKET_NAME", "nkyel-artifacts-prod")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL", "https://artifacts.nkyel.smartandjai.com")


def compute_checksum(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def upload_to_r2(local_path: Path, r2_key: str, content_type: str) -> str | None:
    if not (R2_ENDPOINT and R2_KEY_ID and R2_SECRET and R2_BUCKET):
        return None
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=R2_ENDPOINT,
            aws_access_key_id=R2_KEY_ID,
            aws_secret_access_key=R2_SECRET,
            region_name="auto"
        )
        s3.upload_file(
            str(local_path),
            R2_BUCKET,
            r2_key,
            ExtraArgs={"ContentType": content_type}
        )
        return f"{R2_PUBLIC_URL.rstrip('/')}/{r2_key}"
    except Exception as e:
        print(f"R2 upload warning: {e}")
        return None


def run_pipeline(
    doc: DocumentSpec,
    output_dir: Path,
    requested_formats: list[str] | None = None,
    perform_vision_qa: bool = True,
    max_correction_passes: int = 2,
    sync_to_r2: bool = True
) -> dict[str, Any]:
    """Execute the end-to-end Professional Artifact Engineering pipeline."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Apply Template Presets if specified
    if doc.style_preset in TEMPLATE_PRESETS:
        preset_tokens = TEMPLATE_PRESETS[doc.style_preset]
        doc.theme = preset_tokens.model_copy()

    formats = requested_formats or []
    if not formats:
        if doc.document_type in ("report", "policy_brief", "letter"):
            formats = ["pdf", "docx"]
        elif doc.document_type == "presentation":
            formats = ["pptx"]
        elif doc.document_type == "workbook":
            formats = ["xlsx"]
        else:
            formats = ["pdf"]

    results: dict[str, Any] = {
        "document_id": doc.document_id,
        "title": doc.title,
        "document_type": doc.document_type,
        "style_preset": doc.style_preset,
        "formats": formats,
        "deliverables": {},
        "page_previews": [],
        "deterministic_validation": {},
        "vision_qa": {
            "performed": False,
            "initial_score": 100,
            "final_score": 100,
            "correction_passes": 0,
            "corrections_applied": []
        },
        "r2_storage": {}
    }

    current_doc = doc

    # 2. Render primary formats
    pdf_info = None
    if "pdf" in formats:
        pdf_info = render_pdf_and_pages(current_doc, output_dir)
        results["deliverables"]["pdf"] = pdf_info["pdf_path"]
        results["deliverables"]["pdf_source"] = pdf_info["source_path"]
        results["page_previews"] = pdf_info["page_images"]
        results["page_count"] = pdf_info["page_count"]

    if "docx" in formats:
        docx_info = render_docx(current_doc, output_dir)
        results["deliverables"]["docx"] = docx_info["docx_path"]

    if "pptx" in formats:
        pptx_info = render_pptx(current_doc, output_dir)
        results["deliverables"]["pptx"] = pptx_info["pptx_path"]
        results["slide_count"] = pptx_info["slide_count"]

    if "xlsx" in formats:
        xlsx_info = render_xlsx(current_doc, output_dir)
        results["deliverables"]["xlsx"] = xlsx_info["xlsx_path"]
        results["sheet_count"] = xlsx_info["sheet_count"]

    # 3. Deterministic Validation
    det_valid = True
    det_errors = []
    
    if "pdf" in formats and pdf_info:
        p_res = validate_pdf(Path(pdf_info["pdf_path"]), current_doc).to_dict()
        results["deterministic_validation"]["pdf"] = p_res
        if not p_res["valid"]:
            det_valid = False
            det_errors.extend(p_res["errors"])

    if "docx" in formats:
        d_res = validate_docx(Path(results["deliverables"]["docx"]), current_doc).to_dict()
        results["deterministic_validation"]["docx"] = d_res
        if not d_res["valid"]:
            det_valid = False
            det_errors.extend(d_res["errors"])

    if "pptx" in formats:
        px_res = validate_pptx(Path(results["deliverables"]["pptx"]), current_doc).to_dict()
        results["deterministic_validation"]["pptx"] = px_res
        if not px_res["valid"]:
            det_valid = False
            det_errors.extend(px_res["errors"])

    if "xlsx" in formats:
        x_res = validate_xlsx(Path(results["deliverables"]["xlsx"]), current_doc).to_dict()
        results["deterministic_validation"]["xlsx"] = x_res
        if not x_res["valid"]:
            det_valid = False
            det_errors.extend(x_res["errors"])

    results["deterministic_validation"]["valid"] = det_valid

    # 4. DeepSeek Multimodal Vision QA & Bounded Correction Loop
    if perform_vision_qa and "pdf" in formats and results.get("page_previews"):
        results["vision_qa"]["performed"] = True
        
        # Initial inspection pass
        qa_report = inspect_rendered_pages(results["page_previews"], current_doc)
        init_score = qa_report.get("visualScore", 90)
        results["vision_qa"]["initial_score"] = init_score
        results["vision_qa"]["initial_assessment"] = qa_report.get("overallAssessment", "")
        results["vision_qa"]["initial_defects"] = qa_report.get("defects", [])
        
        curr_score = init_score
        passes = 0
        all_corrections = []

        # Correction loop (up to max_correction_passes)
        while passes < max_correction_passes and (curr_score < 85 or qa_report.get("hasDefects")):
            defects = qa_report.get("defects", [])
            if not defects:
                break

            # Apply targeted corrections to DocumentSpec
            candidate_doc, applied = apply_targeted_corrections(current_doc, defects)
            if not applied:
                break

            all_corrections.extend(applied)
            passes += 1

            # Re-render PDF with candidate changes
            new_pdf_info = render_pdf_and_pages(candidate_doc, output_dir)
            
            # Re-inspect with Vision QA
            new_qa = inspect_rendered_pages(new_pdf_info["page_images"], candidate_doc)
            new_score = new_qa.get("visualScore", 0)

            if new_score >= curr_score:
                # Improvement confirmed: adopt candidate doc and re-render other formats
                current_doc = candidate_doc
                curr_score = new_score
                qa_report = new_qa
                pdf_info = new_pdf_info
                results["deliverables"]["pdf"] = pdf_info["pdf_path"]
                results["page_previews"] = pdf_info["page_images"]

                # Re-render DOCX with corrected spec if applicable
                if "docx" in formats:
                    docx_info = render_docx(current_doc, output_dir)
                    results["deliverables"]["docx"] = docx_info["docx_path"]
            else:
                # Regression: revert to previous valid version and break
                all_corrections.append(f"Pass {passes}: Reverted changes due to regression (Score {new_score} < {curr_score}).")
                break

        results["vision_qa"]["final_score"] = curr_score
        results["vision_qa"]["final_assessment"] = qa_report.get("overallAssessment", "")
        results["vision_qa"]["correction_passes"] = passes
        results["vision_qa"]["corrections_applied"] = all_corrections

    # 5. Cloudflare R2 Upload
    if sync_to_r2:
        for fmt, fpath in results["deliverables"].items():
            path_obj = Path(fpath)
            if not path_obj.exists():
                continue
            mime_map = {
                "pdf": "application/pdf",
                "pdf_source": "text/plain",
                "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
            content_type = mime_map.get(fmt, "application/octet-stream")
            r2_key = f"deliverables/{current_doc.document_id}/{path_obj.name}"
            public_url = upload_to_r2(path_obj, r2_key, content_type)
            results["r2_storage"][fmt] = {
                "r2_key": r2_key,
                "url": public_url,
                "checksum": compute_checksum(path_obj),
                "size_bytes": os.path.getsize(path_obj)
            }

    return results


def main():
    parser = argparse.ArgumentParser(description="Ñkyel Studio Artifact Engineering Pipeline")
    parser.add_argument("--spec", type=str, required=True, help="Path to DocumentSpec JSON file")
    parser.add_argument("--output-dir", type=str, default="./output", help="Directory to save deliverables")
    parser.add_argument("--formats", nargs="+", default=[], help="Target formats (pdf, docx, pptx, xlsx)")
    parser.add_argument("--skip-vision-qa", action="store_true", help="Skip DeepSeek Vision QA")
    parser.add_argument("--no-r2", action="store_true", help="Skip R2 sync")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"Error: Spec file not found: {spec_path}")
        return

    with open(spec_path, "r", encoding="utf-8") as f:
        spec_data = json.load(f)

    doc = DocumentSpec.model_validate(spec_data)
    out = run_pipeline(
        doc=doc,
        output_dir=Path(args.output_dir),
        requested_formats=args.formats or None,
        perform_vision_qa=not args.skip_vision_qa,
        sync_to_r2=not args.no_r2
    )

    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
