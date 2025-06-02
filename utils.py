import os
import json
import requests
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import config as cfg

scheduler = BackgroundScheduler()
db_path = 'wallets.db'

def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS wallets (address TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

def load_watched_wallets():
    if not os.path.exists(db_path):
        init_db()

def add_wallet(address):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO wallets (address) VALUES (?)", (address,))
        conn.commit()
        return f"✅ Wallet added: {address}"
    except sqlite3.IntegrityError:
        return f"⚠️ Wallet already tracked."
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
    response = "<b>Tracked Wallets:</b>\n"
    for row in rows:
        response += f"<code>{row[0]}</code>\n"
    return response

def list_tokens():
    return "Token tracking not implemented in this version."

def get_daily_summary():
    return "Daily summary feature is under development."

def schedule_jobs(bot):
    scheduler.start()

def setup_webhook(app, token):
    url = f"{cfg.WEBHOOK_URL}/{token}"
    requests.post(f"https://api.telegram.org/bot{token}/setWebhook", data={"url": url})
