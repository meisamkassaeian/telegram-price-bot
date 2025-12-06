import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

DATA_FILE = "data.json"

# ذخیره یا خواندن نرخ درهم
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ست کردن نرخ درهم
def set_dirham(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("استفاده صحیح: /setdirham <قیمت درهم>")
        return
    try:
        price = float(context.args[0])
    except ValueError:
        update.message.reply_text("قیمت باید عدد باشد.")
        return
    data = load_data()
    data["dirham"] = price
    save_data(data)
    update.message.reply_text(f"نرخ درهم روی {price} تنظیم شد.")

# ارسال محصول به کانال با دکمه محاسبه قیمت
def send_product(update: Update, context: CallbackContext):
    if len(context.args) < 3:
        update.message.reply_text("استفاده صحیح: /sendproduct <عنوان> <ضریب> <توضیح>")
        return
    try:
        title = context.args[0]
        rate = float(context.args[1])
        description = " ".join(context.args[2:])
    except ValueError:
        update.message.reply_text("ضریب باید عدد باشد.")
        return

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("💰 محاسبه قیمت", callback_data=f"price:{rate}")]]
    )

    channel_id = os.getenv("CHANNEL_ID")
    update.message.bot.send_message(
        chat_id=channel_id,
        text=f"{title}\n{description}",
        reply_markup=keyboard
    )
    update.message.reply_text("محصول ارسال شد ✅")

# محاسبه قیمت هنگام کلیک روی دکمه
def calculate_price(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = load_data()
    dirham = data.get("dirham")
    if not dirham:
        query.edit_message_text("ابتدا نرخ درهم را با /setdirham تعیین کنید.")
        return
    try:
        rate = float(query.data.split(":")[1])
    except:
        query.edit_message_text("خطا در ضریب محصول.")
        return
    price = dirham * rate
    query.answer(f"قیمت: {price} تومان", show_alert=True)
