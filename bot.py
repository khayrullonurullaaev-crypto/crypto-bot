import telebot
import requests
import time
import threading
from datetime import datetime

TOKEN = "8127999792:AAFgC2LR5hEXhxkwf5FnqbCt8Nijz7JVUtQ"
CHAT_ID = "351317325"

bot = telebot.TeleBot(TOKEN)

def get_all_coins():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        r = requests.get(url, timeout=15)
        data = r.json()
        usdt_pairs = [x for x in data if x['symbol'].endswith('USDT')]
        return usdt_pairs
    except:
        return []

def get_pump_signals(coins):
    signals = []
    for coin in coins:
        try:
            change = float(coin['priceChangePercent'])
            price = float(coin['lastPrice'])
            volume = float(coin['quoteVolume'])
            if change >= 50 and volume > 100000:
                signals.append({
                    'symbol': coin['symbol'],
                    'price': price,
                    'change': change,
                    'volume': volume
                })
        except:
            continue
    signals.sort(key=lambda x: x['change'], reverse=True)
    return signals[:10]

def is_trading_time():
    now = datetime.now()
    hour = now.hour
    return hour >= 4 or hour < 2

def send_signals_auto():
    while True:
        if is_trading_time():
            coins = get_all_coins()
            signals = get_pump_signals(coins)
            if signals:
                msg = "ПАМП СИГНАЛЫ - РОСТ 50-100%+\n\n"
                for s in signals:
                    msg += f"{s['symbol']}\n"
                    msg += f"Цена: ${s['price']:,.4f}\n"
                    msg += f"Рост 24ч: +{s['change']:.2f}%\n"
                    msg += f"Объем: ${s['volume']:,.0f}\n\n"
                bot.send_message(CHAT_ID, msg)
        time.sleep(900)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я крипто-бот для памп сигналов!\n\nКоманды:\n/signal - сигналы сейчас\n/top - топ 5 монет")

@bot.message_handler(commands=['signal'])
def signal(message):
    bot.reply_to(message, "Сканирую все монеты Binance...")
    coins = get_all_coins()
    signals = get_pump_signals(coins)
    if signals:
        msg = "ПАМП СИГНАЛЫ - РОСТ 50-100%+\n\n"
        for s in signals:
            msg += f"{s['symbol']}\n"
            msg += f"Цена: ${s['price']:,.4f}\n"
            msg += f"Рост 24ч: +{s['change']:.2f}%\n"
            msg += f"Объем: ${s['volume']:,.0f}\n\n"
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, "Сейчас нет монет с ростом 50%+. Жди...")

@bot.message_handler(commands=['top'])
def top(message):
    bot.reply_to(message, "Получаю топ 5...")
    coins = get_all_coins()
    signals = get_pump_signals(coins)[:5]
    if signals:
        msg = "ТОП 5 ПАМП МОНЕТ\n\n"
        for i, s in enumerate(signals, 1):
            msg += f"{i}. {s['symbol']} +{s['change']:.2f}%\n"
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, "Сейчас нет монет с ростом 50%+.")

t = threading.Thread(target=send_signals_auto)
t.daemon = True
t.start()

print("Бот запущен!")
bot.polling()
