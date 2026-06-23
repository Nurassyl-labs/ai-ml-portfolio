// backend/server.js
require("dotenv").config();
const express = require("express");
const cors = require("cors");
const morgan = require("morgan");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const { v4: uuid } = require("uuid");
const { openDb, initDb } = require("./db");

const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || "dev_secret_change_me";

initDb();
const db = openDb();

const app = express();
app.use(cors());
app.use(express.json({ limit: "1mb" }));
app.use(morgan("dev"));

// --------- helpers ----------
function signToken(user) {
  return jwt.sign({ uid: user.id, email: user.email }, JWT_SECRET, { expiresIn: "7d" });
}

function auth(req, res, next) {
  const h = req.headers.authorization || "";
  const token = h.startsWith("Bearer ") ? h.slice(7) : "";
  if (!token) return res.status(401).json({ error: "Unauthorized" });
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = payload;
    return next();
  } catch {
    return res.status(401).json({ error: "Invalid token" });
  }
}

function getUserById(id) {
  return db.prepare("SELECT id, name, email, created_at FROM users WHERE id = ?").get(id);
}

// --------- auth routes ----------
app.post("/api/auth/register", (req, res) => {
  const { name, email, password } = req.body || {};
  if (!name || !email || !password) return res.status(400).json({ error: "Missing fields" });

  const exists = db.prepare("SELECT id FROM users WHERE email = ?").get(email);
  if (exists) return res.status(409).json({ error: "Email already registered" });

  const id = uuid();
  const password_hash = bcrypt.hashSync(String(password), 10);
  db.prepare(
    "INSERT INTO users (id, name, email, password_hash, created_at) VALUES (?,?,?,?,?)"
  ).run(id, name, email, password_hash, Date.now());

  const user = getUserById(id);
  const token = signToken({ id, email });
  res.json({ token, user });
});

app.post("/api/auth/login", (req, res) => {
  const { email, password } = req.body || {};
  if (!email || !password) return res.status(400).json({ error: "Missing fields" });

  const row = db.prepare("SELECT * FROM users WHERE email = ?").get(email);
  if (!row) return res.status(401).json({ error: "Invalid credentials" });

  const ok = bcrypt.compareSync(String(password), row.password_hash);
  if (!ok) return res.status(401).json({ error: "Invalid credentials" });

  const user = getUserById(row.id);
  const token = signToken(row);
  res.json({ token, user });
});

// --------- books (交易) ----------
app.get("/api/books", (req, res) => {
  const q = String(req.query.q || "").trim();
  const sort = String(req.query.sort || "default");
  const limit = Math.min(Number(req.query.limit || 30), 100);
  const minPrice = req.query.minPrice ? Number(req.query.minPrice) : null;
  const maxPrice = req.query.maxPrice ? Number(req.query.maxPrice) : null;

  let where = "1=1";
  const params = [];

  if (q) {
    where += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ?)";
    params.push(`%${q}%`, `%${q}%`, `%${q}%`, `%${q}%`);
  }
  if (minPrice !== null) { where += " AND price >= ?"; params.push(minPrice); }
  if (maxPrice !== null) { where += " AND price <= ?"; params.push(maxPrice); }

  let order = "created_at DESC";
  if (sort === "price_asc") order = "price ASC";
  if (sort === "price_desc") order = "price DESC";
  if (sort === "latest") order = "created_at DESC";

  const items = db.prepare(
    `SELECT * FROM books WHERE ${where} ORDER BY ${order} LIMIT ?`
  ).all(...params, limit);

  res.json({ items });
});

app.get("/api/books/:id", (req, res) => {
  const row = db.prepare("SELECT * FROM books WHERE id = ?").get(req.params.id);
  if (!row) return res.status(404).json({ error: "Not found" });
  res.json(row);
});

app.post("/api/books", auth, (req, res) => {
  const u = getUserById(req.user.uid);
  if (!u) return res.status(401).json({ error: "Unauthorized" });

  const {
    title, author, isbn = null, price = 0, condition = "", category = "",
    description = "", coverUrl = null
  } = req.body || {};

  if (!title || !author) return res.status(400).json({ error: "Missing title/author" });

  const id = uuid();
  db.prepare(
    `INSERT INTO books (id,title,author,isbn,price,condition,category,description,cover_url,seller_id,created_at)
     VALUES (?,?,?,?,?,?,?,?,?,?,?)`
  ).run(
    id, title, author, isbn, Number(price) || 0, condition, category, description, coverUrl, u.id, Date.now()
  );

  const row = db.prepare("SELECT * FROM books WHERE id = ?").get(id);
  res.json(row);
});

