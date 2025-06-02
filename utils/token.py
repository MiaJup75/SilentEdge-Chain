# utils/token.py

def is_valid_token(token):
    """
    Checks if the token string looks valid.
    This is a placeholder — real validation could check with an API.
    """
    return isinstance(token, str) and len(token) >= 3

def normalize_token(token):
    """
    Standardizes token formatting (e.g., uppercase).
    """
    return token.strip().upper()
