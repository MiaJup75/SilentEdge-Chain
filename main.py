

import os
import logging
import traceback
from flask import Flask, request, abort
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import telegram
import utils.trade as trade_utils
import utils.mev as mev_utils
from wallet_db import get_tracked_tokens, save_tracked_tokens
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
import utils.gpt as gpt_utils
import wallet_db
import token_db
import mirror_db
import ai_db
from utils.token_tracker import check_token_alerts

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
    user_id = update.effective_user.id
    welcome = (
        "👋 *Welcome to SilentEdgeChainBot!*\n\n"
        "Explore cutting-edge crypto tracking tools.\n"
        "Use the buttons below or type /help for all commands."
    )
    keyboard = [
        [InlineKeyboardButton("📊 Wallets", callback_data="quick_wallets"),
         InlineKeyboardButton("🪙 Tokens", callback_data="quick_tokens")],
        [InlineKeyboardButton("📈 Summary", callback_data="quick_summary"),
         InlineKeyboardButton("⚠️ Alerts", callback_data="quick_alerts")],
        [InlineKeyboardButton("🧠 AI Assistant", callback_data="quick_ai")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

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
        "/chatgpt <prompt> – Ask elite ChatGPT assistant\n"
        "/botnet - Botnet detection\n"
        "/max - Max wallet stats\n"
        "/buy <token> – Buy token\n"
        "/sell <token> – Sell token\n"
        "/pnl – View portfolio PnL\n"
        "/mev – Check MEV activity\n"
        "/help – This help message\n"
        "/debug - Debug info\n"

    )
    update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

@restricted
def register_commands(update, context):
    commands = [
        ("start", "Start and show welcome menu"),
        ("help", "Show available bot commands"),
        ("wallets", "List your tracked wallets"),
        ("tokens", "List your tracked tokens"),
        ("addwallet", "Add wallet address"),
        ("removewallet", "Remove wallet"),
        ("summary", "Get daily wallet summary"),
        ("alerts", "Toggle alerts on/off"),
        ("watch", "Watch token"),
        ("addtoken", "Add token"),
        ("scanner", "Scan wallet"),
        ("mirror", "Enable mirror tracking"),
        ("chatgpt", "Ask ChatGPT anything"),
        ("aiprompt", "AI prompt"),
        ("botnet", "Botnet scan"),
        ("max", "Wallet stats"),
        ("debug", "Show debug info"),
        ("buy", "Buy a token"),
        ("sell", "Sell a token"),
        ("pnl", "Portfolio PnL stats"),
        ("mev", "Check MEV activity"),
        ("trades", "Trade history"),
        ("testlp", "Trigger LP test")
    ]
    bot.set_my_commands([telegram.BotCommand(c, d) for c, d in commands])
    update.message.reply_text("✅ Bot commands registered with Telegram.")

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
def chatgpt(update, context):
    prompt = " ".join(context.args)
    if not prompt:
        update.message.reply_text("Usage: /chatgpt <your prompt>")
        return
    try:
        reply = gpt_utils.chat_with_gpt(prompt)
        update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"ChatGPT error: {e}\n{traceback.format_exc()}")
        update.message.reply_text("Error contacting ChatGPT.")
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

@restricted
def buy_command(update, context):
    user_id = update.effective_user.id

    if len(context.args) < 2:
        update.message.reply_text("Usage: /buy <TOKEN> <AMOUNT>\nExample: /buy BONK 0.1")
        return

    token = context.args[0].upper()
    try:
        sol_amount = float(context.args[1])
    except ValueError:
        update.message.reply_text("❌ Invalid amount. Use a number like 0.1")
        return

    try:
        result = trade_utils.execute_buy(token, sol_amount, user_id)
        update.message.reply_text(f"✅ Trade executed:\n{result}")
    except Exception as e:
        logger.error(f"Buy error: {e}")
        update.message.reply_text("❌ Buy command failed.")

@restricted
def sell_command(update, context):
    try:
        token_address = context.args[0]
        token_amount = float(context.args[1])
        user_id = update.effective_user.id
        result = trade_utils.execute_sale(token_address, token_amount, user_id)
        update.message.reply_text(f"✅ Sell executed:\n{result}")
    except Exception as e:
        logger.error(f"Sell error: {e}\n{traceback.format_exc()}")
        update.message.reply_text("❌ Sell command failed.")

@restricted
def pnl_command(update, context):
    try:
        user_id = update.effective_user.id
        result = trade_utils.get_wallet_pnl(user_id)
        update.message.reply_text(f"📈 PnL Report:\n{result}")
    except Exception as e:
        logger.error(f"PnL error: {e}")
        update.message.reply_text("❌ Could not fetch PnL.")

