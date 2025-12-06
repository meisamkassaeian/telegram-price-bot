import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

DATA_FILE = "data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"dirham": 0, "products": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# تنظیم نرخ درهم
def set_dirham(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("استفاده: /setdirham 10.5")
        return
    try:
        rate = float(context.args[0])
        data = load_data()
        data["dirham"] = rate
        save_data(data)
        update.message.reply_text(f"نرخ درهم به روز شد: {rate}")
    except ValueError:
        update.message.reply_text("عدد معتبر وارد کنید.")

# ارسال پیام محصول با دکمه
def send_product(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        update.message.reply_text("استفاده: /send <ضریب> <متن پیام>")
        return
    try:
        factor = float(context.args[0])
        text = " ".join(context.args[1:])
        data = load_data()
        # پیام را در کانال ارسال می‌کنیم
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("💰 محاسبه قیمت", callback_data=str(factor))]]
        )
        context.bot.send_message(
            chat_id=context.bot_data.get("channel_id") or update.effective_chat.id,
            text=text,
            reply_markup=keyboard
        )
        # ذخیره ضریب در data.json
        data["products"][text] = factor
        save_data(data)
        update.message.reply_text("پیام ارسال شد ✅")
    except ValueError:
        update.message.reply_text("ضریب معتبر وارد کنید.")

# محاسبه قیمت وقتی دکمه زده شد
def calculate_price(update: Update, context: CallbackContext):
    query = update.callback_query
    factor = float(query.data)
    data = load_data()
    price = factor * data.get("dirham", 0)
    query.answer()
    query.edit_message_text(
        text=f"{query.message.text}\n\n💰 قیمت به روز: {price}"
    )
