import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

CHANNEL_ID = os.getenv("CHANNEL_ID")
DATE_FILE = "date.json"

# مقدار درهم روزانه
def set_dirham(value):
    data = {"dirham": value}
    with open(DATE_FILE, "w") as f:
        json.dump(data, f)

def get_dirham():
    try:
        with open(DATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("dirham", 1)
    except:
        return 1

# دکمه محاسبه قیمت
def calculate_price(update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    product_value = float(query.data)
    dirham = get_dirham()
    price = product_value * dirham
    query.edit_message_text(f"قیمت به روز: {price} درهم")

# ارسال پست به کانال با دکمه محاسبه قیمت
def send_product(bot, title, product_value):
    keyboard = [[InlineKeyboardButton("محاسبه قیمت", callback_data=str(product_value))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=CHANNEL_ID, text=title, reply_markup=reply_markup)
