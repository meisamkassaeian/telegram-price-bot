import os
from flask import Flask, request
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from telegram import Bot
from bot import set_price, calculate_price

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # مثل https://mybot.onrender.com/webhook

bot = Bot(TOKEN)

app = Flask(__name__)

# Dispatcher
from telegram.ext import Dispatcher
dp = Dispatcher(bot, None, workers=0)
dp.add_handler(CommandHandler("setprice", set_price))
dp.add_handler(CallbackQueryHandler(calculate_price))


@app.route("/")
def home():
    return "Bot is running."


@app.route("/webhook", methods=["POST"])
def webhook():
    update = bot.update_queue.from_json(request.data.decode("utf-8"))
    dp.process_update(update)
    return "OK", 200


# تنظیم وبهوک
@app.route("/setwebhook")
def set_webhook():
    url = f"{WEBHOOK_URL}/webhook"
    bot.set_webhook(url)
    return f"Webhook set to {url}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
