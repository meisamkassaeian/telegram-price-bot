import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# مسیر فایل ذخیره نرخ درهم
DIRHAM_FILE = "dirham.json"

def load_dirham():
    try:
        with open(DIRHAM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)["rate"]
    except:
        return 0

def set_dirham(rate):
    """تنظیم نرخ روزانه درهم"""
    with open(DIRHAM_FILE, "w", encoding="utf-8") as f:
        json.dump({"rate": rate}, f)

def calculate_price(update, context):
    """زمانی که کاربر دکمه را می‌زند"""
    query = update.callback_query
    query.answer()
    factor = float(query.data)  # داده‌ی ضریب محصول
    rate = load_dirham()
    price = factor * rate
    query.edit_message_text(
        f"💰 قیمت محصول: {price:,.2f} تومان"
    )

def send_product(bot, channel_id, name, factor, description):
    """ارسال محصول به کانال با دکمه محاسبه قیمت"""
    button = InlineKeyboardButton(
        text="💲 محاسبه قیمت",
        callback_data=str(factor)
    )
    markup = InlineKeyboardMarkup([[button]])
    
    message = f"🛒 *{name}*\n\n{description}"
    bot.send_message(
        chat_id=channel_id,
        text=message,
        reply_markup=markup,
        parse_mode="Markdown"
    )
