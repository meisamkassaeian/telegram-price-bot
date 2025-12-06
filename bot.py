import json
from telegram.ext import Updater, CommandHandler

DATA_FILE = "data.json"

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def set_derham(update, context):
    try:
        value = int(context.args[0])
        data = load_data()
        data["derham"] = value
        save_data(data)
        update.message.reply_text(f"قیمت درهم روی {value} ذخیره شد.")
    except:
        update.message.reply_text("دستور صحیح:
/setderham 15200")

def set_product(update, context):
    try:
        name = context.args[0].lower()
        factor = float(context.args[1])
        data = load_data()
        data["products"][name] = factor
        save_data(data)
        update.message.reply_text(f"محصول {name} با ضریب {factor} ذخیره شد.")
    except:
        update.message.reply_text("نمونه دستور:
/setproduct laptop 3.7")

def calc(update, context):
    if context.args:
        product_name = context.args[0].lower()
    else:
        update.message.reply_text("محصول مشخص نیست.")
        return

    data = load_data()
    derham = data["derham"]

    if product_name not in data["products"]:
        update.message.reply_text("محصول یافت نشد.")
        return

    factor = data["products"][product_name]
    price_rial = int(derham * factor * 1000)

    update.message.reply_text(
        f"🔹 محصول: {product_name}\n"
        f"💵 قیمت درهم: {derham:,}\n"
        f"📦 ضریب محصول: {factor}\n\n"
        f"💰 قیمت نهایی: {price_rial:,} ریال\n"
        f"({price_rial//10:,} تومان)"
    )

def start(update, context):
    update.message.reply_text("سلام! ربات فعال است.")

def main():
    updater = Updater("8285442997:AAGb2BO0PVlZN5CFqhCRrywIKr3rKzcUe3M")
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setderham", set_derham))
    dp.add_handler(CommandHandler("setproduct", set_product))
    dp.add_handler(CommandHandler("calc", calc))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
