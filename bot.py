import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

DATA_FILE = "data.json"
CHANNEL_ID = os.getenv("CHANNEL_ID")

def set_dirham_command(update: Update, context: CallbackContext):
    """دستور تلگرامی: /setdirham قیمت"""
    args = context.args
    if len(args) != 1:
        update.message.reply_text("فرمت: /setdirham قیمت")
        return
    try:
        price = float(args[0])
    except ValueError:
        update.message.reply_text("قیمت باید عدد باشد")
        return

    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    data["dirham"] = price
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)
    update.message.reply_text(f"قیمت درهم به روز شد: {price}")

def add_product(bot, name: str, coef: float, description: str):
    """افزودن محصول و ارسال پیام به کانال با دکمه Inline"""
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    if "products" not in data:
        data["products"] = {}
    data["products"][name] = {"coef": coef}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(f"محاسبه قیمت این کالا💰", callback_data=name)
    ]])
    bot.send_message(chat_id=CHANNEL_ID, text=description, reply_markup=keyboard)

def add_product_command(update: Update, context: CallbackContext):
    """دستور تلگرامی: /addproduct نام ضریب توضیح"""
    args = context.args
    if len(args) < 3:
        update.message.reply_text("فرمت: /addproduct نام ضریب توضیح")
        return
    name = args[0]
    try:
        coef = float(args[1])
    except ValueError:
        update.message.reply_text("ضریب باید عدد باشد")
        return
    description = " ".join(args[2:])
    add_product(context.bot, name, coef, description)
    update.message.reply_text(f"محصول {name} به کانال فرستاده شد!")

def calculate_price(update: Update, context: CallbackContext):
    """زمانی که کاربر روی دکمه کلیک می‌کند"""
    query = update.callback_query
    product_name = query.data

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        query.answer("قیمتی ثبت نشده", show_alert=True)
        return

    dirham_price = data.get("dirham")
    if dirham_price is None:
        query.answer("قیمت درهم ثبت نشده", show_alert=True)
        return

    product = data.get("products", {}).get(product_name)
    if not product:
        query.answer("محصول پیدا نشد", show_alert=True)
        return

    price = dirham_price * product["coef"]
    rounded_price = int(round(price, -2))  # رند به نزدیک‌ترین صدگان و عدد صحیح
    query.answer(f"قیمت فعلی این کالا💰: {rounded_price} هزار تومان", show_alert=True)
