import os
from flask import Flask, request
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from telegram import Bot
from bot import calculate_price, add_product, set_dirham

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(TOKEN)
app = Flask(__name__)

# Dispatcher
dp = Dispatcher(bot, None, workers=0)
dp.add_handler(CommandHandler("addproduct", add_product))
dp.add_handler(CallbackQueryHandler(calculate_price))
dp.add_handler(CommandHandler("setdirham", set_dirham))  # برای بروزرسانی قیمت درهم

@app.route("/")
def home():
    return "Bot is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    from telegram import Update
    update = Update.de_json(request.get_json(force=True), bot)
    dp.process_update(update)
    return "OK", 200

@app.route("/setwebhook")
def set_webhook():
    url = f"{WEBHOOK_URL}/webhook"
    bot.set_webhook(url)
    return f"Webhook set to {url}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
