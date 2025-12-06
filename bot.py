import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

DATA_FILE = "data.json"

# ثبت قیمت درهم روزانه
def set_dirham(update: Update, context: CallbackContext):
    try:
        value = float(context.args[0])
        data = {"dirham": value}
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
        update.message.reply_text(f"قیمت درهم روی {value} تنظیم شد.")
    except (IndexError, ValueError):
        update.message.reply_text("لطفا عدد صحیح وارد کنید: /setdirham 10.5")

# ارسال پست با ضریب محصول
def send_product(bot, chat_id, title, coefficient):
    keyboard = [
        [InlineKeyboardButton("محاسبه قیمت", callback_data=f"price_{coefficient}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=chat_id, text=title, reply_markup=reply_markup)

# محاسبه قیمت و پاسخ به کاربر
def calculate_price(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    try:
        data = query.data
        coefficient = float(data.split("_")[1])
        with open(DATA_FILE, "r") as f:
            dirham_data = json.load(f)
        dirham = dirham_data.get("dirham", 0)
        price = coefficient * dirham
        query.edit_message_text(f"قیمت روز محصول: {price}")
    except Exception as e:
        query.edit_message_text(f"خطا در محاسبه قیمت: {e}")
