import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from bot import set_dirham, add_product, calculate_price

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(TOKEN)
app = Flask(__name__)

# Dispatcher
dp = Dispatcher(bot, None, workers=0)
dp.add_handler(CommandHandler("setdirham", set_dirham))
dp.add_handler(CommandHandler("addproduct", add_product))
dp.add_handler(CallbackQueryHandler(calculate_price))

@app.route("/")
def home():
    return "Bot is running."

@app.route("/webhook", methods=["POST"])
def webhook():
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
