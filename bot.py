import telebot
import requests
import time
import threading
from datetime import datetime

TOKEN = "8127999792:AAFgC2LR5hEXhxkwf5FnqbCt8Nijz7JVUtQ"
CHAT_ID = "351317325"

bot = telebot.TeleBot(TOKEN)

def get_h4_klines(symbol, limit=50):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=4h&limit={limit}"
        r = requests.get(url, timeout=10)
        data = r.json()
        closes = [float(x[4]) for x in data]
        opens = [float(x[1]) for x in data]
        return closes, opens
    except:
        return [], []

def get_24h_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        r = requests.get(url, timeout=10)
        data = r.json()
        price = float(data['lastPrice'])
        volume = float(data['quoteAssetVolume'])
        price_change = float(data['priceChangePercent'])
        return price, volume, price_change
    except:
        return None, None, None

def check_long_signal(symbol):
    try:
        # H4 зелёная свеча
        closes, opens = get_h4_klines(symbol, 20)
        if len(closes) < 2:
            return None
        
        if closes[-1] <= opens[-1]:
            return None
        
        # 24ч рост
        price, volume, price_change = get_24h_data(symbol)
        if price is None or price_change <= 0:
            return None
        
        return {
            'symbol': symbol,
            'price': price,
            'volume': volume,
        }
    except:
        return None

def get_all_symbols():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        r = requests.get(url, timeout=15)
        data = r.json()
        return [x['symbol'] for x in data if x['symbol'].endswith('USDT')]
    except:
        return []

def scan_market():
    symbols = get_all_symbols()
    results = []
    for symbol in symbols:
        signal = check_long_signal(symbol)
        if signal:
            results.append(signal)
        time.sleep(0.05)
    return results

def format_message(s):
    msg = f"{s['symbol']} | ${s['price']:.6f} | ${s['volume']:,.0f}"
    return msg

def send_auto():
    while True:
        signals = scan_market()
        if signals:
            for s in signals:
                bot.send_message(CHAT_ID, format_message(s))
                time.sleep(1)
        time.sleep(900)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен!\n\nСтратегия: Зелёная H4 + Рост 24ч\n\nКоманды:\n/signal - сканировать рынок")

@bot.message_handler(commands=['signal'])
def signal(message):
    bot.reply_to(message, "Сканирую Binance...")
    signals = scan_market()
    if signals:
        for s in signals:
            bot.reply_to(message, format_message(s))
            time.sleep(1)
    else:
        bot.reply_to(message, "Сейчас нет сигналов.")

t = threading.Thread(target=send_auto)
t.daemon = True
t.start()

print("Бот запущен! H4 + 24ч")
bot.polling()
