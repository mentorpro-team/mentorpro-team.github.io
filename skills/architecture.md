# Architecture

## File tree (essential files)

```text
portfolio/
├── MentorPro.md              # ⭐ Single source of truth cho content
├── templates/
│   └── index.html            # HTML shell với placeholder {{TITLE}}, {{TAGLINE}}, {{NAV}}, {{PANELS}}
├── assets/                   # Source assets (copy đệ quy → docs/)
│   ├── style.css
│   ├── script.js
│   └── images/
│       ├── brand/            # MentorPro logo, EP logo, hero banner, lộ trình banner
│       ├── mentors/          # 5 avatar (lam.jpg, hoa.jpg, bao.png, nguyen.png, anon-meta.svg)
│       ├── stories/          # 7 banner (trang-ant.png, …, long-mbbank.png)
│       └── companies/        # 10 logo (grab.svg, nab.png, …)
├── build.py                  # ⭐ Parser + renderer chính
├── Makefile                  # build / serve / clean / watch / install
├── requirements.txt          # markdown>=3.6
├── scripts/
│   └── inject_full_stories.py  # Re-sync 7 story từ Google Docs
├── skills/                   # ← Bạn đang đọc
├── docs/                     # ⚠ Build output — GH Pages serve từ đây
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   ├── images/               # Copy từ assets/images/
│   ├── robots.txt            # Sinh tự động
│   ├── sitemap.xml           # Sinh tự động
│   └── .nojekyll             # Tắt Jekyll processing
└── .venv/                    # Python venv (auto-tạo, gitignore)
```

## Build pipeline

```text
MentorPro.md ──┐
               │
               ▼
        build.py:
         1. extract_hero(intro)  → title, tagline
         2. split_tabs(text)     → 4 tabs theo regex "# Tab N — ..."
         3. render_markdown(body) cho mỗi tab
         4. build_html(template, ...) → fill placeholder
         5. copy_assets() đệ quy assets/ → docs/
         6. write_robots() + write_sitemap()
               │
               ▼
        docs/index.html (+ assets/)
               │
               ▼
        GitHub Pages serve
```

## Cấu trúc MentorPro.md

```markdown
# MentorPro — Mentor 1-1 với Engineer từ Big Tech   ← H1 (becomes hero title)

> **Tagline:** *Học từ người đã làm. Đi nhanh hơn với người đã đi.*  ← blockquote (becomes hero tagline)

---

# Tab 1 — Thông tin Mentor       ← bắt buộc dạng "# Tab N — ..."
<div class="mentor-grid" markdown="0">
  ...
</div>

# Tab 2 — Câu chuyện thành công
<details class="story-card" markdown="1">
  <summary class="story-summary">…</summary>
  [Q&A content]
</details>
...

# Tab 3 — Lộ trình tại MentorPro
...

# Tab 4 — Liên hệ
...
```

Regex tách tab: `^# Tab (\d+)\s*[—-]\s*(.+?)\s*$` (build.py:23)

## Tech stack

- **Build:** Python 3.9+ (3.14 OK), `markdown` lib với extensions `tables, fenced_code, sane_lists, attr_list, toc, md_in_html`
- **Markup:** Markdown + raw HTML inline (cho mentor card, story accordion, contact card, …)
- **Style:** Pure CSS với CSS custom properties (vars). Không build step.
- **JS:** Vanilla, 1 file `script.js` (tab switching + keyboard nav + URL hash)
- **Hosting:** GitHub Pages từ folder `/docs` của branch `main`
- **Dependencies:** Chỉ 1 — `markdown` lib. Tự install vào `.venv/`.

## Template placeholder

`templates/index.html` có 4 placeholder:
- `{{TITLE}}` — tên site (H1 của MentorPro.md)
- `{{TAGLINE}}` — câu blockquote đầu tiên (HTML)
- `{{NAV}}` — 4 button `<button class="tab-btn">` cho tab nav
- `{{PANELS}}` — 4 `<section class="tab-panel">` chứa rendered content

Phần còn lại (hero, banner, marquee logo, footer, FAB) là **static** trong template.

## Quy ước slug

- **Story slug** = `<name>-<company>` (vd `trang-ant`, `long-mbbank`)
- **Mentor slug** = first name lowercased (vd `lam`, `hoa`, `bao`)
- **Company slug** = brand name lowercased no spaces (vd `antgroup`, `vinbigdata`)

File ảnh đặt tên theo slug + extension phù hợp (`.svg`, `.png`, `.jpg`).

## Build invariants

- `make build` là **idempotent** — chạy nhiều lần kết quả không đổi nếu source không đổi.
- Make tracks recursive vào `assets/` (line `ASSET_FILES := $(shell find $(ASSETS) -type f)`) nên đổi ảnh là tự rebuild.
- `docs/.nojekyll` được tự sinh để GH Pages không xử lý qua Jekyll.
- Khi đổi `MentorPro.md` headers (vd thêm tab thứ 5), regex `TAB_HEADER_RE` trong build.py sẽ tự pick up.
