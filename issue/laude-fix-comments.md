# MentorPro SEO/Project Audit Comments For Laude

Audit date: 2026-05-31
Status: **most items fixed on 2026-05-31** — see ✅ markers below.

Scope checked:
- Source: `MentorPro.md`, `templates/index.html`, `assets/style.css`, `assets/script.js`, `build.py`
- Output: `docs/index.html`, `docs/robots.txt`, `docs/sitemap.xml`, copied assets
- Commands run: `make build`, HTML/meta parser, image size/type scan, `tidy -q -e -utf8 docs/index.html`
- Official references used:
  - Google technical indexing requirements: https://developers.google.com/search/docs/essentials/technical
  - Google title links: https://developers.google.com/search/docs/appearance/title-link
  - Google snippets/meta descriptions: https://developers.google.com/search/docs/appearance/snippet
  - Google structured data intro: https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
  - Google FAQ structured data: https://developers.google.com/search/docs/appearance/structured-data/faqpage
  - Google robots.txt spec: https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec
  - Google sitemap overview: https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview

## Passed Checks

- `make build` is currently up to date and exits cleanly.
- `docs/index.html` has no unreplaced `{{PLACEHOLDER}}`.
- One visible `<h1>` exists.
- `<title>` is present and concise: 47 chars.
- Meta description is present: 153 chars.
- Canonical, Open Graph, Twitter Card, `robots.txt`, `sitemap.xml`, and `.nojekyll` exist.
- JSON-LD parses as valid JSON.
- No `noindex` was found.
- Every `<img>` has an `alt` attribute.
- External `target="_blank"` links include `rel="noopener"`.
- `assets/style.css`/`script.js` match `docs/style.css`/`script.js`.

## ✅ P0 - FAQPage Schema Is Not Currently A Good Google SEO Fit — FIXED

**Resolution (commit pending):** Removed the entire `FAQPage` node from JSON-LD. Remaining `@graph` has only `Organization` + `WebSite`. `skills/seo.md` updated with a warning callout explaining the removal and Google's 2026-05-07 FAQ policy change.

Evidence:
- FAQ JSON-LD is hard-coded in `templates/index.html:72-108`.
- The page does not render a matching visible FAQ section with the exact four Q&A entries. Some information appears across Tab 3/Tab 4, but not as an FAQ block users can find directly.
- Google's current FAQ docs say, as of May 7, 2026, FAQ rich results are no longer appearing in Google Search, and FAQ rich result eligibility is limited to well-known authoritative government or health websites.
- `skills/seo.md` still says FAQPage "có thể đủ tiêu chí rich result", which is stale for this commercial mentoring page.

Why this matters:
- Structured data should describe visible page content. Schema-only FAQ content can create structured data quality risk.
- The old SEO benefit expectation is outdated as of 2026-05-31.

Suggested fix:
- Preferred: remove the `FAQPage` node from JSON-LD and keep only `Organization` + `WebSite`.
- Or render a real FAQ section on the page with the exact same questions/answers, then keep the schema only as machine-readable support, not as a Google FAQ rich-result play.
- Update `skills/seo.md` to remove the claim that this page may get FAQ rich results.

Acceptance criteria:
- JSON-LD still parses.
- No FAQ schema exists unless matching FAQ content is visible in the rendered page.
- SEO docs no longer promise Google FAQ rich-result eligibility for MentorPro.

## ✅ P1 - Important Content Depends On JS Tabs And Is Hidden By Default — FIXED

**Resolution:**
- `<noscript>` style block in `templates/index.html` shows all 4 tab panels stacked with full styling when JS is disabled, and hides the `.tab-nav`.
- `build.py` now injects `<h2 class="visually-hidden tab-heading">{tab title}</h2>` at the top of every panel. Headings outline is now: 1 × h1, 4 × h2, then h3/h4 inside content. Screen readers + crawlers can identify each panel; visual users with JS still see the original design.
- ARIA cleaned up: removed duplicate `role="tablist"` from outer `.tabs`; kept only on `.tab-nav`. Each tab button now has a stable `id` (`tab-btn-<N>-<slug>`), and each panel uses `aria-labelledby="<button-id>"`.
- `.visually-hidden` utility class added to `style.css` for accessible-but-hidden text.

Evidence:
- `templates/index.html:193-201` wraps tabs, with an outer `role="tablist"` and a nested `role="tablist"`.
- `build.py:111-115` renders inactive panels with `aria-hidden="true"`.
- `assets/style.css:451-458` hides inactive panels via `display: none`.
- `assets/script.js:7-29` is required to reveal Tabs 2-4.
- Generated output has 1 `h1`, 0 `h2`, 20 `h3`, 5 `h4`.

