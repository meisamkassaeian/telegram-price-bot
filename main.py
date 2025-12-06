import os
from flask import Flask, request
from telegram.ext import Dispatcher, CallbackQueryHandler
from telegram import Bot
from bot import calculate_price, send_product, set_dirham

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(TOKEN)
app = Flask(__name__)

# Dispatcher
dp = Dispatcher(bot, None, workers=0)
dp.add_handler(CallbackQueryHandler(calculate_price))

@app.route("/")
def home():
    return "Bot is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    from telegram import Update
    import json

    data = json.loads(request.data)
    update = Update.de_json(data, bot)
    dp.process_update(update)
    return "OK", 200

@app.route("/setwebhook")
def set_webhook():
    url = f"{WEBHOOK_URL}/webhook"
    bot.set_webhook(url)
    return f"Webhook set to {url}"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
