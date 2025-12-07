import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

DATA_FILE = "data.json"

# --------------------- فایل JSON ---------------------
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"dirham_price": 0, "products": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --------------------- بررسی ادمین ---------------------
ADMINS = [meisamkassaeian]  # تو این لیست آی‌دی ادمین‌ها بذار

def is_admin(update: Update):
    user_id = update.effective_user.id
    return user_id in ADMINS

# --------------------- تنظیم قیمت درهم ---------------------
def set_dirham(update: Update, context: CallbackContext):
    if not is_admin(update):
        update.message.reply_text("❌ شما اجازه ندارید.")
        return

    try:
        price = float(context.args[0])
    except:
        update.message.reply_text("❌ قیمت معتبر نیست.")
        return

    data = load_data()
    data["dirham_price"] = price
    save_data(data)

    update.message.reply_text(f"✅ قیمت درهم به {price} تغییر کرد.")

# --------------------- اضافه کردن محصول ---------------------
def add_product(update: Update, context: CallbackContext):
    if not is_admin(update):
        update.message.reply_text("❌ شما اجازه ندارید.")
        return

    try:
        name = context.args[0]
        coef = float(context.args[1])
    except:
        update.message.reply_text("❌ فرمت صحیح: /addproduct نام_محصول ضریب")
        return

    data = load_data()
    data["products"][name] = coef
    save_data(data)

    update.message.reply_text(f"✅ محصول {name} با ضریب {coef} اضافه شد.")

# --------------------- ارسال محصول به کانال ---------------------
def send_product(bot, channel_id, name: str, description=""):
    data = load_data()
    if name not in data["products"]:
        return False

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("💰 محاسبه آنلاین قیمت", callback_data=name)]]
    )
    bot.send_message(chat_id=channel_id, text=f"{name}\n{description}", reply_markup=keyboard)
    return True

# --------------------- محاسبه قیمت ---------------------
def calculate_price(update: Update, context: CallbackContext):
    query = update.callback_query
    product = query.data

    data = load_data()
    if product not in data["products"]:
        query.answer("❌ قیمت پیدا نشد", show_alert=True)
        return

    price = round(data["dirham_price"] * data["products"][product])
    query.answer(f"💰 قیمت: {price} هزار تومان", show_alert=True)