Why this matters:
- Without JS, users only see Tab 1; stories, roadmap, pricing, and contact content are inaccessible even though they are high-value SEO and conversion content.
- The heading outline skips from `h1` directly to many `h3`s. Google uses headings and prominent text as signals for title/snippet generation, and this also weakens accessibility.
- Duplicate/incorrect tablist semantics can confuse assistive tech.

Suggested fix:
- Make tabs progressive-enhancement friendly:
  - Render all panels visible by default.
  - Add a `js` class to `<html>` early, then only hide inactive panels under `.js .tab-panel:not(.is-active)`.
  - Or use anchor links/CSS `:target` fallback.
- Add a real `<h2>` at the top of each panel using the tab title.
- Fix ARIA:
  - Remove `role="tablist"` from `.tabs`; keep it only on `.tab-nav`.
  - Give every tab button an `id`.
  - Add `aria-labelledby="<tab-button-id>"` to each panel.
  - Consider `tabindex` roving focus if keeping ARIA tabs.

Acceptance criteria:
- With JS disabled, all critical content remains visible or navigable.
- Heading counts include one `h1` and one `h2` per tab panel.
- A quick screen-reader/keyboard pass can activate each tab and identify each panel label.

## ✅ P1 - Image Performance Is The Biggest Concrete Payload Issue — FIXED

**Resolution:**
- New script `scripts/build_thumbnails.py` (Pillow) generates 360×189 JPG thumbs at quality 82 progressive into `assets/images/stories/thumbs/<slug>.jpg`.
- Result: **5.9 MB → 100 KB total** (98.3% reduction). Each thumb is 13–15 KB (under the 30 KB target).
- `MentorPro.md` story `<img class="story-thumb">` tags now reference `thumbs/<slug>.jpg` and include `width="360" height="189" loading="lazy" decoding="async"`.
- Other key images updated with intrinsic dimensions + `decoding="async"`:
  - Hero banner (LCP candidate): `width="1024" height="389" fetchpriority="high"`, no `loading="lazy"`.
  - Topbar `.brand-logo`: 480×480.
  - Partnership badge logos in footer: 480×480 / 500×500 + `loading="lazy"`.
  - Mentor avatars: 200×200 (or 400×400 for higher-res user photos) + `loading="lazy"`.
  - Engineer Pro `partner-logo` in Tab 3: 500×500 + `loading="lazy"`.
  - Lộ trình banner in Tab 3 (converted markdown image syntax to inline `<img>`): 720×720 + `loading="lazy"`.
- Originals (1200×630) kept in `assets/images/stories/<slug>.png` for potential per-story detail pages (P3 future).

Evidence:
- Story thumbnail images are 1200x630 PNG files and around 844-852 KB each:
  - `assets/images/stories/trang-ant.png` ~848 KB
  - `assets/images/stories/khanhchuong-anz.png` ~848 KB
  - `assets/images/stories/tien-sap.png` ~852 KB
  - `assets/images/stories/chan-deputy.png` ~848 KB
  - `assets/images/stories/viet-vinbigdata.png` ~852 KB
  - `assets/images/stories/hau-nab.png` ~848 KB
  - `assets/images/stories/long-mbbank.png` ~844 KB
- CSS displays story thumbs at only `130x76` desktop and `88x52` mobile (`assets/style.css:638-648`, `assets/style.css:773-783`).
- Parser found 38/38 images missing explicit `width`/`height` and `decoding`.
- Story summary images in `MentorPro.md:83`, `207`, `322`, `485`, `551`, `655`, `751` have no `loading="lazy"` or dimensions.

Why this matters:
- Large hidden/accordion images can hurt LCP/INP/total bytes, especially on mobile.
- Missing dimensions increase layout shift risk.
- Page performance is part of user experience and affects SEO quality signals.

Suggested fix:
- Generate small thumbnail variants for story summaries, for example `assets/images/stories/thumbs/<slug>.webp` around 260x136 or 360x189.
- Use `<picture>` or direct WebP thumbnails for accordion summaries.
- Keep the 1200x630 images only if needed for social cards/detail pages.
- Add `width`, `height`, `loading`, and `decoding="async"` to non-critical images.
- Do not lazy-load a true LCP image. For the hero/banner area, set stable dimensions and consider `fetchpriority="high"` only if that image is actually in the first viewport.

Acceptance criteria:
- Initial page image payload drops materially; target: story thumbs under ~30 KB each.
- All `<img>` tags have intrinsic dimensions.
- Lighthouse/PageSpeed should show no image-related CLS warning.

## ✅ P1 - Canonical/Site URL Is Hard-Coded In Too Many Places — FIXED

