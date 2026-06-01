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

def check_long_signal(symbol):
    try:
        closes, opens = get_h4_klines(symbol, 20)
        if len(closes) < 2:
            return None
        
        # Если последняя H4 свеча зелёная (close > open) - ЛОНГ
        if closes[-1] > opens[-1]:
            return {
                'symbol': symbol,
                'price': closes[-1],
            }
        return None
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
    msg = f"ЛОНГ СИГНАЛ\n\n"
    msg += f"Монета: {s['symbol']}\n"
    msg += f"Цена: ${s['price']:.6f}\n"
    return msg

def send_auto():
    while True:
        now = datetime.now()
        if now.hour >= 4 or now.hour < 2:
            signals = scan_market()
            if signals:
                for s in signals:
                    bot.send_message(CHAT_ID, format_message(s))
                    time.sleep(1)
        time.sleep(900)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен!\n\nСтратегия: ЛОНГ на H4\n\nКоманды:\n/signal - сканировать рынок")

@bot.message_handler(commands=['signal'])
def signal(message):
    bot.reply_to(message, "Сканирую Binance...")
    signals = scan_market()
    if signals:
        for s in signals:
            bot.reply_to(message, format_message(s))
            time.sleep(1)
    else:
        bot.reply_to(message, "Сейчас нет сигналов ЛОНГ на H4.")

t = threading.Thread(target=send_auto)
t.daemon = True
t.start()

print("Бот запущен! ЛОНГ на H4")
bot.polling()
