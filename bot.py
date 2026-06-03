import time
import requests
import telebot
import os
from dotenv import load_dotenv
from binance.client import Client

# Загружаем переменные окружения
load_dotenv()

# Твои данные из переменных
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MY_CHAT_ID = int(os.getenv("MY_CHAT_ID"))
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Проверка, что все переменные установлены
if not all([TELEGRAM_TOKEN, MY_CHAT_ID, BINANCE_API_KEY, BINANCE_API_SECRET]):
    raise ValueError("Все переменные (TELEGRAM_TOKEN, MY_CHAT_ID, BINANCE_API_KEY, BINANCE_API_SECRET) должны быть установлены!")

# Инициализируем бота и клиент Binance
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)

def get_top_growing_coins():
    try:
        # Получаем 24-часовую статистику для всех пар USDT
        tickers = client.get_ticker()
        
        # Фильтруем только USDT пары и ищем монеты с ростом >= 10% за час
        filtered_coins = []
        
        for ticker in tickers:
            symbol = ticker.get("symbol", "")
            
            # Ищем только USDT пары
            if not symbol.endswith("USDT"):
                continue
            
            try:
                # Получаем 1-часовой свечи для расчета часового роста
                klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=2)
                
                if len(klines) >= 2:
                    prev_close = float(klines[0][4])  # Close цена предыдущей свечи
                    curr_close = float(klines[1][4])  # Close цена текущей свечи
                    
                    if prev_close > 0:
                        hour_change = ((curr_close - prev_close) / prev_close) * 100
                        
                        if hour_change >= 10.0:
                            curr_price = float(klines[1][4])
                            filtered_coins.append({
                                "symbol": symbol.replace("USDT", ""),
                                "change": hour_change,
                                "price": curr_price
                            })
            except Exception as e:
                continue
        
        # Сортируем по росту (от большего к меньшему)
        sorted_coins = sorted(filtered_coins, key=lambda x: x["change"], reverse=True)
        
        current_time = time.strftime("%H:%M:%S")
        
        if sorted_coins:
            message_text = f"🚀 <b>IMPULSE DETECTED</b> ({current_time})\n"
            message_text += "<i>Монеты с ростом > 10% за час (Binance Real-Time):</i>\n\n"
            
            # Берем Топ-10
            for index, coin in enumerate(sorted_coins[:10], 1):
                symbol = coin["symbol"]
                change = coin["change"]
                price = coin["price"]
                message_text += f"{index}. <b>{symbol}</b> | 📈 +{change:.2f}% | 💰 ${price:.8f}\n"
            
            bot.send_message(chat_id=MY_CHAT_ID, text=message_text, parse_mode="HTML")
            print(f"[{current_time}] Отправлено: {len(sorted_coins[:10])} монет")
        else:
            print(f"[{current_time}] Нет монет с ростом > 10%. Ждем...")
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    print("Binance Real-Time Impulser запущен (фильтр роста > 10%, реальное время, 15 мин)...")
    while True:
        get_top_growing_coins()
        time.sleep(900)  # 15 минут
