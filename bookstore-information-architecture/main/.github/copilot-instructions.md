# Copilot / AI Contributor Instructions for "北京大学二手书交易平台" (static multipage site)

This file is a short, pragmatic guide to help AI coding agents become productive quickly in this repository.

Key facts
- Project type: static multi-page website made of standalone HTML files (Chinese). No backend code found in the workspace.
- Styling: Tailwind CSS loaded from the CDN in pages (see `图书漂流.html` head). No build step required for Tailwind.
- Icons: Iconify used via CDN (`iconify.min.js`).
- Images: mix of local (`logo.png`) and external (modao.cc) images.
- Navigation: pages are linked with relative URLs (e.g., `首页.html`, `购书通道.html`). Keep filenames and links consistent.

What to inspect first (quick tour)
- `首页.html` — main entry and global navigation structure.
- `个人中心.html` — user/profile UI patterns and avatar usage.
- `图书漂流.html` — example module with header, filters, list cards, and footer (represents typical page structure used across the site).
- `logo.png` — local static asset used in header.

Project-specific conventions and patterns
- Single-file pages: each page is a full HTML document (head + body). Changes to shared layout must be applied consistently across files.
- Inline Tailwind configuration: pages set `tailwind.config = { theme: { extend: { colors: { pkured: '#990000', ... }}}}` in the head. When changing color tokens, update every page's inline config.
- No JS bundler / module system: scripts are plain script tags and inline event handlers (e.g., `onclick="window.location.href='图书漂流领取页.html'"`). Prefer minimal, non-breaking edits.
- Local linking expectations: navigation uses Chinese filenames; do not rename files without updating all links.
- Minimal accessibility: pages use semantic HTML but occasional missing alt text or ARIA; improve incrementally.

Editing and PR guidance for AI agents
- Preserve DOCTYPE, <html lang="zh-CN">, and UTF-8 meta; these are present on every page.
- When updating shared UI (header/footer), search for the snippet across files and update all occurrences. Use exact filename matches (e.g., `导航栏` links).
- Avoid introducing build tooling. If you add new CSS, prefer component-scoped <style> in the head or utility classes using Tailwind.
- If adding JS behavior, keep it small and inline or add a single `scripts/site.js` and reference it from pages; document the change in the PR.

Examples from this repository
- Header/logo: `<img src="./logo.png" alt="" style="width: 150px; height: 50px;">` (update both src and sizing together).
- Tailwind theme override: see `tailwind.config = { theme: { extend: { colors: { pkured: '#990000' }}}}` in `图书漂流.html`.
- Card pattern: `.book-card` style + hover transform used in `图书漂流.html` for list items.

Files to update cautiously
- Any filename referenced in navigation (e.g., `首页.html`, `论坛.html`) — renaming without updating links will break navigation.
- `logo.png` — ensure path (`./logo.png`) remains correct if moving files.

Developer workflows (what exists and what's likely)
- No package.json, no build or test scripts detected. Edits are expected to be direct HTML/CSS/JS changes.
- Local testing: open the HTML files directly in a browser or serve with a tiny static server (e.g., `python -m http.server`) for relative link testing.

Useful quick commands (documented for human developers)
- Serve locally (macOS / zsh):

  python3 -m http.server 8000

  Then open http://localhost:8000/首页.html in a browser.

- Search for header/footer snippets across files before editing.

Limitations and what's not here
- No backend, API, database, or tests found in the workspace.
- No CI/CD or GitHub Actions configuration present to automate checks.

If you (human) need more
- Tell me which pages/components are considered "shared" and I will standardize them into a single include (e.g., `inc/header.html`) and update references.
- If you plan to adopt a build step (Tailwind JIT, bundler), tell me the desired toolchain and I will scaffold `package.json` + config.

Please review this draft or tell me which areas you'd like expanded (e.g., add automated link-checking, standardize header/footer, or create a shared CSS file).