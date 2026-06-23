PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  isbn TEXT,
  price INTEGER NOT NULL DEFAULT 0,
  condition TEXT,
  category TEXT,
  description TEXT,
  cover_url TEXT,
  seller_id TEXT,
  created_at INTEGER NOT NULL,
  FOREIGN KEY (seller_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS forum_posts (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  board TEXT NOT NULL,
  tags TEXT,
  author_id TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  FOREIGN KEY (author_id) REFERENCES users(id)
);

-- 图书漂流: supply/claim, без возврата, no admin recycle
CREATE TABLE IF NOT EXISTS drift_books (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  isbn TEXT,
  category TEXT,
  condition TEXT,
  note TEXT,
  cover_url TEXT,
  mode TEXT NOT NULL, -- transfer_no_return
  status TEXT NOT NULL, -- available / claimed
  supplier_id TEXT NOT NULL,
  supplied_at INTEGER NOT NULL,
  FOREIGN KEY (supplier_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS drift_claims (
  id TEXT PRIMARY KEY,
  drift_id TEXT NOT NULL,
  claimer_id TEXT NOT NULL,
  reason TEXT,
  handover TEXT,
  created_at INTEGER NOT NULL,
  FOREIGN KEY (drift_id) REFERENCES drift_books(id),
  FOREIGN KEY (claimer_id) REFERENCES users(id)
);
