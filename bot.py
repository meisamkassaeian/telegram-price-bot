import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

DATA_FILE = "data.json"


def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"derham": 10000, "products": {}}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# فرمان /setprice <price>
def set_price(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        update.message.reply_text("❗ قیمت درهم را وارد کنید. مثال:\n/setprice 15000")
        return

    price = int(context.args[0])
    data = load_data()
    data["derham"] = price
    save_data(data)

    update.message.reply_text(f"✔ قیمت درهم تنظیم شد: {price:,} ریال")


# وقتی کاربر روی دکمه محاسبه قیمت بزند
def calculate_price(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    product_id = query.data.split("_")[1]
    data = load_data()

    derham = data["derham"]
    product = data["products"].get(product_id)

    if not product:
        query.edit_message_text("❗ محصول یافت نشد.")
        return

    price = derham * product["rate"]

    query.edit_message_text(
        f"💻 {product['name']}\n"
        f"➖➖➖➖\n"
        f"💰 قیمت نهایی: {price:,} ریال"
    )


# ساخت پیام و دکمه برای کانال
def build_product_message(name, rate, product_id):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔢 محاسبه قیمت", callback_data=f"calc_{product_id}")]
    ])

    text = f"💻 *{name}*\n" \
           f"ضریب قیمت: {rate}"

    return text, keyboard
