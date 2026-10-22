# -*- coding: utf-8 -*-
"""Render Polaroid bottom information area in an isolated process.

This worker intentionally does only one rendering attempt with explicit font paths.
If a platform/FreeType font crashes, only this subprocess dies; the main process
can retry with another font or safely skip the annotation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont


def _hex_to_rgba(value: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    value = (value or "#666666").strip().lstrip("#")
    if len(value) != 6:
        return 102, 102, 102, alpha
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha


def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(path)
    layout = getattr(ImageFont, "Layout", None)
    if layout is not None:
        return ImageFont.truetype(str(path_obj), size=size, layout_engine=layout.BASIC)
    return ImageFont.truetype(str(path_obj), size=size)


def _bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> Tuple[int, int, int, int]:
    if not text:
        return 0, 0, 0, 0
    return draw.textbbox((0, 0), text, font=font)


def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
    b = _bbox(draw, text, font)
    return max(0, b[2] - b[0]), max(0, b[3] - b[1])


def _fit_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> str:
    text = text or ""
    if _text_size(draw, text, font)[0] <= max_width:
        return text
    ellipsis = "…"
    result = text
    while result:
        candidate = result + ellipsis
        if _text_size(draw, candidate, font)[0] <= max_width:
            return candidate
        result = result[:-1]
    return ellipsis


def _format_date_for_design(timestamp: str) -> str:
    timestamp = (timestamp or "").strip()
    if not timestamp:
        return ""
    # 2026.04.12 -> 2 0 2 6 . 0 4 . 1 2
    if " " in timestamp:
        date_part, time_part = timestamp.split(" ", 1)
        spaced_date = " ".join(list(date_part))
        return f"{spaced_date}   {time_part}"
    return " ".join(list(timestamp))


def _draw_tracking_text(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: Tuple[int, int, int, int],
    tracking: float = 0.0,
) -> None:
    # Use normal drawing if tracking is tiny. It is cleaner and avoids over-spaced dots.
    if not text or tracking <= 0.01:
        draw.text(xy, text, font=font, fill=fill)
        return

    x, y = xy
    extra = max(0, int(font.size * tracking))
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        w, _ = _text_size(draw, ch, font)
        x += w + extra


def _tracked_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, tracking: float) -> int:
    if not text:
        return 0
    if tracking <= 0.01:
        return _text_size(draw, text, font)[0]
    extra = max(0, int(font.size * tracking))
    widths = [_text_size(draw, ch, font)[0] for ch in text]
    return sum(widths) + extra * max(0, len(text) - 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--title-font", required=True)
    parser.add_argument("--body-font", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))

    frame_w = int(payload["frame_width"])
    frame_h = int(payload["frame_height"])
    photo_x = int(payload["photo_x"])
    photo_y = int(payload["photo_y"])
    photo_w = int(payload["photo_width"])
    photo_h = int(payload["photo_height"])
    bottom_margin = int(payload["bottom_margin"])

    title = str(payload.get("title", "") or "").strip()
    signature = str(payload.get("signature", "") or "").strip()
    timestamp = str(payload.get("timestamp", "") or "").strip()
    note = str(payload.get("note", "") or "").strip()

    title_size = max(24, int(photo_w * float(payload.get("title_size_ratio", 0.047))))
    body_size = max(13, int(photo_w * float(payload.get("body_size_ratio", 0.020))))
    date_size = max(13, int(photo_w * float(payload.get("date_size_ratio", 0.018))))
    note_size = max(13, int(photo_w * float(payload.get("note_size_ratio", 0.018))))

    title_font = _load_font(args.title_font, title_size)
    body_font = _load_font(args.body_font, body_size)
    date_font = _load_font(args.body_font, date_size)
    note_font = _load_font(args.body_font, note_size)

    overlay = Image.new("RGBA", (frame_w, frame_h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    title_color = _hex_to_rgba(payload.get("title_color", "#555555"))
    signature_color = _hex_to_rgba(payload.get("signature_color", "#707070"))
    date_color = _hex_to_rgba(payload.get("date_color", "#666666"))
    note_color = _hex_to_rgba(payload.get("note_color", "#777777"))
    divider_color = _hex_to_rgba(payload.get("divider_color", "#B8B8B8"))

    bottom_top = photo_y + photo_h
    safe_left = photo_x + max(8, int(photo_w * 0.014))
    safe_right = photo_x + photo_w - max(8, int(photo_w * 0.014))
    # Large blank Polaroid area: place text in its visual middle, slightly upper.
    left_y = bottom_top + max(18, int(bottom_margin * 0.24))
    right_y = bottom_top + max(22, int(bottom_margin * 0.31))

    left_max = int(photo_w * 0.48)
    right_max = int(photo_w * 0.43)

    if title:
        title = _fit_text(draw, title, title_font, left_max)
        draw.text((safe_left, left_y), title, font=title_font, fill=title_color)
        title_w, title_h = _text_size(draw, title, title_font)
    else:
        title_w, title_h = 0, 0

    divider_y = left_y + title_h + max(8, int(bottom_margin * 0.07))
    if title_w > 0 and payload.get("show_divider", True):
        line_len = max(int(title_w * 0.92), int(photo_w * 0.16))
        line_len = min(line_len, int(photo_w * 0.30))
        draw.line(
            (safe_left, divider_y, safe_left + line_len, divider_y),
            fill=divider_color,
            width=max(1, int(photo_w * 0.0015)),
        )

    if signature:
        sig_y = divider_y + max(10, int(bottom_margin * 0.11))
        signature = _fit_text(draw, signature, body_font, left_max)
        # Keep signature clean. No excessive tracking.
        _draw_tracking_text(draw, (safe_left, sig_y), signature, body_font, signature_color, tracking=0.03)

    date_text = _format_date_for_design(timestamp)
    if date_text:
        date_text = _fit_text(draw, date_text, date_font, right_max)
        date_w, date_h = _text_size(draw, date_text, date_font)
        draw.text((safe_right - date_w, right_y), date_text, font=date_font, fill=date_color)
    else:
        date_h = 0

    if note:
        note_y = right_y + date_h + max(14, int(bottom_margin * 0.17))
        note = _fit_text(draw, note, note_font, right_max)
        # Slight tracking only. Avoid making it look like tiny separate dots.
        tracking = 0.06
        note_w = _tracked_width(draw, note, note_font, tracking)
        _draw_tracking_text(draw, (safe_right - note_w, note_y), note, note_font, note_color, tracking=tracking)

    overlay.save(args.output, "PNG")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        raise SystemExit(1)
