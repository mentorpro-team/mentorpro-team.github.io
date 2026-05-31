# Content Recipes — How to edit content

Cookbook các task thường gặp khi cập nhật nội dung site.

## 1. Thêm / sửa mentor card (Tab 1)

**File:** `MentorPro.md`, trong block `<div class="mentor-grid">`.

```html
<div class="mentor-card">
  <img class="mentor-avatar" src="images/mentors/<slug>.png" alt="Anh/Chị <Tên>" loading="lazy">
  <h3 class="mentor-name">Anh <Tên></h3>
  <p class="mentor-role">ex-<Title> @ <Company></p>
  <a class="mentor-link" href="https://www.linkedin.com/in/<handle>/" target="_blank" rel="noopener">
    LinkedIn ↗
  </a>
</div>
```

**Variants:**
- Nếu mentor ẩn danh không có LinkedIn, dùng `<span class="mentor-link mentor-link--disabled" aria-disabled="true">LinkedIn ẩn theo yêu cầu</span>` + thêm class `mentor-card--anon` lên `<div>`.
- Đặt avatar vào `assets/images/mentors/<slug>.<ext>`. Format tốt nhất: 200×200+ JPG/PNG vuông (sẽ được crop tròn qua `border-radius: 50%`).

**Lưu ý layout:**
- Grid auto-fit 5/3/2/1 cột theo width (style.css:`.mentor-grid` media queries).
- 5 cards = 1 row trên desktop là vừa đẹp. Thêm cards thứ 6+ sẽ wrap xuống dòng — OK.

---

## 2. Thêm / sửa story (Tab 2)

Có 2 cách:

### A. Sync từ Google Doc (đề xuất)

1. Thêm/sửa entry trong `scripts/inject_full_stories.py`:
   ```python
   DOCS = {
       "trang-ant":       "1dKO3nX95OHFc8O0fJFIX3emZZpR_FsX2tuHeWPznvJU",
       # … các slug khác …
       "newstudent-newco": "<GOOGLE_DOC_ID>",
   }
   ```
2. Trước khi chạy script, **phải có** block `<details>` cho slug đó trong `MentorPro.md`. Copy 1 block hiện có và đổi:
   - Slug `<img src="images/stories/<slug>.png">`
   - Số thứ tự `<span class="story-num">#N</span>`
   - Title + tagline trong `<span class="story-title">` / `<span class="story-tagline">`
3. Đặt banner thumbnail tại `assets/images/stories/<slug>.png`.
4. Chạy: `.venv/bin/python scripts/inject_full_stories.py && make build`

Script tự:
- Fetch text từ Google Doc qua `export?format=txt`
- Parse Q&A (câu hỏi end `?`, paragraphs sau là answer)
- Inject vào giữa `</summary>` và `</details>`
- Áp dụng fix: `Reddit clone` → `Redis clone`, `anh Quang Hòa` → `anh Quang Hoàng @ Google`

### B. Thêm thủ công (story không có Google Doc)

Copy template `<details>` block, đặt vào MentorPro.md, viết Q&A trực tiếp giữa `</summary>` và `</details>` theo format:

```markdown
### TIÊU ĐỀ CÂU CHUYỆN

Intro paragraph 1...

Intro paragraph 2...

**Câu hỏi 1?**

Câu trả lời paragraph 1.

Câu trả lời paragraph 2.

**Câu hỏi 2?**

…

---

*Closing reflection paragraph in italics.*
```

---

## 3. Thêm / sửa logo công ty (marquee strip)

**File:** `templates/index.html` (không phải MentorPro.md), trong `.marquee-track`.

```html
<span class="marquee-item"><img src="images/companies/<slug>.<ext>" alt="<Tên>"></span>
```

⚠ **Phải duplicate** vào set thứ 2 (`aria-hidden="true"`, `alt=""`) ngay sau set đầu tiên để marquee loop seamless.

**Ảnh logo:**
- Đặt vào `assets/images/companies/<slug>.<ext>`
- Format ưu tiên: SVG > PNG transparent BG > PNG có BG
- Logo có nền trắng vẫn OK vì marquee background cũng trắng

