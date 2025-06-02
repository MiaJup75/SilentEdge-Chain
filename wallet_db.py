import sqlite3

def connect_db():
    return sqlite3.connect("wallets.db")

def add_wallet(address):
    conn = connect_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO wallets (address) VALUES (?)", (address,))
        conn.commit()
        return f"✅ Wallet added: {address}"
    except sqlite3.IntegrityError:
        return "⚠️ Wallet already exists."
    finally:
        conn.close()

def remove_wallet(address):
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM wallets WHERE address = ?", (address,))
    conn.commit()
    conn.close()
    return f"🗑️ Removed wallet: {address}"

def get_wallets():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT address FROM wallets")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]
