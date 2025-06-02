import os

# Telegram Bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

# Webhook URL for Render or custom domain (used for webhook setup)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://silentedgechainbot.onrender.com")  # Replace if needed

# Risk Mode: conservative / balanced / aggressive
RISK_MODE = os.getenv("RISK_MODE", "balanced").lower()

# Sim / Live trading toggle
LIVE_MODE = os.getenv("LIVE_MODE", "false").lower() == "true"

# Optional: Wallet for executing trades (burner or main)
BOT_WALLET = os.getenv("BOT_WALLET", "")

# Optional: Friend whitelist Telegram usernames (comma-separated)
WHITELIST = os.getenv("WHITELIST", "").split(",")

# LP creation threshold in SOL (for alerting new launches)
MIN_LP_SOL = float(os.getenv("MIN_LP_SOL", 10.0))

# Scan interval in seconds
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", 60))

# Daily update hour in 24h format (Bangkok time)
DAILY_HOUR = int(os.getenv("DAILY_HOUR", 9))
