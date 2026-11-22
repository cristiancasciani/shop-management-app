"""SQLite access: one connection per request, schema creation and demo seeding."""
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from flask import current_app, g
from werkzeug.security import generate_password_hash

from .seed_data import PRODUCTS

DEMO_USER = ('demo', 'demo123', 'Demo User')


def now() -> str:
    return datetime.now().isoformat(timespec='seconds')


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def close_db(_exc=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(seed: bool = True):
    """(Re)create all tables, then fill them with the demo data."""
    db = get_db()
    db.executescript((Path(__file__).parent / 'schema.sql').read_text())
    if seed:
        seed_demo(db)
    db.commit()


def seed_demo(db: sqlite3.Connection, days: int = 60):
    """Demo products plus 60 days of coherent movements.

    Each product starts with an 'initial' load; random sales, purchases and the odd
    adjustment follow. The final quantity is the sum of its movements, so the
    history always matches the stock.
    """
    rng = random.Random(7)
    username, password, name = DEMO_USER
    db.execute('INSERT INTO users (username, password_hash, name) VALUES (?, ?, ?)',
               (username, generate_password_hash(password), name))
    user_id = 1
    start = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) - timedelta(days=days)

    for n, (sku, pname, brand, category, cost, price, min_stock, demand) in enumerate(PRODUCTS):
        # Some products stop being restocked near the end, so the demo has items to reorder.
        stop_restock = days - 20 if n % 3 == 1 else days + 1
        created = start.isoformat(timespec='seconds')
        cur = db.execute(
            'INSERT INTO products (sku, name, brand, category, cost, price, quantity, min_stock, created_at, updated_at)'
            ' VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?)',
            (sku, pname, brand, category, cost, price, min_stock, created, created))
        pid = cur.lastrowid
        qty = max(min_stock * 3, 6)
        moves = [(pid, 'in', qty, 'initial', '', user_id, created)]

        for day in range(1, days + 1):
            when = start + timedelta(days=day, hours=rng.randint(0, 9), minutes=rng.randint(0, 59))
            if when > datetime.now():  # today: keep every movement in the past
                when = datetime.now() - timedelta(minutes=rng.randint(5, 180))
            stamp = when.isoformat(timespec='seconds')
            # Sales: demand is the average units sold per day.
            sold = sum(1 for _ in range(4) if rng.random() < demand / 4)
            sold = min(sold, qty)
            if sold:
                qty -= sold
                moves.append((pid, 'out', -sold, 'sale', '', user_id, stamp))
            # Restock when low, a few days a week.
            if qty <= min_stock and day < stop_restock and rng.random() < 0.35:
                load = max(min_stock * 2, 5) + rng.randint(0, 6)
                qty += load
                moves.append((pid, 'in', load, 'purchase', '', user_id, stamp))
            # Rare returns and damaged items.
            if rng.random() < 0.012:
                qty += 1
                moves.append((pid, 'in', 1, 'return', '', user_id, stamp))
            if qty and rng.random() < 0.006:
                qty -= 1
                moves.append((pid, 'out', -1, 'damaged', '', user_id, stamp))

        db.executemany(
            'INSERT INTO movements (product_id, kind, qty, reason, note, user_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            moves)
        db.execute('UPDATE products SET quantity = ?, updated_at = ? WHERE id = ?', (qty, moves[-1][-1], pid))


def ensure_db(app):
    """Create and seed the database on first start.

    A file lock stops several server workers from seeding at the same time.
    """
    import fcntl

    path = Path(app.config['DATABASE'])
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(f'{path}.lock', 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not path.exists():
            with app.app_context():
                init_db()
