

import os
import logging
import traceback
from flask import Flask, request, abort
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import telegram
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
)
from telegram.ext import (
    Dispatcher,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)
# --- Modular imports (assume these exist) ---
import utils.wallet as wallet_utils
import utils.token as token_utils
import utils.summary as summary_utils
import utils.alerts as alerts_utils
import utils.scanner as scanner_utils
import utils.mirror as mirror_utils
import utils.botnet as botnet_utils
import utils.aiprompt as aiprompt_utils
import wallet_db
import token_db
import mirror_db
import ai_db

# --- Config ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_IDS = set(map(int, os.getenv("ADMIN_IDS", "").split(",")))
FRIEND_WHITELIST = set(map(int, os.getenv("FRIEND_WHITELIST", "").split(",")))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=getattr(logging, LOG_LEVEL)
)
logger = logging.getLogger("main")

# --- Flask App ---
app = Flask(__name__)
bot = telegram.Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

# --- Helper Functions ---
def is_friend(user_id):
    return user_id in FRIEND_WHITELIST or user_id in ADMIN_IDS

def restricted(func):
    def wrapper(update: Update, context):
        user_id = update.effective_user.id
        if not is_friend(user_id):
            logger.warning(f"Unauthorized access denied for {user_id}.")
            update.message.reply_text("Sorry, you are not authorized to use this bot.")
            return
        return func(update, context)
    return wrapper

# --- Command Handlers ---
@restricted
def start(update, context):
    update.message.reply_text(
        "👋 Welcome! Use /help for a list of commands."
    )

@restricted
def help_command(update, context):
    help_text = (
        "🤖 *Bot Commands:*\n"
        "/wallets - List wallets\n"
        "/tokens - List tracked tokens\n"
        "/addwallet <address> - Add wallet\n"
        "/removewallet <address> - Remove wallet\n"
        "/summary - Daily summary\n"
        "/alerts - Configure alerts\n"
        "/watch <token> - Watch token\n"
        "/addtoken <token> - Add token\n"
        "/scanner <address> - Scan wallet\n"
        "/mirror <address> - Mirror tracking\n"
        "/aiprompt <prompt> - AI prompt\n"
        "/botnet - Botnet detection\n"
        "/max - Max wallet stats\n"
        "/debug - Debug info\n"
        "/help - This help message"
    )
    update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

@restricted
def wallets(update, context):
    user_id = update.effective_user.id
    wallets = wallet_db.get_wallets(user_id)
    if not wallets:
        update.message.reply_text("No wallets found. Use /addwallet <address>.")
    else:
        msg = "💼 *Your Wallets:*\n" + "\n".join(f"- `{w}`" for w in wallets)
        update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

@restricted
def tokens(update, context):
    user_id = update.effective_user.id
    tokens = token_db.get_tokens(user_id)
    if not tokens:
        update.message.reply_text("No tokens tracked. Use /addtoken <token>.")
    else:
        msg = "🪙 *Tracked Tokens:*\n" + "\n".join(f"- `{t}`" for t in tokens)
        update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

