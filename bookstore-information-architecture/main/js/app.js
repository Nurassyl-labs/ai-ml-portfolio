(() => {
  "use strict";

  // ============ CONFIG ============
  const APP = {
    API_BASE: localStorage.getItem("API_BASE") || "http://localhost:3000/api",
    STORAGE_KEYS: {
      token: "pku_token",
      user: "pku_user",
    },
  };

  // ============ HELPERS ============
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function safeJsonParse(s, fallback = null) {
    try { return JSON.parse(s); } catch { return fallback; }
  }

  function getToken() {
    return localStorage.getItem(APP.STORAGE_KEYS.token) || "";
  }

  function setSession({ token, user }) {
    if (token) localStorage.setItem(APP.STORAGE_KEYS.token, token);
    if (user) localStorage.setItem(APP.STORAGE_KEYS.user, JSON.stringify(user));
  }

  function clearSession() {
    localStorage.removeItem(APP.STORAGE_KEYS.token);
    localStorage.removeItem(APP.STORAGE_KEYS.user);
  }

  function getUser() {
    return safeJsonParse(localStorage.getItem(APP.STORAGE_KEYS.user), null);
  }

  function formatDate(ts) {
    const d = new Date(ts);
    if (Number.isNaN(d.getTime())) return "";
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  }

  // ============ UI: toast ============
  function toast(msg, type = "info") {
    const id = "toast-root";
    let root = document.getElementById(id);
    if (!root) {
      root = document.createElement("div");
      root.id = id;
      root.style.cssText = "position:fixed;top:16px;right:16px;z-index:9999;display:flex;flex-direction:column;gap:8px;";
      document.body.appendChild(root);
    }
    const el = document.createElement("div");
    el.textContent = msg;
    el.style.cssText =
      "max-width:360px;padding:10px 12px;border-radius:10px;background:#111;color:#fff;font-size:14px;box-shadow:0 10px 20px rgba(0,0,0,.15);opacity:.98;";
    if (type === "success") el.style.background = "#16a34a";
    if (type === "error") el.style.background = "#dc2626";
    if (type === "warn") el.style.background = "#f59e0b";
    root.appendChild(el);
    setTimeout(() => {
      el.style.transition = "opacity .25s";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 250);
    }, 2200);
  }

  // ============ API ============
  async function api(path, { method = "GET", body, headers = {} } = {}) {
    const token = getToken();
    const h = { "Content-Type": "application/json", ...headers };
    if (token) h.Authorization = `Bearer ${token}`;

    const res = await fetch(`${APP.API_BASE}${path}`, {
      method,
      headers: h,
      body: body ? JSON.stringify(body) : undefined,
    });

    const text = await res.text();
    const data = safeJsonParse(text, { raw: text });

    if (!res.ok) {
      const msg = data?.error || data?.message || `HTTP ${res.status}`;
      throw new Error(msg);
    }
    return data;
  }

  // ============ AUTH ============
  async function login(email, password) {
    const data = await api("/auth/login", { method: "POST", body: { email, password } });
    setSession({ token: data.token, user: data.user });
    toast("登录成功", "success");
    return data;
  }

  async function register(name, email, password) {
    const data = await api("/auth/register", { method: "POST", body: { name, email, password } });
    setSession({ token: data.token, user: data.user });
    toast("注册成功", "success");
    return data;
  }

  function logout() {
    clearSession();
    toast("已退出登录", "success");
    // опционально: редирект
  }

  // ============ PAGE BOOTSTRAP ============
  async function bootstrap() {
    // 1) Подставляем имя пользователя в шапку, если есть
    const user = getUser();
    const userNameEl = $("#js-user-name");
    if (userNameEl) userNameEl.textContent = user?.name || "未登录";

    // 2) Роутинг по странице (data-page на body)
    const page = document.body.dataset.page || "";
    try {
      if (page === "login") bindLoginPage();
      if (page === "home") await loadHomePage();
      if (page === "buy") await loadBuyPage();
      if (page === "sell") bindSellPage();
      if (page === "forum") await loadForumPage();
      if (page === "drift_list") await loadDriftListPage();
      if (page === "drift_supply") bindDriftSupplyPage();
      if (page === "drift_claim") bindDriftClaimPage();
      if (page === "book_detail") await loadBookDetailPage();
    } catch (e) {
      toast(e.message || "加载失败", "error");
    }

    // 3) Универсальные клики
    bindGlobalActions();
  }

  function bindGlobalActions() {
    // logout
    $$(".js-logout").forEach((btn) => btn.addEventListener("click", logout));

    // set api base (debug)
    $$(".js-set-api").forEach((btn) => btn.addEventListener("click", () => {
      const v = prompt("API_BASE", APP.API_BASE);
      if (v) {
        localStorage.setItem("API_BASE", v);
        toast("已设置 API_BASE", "success");
      }
    }));
  }

  // ============ HOME ============
  async function loadHomePage() {
    // Пример: показать热门书籍 + 最新论坛
    const hotWrap = $("#js-hot-books");
    const postsWrap = $("#js-latest-posts");
    if (hotWrap) {
      const books = await api("/books?sort=hot&limit=6");
      hotWrap.innerHTML = books.items.map(renderBookCardMini).join("");
    }
    if (postsWrap) {
      const posts = await api("/forum/posts?sort=latest&limit=6");
      postsWrap.innerHTML = posts.items.map(renderPostMini).join("");
    }
  }

  // ============ BUY ============
  async function loadBuyPage() {
    const qInput = $("#js-buy-q");
    const listWrap = $("#js-buy-list");
    const sortSel = $("#js-buy-sort");
    const filterForm = $("#js-buy-filter-form");

    async function fetchAndRender() {
      const q = qInput?.value?.trim() || "";
      const sort = sortSel?.value || "default";
      const params = new URLSearchParams();
      if (q) params.set("q", q);
      if (sort) params.set("sort", sort);

      // пример фильтров
      const minPrice = $("#js-min-price")?.value;
      const maxPrice = $("#js-max-price")?.value;
      if (minPrice) params.set("minPrice", minPrice);
      if (maxPrice) params.set("maxPrice", maxPrice);

      const data = await api(`/books?${params.toString()}`);
      if (listWrap) listWrap.innerHTML = data.items.map(renderBookCard).join("");
    }

    $("#js-buy-search-btn")?.addEventListener("click", fetchAndRender);
    sortSel?.addEventListener("change", fetchAndRender);
    filterForm?.addEventListener("submit", (e) => { e.preventDefault(); fetchAndRender(); });

    // initial
    await fetchAndRender();
  }

  // ============ SELL ============
  function bindSellPage() {
    const form = $("#js-sell-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const payload = {
        title: $("#js-title")?.value?.trim(),
        author: $("#js-author")?.value?.trim(),
        isbn: $("#js-isbn")?.value?.trim() || null,
        price: Number($("#js-price")?.value || 0),
        condition: $("#js-condition")?.value || "未知",
        category: $("#js-category")?.value || "未分类",
        description: $("#js-desc")?.value?.trim() || "",
        coverUrl: $("#js-cover-url")?.value?.trim() || null,
      };
      if (!payload.title) return toast("请输入书名", "warn");
      if (!payload.author) return toast("请输入作者", "warn");

      try {
        await api("/books", { method: "POST", body: payload });
        toast("发布成功", "success");
        form.reset();
      } catch (err) {
        toast(err.message, "error");
      }
    });
  }

  // ============ BOOK DETAIL ============
  async function loadBookDetailPage() {
    const id = new URLSearchParams(location.search).get("id");
    if (!id) return;

    const book = await api(`/books/${encodeURIComponent(id)}`);
    $("#js-book-title") && ($("#js-book-title").textContent = book.title);
    $("#js-book-author") && ($("#js-book-author").textContent = book.author);
    $("#js-book-meta") && ($("#js-book-meta").textContent = `${book.category} · ${book.condition}`);
    $("#js-book-price") && ($("#js-book-price").textContent = `¥${book.price}`);
    $("#js-book-desc") && ($("#js-book-desc").textContent = book.description || "");
    const img = $("#js-book-cover");
    if (img && book.coverUrl) img.src = book.coverUrl;
  }

  // ============ FORUM ============
  async function loadForumPage() {
    const listWrap = $("#js-forum-list");
    const qInput = $("#js-forum-q");

    async function fetchAndRender() {
      const q = qInput?.value?.trim() || "";
      const params = new URLSearchParams();
      if (q) params.set("q", q);
      const data = await api(`/forum/posts?${params.toString()}`);
      if (listWrap) listWrap.innerHTML = data.items.map(renderPostCard).join("");
    }

    $("#js-forum-search-btn")?.addEventListener("click", fetchAndRender);

    // create post
    $("#js-post-form")?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        title: $("#js-post-title")?.value?.trim(),
        content: $("#js-post-content")?.value?.trim(),
        board: $("#js-post-board")?.value || "学习经验",
        tags: ($("#js-post-tags")?.value || "").split(",").map(s => s.trim()).filter(Boolean),
      };
      if (!payload.title) return toast("请输入标题", "warn");
      if (!payload.content) return toast("请输入内容", "warn");

      await api("/forum/posts", { method: "POST", body: payload });
      toast("发帖成功", "success");
      $("#js-post-form").reset();
      await fetchAndRender();
    });

    await fetchAndRender();
  }

  // ============ DRIFT (图书漂流) ============
  async function loadDriftListPage() {
    const listWrap = $("#js-drift-list");
    const qInput = $("#js-drift-q");
    const sortSel = $("#js-drift-sort");

    async function fetchAndRender() {
      const q = qInput?.value?.trim() || "";
      const sort = sortSel?.value || "latest";
      const params = new URLSearchParams();
      if (q) params.set("q", q);
      if (sort) params.set("sort", sort);
      const data = await api(`/drift/books?${params.toString()}`);
      if (listWrap) listWrap.innerHTML = data.items.map(renderDriftCard).join("");
    }

    $("#js-drift-search-btn")?.addEventListener("click", fetchAndRender);
    sortSel?.addEventListener("change", fetchAndRender);

    await fetchAndRender();
  }

  function bindDriftSupplyPage() {
    const form = $("#js-drift-supply-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const payload = {
        title: $("#js-drift-title")?.value?.trim(),
        author: $("#js-drift-author")?.value?.trim(),
        isbn: $("#js-drift-isbn")?.value?.trim() || null,
        category: $("#js-drift-category")?.value || "未分类",
        condition: $("#js-drift-condition")?.value || "未知",
        note: $("#js-drift-note")?.value?.trim() || "",
        coverUrl: $("#js-drift-cover")?.value?.trim() || null,
        // фикс: no admin recycle — ownership transfer
        mode: "transfer_no_return",
      };

      const agree = $("#js-drift-agree")?.checked;
      if (!payload.title) return toast("请输入书名", "warn");
      if (!payload.author) return toast("请输入作者", "warn");
      if (!agree) return toast("请勾选同意条款", "warn");

      await api("/drift/supply", { method: "POST", body: payload });
      toast("供给成功", "success");
      form.reset();
      // optional redirect
      // location.href = "图书漂流.html";
    });
  }

  function bindDriftClaimPage() {
    const form = $("#js-drift-claim-form");
    if (!form) return;

    const driftId = new URLSearchParams(location.search).get("id");
    if (!driftId) return toast("缺少漂流书籍ID", "error");

    // load details
    api(`/drift/books/${encodeURIComponent(driftId)}`)
      .then((b) => {
        $("#js-drift-book-title") && ($("#js-drift-book-title").textContent = b.title);
        $("#js-drift-book-author") && ($("#js-drift-book-author").textContent = b.author);
        $("#js-drift-book-supplier") && ($("#js-drift-book-supplier").textContent = b.supplierName);
        $("#js-drift-book-time") && ($("#js-drift-book-time").textContent = formatDate(b.suppliedAt));
      })
      .catch((e) => toast(e.message, "error"));

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        reason: $("#js-claim-reason")?.value?.trim() || "",
        handover: $("#js-claim-handover")?.value || "协商",
      };
      await api(`/drift/claim/${encodeURIComponent(driftId)}`, { method: "POST", body: payload });
      toast("申领已提交", "success");
      // redirect to list
      // location.href = "图书漂流.html";
    });
  }

  // ============ LOGIN PAGE ============
  function bindLoginPage() {
    $("#js-login-form")?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = $("#js-email")?.value?.trim();
      const password = $("#js-password")?.value;
      try {
        await login(email, password);
        location.href = "首页.html";
      } catch (err) {
        toast(err.message, "error");
      }
    });

    $("#js-register-form")?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = $("#js-name")?.value?.trim();
      const email = $("#js-email2")?.value?.trim();
      const password = $("#js-password2")?.value;
      try {
        await register(name, email, password);
        location.href = "首页.html";
      } catch (err) {
        toast(err.message, "error");
      }
    });
  }

  // ============ RENDERERS ============
  function renderBookCard(b) {
    return `
      <div class="bg-white rounded-xl shadow overflow-hidden hover:shadow-lg transition p-4">
        <div class="flex gap-4">
          <img src="${escapeHtml(b.coverUrl || "https://via.placeholder.com/120x160")}"
               class="w-20 h-28 object-cover rounded-lg" alt="cover">
          <div class="flex-1">
            <div class="flex items-start justify-between gap-2">
              <div>
                <div class="font-bold text-gray-800">${escapeHtml(b.title)}</div>
                <div class="text-sm text-gray-500">${escapeHtml(b.author)} · ${escapeHtml(b.category || "")}</div>
              </div>
              <div class="font-bold text-pkured">¥${Number(b.price || 0).toFixed(0)}</div>
            </div>
            <div class="mt-2 text-sm text-gray-600">新旧：${escapeHtml(b.condition || "")}</div>
            <div class="mt-3 flex justify-end">
              <a class="px-4 py-2 bg-pkured text-white rounded-lg"
                 href="书籍详情页.html?id=${encodeURIComponent(b.id)}">查看详情</a>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  function renderBookCardMini(b) {
    return `
      <a class="block bg-white rounded-xl shadow hover:shadow-lg transition p-4"
         href="书籍详情页.html?id=${encodeURIComponent(b.id)}">
        <div class="font-bold text-gray-800">${escapeHtml(b.title)}</div>
        <div class="text-sm text-gray-500">${escapeHtml(b.author)}</div>
        <div class="mt-2 text-pkured font-bold">¥${Number(b.price || 0).toFixed(0)}</div>
      </a>
    `;
  }

  function renderPostMini(p) {
    return `
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="font-bold text-gray-800">${escapeHtml(p.title)}</div>
        <div class="text-sm text-gray-500">${escapeHtml(p.authorName)} · ${formatDate(p.createdAt)}</div>
      </div>
    `;
  }

  function renderPostCard(p) {
    return `
      <div class="bg-white rounded-xl shadow p-5">
        <div class="flex items-start justify-between">
          <div>
            <div class="font-bold text-gray-800">${escapeHtml(p.title)}</div>
            <div class="text-sm text-gray-500">${escapeHtml(p.board)} · ${escapeHtml(p.authorName)} · ${formatDate(p.createdAt)}</div>
          </div>
        </div>
        <div class="mt-3 text-gray-700 text-sm whitespace-pre-line">${escapeHtml(p.content)}</div>
      </div>
    `;
  }

  function renderDriftCard(b) {
    return `
      <div class="bg-white rounded-xl shadow p-5 hover:shadow-lg transition">
        <div class="flex gap-4">
          <img src="${escapeHtml(b.coverUrl || "https://via.placeholder.com/120x160")}"
               class="w-20 h-28 object-cover rounded-lg" alt="cover">
          <div class="flex-1">
            <div class="flex items-start justify-between">
              <div>
                <div class="font-bold text-gray-800">${escapeHtml(b.title)}</div>
                <div class="text-sm text-gray-500">${escapeHtml(b.author)} · ${escapeHtml(b.category || "")}</div>
              </div>
              <span class="text-xs px-3 py-1 rounded-full ${b.status === "available" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"}">
                ${b.status === "available" ? "可申领" : "已申领"}
              </span>
            </div>
            <div class="mt-2 grid grid-cols-2 gap-2 text-sm text-gray-600">
              <div>图书供给人：${escapeHtml(b.supplierName)}</div>
              <div>供给时间：${formatDate(b.suppliedAt)}</div>
            </div>
            <div class="mt-3 flex justify-end">
              <a class="px-4 py-2 bg-pkured text-white rounded-lg ${b.status === "available" ? "" : "opacity-50 pointer-events-none"}"
                 href="图书漂流领取页.html?id=${encodeURIComponent(b.id)}">去申领</a>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  function escapeHtml(s) {
    return String(s ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  // expose minimal API to window if нужно
  window.PKU = {
    api,
    login,
    register,
    logout,
    getUser,
  };

  document.addEventListener("DOMContentLoaded", bootstrap);
})();
