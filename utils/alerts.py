# utils/alerts.py

# Simple in-memory toggle store for alerts (in real use, persist this in DB)
user_alert_settings = {}

def get_alert_settings(user_id):
    """
    Returns a dict of alert settings for the user.
    """
    if user_id not in user_alert_settings:
        user_alert_settings[user_id] = {
            "price": False,
            "volume": False
        }
    return user_alert_settings[user_id]

def toggle_alert(user_id, alert_type):
    """
    Toggles the specified alert type ('price' or 'volume') for the user.
    """
    settings = get_alert_settings(user_id)
    if alert_type in settings:
        settings[alert_type] = not settings[alert_type]
