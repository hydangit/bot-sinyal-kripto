import requests, time, telegram

BOT_TOKEN = "7578477675:AAE1EdzKHGtW8cIXhVNV1TTPQyEExQnbV-0"
CHAT_ID = "6682835719"

bot = telegram.Bot(token=BOT_TOKEN)

TIMEFRAME = "15m"
THRESHOLD = 0.0075  # = 0.75%

def get_symbols():
    data = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo").json()
    return [
        s["symbol"] for s in data["symbols"]
        if s["contractType"] == "PERPETUAL" and "USDT" in s["symbol"]
    ]

def get_candle(sym):
    d = requests.get(
        f"https://fapi.binance.com/fapi/v1/klines?symbol={sym}&interval={TIMEFRAME}&limit=2"
    ).json()
    return float(d[-2][1]), float(d[-2][4])  # open, close of previous candle

def send_signal(sym, direction, entry, tp, sl):
    msg = (
        f"📈 *{direction}* - `{sym}`\n"
        f"Entry: `{entry}`\n"
        f"TP: `{tp}`\n"
        f"SL: `{sl}`\n"
        f"TF: {TIMEFRAME}"
    )
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

def main():
    symbols = get_symbols()
    print(f"🔎 Scanning {len(symbols)} pairs...")
    while True:
        for sym in symbols:
            try:
                o, c = get_candle(sym)
                pct = (c - o) / o
                if abs(pct) >= THRESHOLD:
                    direction = "LONG" if pct > 0 else "SHORT"
                    entry = round(c, 4)
                    tp = round(c * (1.015 if pct > 0 else 0.985), 4)
                    sl = round(c * (0.99 if pct > 0 else 1.01), 4)
                    send_signal(sym, direction, entry, tp, sl)
                    print(f"Sent {direction} signal for {sym}")
                time.sleep(0.3)
            except Exception as e:
                print(f"Error on {sym}: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main()
