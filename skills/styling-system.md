# Styling System

Design tokens, component patterns và breakpoints dùng trong `assets/style.css`.

## Design tokens (CSS variables)

Định nghĩa ở `:root` trong `style.css`:

```css
--bg: #0b1020;            /* Dark navy (hero, footer) */
--bg-2: #0f1530;          /* Slightly lighter dark */
--surface: #ffffff;       /* Card background */
--surface-2: #f6f8fc;     /* Page background light */
--border: #e3e7f0;        /* Standard border */
--text: #0d1226;          /* Primary text */
--text-soft: #475068;     /* Secondary text */
--muted: #7b86a3;         /* Tertiary text, captions */

--brand: #6366f1;         /* Indigo (primary CTA, accents) */
--brand-2: #22d3ee;       /* Cyan (gradient stop 2) */
--brand-3: #f472b6;       /* Pink (gradient stop 3) */
--accent: #facc15;        /* Yellow (rare) */
--success: #10b981;       /* Green */

--gradient: linear-gradient(135deg, #6366f1 0%, #22d3ee 60%, #f472b6 100%);

--shadow-sm: 0 1px 2px rgba(13,18,38,.06), 0 1px 4px rgba(13,18,38,.04);
--shadow-md: 0 8px 24px -8px rgba(13,18,38,.18);
--shadow-lg: 0 20px 60px -20px rgba(99,102,241,.35);

--radius-sm: 10px;
--radius-md: 16px;
--radius-lg: 24px;

--max-w: 1180px;  /* Container max width */
```

**Quy ước:** Luôn dùng var qua `var(--name)`. Không hardcode hex màu vào component CSS trừ khi cần override.

## Fonts

Load qua Google Fonts:
- **Inter** (body) — 400/500/600/700/800
- **Plus Jakarta Sans** (headings, brand) — 600/700/800

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
```

## Breakpoints

Mobile-first không, chiến lược desktop-down (max-width):

| Tên | Width | Dùng cho |
|-----|-------|----------|
| `> 1024px` | Desktop | Default styles |
| `≤ 1024px` | Tablet | `mentor-grid → 3 cols`, `companies-grid → 4 cols` |
| `≤ 960px` | Small tablet | `mentor-grid → 2 cols`, `marquee gap giảm` |
| `≤ 800px` | Larger phone | `footer-grid → 2 cols` (legacy) |
| `≤ 720px` | Phone | `tab-nav → 2 cols`, `mentor-grid → 2 cols`, `companies-grid → 3 cols`, `partner-card → vertical` |
| `≤ 600px` | Smaller phone | `partner-card → vertical`, `story-card layout co lại` |
| `≤ 520px` | Tiny phone | `mentor-grid → 1 col`, `fab dock → 52px`, FAB tooltip ẩn |
| `≤ 480px` | Smallest | `companies-grid → 2 cols` |

Nhược điểm: hơi nhiều breakpoint khác nhau. Khi viết component mới, ưu tiên dùng 1 trong các breakpoint trên cho consistent.

## Component patterns

### Card hover lift

Pattern chung cho mentor-card, story-card, contact-card, partner-card:

```css
.foo {
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
.foo:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  border-color: rgba(99,102,241,.45);
}
```

### Pulse animation (FAB)

```css
.fab::before {
  content: "";
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  background: rgba(0,132,255,.35);
  animation: fabPulse 2.4s ease-out infinite;
  z-index: -1;
}
@keyframes fabPulse {
  0%   { transform: scale(.85); opacity: .7; }
  80%, 100% { transform: scale(1.35); opacity: 0; }
}
```

Stagger 2 FAB: thêm `animation-delay: 1.2s` cho cái thứ 2.

### Marquee scroll

```css
.marquee-track {
  display: flex;
  gap: 56px;
  width: max-content;
  animation: marqueeScroll 40s linear infinite;
}
.marquee-viewport:hover .marquee-track {
  animation-play-state: paused;
}
@keyframes marqueeScroll {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }   /* duplicate set của items để loop seamless */
}
```

Mask fade 2 đầu:
```css
mask-image: linear-gradient(to right, transparent 0, #000 8%, #000 92%, transparent 100%);
```

### Stretched link

Khi muốn cả 1 card click được mà giữ HTML semantic:

```html
<div class="some-card" style="position:relative">
  <h4>Title</h4>
  <p>Description</p>
  <a class="stretched-link" href="...">CTA ↗</a>
</div>
```

```css
.stretched-link::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 1;
  border-radius: inherit;
}
```

Bootstrap pattern. Dùng ở `.partner-card` để toàn bộ card → engineerprogurus.com.

### Tab accordion (`<details>`)

Pattern native HTML5, không cần JS:

```html
<details class="story-card" markdown="1">
  <summary class="story-summary">
    <img class="story-thumb" src="...">
    <div class="story-meta">…</div>
    <span class="story-arrow">▾</span>
  </summary>
  …content khi xổ ra…
</details>
```

```css
.story-card[open] .story-arrow { transform: rotate(180deg); }
summary::-webkit-details-marker { display: none; }
summary { list-style: none; }
```

## Anti-patterns (avoid)

1. **Đừng** wrap `<a>` quanh block elements (div, h4, p) — markdown parser sẽ rewrap thành `<p>` và phá DOM. Dùng `.stretched-link` pattern thay thế.
2. **Đừng** dùng inline `style="..."` trừ trường hợp dynamic value cần JS. Tất cả styling → CSS.
3. **Đừng** dùng `!important` trừ khi cần override `.tab-panel img` rule global (đã có `!important` ở `.story-thumb`, `.mentor-avatar`, `.partner-logo`).
4. **Đừng** thêm UI library / framework. Site cố tình giữ vanilla CSS — đơn giản, fast, không build step.

## Animation cheat sheet

- Card lift hover: `.25s ease` translateY(-3px)
- Tab panel fade in: `.35s ease both` opacity + translateY (keyframe `fadeIn`)
- Story open: `.28s ease both` opacity + translateY (keyframe `storyOpen`)
- FAB pulse: `2.4s ease-out infinite` (keyframe `fabPulse`)
- Marquee: `40s linear infinite` translateX (keyframe `marqueeScroll`)

Tôn trọng `prefers-reduced-motion`:
```css
@media (prefers-reduced-motion: reduce) {
  .marquee-track { animation: none; }
}
```
