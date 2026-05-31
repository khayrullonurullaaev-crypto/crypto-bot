import telebot
import requests
import time
import threading
from datetime import datetime

TOKEN = "8127999792:AAFgC2LR5hEXhxkwf5FnqbCt8Nijz7JVUtQ"
CHAT_ID = "351317325"

bot = telebot.TeleBot(TOKEN)

def get_klines(symbol, interval, limit=50):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        r = requests.get(url, timeout=10)
        data = r.json()
        closes = [float(x[4]) for x in data]
        highs = [float(x[2]) for x in data]
        lows = [float(x[3]) for x in data]
        opens = [float(x[1]) for x in data]
        return closes, highs, lows, opens
    except:
        return [], [], [], []

def bullish_engulfing(opens, closes):
    if len(opens) < 2:
        return False
    prev_open = opens[-2]
    prev_close = closes[-2]
    curr_open = opens[-1]
    curr_close = closes[-1]
    prev_bearish = prev_close < prev_open
    curr_bullish = curr_close > curr_open
    engulfing = curr_open <= prev_close and curr_close >= prev_open
    return prev_bearish and curr_bullish and engulfing

def check_h1_long(closes, opens):
    if len(closes) < 3:
        return False
    if closes[-1] > closes[-2]:
        return True
    return False

def check_signal(symbol):
    try:
        # H4 - поглощение
        h4_closes, h4_highs, h4_lows, h4_opens = get_klines(symbol, '4h', 50)
        if len(h4_closes) < 10:
            return None

        if not bullish_engulfing(h4_opens, h4_closes):
            return None

        # H1 - подтверждение
        h1_closes, h1_highs, h1_lows, h1_opens = get_klines(symbol, '1h', 20)
        if len(h1_closes) < 5:
            return None

        if not check_h1_long(h1_closes, h1_opens):
            return None

        return {
            'symbol': symbol,
            'price': h1_closes[-1],
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
        signal = check_signal(symbol)
        if signal:
            results.append(signal)
        time.sleep(0.1)
    return results

def format_message(s):
    msg = f"ЛОНГ СИГНАЛ\n\n"
    msg += f"Монета: {s['symbol']}\n"
    msg += f"Цена: ${s['price']:.6f}\n\n"
    msg += f"Поглощение H4: ДА\n"
    msg += f"Подтверждение H1: ДА\n"
    return msg

def send_auto():
    while True:
        now = datetime.now()
        if now.hour >= 4 or now.hour < 2:
            signals = scan_market()
            if signals:
                for s in signals:
                    bot.send_message(CHAT_ID, format_message(s))
                    time.sleep(2)
        time.sleep(900)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен!\n\nСтратегия:\nПоглощение H4 + Подтверждение H1\n\nКоманды:\n/signal - сканировать рынок")

@bot.message_handler(commands=['signal'])
def signal(message):
    bot.reply_to(message, "Сканирую Binance... Подождите 3-5 минут.")
    signals = scan_market()
    if signals:
        for s in signals:
            bot.reply_to(message, format_message(s))
            time.sleep(1)
    else:
        bot.reply_to(message, "Сейчас нет сигналов. Жди...")

t = threading.Thread(target=send_auto)
t.daemon = True
t.start()

print("Бот запущен! Bullish Engulfing H4 + H1")
bot.polling()