**Resolution:**
- `build.py` now defines a `CONFIG` dict (`SITE_URL`, `SITE_NAME`, `OG_IMAGE_URL`, `LOGO_URL`).
- `templates/index.html` uses placeholders `{{SITE_URL}}`, `{{SITE_NAME}}`, `{{OG_IMAGE_URL}}`, `{{LOGO_URL}}` everywhere (canonical, og:*, twitter:image, JSON-LD `@id` / `url` / `logo` / `image`, etc.).
- `build_html` substitutes all `{{KEY}}` placeholders from `CONFIG` at build time.
- Verify: `rg "mentorpro-team.github.io"` returns only references in `build.py` (config), `skills/` (docs), and the existing `issue/` audit — not in `templates/` or generated `docs/index.html` (post-substitution).

To switch domain (e.g. custom `mentorpro.com`):
1. Update 4 lines in `build.py` (`SITE_URL`, derived constants).
2. `make rebuild`.
3. The new URL propagates to canonical, og:*, sitemap, robots, JSON-LD automatically.

Evidence:
- `build.py:32` defines `SITE_URL`, but it only drives `robots.txt` and `sitemap.xml`.
- `templates/index.html:9`, `18`, `21`, `22`, `32`, `42`, `45`, `46`, `47`, `66`, `68`, `70` hard-code `https://mentorpro-team.github.io/`.
- Docs under `skills/` also mention the same URL in several places.

Why this matters:
- If the repo path or custom domain changes, canonical, Open Graph, JSON-LD, sitemap, and docs can drift.
- Google canonical signals should be consistent: canonical link, sitemap URL, redirects, and structured data should all point to the same preferred URL.

Suggested fix:
- Centralize site config in `build.py` or a small config file:
  - `SITE_URL`
  - `SITE_NAME`
  - `OG_IMAGE`
  - contact URLs
- Replace template hard-codes with placeholders, for example `{{SITE_URL}}`, `{{OG_IMAGE_URL}}`, `{{ORG_ID}}`.
- Regenerate `docs/`.

Acceptance criteria:
- A single config value controls canonical, `og:url`, JSON-LD URLs, robots sitemap URL, and sitemap `<loc>`.
- `rg "mentorpro-team.github.io"` returns only the config/default docs references expected.

## ✅ P1 - Sitemap `lastmod` Uses Build Date Instead Of Content Modified Date — FIXED

**Resolution:** `build.py` now has `_content_last_modified()` which:
1. **First** runs `git log -1 --format=%cI -- MentorPro.md templates/index.html assets/style.css assets/script.js` to get the latest commit timestamp for content files (reproducible, ignores rebuild noise).
2. **Falls back** to `max(filesystem mtime)` of those files when git is unavailable.
3. Used by `write_sitemap()` instead of `datetime.date.today()`.

`make rebuild` without source changes no longer bumps `<lastmod>`.

Evidence:
- `build.py:148-156` writes `lastmod` as `datetime.date.today()`.
- Current `docs/sitemap.xml` says `2026-05-31`.

Why this matters:
- Rebuilding without content changes makes the sitemap claim the page was updated.
- Google says sitemap metadata can include when a page was last updated. It should reflect content changes, not just build time.

Suggested fix:
- Compute `lastmod` from the newest relevant source file mtime: `MentorPro.md`, `templates/index.html`, `assets/style.css`, `assets/script.js`, and content images if those are considered page content.
- Better if available: use the latest git commit date for tracked source files.

Acceptance criteria:
- Running build twice without source changes does not change `docs/sitemap.xml`.
- Editing `MentorPro.md` updates `lastmod`.

## ✅ P2 - HTML Validity And Metadata Polish — FIXED

**Resolution:**
- Escaped `&` → `&amp;` in the Google Fonts URL (line `<link href="https://fonts.googleapis.com/css2?…">`).
- Removed `<meta name="keywords">` entirely (Google ignores; some other crawlers may use but it added noise).
- `build_html` now uses `html.escape(title)` and `html.escape(tab_title)` before inserting into `<title>`, `<h1>`, nav button labels, and the visually-hidden h2 — safe if content ever contains `&`, `<`, `>`, `"`.

Evidence:
- `tidy -q -e -utf8 docs/index.html` warns that the Google Fonts URL has unescaped ampersands at `templates/index.html:116`.
- `templates/index.html:13` includes `<meta name="keywords">`, which Google does not use for ranking and can be removed to reduce noise.
- `build.py:118-122` injects title/tagline/nav HTML via raw string replacement. Since content is local/trusted this is not urgent, but a title containing `&`, `<`, or `"` can produce invalid HTML.

Suggested fix:
- Escape `&` as `&amp;` in the Google Fonts `href`.
- Remove the `meta keywords` tag unless another non-Google consumer explicitly needs it.
- Use `html.escape()` for title and tab labels before inserting them into `<title>`, `<h1>`, nav labels, and attributes.

