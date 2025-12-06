import os
from flask import Flask, request
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from bot import send_product, calculate_price, set_dirham

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(TOKEN)
app = Flask(__name__)

dp = Dispatcher(bot, None, workers=0)

# Handlers
dp.add_handler(CommandHandler("setdirham", set_dirham))
dp.add_handler(CallbackQueryHandler(calculate_price))

@app.route("/")
def home():
    return "Bot is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    update = bot.update_queue.from_json(request.data.decode("utf-8"))
    dp.process_update(update)
    return "OK", 200

@app.route("/setwebhook")
def set_webhook():
    url = f"{WEBHOOK_URL}/webhook"
    bot.set_webhook(url)
    return f"Webhook set to {url}"

@app.route("/sendproduct/<name>/<float:coef>/<desc>")
def test_send_product(name, coef, desc):
    send_product(bot, CHANNEL_ID, name, coef, desc)
    return "Product sent!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
