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

def get_top_longs(coins):
    signals = []
    for coin in coins:
        try:
            change = float(coin['priceChangePercent'])
            if change > 5:
                signals.append({
                    'symbol': coin['symbol'],
                    'price': float(coin['lastPrice']),
                    'change': change,
                    'volume': float(coin['quoteAssetVolume'])
                })
        except:
            continue
    signals.sort(key=lambda x: x['change'], reverse=True)
    return signals[:10]

def send_signals_auto():
    while True:
        coins = get_all_coins()
        signals = get_top_longs(coins)
        if signals:
            msg = "ТОП 10 ЛОНГ\n\n"
            for i, s in enumerate(signals, 1):
                msg += f"{i}. {s['symbol']} | ${s['price']:.6f} | +{s['change']:.2f}% | ${s['volume']:,.0f}\n"
            bot.send_message(CHAT_ID, msg)
        time.sleep(900)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен!")

@bot.message_handler(commands=['signal'])
def signal(message):
    coins = get_all_coins()
    signals = get_top_longs(coins)
    if signals:
        msg = "ТОП 10 ЛОНГ\n\n"
        for i, s in enumerate(signals, 1):
            msg += f"{i}. {s['symbol']} | ${s['price']:.6f} | +{s['change']:.2f}% | ${s['volume']:,.0f}\n"
        bot.reply_to(message, msg)

t = threading.Thread(target=send_signals_auto)
t.daemon = True
t.start()

bot.polling()
