# utils/scanner.py

import random

def scan_wallet(address):
    """
    Mock function that returns basic token analysis.
    Replace with real scanner logic later.
    """
    score = random.randint(1, 100)
    risk = "Low" if score > 70 else "Medium" if score > 40 else "High"
    result = f"🔍 Wallet Scan for `{address}`\nRisk Score: {score}/100\nRisk Level: {risk}"
    return result
