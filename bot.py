import time
import requests
import telebot

# Твои данные
TELEGRAM_TOKEN = "8127999792:AAFgC2LR5hEXhxkwf5FnqbCt8Nijz7JVUtQ"
MY_CHAT_ID = 351317325
API_URL = "https://cryptobubbles.net/backend/data/bubbles1000.usd.json"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_top_growing_coins():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Фильтруем: только те, у кого рост >= 10% (без фильтра объема)
            filtered_coins = [
                c for c in data 
                if c.get("performance", {}).get("hour", 0) >= 10.0
            ]
            
            # Сортируем оставшиеся по силе роста
            sorted_coins = sorted(
                filtered_coins, 
                key=lambda x: x.get("performance", {}).get("hour", 0), 
                reverse=True
            )
            
            current_time = time.strftime("%H:%M:%S")
            
            if sorted_coins:
                message_text = f"🚀 <b>IMPULSE DETECTED</b> ({current_time})\n"
                message_text += "<i>Монеты с ростом > 10% за час:</i>\n\n"
                
                # Берем Топ-10 из отфильтрованных
                for index, coin in enumerate(sorted_coins[:10], 1):
                    symbol = coin.get("symbol", "").upper()
                    change = coin.get("performance", {}).get("hour", 0)
                    price = coin.get("price", 0)
                    message_text += f"{index}. <b>{symbol}</b> | 📈 +{change:.2f}% | 💰 ${price:,.4f}\n"
                
                bot.send_message(chat_id=MY_CHAT_ID, text=message_text, parse_mode="HTML")
                print(f"[{current_time}] Отправлено: {len(sorted_coins[:10])} монет")
            else:
                print(f"[{current_time}] Нет монет с ростом > 10%. Ждем...")
        else:
            print(f"Ошибка API: {response.status_code}")
    except Exception as e:
        print(f"Ошибка: {e}")

print("SMC Impulser запущен (фильтр роста > 10%, без фильтра объема, 15 мин)...")

while True:
    get_top_growing_coins()
    time.sleep(900) # 15 минут
