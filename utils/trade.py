# utils/trade.py

def execute_buy(user_id, token_symbol, amount_sol):
    # Simulated logic for tracking user_id (placeholder)
    print(f"User {user_id} is buying {amount_sol} SOL of {token_symbol}")
    return {
        "status": "success",
        "tx_hash": "placeholder_tx_hash",
        "token": token_symbol,
        "amount": amount_sol
    }

def execute_sell(user_id, token_symbol, amount_token):
    # Simulated logic for tracking user_id (placeholder)
    print(f"User {user_id} is selling {amount_token} of {token_symbol}")
    return {
        "status": "success",
        "tx_hash": "placeholder_tx_hash",
        "token": token_symbol,
        "amount": amount_token
    }
