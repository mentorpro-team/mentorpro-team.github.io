#!/usr/bin/env python3
"""Generate small JPG thumbnails for story banners.

Story banners (`assets/images/stories/<slug>.png`) are 1200×630 PNG (~850 KB).
For the accordion summary card they only render at ~130×76 (desktop) or
~88×52 (mobile). Loading 7 × 850 KB just for thumbnails is wasteful, so
this script generates 360×189 JPG variants targeted ≤ 30 KB each at
`assets/images/stories/thumbs/<slug>.jpg`.

Run from project root:

    .venv/bin/python scripts/build_thumbnails.py
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Cần Pillow: .venv/bin/pip install Pillow")

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "assets" / "images" / "stories"
OUT_DIR = SRC_DIR / "thumbs"
TARGET_W = 360
TARGET_H = 189
JPG_QUALITY = 82  # Sweet spot for crisp text + small file

SLUGS = [
    "trang-ant",
    "khanhchuong-anz",
    "tien-sap",
    "chan-deputy",
    "viet-vinbigdata",
    "hau-nab",
    "long-mbbank",
    "tuan-vin",
    "khanhchuong-vin-grab",
    "dat-axon",
    "hieu-ibm-vin",
    "thy-cognizant",
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total_in = 0
    total_out = 0
    for slug in SLUGS:
        src = SRC_DIR / f"{slug}.png"
        if not src.exists():
            print(f"  ✗ {src.name} not found, skipping", file=sys.stderr)
            continue
        dst = OUT_DIR / f"{slug}.jpg"
        with Image.open(src) as im:
            im = im.convert("RGB")
            im.thumbnail((TARGET_W, TARGET_H), Image.LANCZOS)
            im.save(
                dst,
                "JPEG",
                quality=JPG_QUALITY,
                optimize=True,
                progressive=True,
            )
        in_kb = src.stat().st_size / 1024
        out_kb = dst.stat().st_size / 1024
        total_in += in_kb
        total_out += out_kb
        print(f"  ✓ {slug:24} {in_kb:6.0f} KB → {out_kb:5.1f} KB  ({(out_kb/in_kb)*100:.1f}%)")
    print(f"\n  Tổng: {total_in:.0f} KB → {total_out:.1f} KB  "
          f"(tiết kiệm {total_in - total_out:.0f} KB, {(1 - total_out/total_in)*100:.1f}%)")


if __name__ == "__main__":
    main()
