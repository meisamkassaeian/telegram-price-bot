import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
import firebase_admin
from firebase_admin import credentials, db

# تنظیم Firebase
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")
cred = credentials.Certificate("/etc/secrets/firebase_key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": FIREBASE_DB_URL
    })

CHANNEL_ID = os.getenv("CHANNEL_ID")

def set_dirham(update: Update, context: CallbackContext):
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

    ref = db.reference("/")
    ref.update({"dirham": price})
    update.message.reply_text(f"قیمت درهم به روز شد: {price}")

def add_product(bot, name: str, coef: float, description: str):
    """افزودن محصول و ارسال پیام به کانال با دکمه Inline"""
    ref = db.reference(f"/products/{name}")
    ref.set({"coef": coef})

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(
        "محاسبه قیمت 💰", callback_data=name
    )]])
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

    ref = db.reference("/")
    data = ref.get() or {}

    dirham_price = data.get("dirham")
    if dirham_price is None:
        query.answer("قیمت درهم ثبت نشده", show_alert=True)
        return

    product = data.get("products", {}).get(product_name)
    if not product:
        query.answer("محصول پیدا نشد", show_alert=True)
        return

    price = dirham_price * product["coef"]
    # رند به نزدیک‌ترین صدگان و عدد صحیح
    rounded_price = int(round(price, -2))
    query.answer(f"قیمت فعلی این کالا: {rounded_price} هزار تومان", show_alert=True)
