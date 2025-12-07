import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from bot import set_dirham, add_product, send_product, calculate_price

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # @username کانال یا chat_id
PORT = int(os.getenv("PORT", 5000))

bot = Bot(TOKEN)
dp = Dispatcher(bot, None, workers=0)

# --------------------- هندلرها ---------------------
dp.add_handler(CommandHandler("setdirham", set_dirham))
dp.add_handler(CommandHandler("addproduct", add_product))
dp.add_handler(CallbackQueryHandler(calculate_price))

# --------------------- وب سرور ---------------------
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
    url = f"{os.getenv('WEBHOOK_URL')}/webhook"
    bot.set_webhook(url)
    return f"Webhook set to {url}"

# --------------------- اجرای اپ ---------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
