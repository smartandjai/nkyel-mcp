"""DeepSeek Vision & Visual Grounding Adapter for Ñkyel Computer.

Provides structured image understanding and screen grounding using deepseek-flash
(with clean fallbacks and coordinate normalization) to assist the autonomous agent.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any

import requests

logger = logging.getLogger(__name__)


@dataclass
class GroundedAction:
    action_type: str  # "click", "type", "scroll", "wait", "inspect"
    target_element: str
    x: int | None = None
    y: int | None = None
    text_to_type: str | None = None
    confidence: float = 1.0
    reasoning: str = ""


class VisualGroundingProvider:
    """Grounding provider for vision-based screen understanding and coordinate estimation."""

    def __init__(self, api_key: str | None = None, model: str = "deepseek-flash") -> None:
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model
        self.base_url = "https://api.deepseek.com/v1"

    @staticmethod
    def normalize_coordinates(x: int, y: int, screen_width: int, screen_height: int) -> tuple[int, int]:
        """Normalize pixel coordinates to a standard 1000x1000 grid (0-1000)."""
        norm_x = int(round((x / max(1, screen_width)) * 1000))
        norm_y = int(round((y / max(1, screen_height)) * 1000))
        return min(1000, max(0, norm_x)), min(1000, max(0, norm_y))

    @staticmethod
    def denormalize_coordinates(norm_x: int, norm_y: int, screen_width: int, screen_height: int) -> tuple[int, int]:
        """Convert normalized (0-1000) coordinates back to actual screen resolution pixels."""
        x = int(round((norm_x / 1000.0) * screen_width))
        y = int(round((norm_y / 1000.0) * screen_height))
        return min(screen_width, max(0, x)), min(screen_height, max(0, y))

    def analyze_screen(
        self,
        screenshot_b64: str,
        screen_width: int = 1024,
        screen_height: int = 768,
        instruction: str = "Describe the visible screen and identify key interactive elements",
    ) -> dict[str, Any]:
        """Analyze screen screenshot and return structured observation."""
        if not self.api_key:
            return {"success": False, "error": "DEEPSEEK_API_KEY not configured", "observation": "Vision model unavailable; proceeding with DOM automation."}

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        prompt = (
            f"You are the visual cortex of an autonomous computer agent. "
            f"Screen Resolution: {screen_width}x{screen_height}.\n"
            f"User Goal: {instruction}\n"
            f"Carefully analyze what is on screen. Return your analysis as valid JSON with keys:\n"
            f"- 'active_window': title or description of focused window\n"
            f"- 'visible_elements': list of prominent interactive controls\n"
            f"- 'recommended_action': {{'action': 'click'|'type'|'scroll'|'inspect', 'target': 'description', 'x': x_coord_or_null, 'y': y_coord_or_null}}\n"
            f"- 'summary': short summary of the screen state\n"
        )

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}}]}],
            "max_tokens": 800,
            "temperature": 0.1,
        }

        try:
            resp = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=25)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                # Extract JSON if enclosed in markdown blocks
                json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
                raw_json = json_match.group(1) if json_match else content.strip()
                try:
                    parsed = json.loads(raw_json)
                    return {"success": True, "data": parsed, "raw": content}
                except Exception:
                    return {"success": True, "data": {"summary": content}, "raw": content}
            else:
                logger.warning(f"DeepSeek vision call returned HTTP {resp.status_code}: {resp.text}")
                return {"success": False, "error": f"HTTP {resp.status_code}", "observation": "Visual inspection fallback: using DOM and physical window state."}
        except Exception as e:
            logger.warning(f"Vision provider failed: {e}")
            return {"success": False, "error": str(e), "observation": "Visual inspection fallback: continuing via direct browser DOM / system calls."}


# Singleton provider instance
visual_grounding = VisualGroundingProvider()
