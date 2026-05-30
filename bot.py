import telebot
import requests
import time
import threading
from datetime import datetime

TOKEN = "8127999792:AAFgC2LR5hEXhxkwf5FnqbCt8Nijz7JVUtQ"
CHAT_ID = "351317325"

bot = telebot.TeleBot(TOKEN)

def get_klines(symbol, interval, limit=100):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
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
    return {
        '0.236': low + diff * 0.236,
        '0.382': low + diff * 0.382,
        '0.500': low + diff * 0.500,
        '0.618': low + diff * 0.618,
        '0.786': low + diff * 0.786,
    }

def check_signal(symbol):
    try:
        # D1 - Фибоначчи уровни
        d1_closes, d1_highs, d1_lows = get_klines(symbol, '1d', 100)
        if len(d1_closes) < 20:
            return None

        high_d1 = max(d1_highs[-50:])
        low_d1 = min(d1_lows[-50:])
        fib = fibonacci_levels(high_d1, low_d1)
        golden = fib['0.618']

        # H4 - подтверждение
        h4_closes, h4_highs, h4_lows = get_klines(symbol, '4h', 50)
        if len(h4_closes) < 10:
            return None

        current = h4_closes[-1]
        prev = h4_closes[-2]

        # Цена пересекла 0.618 снизу вверх на H4
        if prev < golden and current > golden:
            # Проверяем что D1 тренд восходящий
            if d1_closes[-1] > d1_closes[-10]:
                entry = current
                take = round(entry * 1.20, 6)
                stop = round(entry * 0.90, 6)
                tv = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}"
                return {
                    'symbol': symbol,
                    'price': current,
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
        signal = check_signal(symbol)
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
                        f"ЛОНГ СИГНАЛ\n\n"
                        f"Монета: {s['symbol']}\n"
                        f"Фибо 0.618 (D1): ${s['golden']:.6f}\n"
                        f"Вход (H4): ${s['entry']:.6f}\n"
                        f"Тейк: ${s['take']:.6f} (+20%)\n"
                        f"Стоп: ${s['stop']:.6f} (-10%)\n"
                        f"График: {s['tv']}"
                    )
                    bot.send_message(CHAT_ID, msg)
                    time.sleep(2)
        time.sleep(900)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен!\n\nФибоначчи D1 + подтверждение H4\n\nКоманды:\n/signal - сканировать рынок")

@bot.message_handler(commands=['signal'])
def signal(message):
    bot.reply_to(message, "Сканирую Binance... Подождите 3-5 минут.")
    signals = scan_market()
    if signals:
        for s in signals:
            msg = (
                f"ЛОНГ СИГНАЛ\n\n"
                f"Монета: {s['symbol']}\n"
                f"Фибо 0.618 (D1): ${s['golden']:.6f}\n"
                f"Вход (H4): ${s['entry']:.6f}\n"
                f"Тейк: ${s['take']:.6f} (+20%)\n"
                f"Стоп: ${s['stop']:.6f} (-10%)\n"
                f"График: {s['tv']}"
            )
            bot.reply_to(message, msg)
            time.sleep(1)
    else:
        bot.reply_to(message, "Сейчас нет сигналов. Жди...")

t = threading.Thread(target=send_auto)
t.daemon = True
t.start()

print("Бот запущен! D1 Фибо + H4 подтверждение")
bot.polling()
