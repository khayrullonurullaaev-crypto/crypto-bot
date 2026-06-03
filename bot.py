import time
import requests
import telebot
import os

# Твои данные (Railway автоматически их устанавливает)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MY_CHAT_ID = int(os.getenv("MY_CHAT_ID"))
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Binance API endpoints
BINANCE_BASE_URL = "https://api.binance.com"
TICKER_ENDPOINT = "/api/v3/ticker/24hr"
KLINES_ENDPOINT = "/api/v3/klines"

# Проверка переменных
if not all([TELEGRAM_TOKEN, MY_CHAT_ID, BINANCE_API_KEY, BINANCE_API_SECRET]):
    raise ValueError("Все переменные должны быть установлены на Railway!")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_binance_data():
    try:
        response = requests.get(f"{BINANCE_BASE_URL}{TICKER_ENDPOINT}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка API: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None

def get_hourly_kline(symbol):
    try:
        params = {
            "symbol": symbol,
            "interval": "1h",
            "limit": 2
        }
        response = requests.get(
            f"{BINANCE_BASE_URL}{KLINES_ENDPOINT}",
            params=params,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if len(data) >= 2:
                prev_close = float(data[0][4])
                curr_close = float(data[1][4])
                
                if prev_close > 0:
                    hour_change = ((curr_close - prev_close) / prev_close) * 100
                    return hour_change, curr_close
        return None, None
    except Exception as e:
        return None, None

def get_top_growing_coins():
    try:
        tickers = get_binance_data()
        
        if not tickers:
            return
        
        filtered_coins = []
        
        for ticker in tickers:
            symbol = ticker.get("symbol", "")
            
            if not symbol.endswith("USDT"):
                continue
            
            hour_change, price = get_hourly_kline(symbol)
            
            if hour_change is not None and hour_change >= 10.0:
                filtered_coins.append({
                    "symbol": symbol.replace("USDT", ""),
                    "change": hour_change,
                    "price": price
                })
        
        sorted_coins = sorted(
            filtered_coins,
            key=lambda x: x["change"],
            reverse=True
        )
        
        current_time = time.strftime("%H:%M:%S")
        
        if sorted_coins:
            message_text = f"🚀 <b>IMPULSE DETECTED</b> ({current_time})\n"
            message_text += "<i>Монеты с ростом > 10% за час (Binance Real-Time):</i>\n\n"
            
            for index, coin in enumerate(sorted_coins[:10], 1):
                symbol = coin["symbol"]
                change = coin["change"]
                price = coin["price"]
                message_text += f"{index}. <b>{symbol}</b> | 📈 +{change:.2f}% | 💰 ${price:.8f}\n"
            
            bot.send_message(chat_id=MY_CHAT_ID, text=message_text, parse_mode="HTML")
            print(f"[{current_time}] Отправлено: {len(sorted_coins[:10])} монет")
        else:
            print(f"[{current_time}] Нет монет с ростом > 10%")
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    print("Binance Real-Time Bot запущен (15 мин интервал)...")
    while True:
        get_top_growing_coins()
        time.sleep(900)
