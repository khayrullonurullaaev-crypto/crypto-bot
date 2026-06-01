import time
import requests
import telebot

# НАСТРОЙКИ БОТА @zet_crypto_signal_bot
TELEGRAM_TOKEN = "8127999792:AAFgC2LR5hEXhxkwf5FnqbCt8Nijz7JVUtQ"
CHAT_ID = "351317325"
# Эндпоинт CryptoBubbles для топ-1000 монет в USD
API_URL = "https://cryptobubbles.net/backend/data/bubbles1000.usd.json"

# Инициализируем Telegram бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)


def get_top_growing_coins():
    try:
        # Запрашиваем данные с сайта
        response = requests.get(API_URL, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Сортируем монеты по росту за последний час ('hour')
            sorted_coins = sorted(
                data,
                key=lambda x: x.get("performance", {}).get("hour", 0),
                reverse=True,
            )

            # Выбираем ТОП-10
            top_10 = sorted_coins[:10]

            # Формируем красивое текстовое сообщение
            current_time = time.strftime("%H:%M:%S")
            message_text = f"🚀 <b>ТОП-10 ИМПУЛЬСНЫХ МОНЕТ ({current_time})</b>\n"
            message_text += "<i>Фильтрация: рост за 1 час</i>\n\n"

            for index, coin in enumerate(top_10, 1):
                symbol = coin.get("symbol", "").upper()
                name = coin.get("name", "Unknown")
                change_hour = coin.get("performance", {}).get("hour", 0)
                price = coin.get("price", 0)

                # Добавляем строчку монеты в общее сообщение
                message_text += (
                    f"{index}. <b>{symbol}</b> ({name})\n"
                    f"   📈 Рост: +{change_hour:.2f}%\n"
                    f"   💰 Цена: ${price:,.4f}\n\n"
                )

            # Отправляем сообщение тебе в Telegram (включаем HTML-теги для жирного шрифта)
            bot.send_message(
                chat_id=MY_CHAT_ID, text=message_text, parse_mode="HTML"
            )
            print(f"[{current_time}] Сигнал успешно отправлен в Telegram.")

        else:
            print(f"Ошибка получения данных. Статус: {response.status_code}")

    except Exception as e:
        print(f"Ошибка в работе парсера: {e}")


# Приветственное сообщение в консоли при запуске
print("Бот-сканер успешно запущен на сервере и начал работу...")

# Сразу делаем первую проверку при запуске, чтобы не ждать 5 минут
get_top_growing_coins()

# Бесконечный цикл с интервалом в 5 минут (300 секунд)
while True:
    time.sleep(300)
    get_top_growing_coins()
