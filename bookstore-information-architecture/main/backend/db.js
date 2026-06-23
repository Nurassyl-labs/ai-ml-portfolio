// backend/db.js
const fs = require("fs");
const path = require("path");
const Database = require("better-sqlite3");

const DB_PATH = process.env.DB_PATH || path.join(__dirname, "data.sqlite");
const SCHEMA_PATH = path.join(__dirname, "schema.sql");

function openDb() {
  return new Database(DB_PATH);
}

function initDb() {
  const db = openDb();
  const schema = fs.readFileSync(SCHEMA_PATH, "utf-8");
  db.exec(schema);
  db.close();
  console.log("DB initialized:", DB_PATH);
}

if (process.argv.includes("--init")) initDb();

module.exports = { openDb, initDb, DB_PATH };
