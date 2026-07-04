#!/usr/bin/env python3
"""Build MentorPro static site.

Đọc ``MentorPro.md``, tách thành các tab theo header ``# Tab N — ...``,
render Markdown sang HTML và nhúng vào template ``templates/index.html``.
Kết quả ghi ra thư mục ``docs/`` để GitHub Pages serve.
"""

from __future__ import annotations

import datetime
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.stderr.write(
        "Thiếu thư viện 'markdown'. Chạy: make install  (hoặc pip install markdown)\n"
    )
    sys.exit(1)


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "MentorPro.md"
TEMPLATE = ROOT / "templates" / "index.html"
ASSETS_DIR = ROOT / "assets"
OUT_DIR = ROOT / "docs"

# ── Single source of truth cho các URL/asset path công khai ────────────────
SITE_URL = "https://mentorpro-team.github.io/"
SITE_NAME = "MentorPro"
OG_IMAGE_URL = SITE_URL + "images/brand/banner-job-offer.jpg"
LOGO_URL = SITE_URL + "images/brand/mentor-pro.png"

CONFIG = {
    "SITE_URL": SITE_URL,
    "SITE_NAME": SITE_NAME,
    "OG_IMAGE_URL": OG_IMAGE_URL,
    "LOGO_URL": LOGO_URL,
}

TAB_HEADER_RE = re.compile(r"^# Tab (\d+)\s*[—-]\s*(.+?)\s*$", re.MULTILINE)
TOC_LINK_RE = re.compile(r"\n\[⬆ Về mục lục\][^\n]*\n")
TRAILING_SEPARATOR_RE = re.compile(r"\n-{3,}\s*$")


def slugify(text: str) -> str:
    """Đơn giản: lowercase, bỏ dấu, thay khoảng trắng bằng dấu gạch."""
    import unicodedata

    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "tab"


def split_tabs(markdown_text: str) -> tuple[str, list[dict]]:
    """Trả về (intro, [{num, title, body_md}, ...])."""
    matches = list(TAB_HEADER_RE.finditer(markdown_text))
    if not matches:
        raise SystemExit("Không tìm thấy header '# Tab N — ...' trong MentorPro.md")

    intro = markdown_text[: matches[0].start()].rstrip()

    tabs: list[dict] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
        body = markdown_text[m.end() : end]
        body = TOC_LINK_RE.sub("\n", body)
        body = TRAILING_SEPARATOR_RE.sub("", body).strip()
        tabs.append(
            {
                "num": m.group(1),
                "title": m.group(2).strip(),
                "body_md": body,
            }
        )
    return intro, tabs


def extract_hero(intro_md: str) -> tuple[str, str]:
    """Lấy title (H1) và tagline (blockquote đầu tiên) từ phần intro."""
    title_match = re.search(r"^#\s+(.+?)\s*$", intro_md, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "MentorPro"

    tagline_match = re.search(r"^>\s*(.+?)\s*$", intro_md, re.MULTILINE)
    tagline_md = tagline_match.group(1).strip() if tagline_match else ""
    tagline_html = markdown.markdown(tagline_md).removeprefix("<p>").removesuffix("</p>")
    return title, tagline_html


def render_markdown(body_md: str) -> str:
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", "attr_list", "toc", "md_in_html"],
        output_format="html5",
    )
    return md.convert(body_md)


