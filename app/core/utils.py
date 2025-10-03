from datetime import datetime, date
import json

def format_currency(amount):
    return f"₱{amount:.2f}"

def get_current_date():
    return date.today().isoformat()

def validate_price(price_str):
    try:
        price = float(price_str)
        return price >= 0
    except ValueError:
        return False

def validate_stock(stock_str):
    try:
        stock = int(stock_str)
        return stock >= 0
    except ValueError:
        return False

def serialize_items(items):
    return json.dumps(items)

def deserialize_items(items_str):
    try:
        return json.loads(items_str)
    except:
        return []