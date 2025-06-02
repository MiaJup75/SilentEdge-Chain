import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8443))

# Risk mode configuration
# Options: "conservative", "balanced", "aggressive"
RISK_MODE = os.getenv("RISK_MODE", "balanced")
