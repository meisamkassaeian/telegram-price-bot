import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

DATA_FILE = "data.json"

# بارگذاری قیمت درهم
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"dirham": 1}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# بروزرسانی قیمت درهم
def set_dirham(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("لطفاً یک عدد برای قیمت درهم وارد کنید.")
        return
    try:
        value = float(context.args[0])
    except ValueError:
        update.message.reply_text("مقدار معتبر نیست.")
        return
    data = load_data()
    data["dirham"] = value
    save_data(data)
    update.message.reply_text(f"قیمت درهم به {value} بروزرسانی شد.")

# تابع ارسال محصول به کانال
def send_product(bot, channel_id, name, coef, desc):
    data = load_data()
    dirham_price = data.get(_
