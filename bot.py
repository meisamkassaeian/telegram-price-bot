import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

DATA_FILE = "data.json"

# Load / Save data
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Set Dirham price
def set_dirham(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("لطفاً قیمت درهم را وارد کنید: /setdirham 1.23")
        return
    try:
        price = float(context.args[0])
        data = load_data()
        data["dirham"] = price
        save_data(data)
        update.message.reply_text(f"قیمت درهم به {price} به روز شد.")
    except ValueError:
        update.message.reply_text("قیمت معتبر نیست!")

# Send product to channel
def send_product(bot, channel_id, name, coef, desc):
    keyboard = [
        [InlineKeyboardButton("محاسبه قیمت", callback_data=f"{coef}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        chat_id=channel_id,
        text=f"محصول: {name}\nتوضیحات: {desc}",
        reply_markup=reply_markup
    )

# Callback for calculating price
def calculate_price(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()  # acknowledge callback

    try:
        coef = float(query.data)
    except ValueError:
        query.answer(text="خطا در محاسبه قیمت", show_alert=True)
        return

    data = load_data()
    dirham = data.get("dirham")
    if not dirham:
        query.answer(text="قیمت درهم هنوز تعیین نشده است", show_alert=True)
        return

    price = coef * dirham
    query.answer(text=f"قیمت امروز: {price:.2f}", show_alert=True)
