def init_wallet_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL UNIQUE,
            label TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_wallet(address, label=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO wallets (address, label) VALUES (?, ?)", (address, label))
        conn.commit()
        return f"✅ Wallet {address} added."
    except sqlite3.IntegrityError:
        return f"⚠️ Wallet {address} already exists."
    except Exception as e:
        return f"❌ Error adding wallet: {str(e)}"
    finally:
        conn.close()

def remove_wallet(address):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM wallets WHERE address = ?", (address,))
        conn.commit()
        if c.rowcount:
            return f"✅ Wallet {address} removed."
        else:
            return f"⚠️ Wallet {address} not found."
    except Exception as e:
        return f"❌ Error removing wallet: {str(e)}"
    finally:
        conn.close()

def get_all_wallets():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT address, label FROM wallets")
    results = c.fetchall()
    conn.close()
    return results
