# SilentEdgeChainBot 🤖🔱

SilentEdgeChainBot is a Tier 1–7 advanced Telegram bot for real-time Solana trading analysis, wallet monitoring, new token detection, and autonomous execution — designed for serious edge seekers.

---

## 🚀 Features (Tier 1–7)

| Tier | Feature Group               | Highlights |
|------|-----------------------------|------------|
| 1    | 📊 Daily Summary            | Scheduled reports of wallet/token status |
| 2    | 🔍 Honeypot & Social Scan   | Scam detection + Trending tokens |
| 3    | 🎯 Stealth Launch Radar     | LP lock detection, early buys |
| 4    | 🧠 AI Signals & Narratives  | Classifies buy zones & token themes |
| 5    | 📈 Watchlists & PnL         | Wallet + Token watchlists, tracked by command |
| 6    | ⚙️ Inline Telegram UI       | Buttons for interaction & management |
| 7    | 🌐 Webhook + Auto Trade     | Sim/Live mode, webhook, background scheduler |

---

## 🛠 Deployment (Render)

1. **Clone repo & upload to GitHub**
2. Create a new **Render Web Service**
3. Set the following **Environment Variables**:
   - `TELEGRAM_TOKEN`
   - `WEBHOOK_URL` (e.g. `https://your-bot.onrender.com`)
   - `BOT_WALLET` (optional)
   - `RISK_MODE` (`conservative` / `balanced` / `aggressive`)
   - `LIVE_MODE` (`true` or `false`)
   - `MIN_LP_SOL` (default: `10`)
   - `SCAN_INTERVAL` (seconds, default: `60`)
   - `DAILY_HOUR` (24h Bangkok time, default: `9`)
   - `WHITELIST` (comma-separated Telegram usernames)

---

## ✅ Telegram Commands

| Command       | Description |
|---------------|-------------|
| `/start`      | Activates bot UI |
| `/wallets`    | Show tracked wallets |
| `/tokens`     | Show tracked tokens |
| `/addwallet`  | Add wallet to monitor |
| `/removewallet` | Remove wallet |
| `/summary`    | Manual summary trigger |
| `/testlp`     | Simulate LP launch for your risk mode |

---

## 📂 Structure

project/
├── main.py
├── utils.py
├── wallet_db.py
├── config.py
├── requirements.txt
├── README.md
└── data/
├── wallets.json
└── tokens.json

---

## 🧪 Built With

- `python-telegram-bot`
- `Flask`
- `APScheduler`
- `Render.com` (for deployment)
- `Solana APIs`, `Honeypot Check`, and custom modules

---

## 🎯 Designed For

Investors, traders, and analysts who want an edge in Solana token markets. Ideal for high-speed meme coin trading, sniper alerts, and whale tracking.

---

## 🧠 Need Help?

For questions or custom integrations, reach out to the SilentEdge team.
