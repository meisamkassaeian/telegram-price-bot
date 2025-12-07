import os
import firebase_admin
from firebase_admin import credentials, db
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

# --- Firebase setup ---
cred_path = os.getenv("FIREBASE_KEY_PATH", "/etc/secrets/firebase_key.json")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv("FIREBASE_DB_URL")
})

# --- Admins ---
ADMINS = [123456789]  # اینجا آی‌دی ادمین‌ها را قرار بده

# --- Functions ---
def set_dirham(value: float):
    ref = db.reference("/dirham")
    ref.set(value)

def add_and_send_product(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        update.message.reply_text("❌ شما دسترسی ندارید.")
        return

    args = context.args
    if len(args) < 3:
        update.message.reply_text("❌ دستور اشتباه. فرمت:\n/addproduct نام_محصول ضریب توضیح")
        return

    name = args[0]
    try:
        coefficient = float(args[1])
    except ValueError:
        update.message.reply_text("❌ ضریب باید عدد باشد.")
        return

    description = " ".join(args[2:])

    # 1️⃣ ذخیره محصول در Firebase
    ref = db.reference("/products")
    ref.child(name).set({
        "coefficient": coefficient,
        "description": description
    })

    # 2️⃣ ارسال پست به کانال
    channel_id = os.getenv("CHANNEL_ID")
    keyboard = [[InlineKeyboardButton("💰 محاسبه قیمت", callback_data=name)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=channel_id,
        text=f"محصول جدید: {name}\n{description}\nبرای مشاهده قیمت روی دکمه زیر کلیک کنید.",
        reply_markup=reply_markup
    )
    update.message.reply_text("✅ محصول اضافه شد و پست ارسال شد.")

def calculate_price(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    product_name = query.data

    ref_product = db.reference(f"/products/{product_name}")
    product = ref_product.get()
    if not product:
        query.edit_message_text("❌ محصول یافت نشد.")
        return

    dirham_ref = db.reference("/dirham")
    dirham_price = dirham_ref.get()
    if dirham_price is None:
        query.edit_message_text("❌ قیمت درهم تنظیم نشده.")
        return

    price = product["coefficient"] * dirham_price
    # رند کردن به صدگان، دهگان، یکان
    price = int(round(price, -0))
    query.answer(f"💵 قیمت: {price} تومان", show_alert=True)
