# utils/summary.py

from utils.wallet import format_wallet

def get_summary(wallets):
    """
    Builds a daily summary message for a list of wallets.
    This is placeholder logic — in a real bot, you’d pull value, volume, etc.
    """
    if not wallets:
        return "No wallets to summarize."

    lines = ["📊 *Daily Wallet Summary:*"]
    for address in wallets:
        lines.append(f"• `{format_wallet(address)}` — value: (mocked) 1.23 SOL")

    return "\n".join(lines)

def get_max_stats(wallets):
    """
    Example of a special command like /max to show the largest token holdings or value.
    This is mocked — in real use, integrate with Solana APIs.
    """
    if not wallets:
        return "No wallets to analyze."

    # Placeholder ranking
    top_wallet = wallets[0]
    return f"🏆 Top wallet by activity: `{format_wallet(top_wallet)}`\nValue: 3.21 SOL (mocked)"
