import sqlite3

DB = "store.db"

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)""")
        c.execute("""CREATE TABLE IF NOT EXISTS orders(
            order_id TEXT PRIMARY KEY, status TEXT, eta TEXT)""")
        if c.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            c.executemany(
                "INSERT INTO products(name, price, stock) VALUES (?,?,?)", [
                    ("Running Shoes", 2499, 12),
                    ("Wireless Earbuds", 1999, 0),
                    ("Cotton T-Shirt", 499, 40),
                    ("Backpack", 1299, 7),
                ])
            c.executemany("INSERT INTO orders VALUES (?,?,?)", [
                ("1001", "Shipped", "Friday"),
                ("1002", "Processing", "Monday"),
                ("1003", "Delivered", "-"),
            ])

def search_products(text):
    text = text.lower()
    with conn() as c:
        rows = c.execute("SELECT * FROM products").fetchall()
    found = []
    for r in rows:
        name = r["name"].lower()
        tokens = [t for t in name.split() if len(t) > 3]
        if name in text or any(t in text for t in tokens):
            found.append(dict(r))
    return found

def all_products():
    with conn() as c:
        rows = c.execute("SELECT * FROM products").fetchall()
    return [dict(r) for r in rows]

def get_order(order_id):
    with conn() as c:
        r = c.execute("SELECT * FROM orders WHERE order_id=?",
                      (order_id,)).fetchone()
    return dict(r) if r else None