@restricted
def trades_command(update, context):
    try:
        user_id = update.effective_user.id
        result = trade_utils.get_trade_history(user_id)
        update.message.reply_text(f"📜 Trade History:\n{result}")
    except Exception as e:
        logger.error(f"Trade history error: {e}")
        update.message.reply_text("❌ Could not fetch trades.")

@restricted
def mev_command(update, context):
    try:
        if not context.args:
            update.message.reply_text("Usage: /mev <TOKEN>\nExample: /mev BONK")
            return
        token_symbol = context.args[0].upper()
        status = mev_utils.simulate_mev_check(token_symbol)
        update.message.reply_text(f"🛡️ MEV Check:\n{status}")
    except Exception as e:
        logger.error(f"MEV error: {e}")
        update.message.reply_text("❌ MEV check failed.")

@restricted
def alerts_command(update, context):
    try:
        alerts = check_token_alerts()
        if not alerts:
            update.message.reply_text("✅ No token activity detected.")
            return
        for alert in alerts:
            update.message.reply_text(alert, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Alerts error: {e}")
        update.message.reply_text("❌ Could not check token activity.")

def viewtrack_command(update, context):
    tokens = get_tracked_tokens()
    if not tokens:
        update.message.reply_text("❌ No tokens or wallets being tracked.")
        return

    for symbol, data in tokens.items():
        name = data.get("name", symbol)
        token_address = data.get("address")
        wallets = data.get("tracked_wallets", [])

        for wallet in wallets:
            short_wallet = wallet[:4] + "..." + wallet[-4:]
            text = f"""
<b>👀 Tracking:</b> <b>{name}</b>
📬 Wallet: <code>{short_wallet}</code>
🔗 <a href='https://solscan.io/token/{token_address}'>View Token</a>
"""
            keyboard = [[
                InlineKeyboardButton("🗑️ Untrack", callback_data=f"untrack|{symbol}|{wallet}"),
                InlineKeyboardButton("✏️ Rename", callback_data=f"rename|{symbol}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            
@restricted
def tracktoken_command(update, context):
    try:
        if len(context.args) != 2:
            update.message.reply_text("Usage:\n/tracktoken <WALLET_ADDRESS> <TOKEN_ADDRESS>")
            return

        wallet, token = context.args

        from wallet_db import get_tracked_tokens, save_tracked_tokens
        from utils.token_lookup import get_token_name

        resolved_name = get_token_name(token)
        symbol = resolved_name or token[-4:].upper()

        tokens = get_tracked_tokens()
        if symbol not in tokens:
            tokens[symbol] = {
                "name": resolved_name or f"Token {symbol}",
                "address": token,
                "tracked_wallets": [],
                "network": "Solana"
            }

        if wallet not in tokens[symbol]["tracked_wallets"]:
            tokens[symbol]["tracked_wallets"].append(wallet)
            save_tracked_tokens(tokens)
            update.message.reply_text(f"✅ Now tracking {symbol} for wallet ending in ...{wallet[-6:]}")
        else:
            update.message.reply_text(f"⚠️ Already tracking this combo.")
    except Exception as e:
        logger.error(f"/tracktoken error: {e}")
        update.message.reply_text("❌ Failed to set tracking.")

# --- Inline Button Handlers ---
# --- Inline Button Callback Handler ---
def inline_callback(update, context):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data == "quick_wallets":
        wallets = wallet_db.get_wallets(user_id)
        if not wallets:
            query.answer("No wallets found.")
        else:
            msg = "💼 *Your Wallets:*\n" + "\n".join(f"- `{w}`" for w in wallets)
            query.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    elif data == "quick_tokens":
        tokens = token_db.get_tokens(user_id)
        if not tokens:
            query.answer("No tokens tracked.")
        else:
            msg = "🪙 *Tracked Tokens:*\n" + "\n".join(f"- `{t}`" for t in tokens)
            query.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    elif data == "quick_summary":
        wallets = wallet_db.get_wallets(user_id)
        if not wallets:
            query.message.reply_text("No wallets to summarize.")
        else:
            try:
                summary = summary_utils.get_summary(wallets)
                query.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                logger.error(f"Summary error: {e}")
                query.message.reply_text("Error generating summary.")

    elif data == "quick_alerts":
        settings = alerts_utils.get_alert_settings(user_id)
        keyboard = [
            [InlineKeyboardButton(f"Price Alerts: {'On' if settings['price'] else 'Off'}", callback_data="toggle_price")],
            [InlineKeyboardButton(f"Volume Alerts: {'On' if settings['volume'] else 'Off'}", callback_data="toggle_volume")]
        ]
        query.message.reply_text("⚠️ Alert Settings:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "quick_ai":
        query.message.reply_text("Try asking ChatGPT:\n/chatgpt What’s the best meme coin today?")

    elif data == "toggle_price":
        alerts_utils.toggle_alert(user_id, "price")
        query.answer("Toggled price alerts.")
    elif data == "toggle_volume":
        alerts_utils.toggle_alert(user_id, "volume")
        query.answer("Toggled volume alerts.")

    elif data == "show_help":
        help_command(update, context)

    elif data == "add_wallet":
        query.message.reply_text("Use /addwallet <address> to track a wallet.")

    elif data == "chatgpt_sample":
        query.message.reply_text("Ask anything using /chatgpt — e.g.\n/chatgpt Suggest 3 trending coins")

    elif data.startswith("untrack|"):
        _, symbol, wallet = data.split("|")
    from wallet_db import get_tracked_tokens, save_tracked_tokens
    tokens = get_tracked_tokens()
    if symbol in tokens and wallet in tokens[symbol]["tracked_wallets"]:
        tokens[symbol]["tracked_wallets"].remove(wallet)
        save_tracked_tokens(tokens)
        query.answer("🗑️ Untracked.")
        query.edit_message_text(f"🗑️ Untracked {symbol} for wallet ending in ...{wallet[-6:]}")
    else:
        query.answer("⚠️ Not found.")
    
    elif data.startswith("mirror_"):
        mirror_utils.toggle_mirror(user_id, data.split("_", 1)[1])
        query.answer("Mirror toggled.")

    else:
        query.answer("Unrecognized action.")
# --- Webhook Route ---
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
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

def handle_rename_text(update, context):
    if "renaming_symbol" in context.user_data:
        symbol = context.user_data.pop("renaming_symbol")
        new_name = update.message.text.strip()
        from wallet_db import get_tracked_tokens, save_tracked_tokens
        tokens = get_tracked_tokens()
        if symbol in tokens:
            tokens[symbol]["name"] = new_name
            save_tracked_tokens(tokens)
            update.message.reply_text(f"✅ Renamed {symbol} to <b>{new_name}</b>", parse_mode=ParseMode.HTML)
        else:
            update.message.reply_text("❌ Token not found.")

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
dispatcher.add_handler(CommandHandler("register", register_commands))
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
dispatcher.add_handler(CommandHandler("chatgpt", chatgpt))
dispatcher.add_handler(CommandHandler("aiprompt", aiprompt))
dispatcher.add_handler(CommandHandler("botnet", botnet))
dispatcher.add_handler(CommandHandler("testlp", test_lp))
dispatcher.add_handler(CallbackQueryHandler(inline_callback))
dispatcher.add_handler(CommandHandler("buy", buy_command))
dispatcher.add_handler(CommandHandler("sell", sell_command))
dispatcher.add_handler(CommandHandler("pnl", pnl_command))
dispatcher.add_handler(CommandHandler("trades", trades_command))
dispatcher.add_handler(CommandHandler("mev", mev_command))
dispatcher.add_handler(CommandHandler("alerts", alerts_command))
dispatcher.add_handler(CommandHandler("tracktoken", tracktoken_command))
dispatcher.add_handler(CommandHandler("viewtrack", viewtrack_command))
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_rename_text))
dispatcher.add_handler(CallbackQueryHandler(inline_callback))

def run_auto_alerts():
    try:
        alerts = check_token_alerts()
        for alert in alerts:
            for user_id in FRIEND_WHITELIST:
                bot.send_message(chat_id=user_id, text=alert, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Auto alert error: {e}")

# --- Scheduler Startup ---
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(daily_summary_job, "cron", hour=8, minute=0, timezone=pytz.timezone("Asia/Bangkok"))
    scheduler.add_job(mirror_tracking_job, "interval", minutes=30, timezone=pytz.timezone("Asia/Bangkok"))
    scheduler.add_job(botnet_detection_job, "cron", hour=4, minute=0, timezone=pytz.timezone("Asia/Bangkok"))
    scheduler.add_job(run_auto_alerts, "interval", minutes=5, timezone=pytz.timezone("Asia/Bangkok"))
    scheduler.start()
    logger.info("Scheduler started.")

# --- Start Flask App and Scheduler ---
if __name__ == "__main__":
    logger.info("Starting bot...")
    start_scheduler()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8443)))
