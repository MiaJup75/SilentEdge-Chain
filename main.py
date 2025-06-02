import logging
from flask import Flask, request
import telegram
import utils
import wallet_db
import config as cfg
from threading import Thread

app = Flask(__name__)
bot = telegram.Bot(token=cfg.TELEGRAM_TOKEN)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global toggle
bot_active = True

def start_bot():
    utils.init_db()
    utils.load_watched_wallets()
    utils.schedule_jobs(bot)
    logger.info("SilentEdgeChainBot is running...")

@app.route(f"/{cfg.TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    if update.message:
        handle_message(update.message)
    elif update.callback_query:
        handle_callback(update.callback_query)
    return "OK"

def handle_message(msg):
    text = msg.text or ""
    chat_id = msg.chat.id

    if text == "/start":
        bot.send_message(chat_id, "🤖 SilentEdgeChainBot is active.\nUse /wallets or /tokens to begin.")
    elif text == "/wallets":
        response = utils.list_wallets()
        bot.send_message(chat_id, response, parse_mode=telegram.ParseMode.HTML)
    elif text == "/tokens":
        response = utils.list_tokens()
        bot.send_message(chat_id, response, parse_mode=telegram.ParseMode.HTML)
    elif text.startswith("/addwallet "):
        addr = text.split(" ", 1)[1].strip()
        result = wallet_db.add_wallet(addr)
        bot.send_message(chat_id, result)
    elif text == "/summary":
        summary = utils.get_daily_summary()
        bot.send_message(chat_id, summary, parse_mode=telegram.ParseMode.HTML)
    elif text.startswith("/removewallet "):
        addr = text.split(" ", 1)[1].strip()
        result = wallet_db.remove_wallet(addr)
        bot.send_message(chat_id, result)
    elif text.startswith("/testlp"):
        from config import RISK_MODE
        trade_amounts = {
            "conservative": 0.25,
            "balanced": 0.5,
            "aggressive": 1.0
        }
        amount = trade_amounts.get(RISK_MODE, 0.5)

        bot.send_message(chat_id, f"""
🚀 <b>Simulated LP Launch Detected</b>
• Token: TEST123
• Risk Mode: <b>{RISK_MODE.capitalize()}</b>
• Executing test trade...
• Sent: <b>{amount} SOL</b>
        """, parse_mode=telegram.ParseMode.HTML)
    else:
        bot.send_message(chat_id, "Unknown command.")

def handle_callback(callback):
    data = callback.data
    chat_id = callback.message.chat.id

    if data.startswith("delwallet_"):
        addr = data.replace("delwallet_", "")
        result = wallet_db.remove_wallet(addr)
        bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text=result)

if __name__ == "__main__":
    utils.setup_webhook(app, cfg.TELEGRAM_TOKEN)
    Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=cfg.PORT)
