# utils/mirror.py

import random

def is_valid_mirror(address):
    return address.startswith("0x") and len(address) == 42

def track_mirror(address):
    """
    Simulate mirror tracking status updates.
    """
    price = round(random.uniform(0.01, 0.25), 4)
    buys = random.randint(1, 20)
    sells = random.randint(0, 10)
    return f"Price: {price} SOL\nBuys: {buys} | Sells: {sells}"

def toggle_mirror(user_id, address):
    """
    Simulate toggling mirror tracking for the given address.
    """
    # Replace this with a real toggle once DB structure is in place
    return f"Mirror for `{address}` toggled for user {user_id}."
