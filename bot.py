import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.update import Update

DATA_FILE = "data.json"
CHANNEL_ID = os.getenv("CHANNEL_ID")  # مثلا @yourchannelusername

# تنظیم قیمت درهم
def set_dirham(update: Update, context: CallbackContext):
    try:
        rate = float(context.args[0])
        with open(DATA_FILE, "w") as f:
            json.dump({"dirham": rate}, f)
        update.message.reply_text(f"قیمت درهم روی {rate} تنظیم شد ✅")
    except Exception as e:
        update.message.reply_text(f"خطا: {e}")

# ارسال محصول به کانال با دکمه
def add_product(update: Update, context: CallbackContext):
    try:
        text = update.message.text.split(" ", 3)  # /sendproduct نام محصول ضریب توضیح
        if len(text) < 4:
            update.message.reply_text("فرمت صحیح: /sendproduct نام ضریب توضیح")
            return

        _, name, factor, description = text
        factor = float(factor)

        keyboard = [[InlineKeyboardButton("محاسبه قیمت", callback_data=factor)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"محصول: {name}\nتوضیح: {description}\nضریب: {factor}",
            reply_markup=reply_markup
        )

        update.message.reply_text("محصول با موفقیت به کانال ارسال شد ✅")
    except Exception as e:
        update.message.reply_text(f"خطا: {e}")

# محاسبه قیمت هنگام زدن دکمه
def calculate_price(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        dirham_price = data.get("dirham", 0)
        factor = float(query.data)
        total_price = dirham_price * factor
        query.message.reply_text(f"قیمت به روز: {total_price}")
    except Exception as e:
        query.message.reply_text(f"خطا در محاسبه قیمت: {e}")
