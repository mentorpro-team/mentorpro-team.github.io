# MentorPro Portfolio — Skills / Context Primer

Thư mục này chứa **MD context primer** dành cho các agent session sau này khi cần improve / sửa portfolio. Đọc các file dưới đây trước khi sửa code để có ngữ cảnh nhanh.

## Đọc theo thứ tự khi cần

| File | Khi nào đọc |
|------|-------------|
| [`architecture.md`](architecture.md) | Hiểu kiến trúc, tech stack, build pipeline |
| [`content-recipes.md`](content-recipes.md) | Cần **thêm/sửa** mentor, story, logo công ty, banner |
| [`styling-system.md`](styling-system.md) | Cần **đổi style**, thêm component UI mới |
| [`seo.md`](seo.md) | Cần **verify SEO**, refresh social preview, thêm structured data |
| [`deployment.md`](deployment.md) | Cần **deploy**, debug GH Pages, đổi domain |

## Bối cảnh dự án (TL;DR)

- **MentorPro** — nền tảng mentor 1-1 với engineer từ Big Tech (NVIDIA, AWS, Google, TikTok, ByteDance).
- Site là **single-page portfolio** với 4 tab: Mentor, Câu chuyện thành công, Lộ trình, Liên hệ.
- **Hợp tác chiến lược** với **Engineer Pro** (engineerprogurus.com) — đối tác đào tạo, mentee được học miễn phí các khoá chỉ định.
- Founded **7/2025**. Tới thời điểm hiện tại: **25 học viên** có offer, **5 mentor** Big Tech.
- **Stack:** Markdown source → Python build script → static HTML/CSS/JS → GitHub Pages.
- **Live URL:** https://mentorpro-team.github.io/portfolio/
- **Repo:** https://github.com/mentorpro-team/portfolio

## Commands cheat sheet

```bash
# Lần đầu (tự tạo .venv + cài markdown)
make install

# Build (mặc định)
make                 # = make build
make rebuild         # xoá docs/ rồi build lại
make serve           # http://localhost:8000
make watch           # tự rebuild khi sửa source (cần fswatch)
make clean           # xoá docs/
make distclean       # xoá cả docs/ và .venv/
make help            # xem toàn bộ target

# Re-sync 7 story từ Google Docs (auto fix "Reddit clone" → "Redis clone", etc.)
.venv/bin/python scripts/inject_full_stories.py

# Deploy
git add -A && git commit -m "..." && git push origin main
# GH Pages tự deploy sau ~1-2 phút
```

## Quy ước chung

- **Không bịa số liệu / nội dung** — chỉ dùng dữ liệu thật user cung cấp. Site đã từng có chỗ "bịa" (offices, hotline, $385K offer, …) bị user yêu cầu xoá. Khi có thông tin không chắc, hỏi user thay vì điền giả.
- **Tiếng Việt** là ngôn ngữ chính (`<html lang="vi">`, `og:locale="vi_VN"`).
- **Mọi link external** mở tab mới: `target="_blank" rel="noopener"`.
- **Mọi ảnh** phải có `alt` mô tả (trừ ảnh decorative trong marquee duplicate set thì `aria-hidden="true"` + `alt=""`).
- **Không thêm gói/giá cụ thể** vào Tab 3 — học phí là quote riêng sau buổi tư vấn.
- **Chỉ 2 kênh liên hệ** ở Tab 4: Fanpage Messenger + Zalo. Không bịa email/hotline/văn phòng.
