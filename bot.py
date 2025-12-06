import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

DATA_FILE = "data.json"

# ذخیره و خواندن داده‌ها
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# تعیین نرخ درهم
def set_dirham(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("لطفا مقدار درهم را وارد کنید. مثال: /setdirham 12000")
        return
    try:
        price = float(context.args[0])
        data = load_data()
        data["dirham"] = price
        save_data(data)
        update.message.reply_text(f"نرخ درهم به {price} تومان تنظیم شد.")
    except ValueError:
        update.message.reply_text("لطفا عدد معتبر وارد کنید.")

# افزودن محصول
def add_product(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        update.message.reply_text("لطفا نام محصول و ضریب را وارد کنید. مثال: /sendproduct ساعت_طلایی 3.5")
        return
    try:
        name = context.args[0]
        coefficient = float(context.args[1])
        description = " ".join(context.args[2:]) if len(context.args) > 2 else ""
        data = load_data()
        if "products" not in data:
            data["products"] = {}
        data["products"][name] = {"coefficient": coefficient, "description": description}
        save_data(data)

        keyboard = [
            [InlineKeyboardButton("💰 محاسبه قیمت", callback_data=name)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f"{name}\n{description}", reply_markup=reply_markup)
    except ValueError:
        update.message.reply_text("ضریب باید عدد باشد.")

# محاسبه قیمت هنگام کلیک روی دکمه
def calculate_price(update: Update, context: CallbackContext):
    query = update.callback_query
    if not query:
        return
    product_name = query.data
    data = load_data()
    dirham = data.get("dirham")
    if not dirham:
        query.answer("نرخ درهم تنظیم نشده!", show_alert=True)
        return
    product = data.get("products", {}).get(product_name)
    if not product:
        query.answer("محصول یافت نشد!", show_alert=True)
        return

    price = product["coefficient"] * dirham
    query.answer(text=f"قیمت {product_name}: {price:,} تومان", show_alert=True)