@restricted
def addwallet(update, context):
    user_id = update.effective_user.id
    if len(context.args) != 1:
        update.message.reply_text("Usage: /addwallet <address>")
        return
    address = context.args[0]
    if wallet_utils.is_valid_wallet(address):
        wallet_db.add_wallet(user_id, address)
        update.message.reply_text(f"Wallet `{address}` added.", parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text("Invalid wallet address.")

@restricted
def removewallet(update, context):
    user_id = update.effective_user.id
    if len(context.args) != 1:
        update.message.reply_text("Usage: /removewallet <address>")
        return
    address = context.args[0]
    wallet_db.remove_wallet(user_id, address)
    update.message.reply_text(f"Wallet `{address}` removed.", parse_mode=ParseMode.MARKDOWN)

@restricted
def summary(update, context):
    user_id = update.effective_user.id
    wallets = wallet_db.get_wallets(user_id)
    if not wallets:
        update.message.reply_text("No wallets to summarize.")
        return
    try:
        summary_text = summary_utils.get_summary(wallets)
        update.message.reply_text(summary_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Summary error: {e}\n{traceback.format_exc()}")
        update.message.reply_text("Error generating summary.")

@restricted
def alerts(update, context):
    user_id = update.effective_user.id
    # Show alert settings inline
    settings = alerts_utils.get_alert_settings(user_id)
    keyboard = [
        [InlineKeyboardButton(f"Price Alerts: {'On' if settings['price'] else 'Off'}", callback_data="toggle_price")],
        [InlineKeyboardButton(f"Volume Alerts: {'On' if settings['volume'] else 'Off'}", callback_data="toggle_volume")],
    ]
    update.message.reply_text(
        "⚠️ *Alert Settings:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )

def alert_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    if data == "toggle_price":
        alerts_utils.toggle_alert(user_id, "price")
        query.answer("Toggled price alerts.")
    elif data == "toggle_volume":
        alerts_utils.toggle_alert(user_id, "volume")
        query.answer("Toggled volume alerts.")
    # Refresh settings
    settings = alerts_utils.get_alert_settings(user_id)
    keyboard = [
        [InlineKeyboardButton(f"Price Alerts: {'On' if settings['price'] else 'Off'}", callback_data="toggle_price")],
        [InlineKeyboardButton(f"Volume Alerts: {'On' if settings['volume'] else 'Off'}", callback_data="toggle_volume")],
    ]
    query.edit_message_text(
        "⚠️ *Alert Settings:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )

@restricted
def watch(update, context):
    user_id = update.effective_user.id
    if len(context.args) < 1:
        update.message.reply_text("Usage: /watch <token>")
        return
    token = context.args[0]
    token_db.watch_token(user_id, token)
    update.message.reply_text(f"Now watching `{token}`.", parse_mode=ParseMode.MARKDOWN)

@restricted
def addtoken(update, context):
    user_id = update.effective_user.id
    if len(context.args) < 1:
        update.message.reply_text("Usage: /addtoken <token>")
        return
    token = context.args[0]
    if token_utils.is_valid_token(token):
        token_db.add_token(user_id, token)
        update.message.reply_text(f"Token `{token}` added.", parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text("Invalid token address.")

@restricted
def debug(update, context):
    user_id = update.effective_user.id
    debug_info = {
        "wallets": wallet_db.get_wallets(user_id),
        "tokens": token_db.get_tokens(user_id),
        "alerts": alerts_utils.get_alert_settings(user_id),
    }
    update.message.reply_text(f"Debug info:\n{debug_info}")

@restricted
def scanner(update, context):
    if len(context.args) < 1:
        update.message.reply_text("Usage: /scanner <address>")
        return
    address = context.args[0]
    try:
        scan_result = scanner_utils.scan_wallet(address)
        update.message.reply_text(scan_result, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Scanner error: {e}")
        update.message.reply_text("Error scanning wallet.")

@restricted
def max_command(update, context):
    user_id = update.effective_user.id
    wallets = wallet_db.get_wallets(user_id)
    if not wallets:
        update.message.reply_text("No wallets found.")
        return
    try:
        max_stats = summary_utils.get_max_stats(wallets)
        update.message.reply_text(max_stats, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Max error: {e}")
        update.message.reply_text("Error fetching max stats.")

# --- Tier 6–7 Advanced Features ---
@restricted
def mirror(update, context):
    user_id = update.effective_user.id
    if len(context.args) < 1:
        update.message.reply_text("Usage: /mirror <address>")
        return
    address = context.args[0]
    if mirror_utils.is_valid_mirror(address):
        mirror_db.add_mirror(user_id, address)
        update.message.reply_text(f"Mirror tracking enabled for `{address}`.", parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text("Invalid address for mirror tracking.")

@restricted
def aiprompt(update, context):
    user_id = update.effective_user.id
    prompt = " ".join(context.args)
    if not prompt:
        update.message.reply_text("Usage: /aiprompt <prompt>")
        return
    try:
        ai_response = aiprompt_utils.generate_response(prompt)
        ai_db.save_prompt(user_id, prompt, ai_response)
        update.message.reply_text(f"🤖 AI:\n{ai_response}")
    except Exception as e:
        logger.error(f"AI prompt error: {e}")
        update.message.reply_text("Error processing AI prompt.")

@restricted
def botnet(update, context):
    user_id = update.effective_user.id
    try:
        botnet_report = botnet_utils.detect_botnets(user_id)
        update.message.reply_text(botnet_report, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Botnet error: {e}")
        update.message.reply_text("Error running botnet detection.")

# --- Test LP triggers (for dev/admin only) ---
@restricted
def test_lp(update, context):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        update.message.reply_text("Admin only.")
        return
    try:
        result = utils.lp.test_trigger()
        update.message.reply_text(f"LP Test Result:\n{result}")
    except Exception as e:
        logger.error(f"LP test error: {e}")
        update.message.reply_text("LP test failed.")

# --- Inline Button Handlers ---
def inline_callback(update, context):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    # Route to appropriate callback
    if data.startswith("toggle_"):
        alert_callback(update, context)
    elif data.startswith("mirror_"):
        # Example: mirror enable/disable
        mirror_utils.toggle_mirror(user_id, data.split("_", 1)[1])
        query.answer("Mirror toggled.")
    else:
        query.answer("Unknown action.")

# --- Webhook Route ---
@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    if request.method == "POST":
        try:
            update = telegram.Update.de_json(request.get_json(force=True), bot)
            dispatcher.process_update(update)
        except Exception as e:
            logger.error(f"Webhook error: {e}\n{traceback.format_exc()}")
        return "ok"
    else:
        abort(403)

# --- Scheduler Jobs ---
def daily_summary_job():
    logger.info("Running daily summary job...")
    for user_id in wallet_db.get_all_users():
        try:
            wallets = wallet_db.get_wallets(user_id)
            if wallets:
                summary = summary_utils.get_summary(wallets)
                bot.send_message(user_id, f"📈 Daily Summary:\n{summary}", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Daily summary for {user_id} failed: {e}")

def mirror_tracking_job():
    logger.info("Running mirror tracking job...")
    for user_id in mirror_db.get_all_users():
        mirrors = mirror_db.get_mirrors(user_id)
        for address in mirrors:
            try:
                status = mirror_utils.track_mirror(address)
                if status:
                    bot.send_message(user_id, f"🔎 Mirror Update for `{address}`:\n{status}", parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                logger.error(f"Mirror job error for {address}: {e}")

def botnet_detection_job():
    logger.info("Running botnet detection job...")
    for user_id in wallet_db.get_all_users():
        try:
            report = botnet_utils.detect_botnets(user_id)
            if report:
                bot.send_message(user_id, f"🤖 Botnet Report:\n{report}", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Botnet job error for {user_id}: {e}")

# --- Register Handlers ---
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("wallets", wallets))
dispatcher.add_handler(CommandHandler("tokens", tokens))
dispatcher.add_handler(CommandHandler("addwallet", addwallet))
dispatcher.add_handler(CommandHandler("removewallet", removewallet))
dispatcher.add_handler(CommandHandler("summary", summary))
dispatcher.add_handler(CommandHandler("alerts", alerts))
dispatcher.add_handler(CommandHandler("watch", watch))
dispatcher.add_handler(CommandHandler("addtoken", addtoken))
dispatcher.add_handler(CommandHandler("debug", debug))
dispatcher.add_handler(CommandHandler("scanner", scanner))
dispatcher.add_handler(CommandHandler("max", max_command))
dispatcher.add_handler(CommandHandler("mirror", mirror))
dispatcher.add_handler(CommandHandler("aiprompt", aiprompt))
dispatcher.add_handler(CommandHandler("botnet", botnet))
dispatcher.add_handler(CommandHandler("testlp", test_lp))
dispatcher.add_handler(CallbackQueryHandler(inline_callback))

# --- Scheduler Startup ---
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(daily_summary_job, "cron", hour=8, minute=0, timezone=pytz.timezone("Asia/Bangkok"))
    scheduler.add_job(mirror_tracking_job, "interval", minutes=30)
    scheduler.add_job(botnet_detection_job, "cron", hour=4, minute=0)
    scheduler.start()
    logger.info("Scheduler started.")

# --- Start Flask App and Scheduler ---
if __name__ == "__main__":
    logger.info("Starting bot...")
    start_scheduler()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8443)))
