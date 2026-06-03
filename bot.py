import time
import requests
import telebot
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MY_CHAT_ID = int(os.getenv("MY_CHAT_ID"))

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def send_signals():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return
        
        data = response.json()
        coins = []
        
        for item in data:
            symbol = item.get("symbol", "")
            if not symbol.endswith("USDT"):
                continue
            
            try:
                change = float(item.get("priceChangePercent", 0))
                if change >= 10:
                    price = float(item.get("lastPrice", 0))
                    coins.append({
                        "sym": symbol.replace("USDT", ""),
                        "chg": change,
                        "price": price
                    })
            except:
                continue
        
        coins = sorted(coins, key=lambda x: x["chg"], reverse=True)
        
        if coins:
            msg = f"🚀 IMPULSE ({time.strftime('%H:%M:%S')})\n\n"
            
            for i, c in enumerate(coins[:10], 1):
                msg += f"{i}. {c['sym']} | +{c['chg']:.2f}% | ${c['price']:.8f}\n"
            
            bot.send_message(MY_CHAT_ID, msg)
            print(f"Sent {len(coins[:10])} coins")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Bot started...")
    while True:
        send_signals()
        time.sleep(900)
