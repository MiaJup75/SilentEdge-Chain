import logging
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from config import DAILY_HOUR, TELEGRAM_TOKEN, WHITELIST
import wallet_db

bot = None
scheduler = BackgroundScheduler()

# ========== INIT & SETUP ==========
def init_db():
    wallet_db.init()

def load_watched_wallets():
    wallet_db.load_all()

def send_message(chat_id, text, parse_mode=None):
    import telegram
    tbot = telegram.Bot(token=TELEGRAM_TOKEN)
    tbot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)

# ========== TIER 1: DAILY SUMMARY ==========
def get_daily_summary():
    wallets = wallet_db.get_all_wallets()
    lines = ["<b>📊 Daily Wallet Summary</b>"]
    for w in wallets:
        lines.append(f"\n<b>{w['address']}</b>\nValue: {w.get('value', 'N/A')} SOL")
    return "\n".join(lines)

def send_daily_report(bot):
    summary = get_daily_summary()
    for user in WHITELIST:
        if user.strip():
            try:
                bot.send_message(chat_id=user.strip(), text=summary, parse_mode='HTML')
            except Exception as e:
                logging.error(f"Error sending to {user}: {e}")
# ========== TIER 2: HONEYPOT SCANNER ==========
def check_honeypot(token_address):
    try:
        response = requests.get(f"https://api.honeypot.is/v1/check/{token_address}")
        result = response.json()
        return result.get("status", "unknown")
    except:
        return "error"

# ========== TIER 2: SOCIAL SIGNALS ==========
def check_social_signals(token_name):
    trending_tokens = ["DEGEN", "DOGWIFHAT", "BOME"]
    return token_name.upper() in trending_tokens

# ========== TIER 3: STEALTH RADAR + PRICE ALERTS ==========
def stealth_launch_detected(token):
    return token.get("lp_locked", 0) > 50 and token.get("age_mins", 0) < 10

def check_price_target(current_price, target_price):
    return current_price >= target_price

# ========== TIER 4: AI SIGNALS + NARRATIVES ==========
def ai_buy_signal(token):
    score = token.get("momentum", 0) + token.get("volume_change", 0)
    return score > 15

def classify_narrative(token):
    name = token["name"].lower()
    if "dog" in name:
        return "Meme"
    elif "ai" in name:
        return "AI"
    elif "eth" in name:
        return "Layer 2"
    return "Unclassified"

# ========== TIER 5: WATCHLIST TOOLS ==========
def list_wallets():
    wallets = wallet_db.get_all_wallets()
    if not wallets:
        return "No wallets being tracked."
    return "\n".join([f"{w['address']}" for w in wallets])

def list_tokens():
    tokens = wallet_db.get_all_tokens()
    if not tokens:
        return "No tokens tracked."
    out = []
    for t in tokens:
        out.append(f"<b>{t['symbol']}</b>\nPrice: {t['price']} | Market Cap: {t['market_cap']}\n")
    return "\n".join(out)

# ========== TIER 6: INLINE CONTROLS ==========
def build_inline_buttons(wallets):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    buttons = []
    for w in wallets:
        buttons.append([
            InlineKeyboardButton(f"Remove {w['address'][:6]}...", callback_data=f"delwallet_{w['address']}")
        ])
    return InlineKeyboardMarkup(buttons)

# ========== TIER 7: WEBHOOK + AUTONOMY ==========
def setup_webhook(app, token):
    url = get_webhook_url(token)
    try:
        import telegram
        tbot = telegram.Bot(token=token)
        tbot.set_webhook(url)
        logging.info(f"Webhook set to {url}")
    except Exception as e:
        logging.error(f"Failed to set webhook: {e}")

def get_webhook_url(token):
    from config import WEBHOOK_URL
    return f"{WEBHOOK_URL}/{token}"

# ========== SCHEDULER ==========
def schedule_jobs(bot_instance):
    global bot
    bot = bot_instance
    scheduler.add_job(
        func=lambda: send_daily_report(bot),
        trigger="cron",
        hour=DAILY_HOUR,
        timezone="Asia/Bangkok"
    )
    scheduler.start()
