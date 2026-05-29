#!/usr/bin/env python3
"""One-shot helper: replace the summary content in each story accordion
in MentorPro.md with the full interview text fetched from Google Docs.

Run from project root: python scripts/inject_full_stories.py
"""

from __future__ import annotations

import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent
MD_FILE = ROOT / "MentorPro.md"

# slug used in `images/stories/<slug>.png` → Google Doc ID
DOCS = {
    "trang-ant":       "1dKO3nX95OHFc8O0fJFIX3emZZpR_FsX2tuHeWPznvJU",
    "khanhchuong-anz": "1YnNcmocI559_0t1cXr-eMdl8uZ-_OSG-U0LR_88VoHI",
    "tien-sap":        "1krzWbkd21HgEMBNg_zsDQlcaWBnjAcFah4IdJRUUISc",
    "chan-deputy":     "1p5gqA4gKxnYrY5VaOIYUFNLgLJEYQpPFs9BdKUwS0uE",
    "viet-vinbigdata": "1NMyBX2edG1MbaG1aAy29qtQkb2e38CymbHyHfw1GYAk",
    "hau-nab":         "117FZewuFX_dvdefZeYTrqCal0qJSlmwiE4VfnDORpiQ",
    "long-mbbank":     "1rSQpLq6WVAZnQr6h2WPJOPX_WS1O0QU0OV_ADSJf6H8",
}


def fetch_doc_text(doc_id: str, retries: int = 4) -> str:
    """Fetch a Google Doc as plain text via the public export endpoint.

    Retries with exponential backoff on transient HTTP errors (429, 5xx).
    """
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    req = urllib.request.Request(url, headers={"User-Agent": "MentorProBuilder/1.0"})
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code not in (429, 500, 502, 503, 504):
                raise
            delay = 1.5 * (2 ** attempt)
            print(f"  ⚠ HTTP {e.code}, retry trong {delay:.1f}s …", file=sys.stderr)
            time.sleep(delay)
        except (urllib.error.URLError, TimeoutError) as e:
            last_err = e
            delay = 1.5 * (2 ** attempt)
            print(f"  ⚠ {e!r}, retry trong {delay:.1f}s …", file=sys.stderr)
            time.sleep(delay)
    raise RuntimeError(f"Không fetch được {doc_id} sau {retries} lần thử") from last_err


