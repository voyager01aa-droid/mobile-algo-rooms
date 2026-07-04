# Kotak Neo API Auto-Execution Logic
from neo_api_client import NeoAPI

def login_kotak_neo(consumer_key, consumer_secret, username, password, pin):
    try:
        client = NeoAPI(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            environment="PROD"
        )
        client.login(username=username, password=password, password_type="P")
        client.session_2fa(OTP=pin)
        return client
    except Exception as e:
        return f"Login Failed: {str(e)}"

def place_auto_order(client, symbol, quantity, side):
    try:
        order = client.place_order(
            exchange_segment="NSE",
            product="MIS",      
            product_type="M",    
            quantity=str(quantity),
            price="0",
            order_side=side,
            market_protection="0",
            disclosed_quantity="0",
            trigger_price="0",
            validity="DAY",
            trading_symbol=symbol
        )
        return order
    except Exception as e:
        return None
