import os
import requests
import firebase_admin
from firebase_admin import credentials, db

# --- Firebase init (فقط یکبار) ---
if not firebase_admin._apps:
    cred = credentials.Certificate("/etc/secrets/firebase_key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": os.getenv("FIREBASE_DB_URL")
    })

WC_URL = os.getenv("WC_URL")
WC_KEY = os.getenv("WC_CONSUMER_KEY")
WC_SECRET = os.getenv("WC_CONSUMER_SECRET")


def update_prices():
    """
    قیمت محصولات ووکامرس را بر اساس Firebase آپدیت می‌کند
    """
    ref = db.reference("/")
    data = ref.get()

    dirham = data.get("dirham")
    products = data.get("products", {})

    if not dirham:
        raise Exception("Dirham price not found")

    updated = 0

    for name, p in products.items():
        sku = p.get("sku")
        coef = p.get("coef")

        if not sku or not coef:
            continue

        final_price = int(round(dirham * coef, -2))

        # --- WooCommerce API ---
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/products",
            auth=(WC_KEY, WC_SECRET),
            params={"sku": sku}
        )

        if r.status_code != 200 or not r.json():
            continue

        product_id = r.json()[0]["id"]

        requests.put(
            f"{WC_URL}/wp-json/wc/v3/products/{product_id}",
            auth=(WC_KEY, WC_SECRET),
            json={"regular_price": str(final_price)}
        )

        updated += 1

    return {
        "updated": updated
    }
