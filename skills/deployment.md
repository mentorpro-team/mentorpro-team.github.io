# Deployment

## Current setup

- **Hosting:** GitHub Pages
- **Source branch:** `main`
- **Folder:** `/docs`
- **Repo:** https://github.com/mentorpro-team/portfolio
- **Live URL:** https://mentorpro-team.github.io/
- **HTTPS:** Tự động qua GH Pages (Let's Encrypt cert)

## Deploy workflow

```bash
# 1. Build sạch
make rebuild

# 2. Stage + commit
git add -A
git commit -m "$(cat <<'EOF'
<scope>: <short description>

<longer description if needed>
EOF
)"

# 3. Push
git push origin main

# 4. GH Pages tự deploy sau ~1-2 phút
#    Verify tại: https://github.com/mentorpro-team/portfolio/actions
```

## Lần đầu setup GH Pages

(Đã làm rồi, lưu lại để future reference)

1. Tạo repo public trên GH (`mentorpro-team/portfolio`)
2. Push initial commit có cả `docs/` folder
3. Settings → Pages
   - Source: **Deploy from a branch**
   - Branch: `main`
   - Folder: `/docs`
   - Save
4. Đợi ~1 phút, site live tại `https://<user>.github.io/<repo>/`

## Commit message convention

Format:
```
<type>(<scope>): <subject>

<body>
```

Types đã dùng trong repo:
- `init` — initial commit
- `feat` — new feature/content
- `feat(seo)` — SEO improvements
- `fix` — bug fixes (chưa có)
- `docs` — documentation only
- `style` — CSS/visual only
- `refactor` — refactor internal
- `chore` — maintenance, deps

Ví dụ:
```
feat(seo): add Open Graph + Twitter Card meta tags for link previews

Facebook Messenger, Slack, Telegram, etc. use og:* tags to render link
previews. The site now ships a 1024x389 banner-job-offer.jpg as og:image
plus matching twitter:image (summary_large_image card).
```

## Verify deploy

Sau push:

```bash
# Check action status
gh run list --limit 3        # cần gh CLI
# Hoặc xem tại
# https://github.com/mentorpro-team/portfolio/actions

# Verify content đã deploy
curl -sL https://mentorpro-team.github.io/ | grep -i "<title>"

# Check critical assets
curl -I https://mentorpro-team.github.io/images/brand/banner-job-offer.jpg
curl     https://mentorpro-team.github.io/robots.txt
curl     https://mentorpro-team.github.io/sitemap.xml
```

Tất cả nên return 200 OK.

## Troubleshooting

### "404 — site not found"

- Verify Settings → Pages còn được bật
- Check folder = `/docs` (không phải `/`)
- Đợi thêm vài phút sau push

### Build lỗi nhưng push thành công

GH Pages có thể fail silently. Check Actions tab:
- https://github.com/mentorpro-team/portfolio/actions

Common cause: file lỗi character encoding (UTF-8 BOM), file size > 100MB (Git limit), invalid `_config.yml`.

### Cache stale (preview FB cũ)

- FB cache aggressive — dùng FB Sharing Debugger để force scrape (xem [`seo.md`](seo.md))
- Browser cache — Ctrl/Cmd + Shift + R
- GH Pages CDN cache — 10-30 phút sau push mới propagate hết edge nodes

### Đổi từ ảnh `<x>.png` sang `<x>.jpg`

⚠ Cần update reference ở:
- `templates/index.html` (`<img src=...>`, `og:image`, `<link rel="icon">`)
- `MentorPro.md` (`<img>` inside details / mentor-card / partner-card)
- File extension trong `assets/images/.../`

Rồi `make rebuild`. Search-replace toàn repo bằng:
```bash
grep -rn "<x>.png" --include='*.html' --include='*.md' --include='*.css'
```

## Custom domain (nếu mua sau)

1. Mua domain (vd `mentorpro.com`)
2. Tạo file `docs/CNAME` chứa 1 dòng `mentorpro.com`
3. Trong DNS provider, tạo:
   - `A` record → 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
   - hoặc `CNAME` `www.mentorpro.com` → `mentorpro-team.github.io`
4. Trong Settings → Pages, nhập custom domain → Save
5. Đợi GH verify SSL (~24h)
6. **Update everywhere:** đổi `https://mentorpro-team.github.io/` thành `https://mentorpro.com/` trong:
   - JSON-LD (`@id`, `url`, `image`, `sameAs`)
   - og:* tags
   - canonical link
   - `build.py` constant `SITE_URL`
   - sitemap.xml (auto regenerate)
   - skills/ docs (nếu cần)

## Rollback

Nếu push commit lỗi:

```bash
# Cách 1: Force push (nếu chưa merge)
git reset --hard HEAD~1
git push --force origin main

# Cách 2: Revert (giữ history sạch hơn)
git revert HEAD
git push origin main
```

GH Pages sẽ rebuild và rollback site sau ~1-2 phút.