def build_html(template: str, title: str, tagline: str, tabs: list[dict]) -> str:
    nav_items = []
    panels = []

    title_safe = html.escape(title, quote=False)

    for idx, tab in enumerate(tabs):
        is_active = idx == 0
        slug = slugify(tab["title"])
        panel_id = f"tab-{tab['num']}-{slug}"
        button_id = f"tab-btn-{tab['num']}-{slug}"
        tab_title_safe = html.escape(tab["title"], quote=False)

        nav_items.append(
            f'<button id="{button_id}" '
            f'class="tab-btn{" is-active" if is_active else ""}" '
            f'role="tab" aria-selected="{"true" if is_active else "false"}" '
            f'aria-controls="{panel_id}" data-target="{panel_id}">'
            f'<span class="tab-num">{tab["num"]}</span>'
            f'<span class="tab-name">{tab_title_safe}</span>'
            f"</button>"
        )

        panel_html = render_markdown(tab["body_md"])
        # Inject h2 (visually-hidden — visible với screen reader, SEO crawler,
        # và no-JS fallback. CSS .visually-hidden ẩn về mặt thị giác khi JS bật.)
        h2 = f'<h2 class="visually-hidden tab-heading">{tab_title_safe}</h2>'
        panels.append(
            f'<section class="tab-panel{" is-active" if is_active else ""}" '
            f'id="{panel_id}" role="tabpanel" '
            f'aria-labelledby="{button_id}" '
            f'aria-hidden="{"false" if is_active else "true"}">'
            f"{h2}{panel_html}"
            f"</section>"
        )

    result = (
        template.replace("{{TITLE}}", title_safe)
        .replace("{{TAGLINE}}", tagline)
        .replace("{{NAV}}", "\n          ".join(nav_items))
        .replace("{{PANELS}}", "\n        ".join(panels))
    )
    # Replace centralized config placeholders ({{SITE_URL}}, {{OG_IMAGE_URL}}, …)
    for key, value in CONFIG.items():
        result = result.replace("{{" + key + "}}", value)
    return result


def copy_assets() -> None:
    for asset in ASSETS_DIR.iterdir():
        target = OUT_DIR / asset.name
        if asset.is_file():
            shutil.copy2(asset, target)
        elif asset.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(asset, target)


def write_robots() -> None:
    """Allow all crawlers and point to the sitemap."""
    txt = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {SITE_URL}sitemap.xml\n"
    )
    (OUT_DIR / "robots.txt").write_text(txt, encoding="utf-8")


def _content_last_modified() -> str:
    """Return the latest modification date of content sources (ISO 8601).

    Strategy:
    1. Prefer the latest git commit timestamp for tracked content files —
       this makes lastmod reproducible regardless of clone/build time.
    2. Fall back to the latest filesystem mtime when git is unavailable.
    """
    content_files = [
        SRC,
        TEMPLATE,
        ASSETS_DIR / "style.css",
        ASSETS_DIR / "script.js",
    ]
    # Try git log (most accurate, ignores rebuild noise)
    try:
        out = subprocess.run(
            [
                "git", "-C", str(ROOT), "log", "-1",
                "--format=%cI",
                "--",
                *(str(p.relative_to(ROOT)) for p in content_files if p.exists()),
            ],
            capture_output=True, text=True, check=True, timeout=5,
        )
        stamp = out.stdout.strip()
        if stamp:
            return stamp.split("T", 1)[0]
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: filesystem mtime
    mtimes = [p.stat().st_mtime for p in content_files if p.exists()]
    if mtimes:
        return datetime.date.fromtimestamp(max(mtimes)).isoformat()
    return datetime.date.today().isoformat()


def write_sitemap() -> None:
    """Single-page sitemap; lastmod = max(content file mtimes / git commit)."""
    last_mod = _content_last_modified()
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '  <url>\n'
        f'    <loc>{SITE_URL}</loc>\n'
        f'    <lastmod>{last_mod}</lastmod>\n'
        '    <changefreq>weekly</changefreq>\n'
        '    <priority>1.0</priority>\n'
        '  </url>\n'
        '</urlset>\n'
    )
    (OUT_DIR / "sitemap.xml").write_text(xml, encoding="utf-8")


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Không tìm thấy {SRC}")
    if not TEMPLATE.exists():
        raise SystemExit(f"Không tìm thấy template {TEMPLATE}")

    md_text = SRC.read_text(encoding="utf-8")
    intro_md, tabs = split_tabs(md_text)
    title, tagline = extract_hero(intro_md)
    template = TEMPLATE.read_text(encoding="utf-8")
    html = build_html(template, title, tagline, tabs)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")

    if ASSETS_DIR.exists():
        copy_assets()

    write_robots()
    write_sitemap()

    nojekyll = OUT_DIR / ".nojekyll"
    if not nojekyll.exists():
        nojekyll.write_text("")

    print(f"  → {OUT_DIR / 'index.html'}")
    for asset in OUT_DIR.iterdir():
        if asset.name not in {"index.html"}:
            print(f"  → {asset}")
    print(f"  Tabs: {', '.join(t['title'] for t in tabs)}")


if __name__ == "__main__":
    main()
