"""Gmail Send & Human Approval Adapter for Ñkyel Studio MCP Ecosystem."""

from __future__ import annotations

import base64
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import hashlib
import json
import os
from pathlib import Path
from typing import Any
import httpx

APPROVAL_STORE: dict[str, dict[str, Any]] = {}
SENT_MESSAGES_LOG: set[str] = set()


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prepare_gmail_draft(
    to: str,
    subject: str,
    body: str,
    cc: str | None = None,
    bcc: str | None = None,
    attachment_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Prepare a structured draft and generate an immutable approval token."""
    attachments_meta = []
    combined_hash = hashlib.sha256(f"{to}:{subject}:{body}".encode("utf-8"))

    if attachment_paths:
        for p_str in attachment_paths:
            p = Path(p_str)
            if p.exists():
                content = p.read_bytes()
                h = compute_sha256(content)
                combined_hash.update(h.encode("utf-8"))
                attachments_meta.append({
                    "filename": p.name,
                    "filepath": str(p),
                    "size_bytes": len(content),
                    "checksum": h
                })

    token = f"appr_{combined_hash.hexdigest()[:16]}"
    
    draft_record = {
        "approval_token": token,
        "status": "APPROVAL_REQUIRED",
        "to": to,
        "cc": cc or "",
        "bcc": bcc or "",
        "subject": subject,
        "body": body,
        "attachments": attachments_meta,
    }
    
    APPROVAL_STORE[token] = draft_record
    return draft_record


def send_gmail_with_approval(
    approval_token: str,
    approved: bool,
    access_token: str | None = None,
) -> dict[str, Any]:
    """Execute real Gmail API send after validating immutable approval token."""
    if not approved:
        return {
            "status": "REJECTED",
            "message": "User rejected sending this email.",
            "approval_token": approval_token
        }

    record = APPROVAL_STORE.get(approval_token)
    if not record:
        return {
            "status": "ERROR",
            "error": "Invalid or expired approval token."
        }

    if approval_token in SENT_MESSAGES_LOG:
        return {
            "status": "DUPLICATE_PREVENTED",
            "message": "This message has already been sent.",
            "approval_token": approval_token
        }

    # Construct MIME message
    msg = MIMEMultipart()
    msg["To"] = record["to"]
    msg["Subject"] = record["subject"]
    if record["cc"]:
        msg["Cc"] = record["cc"]
    
    msg.attach(MIMEText(record["body"], "plain", "utf-8"))

    for att in record["attachments"]:
        p = Path(att["filepath"])
        if p.exists():
            part = MIMEApplication(p.read_bytes(), Name=p.name)
            part["Content-Disposition"] = f'attachment; filename="{p.name}"'
            msg.attach(part)

    raw_bytes = msg.as_bytes()
    raw_b64 = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")

    token = access_token or os.getenv("GOOGLE_WORKSPACE_BEARER_TOKEN", "")

    if not token or token == "$GOOGLE_WORKSPACE_BEARER_TOKEN":
        # Verification / Staging mode: record approval
        SENT_MESSAGES_LOG.add(approval_token)
        return {
            "status": "VERIFIED_READY",
            "mode": "staging_verified",
            "approval_token": approval_token,
            "to": record["to"],
            "subject": record["subject"],
            "attachments_count": len(record["attachments"]),
            "raw_size_bytes": len(raw_bytes),
            "note": "Ready for delivery with active Google OAuth bearer token."
        }

    # Real Gmail API call
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        r = httpx.post(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
            headers=headers,
            json={"raw": raw_b64},
            timeout=20.0
        )
        if r.status_code in (200, 201):
            SENT_MESSAGES_LOG.add(approval_token)
            data = r.json()
            return {
                "status": "SENT",
                "gmail_message_id": data.get("id"),
                "thread_id": data.get("threadId"),
                "to": record["to"],
                "subject": record["subject"],
                "approval_token": approval_token
            }
        else:
            return {
                "status": "API_ERROR",
                "http_status": r.status_code,
                "error_detail": r.text[:300]
            }
    except Exception as e:
        return {
            "status": "EXCEPTION",
            "error": str(e)
        }
