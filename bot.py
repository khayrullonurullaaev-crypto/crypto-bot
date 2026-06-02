import time
import requests
import telebot

# Твои данные
TELEGRAM_TOKEN = "8127999792:AAFgC2LR5hEXhxkwf5FnqbCt8Nijz7JVUtQ"
MY_CHAT_ID = 351317325
API_URL = "https://cryptobubbles.net/backend/data/bubbles1000.usd.json"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Порог объема (в долларах)
MIN_VOLUME = 1000000 

def get_top_growing_coins():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Фильтруем: рост >= 10% И объем >= 1 млн $
            filtered_coins = [
                c for c in data 
                if c.get("performance", {}).get("hour", 0) >= 10.0 
                and c.get("volume24", 0) >= MIN_VOLUME
            ]
            
            # Сортируем оставшиеся по силе роста
            sorted_coins = sorted(
                filtered_coins, 
                key=lambda x: x.get("performance", {}).get("hour", 0), 
                reverse=True
            )
            
            current_time = time.strftime("%H:%M:%S")
            
            if sorted_coins:
                message_text = f"🛡 <b>SMC IMPULSE (Volume Filtered)</b> ({current_time})\n"
                message_text += "<i>Рост > 10%, Volume > $1M:</i>\n\n"
                
                for index, coin in enumerate(sorted_coins[:10], 1):
                    symbol = coin.get("symbol", "").upper()
                    change = coin.get("performance", {}).get("hour", 0)
                    price = coin.get("price", 0)
                    volume = coin.get("volume24", 0)
                    message_text += f"{index}. <b>{symbol}</b> | 📈 +{change:.2f}% | 💰 ${price:,.4f}\n"
                
                bot.send_message(chat_id=MY_CHAT_ID, text=message_text, parse_mode="HTML")
                print(f"[{current_time}] Отправлено монет: {len(sorted_coins[:10])}")
            else:
                print(f"[{current_time}] Нет монет под фильтры (Volume > 1M, Change > 10%)")
        else:
            print(f"Ошибка API: {response.status_code}")
    except Exception as e:
        print(f"Ошибка: {e}")

print("Бот запущен с фильтром объема 1млн$...")

while True:
    get_top_growing_coins()
    time.sleep(900) # 15 минут
