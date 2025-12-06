import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

DATA_FILE = "data.json"

# ذخیره ضریب درهم
def set_dirham(update: Update, context: CallbackContext):
    try:
        value = float(context.args[0])
        data = {"dirham": value, "products": {}}
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                old_data = json.load(f)
            old_data["dirham"] = value
            data = old_data
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
        update.message.reply_text(f"قیمت درهم تنظیم شد: {value}")
    except (IndexError, ValueError):
        update.message.reply_text("لطفا عدد معتبر وارد کنید. مثال: /setdirham 3.5")

# اضافه کردن محصول
def add_product(update: Update, context: CallbackContext):
    try:
        name = context.args[0]
        coef = float(context.args[1])
        description = " ".join(context.args[2:]) if len(context.args) > 2 else ""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {"dirham": 0, "products": {}}

        message = f"{name}\n{description}"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("محاسبه قیمت", callback_data=name)
        ]])

        sent_message = update.message.reply_text(message, reply_markup=keyboard)

        data["products"][name] = {"coef": coef}
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except (IndexError, ValueError):
        update.message.reply_text(
            "مثال استفاده: /addproduct ساعت_طلایی 3.5 محصول_ویژه"
        )

# محاسبه قیمت و نمایش popup
def calculate_price(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()  # جواب دادن به کلیک بدون ارسال پیام جدید
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
