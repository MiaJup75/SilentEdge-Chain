# utils/botnet.py

def detect_botnets(user_id):
    """
    Simulate botnet detection logic for user's tracked wallets.
    """
    # Placeholder data – replace with real clustering logic if needed
    suspected_bots = [
        "BotWallet1...fae2",
        "BotWallet2...cc91",
        "BotWallet3...b21e",
    ]
    if not suspected_bots:
        return "No botnet activity detected."

    report = "🤖 *Botnet Activity Detected!*\n\n"
    for bot in suspected_bots:
        report += f"• `{bot}`\n"
    return report
