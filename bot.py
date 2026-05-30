import telebot
import requests
import time
import threading
from datetime import datetime

TOKEN = "8127999792:AAFgC2LR5hEXhxkwf5FnqbCt8Nijz7JVUtQ"
CHAT_ID = "351317325"

bot = telebot.TeleBot(TOKEN)

def get_signals():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        r = requests.get(url, timeout=15)
        data = r.json()
        signals = []
        for coin in data:
            if not coin['symbol'].endswith('USDT'):
                continue
            change = float(coin['priceChangePercent'])
            price = float(coin['lastPrice'])
            volume = float(coin['quoteVolume'])
            if change >= 20 and volume > 1000000:
                entry = price
                take = round(price * 1.20, 6)
                stop = round(price * 0.90, 6)
                tv = f"https://www.tradingview.com/chart/?symbol=BINANCE:{coin['symbol']}"
                signals.append({
                    'symbol': coin['symbol'],
                    'price': price,
                    'change': change,
                    'entry': entry,
                    'take': take,
                    'stop': stop,
                    'tv': tv
                })
        signals.sort(key=lambda x: x['change'], reverse=True)
        return signals[:10]
    except:
        return []

def send_auto():
    while True:
        now = datetime.now()
        if now.hour >= 4 or now.hour < 2:
            signals = get_signals()
            if signals:
                for s in signals:
                    msg = (
                        f"СИГНАЛ: {s['symbol']}\n"
                        f"Рост: +{s['change']:.2f}%\n"
                        f"Вход: ${s['entry']:.6f}\n"
                        f"Тейк: ${s['take']:.6f} (+20%)\n"
                        f"Стоп: ${s['stop']:.6f} (-10%)\n"
                        f"График: {s['tv']}"
                    )
                    bot.send_message(CHAT_ID, msg)
                    time.sleep(2)
        time.sleep(900)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен! Ищу монеты с ростом 20%+\n\nКоманды:\n/signal - сигналы сейчас")

@bot.message_handler(commands=['signal'])
def signal(message):
    bot.reply_to(message, "Сканирую Binance...")
    signals = get_signals()
    if signals:
        for s in signals:
            msg = (
                f"СИГНАЛ: {s['symbol']}\n"
                f"Рост: +{s['change']:.2f}%\n"
                f"Вход: ${s['entry']:.6f}\n"
                f"Тейк: ${s['take']:.6f} (+20%)\n"
                f"Стоп: ${s['stop']:.6f} (-10%)\n"
                f"График: {s['tv']}"
            )
            bot.reply_to(message, msg)
            time.sleep(1)
    else:
        bot.reply_to(message, "Сейчас нет монет с ростом 20%+. Жди...")

t = threading.Thread(target=send_auto)
t.daemon = True
t.start()

print("Бот запущен!")
bot.polling()
