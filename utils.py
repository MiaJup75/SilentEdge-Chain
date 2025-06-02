import os
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import config as cfg

db_path = 'wallets.db'
scheduler = BackgroundScheduler()

def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS wallets (address TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

def load_watched_wallets():
    pass  # placeholder for future cache preloading

def add_wallet(address):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO wallets (address) VALUES (?)", (address,))
        conn.commit()
        return f"✅ Wallet added: {address}"
    except sqlite3.IntegrityError:
        return f"⚠️ Wallet already exists."
    finally:
        conn.close()

def remove_wallet(address):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM wallets WHERE address=?", (address,))
    conn.commit()
    conn.close()
    return f"🗑️ Removed wallet: {address}"

def list_wallets():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT address FROM wallets")
    rows = c.fetchall()
    conn.close()
    if not rows:
        return "No wallets being tracked."
    return "<b>Tracked Wallets:</b>\n" + "\n".join([f"<code>{row[0]}</code>" for row in rows])

def list_tokens():
    return "Token tracking not implemented in this version."

def get_daily_summary():
    return "Daily summary feature is under development."

def schedule_jobs(bot):
    scheduler.start()

def setup_webhook(app, token):
    webhook_url = f"{cfg.WEBHOOK_URL}/{token}"
    requests.post(f"https://api.telegram.org/bot{token}/setWebhook", data={"url": webhook_url})
