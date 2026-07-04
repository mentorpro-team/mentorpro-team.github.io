# SEO Setup & Verification

## Đã setup

### Meta tags (template/index.html `<head>`)

| Tag | Giá trị |
|-----|---------|
| `<html lang="vi">` | Locale Vietnamese |
| `<meta charset="UTF-8">` | UTF-8 |
| `<meta viewport>` | Responsive |
| `<meta name="description">` | ≤160 chars mô tả site |
| `<meta name="keywords">` | MentorPro, mentor 1-1, Big Tech, … |
| `<meta name="author">` | MentorPro |
| `<meta name="theme-color">` | `#0b1020` (PWA, mobile browser chrome) |
| `<link rel="canonical">` | https://mentorpro-team.github.io/ |
| `<link rel="icon">` | mentor-pro.png |
| `<link rel="apple-touch-icon">` | mentor-pro.png |

### Open Graph (Facebook / Messenger / Slack / Telegram)

```html
og:type, og:site_name, og:url, og:title, og:description, og:locale
og:image (1024×389 JPEG, absolute HTTPS URL)
og:image:secure_url, og:image:type, og:image:width, og:image:height, og:image:alt
```

### Twitter Card

```html
twitter:card="summary_large_image"
twitter:title, twitter:description, twitter:image
```

### JSON-LD Schema.org structured data

2 entity trong 1 `@graph`:
1. **Organization** — name, url, logo, image, description, foundingDate, sameAs (FB, m.me, Zalo), contactPoint
2. **WebSite** — publisher reference back to Organization

Dùng `@id` để cross-reference giữa entities.

> ⚠ **Đã bỏ FAQPage schema (5/2026).** Theo Google FAQ docs cập nhật 7/5/2026, FAQ rich result chỉ áp dụng cho website chính phủ / y tế có thẩm quyền — không còn áp dụng cho trang thương mại như MentorPro. Schema-only FAQ (không có visible FAQ section trên page) là **structured data quality risk**.
>
> Nếu sau này MentorPro muốn add FAQ rich result, cần: (1) render FAQ section visible trên trang với cùng Q&A; (2) verify đủ tiêu chí Google hiện tại.

### Robots & Sitemap

Tự sinh bởi `build.py`:
- `docs/robots.txt` — Allow all, point to sitemap
- `docs/sitemap.xml` — Single URL với lastmod = today

### Heading hierarchy

```text
<h1> MentorPro — Mentor 1-1 với Engineer từ Big Tech    [hero, duy nhất 1 h1]
  (no h2 — tab nav buttons serve as section landmarks)
    <h3> Section titles trong tab content
      <h4> Subsections / Question prompts
```

Đây là **single-page site** nên không có h2 explicit cho tab. Có thể cải thiện bằng cách thêm `<h2 class="sr-only">` cho từng tab panel — chưa làm.

### Image alt texts

- Hero banner: alt mô tả mục đích
- Logo MentorPro/Engineer Pro: alt = tên thương hiệu
- Story thumbnails: alt mô tả nội dung (vd "Trang nhận offer Java Developer @ ANT Group")
- Mentor avatar: alt = "Anh/Chị <Tên>"
- Company marquee logos: set 1 có alt = tên company, set 2 (duplicate) có `aria-hidden="true"` + `alt=""`

### Other accessibility / SEO

- `loading="lazy"` cho ảnh không-above-the-fold
- `aria-label` cho icon-only links (FAB Messenger/Zalo, partnership badge)
- `aria-hidden="true"` cho decorative duplicate images trong marquee
- `aria-selected` toggle trên tab buttons
- `aria-controls` link tab button → tab panel
- Keyboard nav cho tabs (ArrowLeft/Right/Home/End)

## Verify SEO

### 1. Verify meta tags được serve đúng

```bash
curl -sL https://mentorpro-team.github.io/ | grep -iE 'og:image|twitter:card|<title>'
```

### 2. Test FB / Messenger preview

**FB Sharing Debugger:** https://developers.facebook.com/tools/debug/

- Paste URL → bấm **Debug**
- Lần đầu: bot scrape live, hiện preview
- Cập nhật meta xong: bấm **Scrape Again** để force refresh (FB cache ~24h-nhiều ngày)
- Cần preview hiển thị banner JPEG + title + description

### 3. Test LinkedIn preview

**LinkedIn Post Inspector:** https://www.linkedin.com/post-inspector/

### 4. Test Twitter/X card

X chỉ render khi share, không có debugger nữa. Twitter card meta tags fallback sang og:* nếu thiếu.

### 5. Verify JSON-LD

**Google Rich Results Test:** https://search.google.com/test/rich-results

Paste URL → check schema parser nhận diện được Organization + WebSite + FAQPage. FAQPage có thể đủ tiêu chí "rich result" cho Google Search.

### 6. Verify sitemap & robots

```bash
curl https://mentorpro-team.github.io/robots.txt
curl https://mentorpro-team.github.io/sitemap.xml
```

### 7. Page speed / Lighthouse

```text
https://pagespeed.web.dev/?url=https://mentorpro-team.github.io/
```

Mục tiêu: SEO score ≥ 95, Performance ≥ 80.

### 8. Submit sitemap lên Google Search Console

1. Verify domain ownership tại https://search.google.com/search-console
2. Submit sitemap `https://mentorpro-team.github.io/sitemap.xml`
3. Sau ~ngày-tuần, Google sẽ index trang

## Improvements chưa làm (future)

- [ ] Image compression — banner stories ~860 KB mỗi cái, có thể giảm 5–8x bằng JPEG quality 85
- [ ] `<h2 class="sr-only">` cho mỗi tab panel (perfect heading hierarchy)
- [ ] BreadcrumbList schema (single-page nên ít cần)
- [ ] ItemList / Review schema cho 7 story
- [ ] Critical CSS inline để FCP nhanh hơn (hiện CSS load qua external link)
- [ ] Pre-render fonts hoặc dùng `font-display: swap` (Google Fonts đã làm swap rồi)
- [ ] Custom domain (mentorpro.com hoặc tương tự) thay cho mentorpro-team.github.io
- [ ] Self-host fonts thay vì Google CDN (privacy + speed)

## Cache invalidation

Sau khi đổi nội dung quan trọng (title, og:image, …):
1. `git push` lên main
2. Đợi ~1-2 phút GH Pages deploy
3. **Force FB cache refresh** qua Sharing Debugger
4. Đôi khi cần xoá browser cache (Ctrl/Cmd + Shift + R)

## Tracking ID (chưa setup)

Khi có Google Analytics / Facebook Pixel:
- Thêm tracking script trước `</head>` trong `templates/index.html`
- Tôn trọng GDPR/CCPA: cần consent banner nếu nhắm EU/CA users
