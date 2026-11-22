-- Circuito: shop management demo. SQLite schema.
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS movements;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id            INTEGER PRIMARY KEY,
  username      TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  name          TEXT NOT NULL
);

CREATE TABLE products (
  id         INTEGER PRIMARY KEY,
  sku        TEXT NOT NULL UNIQUE,
  name       TEXT NOT NULL,
  brand      TEXT NOT NULL,
  category   TEXT NOT NULL,
  cost       REAL NOT NULL CHECK (cost >= 0),
  price      REAL NOT NULL CHECK (price >= 0),
  quantity   INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
  min_stock  INTEGER NOT NULL DEFAULT 0 CHECK (min_stock >= 0),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- Every stock change is a movement: qty is the signed change (+ in, - out).
CREATE TABLE movements (
  id         INTEGER PRIMARY KEY,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  kind       TEXT NOT NULL CHECK (kind IN ('in', 'out', 'adjust')),
  qty        INTEGER NOT NULL,
  reason     TEXT NOT NULL,
  note       TEXT NOT NULL DEFAULT '',
  user_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_movements_product ON movements(product_id, created_at);
CREATE INDEX idx_movements_date ON movements(created_at);
