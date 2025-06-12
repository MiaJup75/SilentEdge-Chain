# utils/elite_ladder.py

from decimal import Decimal

ELITE_LADDER_TEMPLATE = {
    "tp1": {"gain": 4, "sell_pct": 25},
    "tp2": {"gain": 10, "sell_pct": 25},
    "tp3": {"gain": 25, "sell_pct": 25},
    "tp4": {"gain": 50, "sell_pct": 25}
}

DEFAULT_TRAILING_SL_PCT = 30  # Optional trailing stop-loss after first TP
STOP_LOSS_PCT = -25

class LadderTracker:
    def __init__(self, token_name, entry_price, trailing_sl_pct=DEFAULT_TRAILING_SL_PCT):
        self.token_name = token_name
        self.entry_price = Decimal(str(entry_price))
        self.tp_levels = ELITE_LADDER_TEMPLATE
        self.hit_levels = []
        self.stop_loss_triggered = False
        self.trailing_sl_pct = Decimal(str(trailing_sl_pct))
        self.highest_price_seen = self.entry_price
        self.trailing_active = False

    def check_price(self, current_price):
        price = Decimal(str(current_price))
        price_change = ((price - self.entry_price) / self.entry_price) * 100
        actions = []

        # Standard stop-loss (before any TPs are hit)
        if not self.hit_levels and price_change <= STOP_LOSS_PCT and not self.stop_loss_triggered:
            self.stop_loss_triggered = True
            return [{"action": "stop_loss", "token": self.token_name, "price": float(price), "loss_pct": float(price_change)}]

        # Update highest price seen
        if price > self.highest_price_seen:
            self.highest_price_seen = price

        # Trigger trailing stop-loss if enabled and TP1 has been hit
        if "tp1" in self.hit_levels and not self.stop_loss_triggered:
            self.trailing_active = True
            trail_price = self.highest_price_seen * (Decimal("1") - self.trailing_sl_pct / Decimal("100"))
            if price < trail_price:
                self.stop_loss_triggered = True
                return [{
                    "action": "trailing_stop",
                    "token": self.token_name,
                    "price": float(price),
                    "trail_price": float(trail_price),
                    "loss_from_peak": float((price - self.highest_price_seen) / self.highest_price_seen * 100)
                }]

        # Check TPs
        for tp_key, tp_data in self.tp_levels.items():
            if tp_key not in self.hit_levels:
                gain_multiple = Decimal(str(tp_data["gain"]))
                if price >= self.entry_price * gain_multiple:
                    self.hit_levels.append(tp_key)
                    actions.append({
                        "action": "take_profit",
                        "token": self.token_name,
                        "tp_level": tp_key,
                        "sell_pct": tp_data["sell_pct"],
                        "price": float(price),
                        "gain_multiple": float(gain_multiple)
                    })

        return actions if actions else None

    def reset(self):
        self.hit_levels = []
        self.stop_loss_triggered = False
        self.highest_price_seen = self.entry_price
        self.trailing_active = False
