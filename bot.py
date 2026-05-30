import telebot
import requests
import time
import threading
from datetime import datetime

TOKEN = "8127999792:AAFgC2LR5hEXhxkwf5FnqbCt8Nijz7JVUtQ"
CHAT_ID = "351317325"

bot = telebot.TeleBot(TOKEN)

def get_klines(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d&limit=100"
        r = requests.get(url, timeout=10)
        data = r.json()
        closes = [float(x[4]) for x in data]
        highs = [float(x[2]) for x in data]
        lows = [float(x[3]) for x in data]
        return closes, highs, lows
    except:
        return [], [], []

def fibonacci_levels(high, low):
    diff = high - low
    levels = {
        '0.236': low + diff * 0.236,
        '0.382': low + diff * 0.382,
        '0.500': low + diff * 0.500,
        '0.618': low + diff * 0.618,
        '0.786': low + diff * 0.786,
    }
    return levels

def check_golden_cross(symbol):
    try:
        closes, highs, lows = get_klines(symbol)
        if len(closes) < 20:
            return None

        high = max(highs[-50:])
        low = min(lows[-50:])
        levels = fibonacci_levels(high, low)

        current_price = closes[-1]
        prev_price = closes[-2]
        golden = levels['0.618']

        if prev_price < golden and current_price > golden:
            entry = current_price
            take = round(entry * 1.20, 6)
            stop = round(entry * 0.90, 6)
            tv = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}"
            return {
                'symbol': symbol,
                'price': current_price,
                'golden': round(golden, 6),
                'entry': entry,
                'take': take,
                'stop': stop,
                'tv': tv
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
        signal = check_golden_cross(symbol)
        if signal:
            results.append(signal)
        time.sleep(0.1)
    return results

def send_auto():
    while True:
        now = datetime.now()
        if now.hour >= 4 or now.hour < 2:
            signals = scan_market()
            if signals:
                for s in signals:
                    msg = (
                        f"ЛОНГ СИГНАЛ - ЗОЛОТОЕ СЕЧЕНИЕ\n\n"
                        f"Монета: {s['symbol']}\n"
                        f"Цена: ${s['price']:.6f}\n"
                        f"Уровень 0.618: ${s['golden']:.6f}\n"
                        f"Вход: ${s['entry']:.6f}\n"
                        f"Тейк: ${s['take']:.6f} (+20%)\n"
                        f"Стоп: ${s['stop']:.6f} (-10%)\n"
                        f"График: {s['tv']}"
                    )
                    bot.send_message(CHAT_ID, msg)
                    time.sleep(2)
            else:
                bot.send_message(CHAT_ID, "Нет монет пересекших золотое сечение. Жду...")
        time.sleep(900)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен!\n\nКоманды:\n/signal - сканировать рынок сейчас")

@bot.message_handler(commands=['signal'])
def signal(message):
    bot.reply_to(message, "Сканирую все монеты Binance по золотому сечению... Подождите 2-3 минуты.")
    signals = scan_market()
    if signals:
        for s in signals:
            msg = (
                f"ЛОНГ СИГНАЛ - ЗОЛОТОЕ СЕЧЕНИЕ\n\n"
                f"Монета: {s['symbol']}\n"
                f"Цена: ${s['price']:.6f}\n"
                f"Уровень 0.618: ${s['golden']:.6f}\n"
                f"Вход: ${s['entry']:.6f}\n"
                f"Тейк: ${s['take']:.6f} (+20%)\n"
                f"Стоп: ${s['stop']:.6f} (-10%)\n"
                f"График: {s['tv']}"
            )
            bot.reply_to(message, msg)
            time.sleep(1)
    else:
        bot.reply_to(message, "Сейчас нет монет пересекших золотое сечение.")

t = threading.Thread(target=send_auto)
t.daemon = True
t.start()

print("Бот запущен!")
bot.polling()
