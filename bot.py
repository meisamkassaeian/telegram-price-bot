import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

DATA_FILE = "data.json"

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"dirham": 1, "products": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def set_dirham(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("لطفاً قیمت درهم را وارد کنید.")
        return
    try:
        dirham_price = float(context.args[0])
        data = load_data()
        data["dirham"] = dirham_price
        save_data(data)
        update.message.reply_text(f"✅ قیمت درهم به {dirham_price} تغییر کرد.")
    except ValueError:
        update.message.reply_text("❌ مقدار نامعتبر است، لطفاً عدد وارد کنید.")

def send_product(update: Update, context: CallbackContext):
    if len(context.args) < 3:
        update.message.reply_text("❌ دستور اشتباه است. فرمت: /sendproduct نام_محصول ضریب توضیح")
        return
    try:
        name = context.args[0]
        coef = float(context.args[1])
        description = " ".join(context.args[2:])
    except ValueError:
        update.message.reply_text("❌ ضریب باید عدد باشد.")
        return

    data = load_data()
    products = data.get("products", [])
    product = {"name": name, "coef": coef, "description": description}
    products.append(product)
    data["products"] = products
    save_data(data)

    # ایجاد دکمه inline برای محاسبه قیمت
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 محاسبه قیمت", callback_data=json.dumps({"coef": coef}))]
    ])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📦 محصول: {name}\n{description}",
        reply_markup=keyboard
    )

def calculate_price(update: Update, context: CallbackContext):
    query = update.callback_query
    if not query:
        return
    data = json.loads(query.data)
    coef = data.get("coef", 1)
    dirham = load_data().get("dirham", 1)
    price = coef * dirham
    query.answer(text=f"💵 قیمت امروز: {price:.2f} تومان", show_alert=True)
