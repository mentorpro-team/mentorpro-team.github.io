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


def build_html(template: str, title: str, tagline: str, tabs: list[dict]) -> tuple[str, list[str]]:
    nav_items = []
    panels = []

    title_safe = html.escape(title, quote=False)

    tab_slugs: list[str] = []
    for idx, tab in enumerate(tabs):
        is_active = idx == 0
        slug = slugify(tab["title"])
        tab_slugs.append(slug)
        # Panel id = slug (drops the noisy `tab-N-` prefix so URLs stay clean
        # when routing via pathname: /thong-tin-mentor, /cau-chuyen-thanh-cong…).
        # Button id keeps the `nav-` prefix to remain unique.
        panel_id = slug
        button_id = f"nav-{slug}"
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
    return result, tab_slugs


STORY_BLOCK_RE = re.compile(
    r'<details class="story-card">\s*'
    r'<summary class="story-summary">'
    r'([\s\S]*?)'         # group 1 — summary inner html
    r'</summary>\s*'
    r'([\s\S]*?)'         # group 2 — body html
    r'\s*</details>',
    re.MULTILINE,
)

SLUG_FROM_IMG_RE = re.compile(
    r'src="images/stories/(?:thumbs/)?([a-z0-9-]+)\.(?:png|jpg|jpeg|webp)"'
)


def _extract_story(summary_inner: str, body_html: str) -> dict | None:
    """Pull structured fields out of a rendered story <details> block."""
    m_slug = SLUG_FROM_IMG_RE.search(summary_inner)
    if not m_slug:
        return None
    slug = m_slug.group(1)

    m_title = re.search(r'<span class="story-title">([\s\S]*?)</span>', summary_inner)
    title = m_title.group(1).strip() if m_title else "Câu chuyện thành công"

    m_tag = re.search(r'<span class="story-tagline">([\s\S]*?)</span>', summary_inner)
    tagline = m_tag.group(1).strip() if m_tag else ""

    m_num = re.search(r'<span class="story-num">#(\d+)</span>', summary_inner)
    num = m_num.group(1) if m_num else "?"

    # First non-blockquote <p> for meta description
    desc_html = re.search(
        r'(?:<h3[^>]*>[\s\S]*?</h3>\s*)?<p>([\s\S]*?)</p>', body_html
    )
    desc = ""
    if desc_html:
        desc = re.sub(r"<[^>]+>", "", desc_html.group(1))
        desc = html.unescape(desc).strip()
        if len(desc) > 160:
            desc = desc[:157].rstrip() + "…"

    # Drop the first <h3> (doc headline) — it becomes <h1> on the detail page.
    body_cleaned = re.sub(
        r"\A\s*<h3[^>]*>[\s\S]*?</h3>\s*", "", body_html, count=1
    )

    return {
        "slug": slug,
        "num": num,
        "title": title,
        "tagline": tagline,
        "description": desc,
        "body_html": body_cleaned,
        "summary_inner": summary_inner,
    }


def _card_link_html(story: dict) -> str:
    """Home-page click-through card that replaces the old accordion."""
    # Swap the down-caret for a forward arrow so the affordance matches a link.
    inner = story["summary_inner"].replace("▾", "→")
    return (
        f'<a class="story-card story-card--link" href="/success-story/{story["slug"]}/">\n'
        f'{inner}'
        f'</a>'
    )


def _write_story_page(
    story: dict,
    prev_s: dict | None,
    next_s: dict | None,
    template: str,
) -> None:
    """Render one story detail page into ``docs/success-story/<slug>/``."""
    story_url = f"{SITE_URL}success-story/{story['slug']}/"
    banner_rel = f"images/stories/{story['slug']}.png"
    banner_abs = SITE_URL + banner_rel

    def other(s: dict | None, fallback_url: str, fallback_title: str) -> tuple[str, str]:
        if s is None:
            return fallback_url, fallback_title
        return f"/success-story/{s['slug']}/", s["title"]

    prev_url, prev_title = other(prev_s, "/cau-chuyen-thanh-cong", "Xem tất cả câu chuyện")
    next_url, next_title = other(next_s, "/cau-chuyen-thanh-cong", "Xem tất cả câu chuyện")

    def esc(text: str) -> str:
        return html.escape(text, quote=True)

    # JSON string escaping: use json.dumps for safety, strip the outer quotes.
    import json
    json_title = json.dumps(story["title"], ensure_ascii=False)[1:-1]

    substitutions = {
        "STORY_URL":            story_url,
        "STORY_TITLE":          esc(story["title"]),
        "STORY_TITLE_JSON":     json_title,
        "STORY_OG_TITLE":       esc(f"{story['title']} — {SITE_NAME}"),
        "STORY_TAGLINE":        esc(story["tagline"]),
        "STORY_DESCRIPTION":    esc(story["description"] or story["tagline"] or f"Câu chuyện thành công #{story['num']} tại MentorPro."),
        "STORY_NUM":            story["num"],
        "STORY_BANNER_URL":     banner_abs,
        "STORY_BANNER_URL_REL": banner_rel,
        "STORY_ALT":            esc(story["tagline"] or story["title"]),
        "STORY_BODY":           story["body_html"],
        "PREV_URL":             prev_url,
        "PREV_TITLE":           esc(prev_title),
        "NEXT_URL":             next_url,
        "NEXT_TITLE":           esc(next_title),
        **CONFIG,
    }

    page = template
    for key, value in substitutions.items():
        page = page.replace("{{" + key + "}}", value)

    out_dir = OUT_DIR / "success-story" / story["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8")


