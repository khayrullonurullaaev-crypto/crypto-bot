import telebot
import requests
import time
import threading

TOKEN = "8127999792:AAFgC2LR5hEXhxkwf5FnqbCt8Nijz7JVUtQ"
CHAT_ID = "351317325"

bot = telebot.TeleBot(TOKEN)

def get_h1_klines(symbol, limit=50):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit={limit}"
        r = requests.get(url, timeout=10)
        data = r.json()
        closes = [float(x[4]) for x in data]
        highs = [float(x[2]) for x in data]
        lows = [float(x[3]) for x in data]
        opens = [float(x[1]) for x in data]
        return closes, highs, lows, opens
    except:
        return [], [], [], []

def check_bullish_trend(closes):
    if len(closes) < 3:
        return False
    if closes[-1] > closes[-2] > closes[-3]:
        return True
    return False

def check_bos(highs):
    if len(highs) < 10:
        return False
    prev_high = max(highs[-10:-1])
    if highs[-1] > prev_high:
        return True
    return False

def check_signal(symbol):
    try:
        closes, highs, lows, opens = get_h1_klines(symbol, 50)
        if len(closes) < 15:
            return None
        
        if not check_bullish_trend(closes):
            return None
        
        if not check_bos(highs):
            return None
        
        price = closes[-1]
        
        # Объём
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        r = requests.get(url, timeout=10)
        data = r.json()
        volume = float(data['quoteAssetVolume'])
        
        return {
            'symbol': symbol,
            'price': price,
            'volume': volume
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
    msg = f"{s['symbol']} | ${s['price']:.6f} | ${s['volume']:,.0f}"
    return msg

def send_signals_auto():
    while True:
        signals = scan_market()
        if signals:
            for s in signals:
                bot.send_message(CHAT_ID, format_message(s))
                time.sleep(1)
        time.sleep(900)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен!\n\nСтратегия: Бычий тренд H1 + BOS\n\nКоманды:\n/signal - сигналы сейчас")

@bot.message_handler(commands=['signal'])
def signal(message):
    bot.reply_to(message, "Сканирую Binance...")
    signals = scan_market()
    if signals:
        for s in signals:
            bot.reply_to(message, format_message(s))
            time.sleep(1)
    else:
        bot.reply_to(message, "Сейчас нет сигналов. Жди...")

t = threading.Thread(target=send_signals_auto)
t.daemon = True
t.start()

print("Бот запущен! Bullish Trend H1 + BOS")
bot.polling()