**Trường hợp không có logo thật:**
Tạo SVG wordmark đồng style. Template ở `scripts/inject_full_stories.py` không có sẵn — viết SVG trực tiếp ~240×96 với text + brand color, ví dụ:
```svg
<svg viewBox="0 0 240 96" width="240" height="96" xmlns="http://www.w3.org/2000/svg">
  <text x="120" y="48" text-anchor="middle" dominant-baseline="central"
        font-family="'Plus Jakarta Sans','Inter',sans-serif"
        font-weight="800" font-size="28" letter-spacing="-0.5" fill="#<BRAND_COLOR>">
    <Tên>
  </text>
</svg>
```

---

## 4. Đổi hero banner image

**File:** `assets/images/brand/banner-job-offer.jpg` (1024×389 JPEG).

Khi thay ảnh mới:
1. Replace file giữ nguyên tên + dimension giống.
2. **Quan trọng:** Update `og:image:width` / `og:image:height` trong `templates/index.html` nếu dimensions khác.
3. `make build` rồi rerun **FB Sharing Debugger** (https://developers.facebook.com/tools/debug/) để force refresh cache.

---

## 5. Đổi MentorPro × Engineer Pro logo (footer + topbar)

- **MP logo:** `assets/images/brand/mentor-pro.png` (480×480 với "MENTOR PRO" wordmark)
- **EP logo:** `assets/images/brand/engineer-pro.png` (500×500)
- **Lộ trình banner Tab 3:** `assets/images/brand/lo-trinh-mentor-pro.png` (720×720)

Topbar dùng MP logo (CSS `.brand-logo` height 56px, padding chip trắng).

---

## 6. Đổi target / company list ở Tab 2 highlights

Trong `MentorPro.md`, dòng:
```markdown
- Công ty học viên đã nhận offer: **ANT Group · ANZ · SAP · Deputy · VinBigData · NAB · MB Bank · IBM · Dytech Lab · Grab**.
```

Sửa danh sách, các tên cách nhau bằng ` · `.

---

## 7. Đổi hero stats (3 con số)

**File:** `templates/index.html`, trong `<div class="hero-stats hero-stats--3">`:

```html
<div class="stat">
  <span class="stat-num">25</span>
  <span class="stat-label">Học viên có offer</span>
</div>
```

Đổi `25 / 5 / 7/2025` thành số mới. Note line ngay dưới:
```html
<p class="hero-note">* Tất cả số liệu được ghi nhận từ <strong>tháng 7/2025</strong> đến nay.</p>
```

---

## 8. Đổi link Messenger / Zalo / Facebook

**Search-replace** trong toàn repo:
- `m.me/Mentor.Pro.Official` (FB Messenger deep link)
- `facebook.com/Mentor.Pro.Official` (Fanpage)
- `zalo.me/0352911223` (Zalo deep link)

Các vị trí:
- `templates/index.html` (topbar CTA, footer, FAB dock)
- `MentorPro.md` (Tab 3 "bước đầu tiên", Tab 4 contact cards)
- JSON-LD `sameAs` array trong `templates/index.html`
- Quy chuẩn URL Zalo: `https://zalo.me/<phone>` (deep link mở app)

---

## 9. Đổi tagline / mission

Dòng đầu tiên có `>` trong MentorPro.md là tagline → hero. Để đổi:

```markdown
> **Tagline:** *Học từ người đã làm. Đi nhanh hơn với người đã đi.*
```

⚠ Đổi cả `og:title`, `og:description`, `twitter:title`, JSON-LD `description` trong template.

---

## 10. Thêm Tab thứ 5

Hiện chỉ có 4 tab. Thêm bằng cách:

1. Mở `MentorPro.md`, thêm cuối file:
   ```markdown
   # Tab 5 — <Tên>
   
   Nội dung tab 5…
   ```
2. Build script tự pickup vì regex `^# Tab (\d+)` linh hoạt.
3. CSS tab nav grid hiện là `repeat(4, …)` ở `.tab-nav` → đổi sang `repeat(5, …)` hoặc `auto-fit` cho responsive.
4. `make build`.