def write_story_pages(html_output: str) -> tuple[str, list[dict]]:
    """Extract all story blocks, generate detail pages, return new home HTML + list.

    The home page keeps a preview card per story (banner thumbnail + title +
    tagline) but the click target now navigates to a dedicated URL instead of
    toggling an accordion. Prev/next on each detail page is circular so users
    can walk through the collection in either direction.
    """
    story_tpl_path = ROOT / "templates" / "story.html"
    if not story_tpl_path.exists():
        # Legacy fallback — keep accordion behaviour if template missing.
        return html_output, []
    story_template = story_tpl_path.read_text(encoding="utf-8")
    # Substitute CONFIG placeholders once for values that are the same across
    # all story pages (site URL, logo, etc.). Story-specific keys are handled
    # inside _write_story_page.
    for key, value in CONFIG.items():
        story_template = story_template.replace("{{" + key + "}}", value)

    stories: list[dict] = []
    for m in STORY_BLOCK_RE.finditer(html_output):
        data = _extract_story(m.group(1), m.group(2))
        if data is not None:
            stories.append(data)

    for i, s in enumerate(stories):
        prev_s = stories[(i - 1) % len(stories)]
        next_s = stories[(i + 1) % len(stories)]
        _write_story_page(s, prev_s, next_s, story_template)

    def _replace(m: re.Match) -> str:
        data = _extract_story(m.group(1), m.group(2))
        if data is None:
            return m.group(0)
        return _card_link_html(data)

    new_html = STORY_BLOCK_RE.sub(_replace, html_output)
    return new_html, stories


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


def write_sitemap(
    tab_slugs: list[str] | None = None,
    story_slugs: list[str] | None = None,
) -> None:
    """Sitemap.xml with homepage + tab URLs + individual success-story URLs.

    ``lastmod`` uses ``_content_last_modified()`` so rebuilds without source
    changes do not bump the timestamp. Deep-linked tab URLs resolve to the
    same SPA page (via ``docs/404.html`` + History API); story detail URLs
    resolve to real static HTML files at ``/success-story/<slug>/``.
    """
    last_mod = _content_last_modified()
    tab_slugs = tab_slugs or []
    story_slugs = story_slugs or []

    urls: list[tuple[str, str, str]] = [(SITE_URL, "1.0", "weekly")]
    for slug in tab_slugs[1:]:  # skip first tab slug — same URL as SITE_URL
        urls.append((f"{SITE_URL}{slug}", "0.8", "monthly"))
    for slug in story_slugs:
        urls.append((f"{SITE_URL}success-story/{slug}/", "0.7", "monthly"))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, priority, changefreq in urls:
        lines.append('  <url>')
        lines.append(f'    <loc>{loc}</loc>')
        lines.append(f'    <lastmod>{last_mod}</lastmod>')
        lines.append(f'    <changefreq>{changefreq}</changefreq>')
        lines.append(f'    <priority>{priority}</priority>')
        lines.append('  </url>')
    lines.append('</urlset>')
    (OUT_DIR / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_404() -> None:
    """GitHub Pages SPA-routing helper.

    When a visitor hits ``/lien-he`` or any other pretty URL directly,
    GitHub Pages returns 404 because no such file exists. This ``404.html``
    catches those requests and redirects to ``/?p=<slug>``. The main
    ``index.html`` boot script reads ``?p=`` and restores the original path
    via ``history.replaceState`` before activating the matching tab, so the
    user never sees the ``?p=`` in the URL bar.
    """
    html_doc = (
        "<!DOCTYPE html>\n"
        '<html lang="vi">\n'
        "<head>\n"
        '  <meta charset="UTF-8" />\n'
        '  <meta name="robots" content="noindex" />\n'
        "  <title>MentorPro — Đang chuyển hướng…</title>\n"
        "  <script>\n"
        "    (function () {\n"
        "      var path = window.location.pathname.replace(/^\\//, '');\n"
        "      var search = window.location.search;\n"
        "      var hash = window.location.hash;\n"
        "      var qs = '?p=' + encodeURIComponent(path.replace(/\\/$/, ''));\n"
        "      if (search) qs += '&' + search.slice(1);\n"
        "      window.location.replace('/' + qs + hash);\n"
        "    })();\n"
        "  </script>\n"
        '  <noscript><meta http-equiv="refresh" content="0; url=/"></noscript>\n'
        "</head>\n"
        "<body>\n"
        '  <p style="font-family:system-ui,sans-serif;text-align:center;margin:80px 24px">\n'
        '    Đang chuyển về <a href="/">MentorPro</a> …\n'
        "  </p>\n"
        "</body>\n"
        "</html>\n"
    )
    (OUT_DIR / "404.html").write_text(html_doc, encoding="utf-8")


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Không tìm thấy {SRC}")
    if not TEMPLATE.exists():
        raise SystemExit(f"Không tìm thấy template {TEMPLATE}")

    md_text = SRC.read_text(encoding="utf-8")
    intro_md, tabs = split_tabs(md_text)
    title, tagline = extract_hero(intro_md)
    template = TEMPLATE.read_text(encoding="utf-8")
    html_out, tab_slugs = build_html(template, title, tagline, tabs)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Post-process: extract each <details> block, emit a per-story page,
    # and swap the accordion for a click-through card on the home page.
    html_out, stories = write_story_pages(html_out)
    (OUT_DIR / "index.html").write_text(html_out, encoding="utf-8")

    if ASSETS_DIR.exists():
        copy_assets()

    story_slugs = [s["slug"] for s in stories]
    write_robots()
    write_sitemap(tab_slugs, story_slugs)
    write_404()

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
