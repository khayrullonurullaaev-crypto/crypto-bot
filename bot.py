import time
import requests
import telebot
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MY_CHAT_ID = os.getenv("MY_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_growing_coins():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=10)
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
                        "change": change,
                        "price": price
                    })
            except:
                pass
        
        coins = sorted(coins, key=lambda x: x["change"], reverse=True)
        
        if coins:
            msg = f"🚀 IMPULSE ({time.strftime('%H:%M:%S')})\n"
            msg += f"Топ-10 монет с ростом > 10% за час:\n\n"
            
            for i, c in enumerate(coins[:10], 1):
                msg += f"{i}. {c['sym']} | 📈 +{c['change']:.2f}% | 💰 ${c['price']:.8f}\n"
            
            bot.send_message(MY_CHAT_ID, msg)
            print(f"✅ Отправлено {len(coins[:10])} монет")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🤖 Бот запущен! Проверка каждые 15 минут...")
    while True:
        get_growing_coins()
        time.sleep(900)
