import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from bot import send_product, calculate_price, set_dirham

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # مثل https://telegram-price-bot-1-oepx.onrender.com

bot = Bot(TOKEN)
dp = Dispatcher(bot, None, workers=0)

# Command Handlers
dp.add_handler(CommandHandler("setdirham", set_dirham))
dp.add_handler(CommandHandler("sendproduct", send_product))
dp.add_handler(CallbackQueryHandler(calculate_price))

app = Flask(__name__)

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
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