def parse_doc(raw: str) -> str:
    """Parse a fetched doc into clean markdown for the story body."""
    # Strip BOM and normalize line endings
    raw = raw.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")

    # Drop the EP boilerplate footer (everything from the separator line)
    raw = re.split(r"\n_+\s*\n", raw, maxsplit=1)[0]

    # Phỏng vấn ghi nhầm: project là Redis clone, không phải Reddit clone
    raw = re.sub(r"\bReddit clone\b", "Redis clone", raw)
    raw = re.sub(r"khóa Reddit\b", "khóa Redis", raw)
    # Mentor là anh Quang Hoàng @ Google (không phải Quang Hòa)
    raw = re.sub(r"\banh Quang Hòa\b", "anh Quang Hoàng @ Google", raw)

    # Split into non-empty stripped lines
    lines = [ln.strip() for ln in raw.split("\n")]
    lines = [ln for ln in lines if ln]

    if not lines:
        return ""

    # First line is the headline (all caps in the originals)
    title = lines[0]
    body_lines = lines[1:]

    # Split intro vs Q&A: questions are lines ending with "?" that come after
    # the intro paragraphs. We identify the first question line and treat
    # everything before it as intro, everything from it as Q&A.
    intro_paragraphs: List[str] = []
    qa_chunks: List[tuple[str, List[str]]] = []  # [(question, [answer lines])]

    in_qa = False
    current_q: str | None = None
    current_a: List[str] = []

    for ln in body_lines:
        is_question = ln.endswith("?")
        # First question marks the start of Q&A
        if not in_qa and is_question:
            in_qa = True

        if not in_qa:
            intro_paragraphs.append(ln)
            continue

        if is_question:
            if current_q is not None:
                qa_chunks.append((current_q, current_a))
            current_q = ln
            current_a = []
        else:
            current_a.append(ln)

    if current_q is not None:
        qa_chunks.append((current_q, current_a))

    # The trailing answer of the last "question" sometimes contains the
    # wrap-up commentary (general reflections by the interviewer) – those
    # paragraphs typically don't start with "Em/Mình" and refer to the
    # student in third person. We split them out as closing italics.
    closing_lines: List[str] = []
    if qa_chunks:
        last_q, last_a = qa_chunks[-1]
        wrap_idx = None
        for i, line in enumerate(last_a):
            # Heuristic: wrap-up sentences refer to "bạn học viên", "hành trình",
            # "minh chứng", "Mentor Pro" in third person, or start with "Hành trình".
            third_person_markers = (
                "Qua những chia sẻ",
                "Hành trình của",
                "Hành trình từ",
                "Câu chuyện của",
                "Hành trình 6 tháng",
                "Không chỉ dừng lại",
                "Mentor Pro không chỉ",
                "Hy vọng câu chuyện",
                "Kết bài",
                "Chúc bạn",
            )
            if line.startswith(third_person_markers):
                wrap_idx = i
                break
        if wrap_idx is not None:
            closing_lines = last_a[wrap_idx:]
            qa_chunks[-1] = (last_q, last_a[:wrap_idx])
            # If the last Q now has no answer, drop it (it was probably the wrap header)
            if not qa_chunks[-1][1]:
                qa_chunks.pop()

    # Build markdown
    out: List[str] = []
    out.append(f"### {title}")
    out.append("")
    for p in intro_paragraphs:
        out.append(p)
        out.append("")

    for q, a_lines in qa_chunks:
        # Format list items that originally started with "* " into proper md bullets.
        # In source these arrive as separate lines starting with "* ".
        out.append(f"**{q}**")
        out.append("")
        for line in a_lines:
            if line.startswith("* "):
                out.append(f"- {line[2:].strip()}")
            else:
                out.append(line)
                out.append("")
        # Strip duplicate trailing blank
        while len(out) >= 2 and out[-1] == "" and out[-2] == "":
            out.pop()
        if out and out[-1] != "":
            out.append("")

    if closing_lines:
        out.append("---")
        out.append("")
        for line in closing_lines:
            out.append(f"*{line}*")
            out.append("")

    return "\n".join(out).rstrip() + "\n"


def replace_story_body(md: str, slug: str, new_body: str) -> str:
    """Replace everything between `</summary>` and `</details>` for a given story."""
    # Find the <details> block containing the given image slug
    detail_pattern = re.compile(
        r'(<details class="story-card" markdown="1">\s*\n<summary class="story-summary">[\s\S]*?'
        rf'images/stories/{re.escape(slug)}\.png'
        r'[\s\S]*?</summary>\n)'
        r'([\s\S]*?)'
        r'(\n</details>)',
        re.MULTILINE,
    )

    def _sub(m: re.Match) -> str:
        # Pad body with blank lines so it renders as markdown inside the details
        return f"{m.group(1)}\n{new_body}\n{m.group(3)}"

    new_md, n = detail_pattern.subn(_sub, md, count=1)
    if n == 0:
        print(f"⚠ Could not find story block for slug: {slug}", file=sys.stderr)
        return md
    return new_md


def main() -> None:
    md = MD_FILE.read_text(encoding="utf-8")
    for slug, doc_id in DOCS.items():
        print(f"▶ Fetching {slug} …")
        raw = fetch_doc_text(doc_id)
        body = parse_doc(raw)
        if not body.strip():
            print(f"  ✗ Empty body, skipping {slug}")
            continue
        md = replace_story_body(md, slug, body)
        print(f"  ✓ Injected {len(body)} chars for {slug}")

    MD_FILE.write_text(md, encoding="utf-8")
    print(f"\n✓ Updated {MD_FILE}")


if __name__ == "__main__":
    main()
