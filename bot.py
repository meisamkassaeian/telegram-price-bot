import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.ext import CallbackContext

DATA_FILE = "data.json"
CHANNEL_ID = os.getenv("CHANNEL_ID")  # @username کانال یا chat_id کانال

def set_dirham(update: Update, context: CallbackContext):
    try:
        value = float(context.args[0])
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {"dirham": 0, "products": {}}
        data["dirham"] = value
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
        update.message.reply_text(f"قیمت درهم تنظیم شد: {value}")
    except (IndexError, ValueError):
        update.message.reply_text("لطفا عدد معتبر وارد کنید. مثال: /setdirham 3.5")

def add_product(update: Update, context: CallbackContext):
    try:
        name = context.args[0]
        coef = float(context.args[1])
        description = " ".join(context.args[2:]) if len(context.args) > 2 else ""

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("محاسبه قیمت", callback_data=name)
        ]])

        # ارسال پیام به کانال
        bot: Bot = context.bot
        bot.send_message(chat_id=CHANNEL_ID, text=f"{name}\n{description}", reply_markup=keyboard)

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {"dirham": 0, "products": {}}

        data["products"][name] = {"coef": coef}
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except (IndexError, ValueError):
        update.message.reply_text("مثال استفاده: /addproduct ساعت_طلایی 3.5 محصول_ویژه")

def calculate_price(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()  # پاسخ به کلیک بدون پیام جدید
    name = query.data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        dirham = data.get("dirham", 0)
        product = data["products"].get(name)
        if product:
            price = product["coef"] * dirham
            query.answer(f"قیمت {name}: {price:.2f}", show_alert=True)
        else:
            query.answer("محصول پیدا نشد.", show_alert=True)
