print("### MAIN.PY LOADED ###")
import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from bot import set_dirham, add_and_send_product, calculate_price

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PORT = int(os.getenv("PORT", 5000))

bot = Bot(TOKEN)

# Dispatcher بدون workers برای webhook
dp = Dispatcher(bot, None, workers=0)
dp.add_handler(CommandHandler("setdirham", set_dirham))
dp.add_handler(CommandHandler("addproduct", add_and_send_product))
dp.add_handler(CallbackQueryHandler(calculate_price))

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    dp.process_update(update)
    return "OK", 200

@app.route("/setwebhook")
def set_webhook():
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    url = f"{WEBHOOK_URL}/webhook"
    bot.set_webhook(url)
    return f"Webhook set to {url}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

from flask import Flask
app = Flask(__name__)

@app.route("/debug")
def debug():
    return "DEBUG OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


