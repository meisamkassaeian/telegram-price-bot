import os
import requests
import firebase_admin
from firebase_admin import credentials, db

# ---------- Firebase ----------
cred = credentials.Certificate("/etc/secrets/firebase_key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv("FIREBASE_DB_URL")
})

# ---------- WooCommerce ----------
WC_URL = os.getenv("WC_URL")
CK = os.getenv("WC_CONSUMER_KEY")
CS = os.getenv("WC_CONSUMER_SECRET")

# ---------- 1. خواندن قیمت درهم ----------
dirham = db.reference("/dirham").get()
if not dirham:
    raise Exception("❌ قیمت درهم پیدا نشد")

# ---------- 2. پیدا کردن محصول دارای SKU ----------
products = db.reference("/products").get()
target = None

for name, data in products.items():
    if data.get("sku") == "DL5510":
        target = data
        break

if not target:
    raise Exception("❌ محصول با SKU DL5510 پیدا نشد")

coef = target.get("coef")

# ---------- 3. محاسبه قیمت ----------
price = int(round(dirham * coef, -2))  # رند به صدگان

print("قیمت نهایی:", price)

# ---------- 4. پیدا کردن محصول در ووکامرس ----------
res = requests.get(
    f"{WC_URL}/wp-json/wc/v3/products",
    auth=(CK, CS),
    params={"sku": "DL5510"}
)

items = res.json()
if not items:
    raise Exception("❌ محصول در ووکامرس پیدا نشد")

product_id = items[0]["id"]

# ---------- 5. آپدیت قیمت ----------
update = requests.put(
    f"{WC_URL}/wp-json/wc/v3/products/{product_id}",
    auth=(CK, CS),
    json={
        "regular_price": str(price)
    }
)

if update.status_code == 200:
    print("✅ قیمت با موفقیت آپدیت شد")
else:
    print("❌ خطا در آپدیت:", update.text)
