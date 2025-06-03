# utils/trade.py

def execute_buy(token_symbol, amount_sol):
    return {
        "status": "success",
        "tx_hash": "placeholder_tx_hash",
        "token": token_symbol,
        "amount": amount_sol
    }

def execute_sell(token_symbol, amount_token):
    return {
        "status": "success",
        "tx_hash": "placeholder_tx_hash",
        "token": token_symbol,
        "amount": amount_token
    }
