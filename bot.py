import os
import json
import firebase_admin
from firebase_admin import credentials, db
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
ADMINS = [109597263]  # جایگزین با Telegram user ID ادمین‌ها
CHANNEL_ID = os.getenv("CHANNEL_ID")
DATA_FILE = "data.json"

# Firebase init
if not firebase_admin._apps:
    cred = credentials.Certificate("/etc/secrets/firebase_key.json")  # secret file
    firebase_admin.initialize_app(cred, {
        "databaseURL": os.getenv("FIREBASE_DB_URL")
    })

def set_dirham(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        update.message.reply_text("❌ شما دسترسی ندارید!")
        return

    args = context.args
    if len(args) != 1:
        update.message.reply_text("فرمت: /setdirham قیمت")
        return

    try:
        price = float(args[0])
    except ValueError:
        update.message.reply_text("قیمت باید عدد باشد")
        return

    # رند کردن قیمت به نزدیک‌ترین عدد صحیح
    rounded_price = int(round(price))

    # ذخیره در Firebase
    ref = db.reference("/dirham")
    ref.set(rounded_price)

    # نمایش قیمت با جداکننده هزارگان
    price_str = f"{rounded_price:,}"
    update.message.reply_text(f"✅ قیمت درهم به روز شد: {price_str} تومان")
def add_and_send_product(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        update.message.reply_text("❌ شما دسترسی ندارید!")
        return

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

    # ذخیره در Firebase
    ref = db.reference("/products")
    ref.update({name: {"coef": coef, "description": description}})

    # دکمه Inline
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 محاسبه قیمت بروز کالا", callback_data=name)]
    ])
    bot = context.bot
    bot.send_message(chat_id=CHANNEL_ID, text=description, reply_markup=keyboard)
    update.message.reply_text(f"محصول {name} با موفقیت به کانال فرستاده شد!")

def calculate_price(update: Update, context: CallbackContext):
    query = update.callback_query
    product_name = query.data

    dirham_ref = db.reference("/dirham")
    dirham_price = dirham_ref.get()
    if dirham_price is None:
        query.answer("قیمت درهم ثبت نشده", show_alert=True)
        return

    product_ref = db.reference(f"/products/{product_name}")
    product = product_ref.get()
    if not product:
        query.answer("محصول پیدا نشد", show_alert=True)
        return

    price = dirham_price * product["coef"]
    # رند کردن به نزدیک‌ترین صدگان
    rounded_price1 = int(round(price, -5))
    rounded_price = f"{rounded_price1:,}"       # خروجی: '123,000'
    query.answer(f"قیمت فعلی این کالا💰: {rounded_price} تومان", show_alert=True)
