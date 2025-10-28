-- schema.sql
CREATE TABLE browsing_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  browser_url TEXT NOT NULL,
  tag TEXT
);