Acceptance criteria:
- HTML5 validator has no avoidable template-level warnings.
- Generated `<title>` and nav labels remain valid if content contains special characters.

## ⏸ P2 - Social Preview Image Ratio Is Non-Standard — DEFERRED

Banner còn 1024×389 (~2.63:1) thay vì chuẩn 1.91:1 (1200×630). Sửa cần redesign ảnh — user vẫn dùng banner gốc đã gửi, để nguyên cho lần sau khi có asset 1200×630 mới.

Khi đổi: thay file `assets/images/brand/banner-job-offer.jpg` + update `og:image:width` / `og:image:height` trong template.

Evidence:
- `templates/index.html:21-25` uses `banner-job-offer.jpg` as OG/Twitter image and declares `1024x389`.
- This is a very wide ratio (~2.63:1). Common large social cards crop more predictably around 1.91:1, e.g. 1200x630.

Suggested fix:
- Create a dedicated `og-image.jpg` at 1200x630.
- Update `og:image`, `og:image:width`, `og:image:height`, and `twitter:image`.
- Keep the on-page banner separate if its current aspect ratio is intentional.

Acceptance criteria:
- Facebook/LinkedIn preview crops cleanly and text/logo remain readable.

## ◐ P2 - Content Claims And Docs Need Trust Cleanup Before Publishing — PARTIALLY FIXED

**Resolution:**
- `README.md:87` updated: removed the stale "dữ liệu mẫu" line. Now confirms content is real + adds note about story thumbnail generation.

**Still TODO** (need user confirmation before changing copy):
- "95% học viên có job offer" in banner alt — keep or remove? (Banner image itself says 95%, which is from MentorPro's own marketing artwork; alt text just transcribes.)
- "đến nay" without anchor date — could replace with "từ tháng 7/2025 đến tháng 5/2026" but that requires manual refresh each report cycle. Alternative: render dynamically from `CONFIG["REPORT_THROUGH_DATE"]`.

Evidence:
- Public page claims include:
  - 25 students with offers (`templates/index.html:137-149`, `MentorPro.md:70-75`)
  - "95% học viên có job offer" in the banner alt (`templates/index.html:157`)
  - "đến nay" without an exact through-date (`templates/index.html:149`)
- `README.md:87` still says mentor/student/stat content is sample data and should be replaced before publishing.

Why this matters:
- Trust-heavy SEO pages should keep claims precise, verifiable, and current.
- "Đến nay" becomes stale quickly unless it is tied to an update date.

Suggested fix:
- Confirm which claims are real and approved.
- Replace "đến nay" with a concrete date range, for example "từ tháng 7/2025 đến tháng 5/2026", or generate it from a config field.
- If the data is real, update `README.md`; if not, change the public page copy before deploy.
- Consider adding visible proof/context: links to public posts, screenshots, or anonymized evidence for success stories.

Acceptance criteria:
- README and public page no longer contradict each other.
- Every numeric claim has either a source/context or an explicit reporting period.

## ⏸ P3 - Strategic SEO Upside: Success Stories Deserve Their Own URLs — DEFERRED

Architectural change (multi-page generation, per-story canonical / og:image / sitemap entries). Bỏ qua đợt này — site vẫn đang single-page MVP. Khi sẵn sàng, plan:
1. `build.py` thêm pipeline `build_story_pages()` — render mỗi story body thành `docs/stories/<slug>/index.html` với template riêng.
2. `MentorPro.md` summary card trỏ tới `/stories/<slug>/` thay vì accordion expand.
3. Sitemap includes 7 + 1 URLs.
4. Per-story og:image dùng banner gốc 1200×630.

Evidence:
- All seven long success stories live inside one hidden accordion on one URL.
- Sitemap has one URL only.

Why this matters:
- The current single page can rank for brand/core terms, but each story has distinct search intent: company names, career-switch stories, Java/backend/system design interview paths, etc.
- Separate pages allow unique title/meta description, canonical URL, structured data, internal links, and sitemap entries.

Suggested fix:
- Keep the current homepage as an overview.
- Generate `/stories/<slug>/` pages from the existing story blocks.
- Add each story URL to the sitemap.
- Link story cards to their detail pages while keeping a short expandable preview on the homepage.

Acceptance criteria:
- Each story has a unique URL, title, meta description, canonical, and sitemap entry.
- Homepage still works as a strong conversion page.

## Suggested Fix Order

1. Remove/fix FAQPage schema and update stale SEO docs.
2. Make tabs progressive-enhancement friendly and add h2 panel headings.
3. Compress/replace story thumbnails and add image dimensions.
4. Centralize site URL config and regenerate SEO URLs.
5. Fix sitemap `lastmod`.
6. Clean metadata/HTML validity and claim consistency.
7. Consider story detail pages as the next SEO expansion.
