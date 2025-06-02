# SilentEdgeChainBot 🤖🔱

An elite Solana trading intelligence bot built for 0.1% performance. This bot watches wallets, snipes launches, detects LP creation, scans contracts, and more. Designed to operate autonomously on Telegram.

---

## 🛠 Features

### ✅ Tier 1 – Core Trading Tools
- `/wallets` – View all tracked wallets
- `/tokens` – View all SPL tokens held
- `/summary` – Daily snapshot
- `/addwallet` – Add wallet to track
- `/removewallet` – Remove wallet
- `/testlp` – Simulate a launch + trade

### 🟡 Tier 2 – Advanced Detection
- New token LP creation alerts
- Honeypot / scam scanner
- Whale / bot wallet activity alerts
- Post-launch token scorecard
- X / Telegram trend monitor

### 🔵 Tier 3 – Trade Execution Layer
- Target price triggers
- Gas-timed trade execution
- Auto PnL tracking
- Sentiment-based risk filter

### 🔴 Tier 4 – AI & Network Layer
- Mirror trade detection
- Friend wallet sync
- Narrative classification (daily)
- AI-powered buy/sell prompts

---

## 🧪 Environment Variables

| Key              | Description                                  | Example                      |
|------------------|----------------------------------------------|------------------------------|
| TELEGRAM_TOKEN   | Bot token from BotFather                     | `1234:ABC...`                |
| RISK_MODE        | Trading style (conservative/balanced/aggressive) | `balanced`                |
| LIVE_MODE        | Run live trades? `true` or `false`           | `false`                      |
| BOT_WALLET       | Solana wallet for executing trades           | `ABCD1234...`                |
| WHITELIST        | Comma-separated Telegram usernames           | `james,thomas`               |
| MIN_LP_SOL       | Minimum LP in SOL to trigger alert           | `10.0`                       |
| SCAN_INTERVAL    | Seconds between token scan sweeps            | `60`                         |
| DAILY_HOUR       | Time of daily report (Bangkok time)          | `9`                          |

---

## 🚀 Deploy

1. Set all `.env` variables in Render or Replit.
2. Ensure `webhook` route in `main.py` matches your token.
3. Deploy the bot.
4. Interact via Telegram.

---

## 💬 Commands (User Interface)

- `/start`
- `/wallets`
- `/tokens`
- `/summary`
- `/addwallet <address>`
- `/removewallet <address>`
- `/testlp` *(simulate launch & trade)*

---

## 📈 Future Tiers

> TIER 5+: Copy trading, sniper mode, gas racing, stealth honeypot dodging

---

SilentEdgeChainBot is part of the **SilentEdge Trading Suite** 🧠💰  
Engineered for high-performance crypto intelligence.
