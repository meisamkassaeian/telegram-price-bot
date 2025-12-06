import os
from flask import Flask, request
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from bot import set_price, calculate_price, send_product, set_dirham

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # مثلا @mychannel

bot = Bot(TOKEN)
app = Flask(__name__)

dp = Dispatcher(bot, None, workers=0)

# هندلرها
dp.add_handler(CommandHandler("send", send_product))         # ارسال پیام تست
dp.add_handler(CommandHandler("setdirham", set_dirham))      # تنظیم نرخ درهم
dp.add_handler(CallbackQueryHandler(calculate_price))        # دکمه محاسبه قیمت

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
