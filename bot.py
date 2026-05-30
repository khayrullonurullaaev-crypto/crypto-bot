import telebot
import requests
import time
import threading
from datetime import datetime

TOKEN = "8127999792:AAFgC2LR5hEXhxkwf5FnqbCt8Nijz7JVUtQ"
CHAT_ID = "351317325"

bot = telebot.TeleBot(TOKEN)

def get_klines(symbol, interval, limit=200):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        r = requests.get(url, timeout=10)
        data = r.json()
        closes = [float(x[4]) for x in data]
        highs = [float(x[2]) for x in data]
        lows = [float(x[3]) for x in data]
        volumes = [float(x[5]) for x in data]
        return closes, highs, lows, volumes
    except:
        return [], [], [], []

def ema(closes, period):
    if len(closes) < period:
        return []
    k = 2 / (period + 1)
    ema_values = [sum(closes[:period]) / period]
    for price in closes[period:]:
        ema_values.append(price * k + ema_values[-1] * (1 - k))
    return ema_values

def fibonacci_levels(high, low):
    diff = high - low
    return {
        '0.618': low + diff * 0.618,
        '0.650': low + diff * 0.650,
    }

def find_order_block(closes, highs, lows, current_price):
    for i in range(len(closes) - 10, len(closes) - 2):
        if closes[i] < lows[i-1] and closes[i+1] > highs[i]:
            ob_high = highs[i]
            ob_low = lows[i]
            if ob_low <= current_price <= ob_high * 1.01:
                return ob_low, ob_high
    return None, None

def check_bos(closes):
    if len(closes) < 20:
        return False
    recent_high = max(closes[-20:-1])
    if closes[-1] > recent_high:
        return True
    return False

def check_signal(symbol):
    try:
        # H4 - Фибоначчи Golden Pocket
        h4_closes, h4_highs, h4_lows, h4_vols = get_klines(symbol, '4h', 100)
        if len(h4_closes) < 50:
            return None

        high_h4 = max(h4_highs[-50:])
        low_h4 = min(h4_lows[-50:])
        fib = fibonacci_levels(high_h4, low_h4)
        golden_low = fib['0.618']
        golden_high = fib['0.650']

        # EMA 50/200 на H4 - золотой крест
        ema50 = ema(h4_closes, 50)
        ema200 = ema(h4_closes, 200)
        if len(ema50) < 2 or len(ema200) < 2:
            return None

        # EMA 50 должна быть выше EMA 200 (восходящий тренд)
        if ema50[-1] <= ema200[-1]:
            return None

        # H1 - точка входа и подтверждение
        h1_closes, h1_highs, h1_lows, h1_vols = get_klines(symbol, '1h', 50)
        if len(h1_closes) < 20:
            return None

        current = h1_closes[-1]
        prev = h1_closes[-2]

        # Цена пересекла Golden Pocket снизу вверх
        if not (prev < golden_low and current > golden_low):
            return None

        # BOS - Break of Structure на H1
        bos = check_bos(h1_closes)

        # Order Block на H1
        ob_low, ob_high = find_order_block(h1_closes, h1_highs, h1_lows, current)

        entry = current
        take = round(entry * 1.20, 6)
        stop = round(entry * 0.90, 6)
        tv = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}"

        return {
            'symbol': symbol,
            'price': current,
            'golden_low': round(golden_low, 6),
            'golden_high': round(golden_high, 6),
            'ema50': round(ema50[-1], 6),
            'ema200': round(ema200[-1], 6),
            'bos': bos,
            'ob_low': round(ob_low, 6) if ob_low else None,
            'ob_high': round(ob_high, 6) if ob_high else None,
            'entry': entry,
            'take': take,
            'stop': stop,
            'tv': tv
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
    msg += f"ФИБОНАЧЧИ H4\n"
    msg += f"Golden Pocket: ${s['golden_low']:.6f} - ${s['golden_high']:.6f}\n\n"
    msg += f"EMA\n"
    msg += f"EMA 50: ${s['ema50']:.6f}\n"
    msg += f"EMA 200: ${s['ema200']:.6f}\n"
    msg += f"Тренд: ВВЕРХ\n\n"
    msg += f"SMC\n"
    msg += f"BOS: {'ДА' if s['bos'] else 'НЕТ'}\n"
    if s['ob_low']:
        msg += f"Order Block: ${s['ob_low']:.6f} - ${s['ob_high']:.6f}\n"
    msg += f"\nТОЧКА ВХОДА (H1): ${s['entry']:.6f}\n"
    msg += f"ТЕЙК: ${s['take']:.6f} (+20%)\n"
    msg += f"СТОП: ${s['stop']:.6f} (-10%)\n\n"
    msg += f"График: {s['tv']}"
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
    bot.reply_to(message, "Бот запущен!\n\nСтратегия:\nFibonacci H4 + EMA 50/200 + SMC + H1 вход\n\nКоманды:\n/signal - сканировать рынок")

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

print("Бот запущен! Fibonacci H4 + EMA 50/200 + SMC + H1")
bot.polling()
