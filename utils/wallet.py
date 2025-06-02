# utils/wallet.py

def is_valid_wallet(address):
    """
    Simple check for a Solana wallet address.
    Real logic can be extended to validate format or API ping.
    """
    return isinstance(address, str) and len(address) >= 32 and len(address) <= 44

def format_wallet(address):
    """
    Formats a wallet address for display (e.g., shortening it).
    """
    return address[:4] + "..." + address[-4:]
