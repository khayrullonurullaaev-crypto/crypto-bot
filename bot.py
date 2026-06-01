import telebot
import requests
import time
import threading

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

def get_long_signals(coins):
    signals = []
    for coin in coins:
        try:
            change = float(coin['priceChangePercent'])
            price = float(coin['lastPrice'])
            volume = float(coin['quoteAssetVolume'])
            if change >= 20:
                signals.append({
                    'symbol': coin['symbol'],
                    'price': price,
                    'volume': volume
                })
        except:
            continue
    signals.sort(key=lambda x: x['price'], reverse=True)
    return signals[:50]

def send_signals_auto():
    while True:
        coins = get_all_coins()
        signals = get_long_signals(coins)
        if signals:
            for s in signals:
                msg = f"{s['symbol']} | ${s['price']:.6f} | ${s['volume']:,.0f}"
                bot.send_message(CHAT_ID, msg)
                time.sleep(1)
        time.sleep(900)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен!\n\nСтратегия: Рост 20%+ за 24ч\n\nКоманды:\n/signal - сигналы сейчас")

@bot.message_handler(commands=['signal'])
def signal(message):
    bot.reply_to(message, "Сканирую Binance...")
    coins = get_all_coins()
    signals = get_long_signals(coins)
    if signals:
        for s in signals:
            msg = f"{s['symbol']} | ${s['price']:.6f} | ${s['volume']:,.0f}"
            bot.reply_to(message, msg)
            time.sleep(0.5)
    else:
        bot.reply_to(message, "Сейчас нет монет с ростом 20%+. Жди...")

t = threading.Thread(target=send_signals_auto)
t.daemon = True
t.start()

print("Бот запущен! Рост 20%+")
bot.polling()
