import os
import firebase_admin
from firebase_admin import credentials, db
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

# مقداردهی Firebase
cred = credentials.Certificate("/etc/secrets/firebase_key.json")  # مسیر Secret File
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv("FIREBASE_URL")  # https://telegram-bot-pric-default-rtdb.firebaseio.com/
})

# لیست ادمین‌ها
ADMINS = [109597263]  # آی‌دی تلگرام ادمین‌ها را قرار بده

def set_dirham(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        update.message.reply_text("❌ اجازه ندارید.")
        return
    try:
        price = float(context.args[0])
        db.reference("dirham").set(price)
        update.message.reply_text(f"✅ قیمت درهم به {price} تنظیم شد.")
    except (IndexError, ValueError):
        update.message.reply_text("❌ فرمت اشتباه است. /setdirham 10.5")


def add_product(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        update.message.reply_text("❌ اجازه ندارید.")
        return
    try:
        name = context.args[0]
        factor = float(context.args[1])
        description = " ".join(context.args[2:]) if len(context.args) > 2 else ""
        product_ref = db.reference(f"products/{name}")
        product_ref.set({
            "factor": factor,
            "description": description
        })
        update.message.reply_text(f"✅ محصول {name} اضافه شد.")
    except (IndexError, ValueError):
        update.message.reply_text("❌ فرمت اشتباه است. /addproduct نام محصول ضریب توضیح")


def calculate_price(update: Update, context: CallbackContext):
    query = update.callback_query
    product_name = query.data  # فرض می‌کنیم data همان نام محصول است
    product_ref = db.reference(f"products/{product_name}")
    product = product_ref.get()
    if not product:
        query.answer("❌ قیمت پیدا نشد", show_alert=True)
        return
    dirham_price = db.reference("dirham").get()
    if dirham_price is None:
        query.answer("❌ قیمت درهم تنظیم نشده", show_alert=True)
        return
    price = int(product["factor"] * dirham_price)
    # رند کردن به عدد صحیح و حذف ممیز
    query.answer(f"💰 قیمت این کالا: {price} هزار تومان", show_alert=True)