// --------- forum ----------
app.get("/api/forum/posts", (req, res) => {
  const q = String(req.query.q || "").trim();
  const sort = String(req.query.sort || "latest");
  const limit = Math.min(Number(req.query.limit || 50), 100);

  let where = "1=1";
  const params = [];
  if (q) {
    where += " AND (title LIKE ? OR content LIKE ? OR board LIKE ?)";
    params.push(`%${q}%`, `%${q}%`, `%${q}%`);
  }

  const order = sort === "latest" ? "created_at DESC" : "created_at DESC";

  const rows = db.prepare(
    `SELECT p.*, u.name AS authorName
     FROM forum_posts p
     JOIN users u ON u.id = p.author_id
     WHERE ${where}
     ORDER BY ${order}
     LIMIT ?`
  ).all(...params, limit);

  // tags stored as JSON string
  const items = rows.map(r => ({ ...r, tags: r.tags ? JSON.parse(r.tags) : [] }));
  res.json({ items });
});

app.post("/api/forum/posts", auth, (req, res) => {
  const u = getUserById(req.user.uid);
  if (!u) return res.status(401).json({ error: "Unauthorized" });

  const { title, content, board = "学习经验", tags = [] } = req.body || {};
  if (!title || !content) return res.status(400).json({ error: "Missing title/content" });

  const id = uuid();
  db.prepare(
    `INSERT INTO forum_posts (id,title,content,board,tags,author_id,created_at)
     VALUES (?,?,?,?,?,?,?)`
  ).run(id, title, content, board, JSON.stringify(tags || []), u.id, Date.now());

  const row = db.prepare(
    `SELECT p.*, u.name AS authorName
     FROM forum_posts p JOIN users u ON u.id = p.author_id
     WHERE p.id = ?`
  ).get(id);

  res.json({ ...row, tags: row.tags ? JSON.parse(row.tags) : [] });
});

// --------- drift (图书漂流) ----------
app.get("/api/drift/books", (req, res) => {
  const q = String(req.query.q || "").trim();
  const sort = String(req.query.sort || "latest");
  const limit = Math.min(Number(req.query.limit || 50), 100);

  let where = "1=1";
  const params = [];
  if (q) {
    where += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ?)";
    params.push(`%${q}%`, `%${q}%`, `%${q}%`, `%${q}%`);
  }

  let order = "supplied_at DESC";
  if (sort === "latest") order = "supplied_at DESC";
  if (sort === "hot") order = "supplied_at DESC";

  const rows = db.prepare(
    `SELECT d.*, u.name AS supplierName
     FROM drift_books d
     JOIN users u ON u.id = d.supplier_id
     WHERE ${where}
     ORDER BY ${order}
     LIMIT ?`
  ).all(...params, limit);

  res.json({ items: rows });
});

app.get("/api/drift/books/:id", (req, res) => {
  const row = db.prepare(
    `SELECT d.*, u.name AS supplierName
     FROM drift_books d
     JOIN users u ON u.id = d.supplier_id
     WHERE d.id = ?`
  ).get(req.params.id);

  if (!row) return res.status(404).json({ error: "Not found" });
  res.json(row);
});

app.post("/api/drift/supply", auth, (req, res) => {
  const u = getUserById(req.user.uid);
  if (!u) return res.status(401).json({ error: "Unauthorized" });

  const {
    title, author, isbn = null, category = "", condition = "", note = "",
    coverUrl = null, mode = "transfer_no_return"
  } = req.body || {};

  if (!title || !author) return res.status(400).json({ error: "Missing title/author" });

  const id = uuid();
  db.prepare(
    `INSERT INTO drift_books (id,title,author,isbn,category,condition,note,cover_url,mode,status,supplier_id,supplied_at)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`
  ).run(
    id, title, author, isbn, category, condition, note, coverUrl, mode, "available", u.id, Date.now()
  );

  const row = db.prepare(
    `SELECT d.*, u.name AS supplierName
     FROM drift_books d JOIN users u ON u.id = d.supplier_id WHERE d.id = ?`
  ).get(id);

  res.json(row);
});

app.post("/api/drift/claim/:id", auth, (req, res) => {
  const u = getUserById(req.user.uid);
  if (!u) return res.status(401).json({ error: "Unauthorized" });

  const driftId = req.params.id;
  const drift = db.prepare("SELECT * FROM drift_books WHERE id = ?").get(driftId);
  if (!drift) return res.status(404).json({ error: "Not found" });
  if (drift.status !== "available") return res.status(400).json({ error: "Already claimed" });

  const { reason = "", handover = "协商" } = req.body || {};

  const claimId = uuid();
  const now = Date.now();

  const tx = db.transaction(() => {
    db.prepare(
      `INSERT INTO drift_claims (id, drift_id, claimer_id, reason, handover, created_at)
       VALUES (?,?,?,?,?,?)`
    ).run(claimId, driftId, u.id, reason, handover, now);

    db.prepare(`UPDATE drift_books SET status = 'claimed' WHERE id = ?`).run(driftId);
  });

  tx();

  res.json({ ok: true, claimId });
});

// --------- health ----------
app.get("/api/health", (req, res) => res.json({ ok: true }));

app.listen(PORT, () => {
  console.log(`API running on http://localhost:${PORT}`);
  console.log(`Base path: /api`);
});
