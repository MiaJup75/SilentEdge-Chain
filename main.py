# SilentEdgeChainBot v1.1 – Deployment Guide (Render)

## ✅ Requirements
- A free [Render.com](https://render.com) account
- Telegram Bot Token from @BotFather
- Webhook URL (can use Render URL once deployed)

## 📂 Files to Include
- main.py
- utils.py
- wallet_db.py
- config.py
- render.yaml
- requirements.txt

## ⚙️ Setup Instructions (Render)
1. **Push files to a GitHub repo**
2. Go to Render > Create New > Web Service
3. Connect to your GitHub repo
4. Use `render.yaml` to auto-configure service

### 🧾 Required Environment Variables
- `TELEGRAM_TOKEN` = Your Telegram bot token
- `WEBHOOK_URL` = Full URL to this bot on Render (e.g., `https://your-bot.onrender.com`)
- `PORT` = 8443
- `RISK_MODE` = balanced *(or conservative / aggressive)*

## 🧪 Test It
1. Start the service on Render
2. Go to Telegram, send `/start` to your bot
3. Try `/wallets` or `/addwallet WALLET_ADDRESS`

## 🔄 Risk Mode Behavior
- Conservative = 0.25 SOL per trade
- Balanced = 0.5 SOL *(default)*
- Aggressive = 1.0 SOL per trade

Edit `RISK_MODE` in your environment settings to adjust.

---

You're ready to trade silently. 🔱
