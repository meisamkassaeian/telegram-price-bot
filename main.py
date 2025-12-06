import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
from bot import send_product, calculate_price, set_dirham

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PORT = int(os.getenv("PORT", 5000))

bot = Bot(TOKEN)
app = Flask(__name__)

dp = Dispatcher(bot, None, workers=0)
dp.add_handler(CallbackQueryHandler(calculate_price))

# دستور برای ارسال محصول
def add_product(update, context):
    try:
        args = context.args
        if len(args) < 3:
            update.message.reply_text("❌ فرمت دستور: /addproduct نام ضریب توضیح")
            return

        name = args[0]
        factor = float(args[1])
        description = " ".join(args[2:])
        
        send_product(context.bot, CHANNEL_ID, name, factor, description)
        update.message.reply_text(f"✅ محصول '{name}' ارسال شد.")
    except Exception as e:
        update.message.reply_text(f"❌ خطا: {e}")

dp.add_handler(CommandHandler("addproduct", add_product))

# دستور برای تنظیم نرخ درهم
def update_dirham(update, context):
    try:
        rate = float(context.args[0])
        set_dirham(rate)
        update.message.reply_text(f"✅ نرخ درهم روی {rate} تنظیم شد.")
    except Exception as e:
        update.message.reply_text(f"❌ خطا: {e}")

dp.add_handler(CommandHandler("setdirham", update_dirham))

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
    app.run(host="0.0.0.0", port=PORT)
