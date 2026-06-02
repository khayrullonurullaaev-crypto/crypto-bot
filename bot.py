import time
import requests
import telebot

TELEGRAM_TOKEN = "8127999792:AAFgC2LR5hEXhxkwf5FnqbCt8Nijz7JVUtQ"
MY_CHAT_ID = 351317325
API_URL = "https://cryptobubbles.net/backend/data/bubbles1000.usd.json"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_top_growing_coins():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            sorted_coins = sorted(
                data,
                key=lambda x: x.get("performance", {}).get("hour", 0),
                reverse=True,
            )
            top_10 = sorted_coins[:10]
            current_time = time.strftime("%H:%M:%S")
            message_text = f"🚀 <b>ТОП-10 МОНЕТ ({current_time})</b>\n"
            message_text += "<i>Рост за 1 час</i>\n\n"
            for index, coin in enumerate(top_10, 1):
                symbol = coin.get("symbol", "").upper()
                name = coin.get("name", "Unknown")
                change_hour = coin.get("performance", {}).get("hour", 0)
                price = coin.get("price", 0)
                message_text += (
                    f"{index}. <b>{symbol}</b> ({name})\n"
                    f"   📈 +{change_hour:.2f}%\n"
                    f"   💰 ${price:,.4f}\n\n"
                )
            bot.send_message(
                chat_id=MY_CHAT_ID, text=message_text, parse_mode="HTML"
            )
            print(f"[{current_time}] Отправлено")
        else:
            print(f"Ошибка: {response.status_code}")
    except Exception as e:
        print(f"Ошибка: {e}")

print("Бот запущен...")
get_top_growing_coins()

while True:
    time.sleep(300)
    get_top_growing_coins()
