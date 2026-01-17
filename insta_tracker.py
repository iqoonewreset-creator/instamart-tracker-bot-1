from playwright.sync_api import sync_playwright
import time
import requests
import re

# ========= TELEGRAM =========
BOT_TOKEN = "8558476155:AAEgDA0tPNBkj3M8ztCHtpwMEm6ICD85Epk"
CHAT_ID = "1377959451"

# ========= SETTINGS =========
CART_URL = "https://www.swiggy.com/instamart/cart"
TARGET_PRICE = 60
CHECK_INTERVAL = 300  # 5 minutes

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def extract_price(text):
    match = re.search(r"₹\s*(\d+(?:\.\d+)?)", text)
    if match:
        return int(float(match.group(1)))
    return None

with sync_playwright() as p:
    # 🔹 CLOUD-READY: headless = True
    context = p.chromium.launch_persistent_context(
        user_data_dir="swiggy_profile",
        headless=True
    )

    page = context.new_page()
    print("➡️ CREATED BY @SPIDERYASHU (Cloud Mode)")

    while True:
        try:
            page.goto(CART_URL, timeout=60000)
            page.wait_for_timeout(8000)

            texts = page.locator("text=/₹/").all_inner_texts()

            prices = []
            for t in texts:
                val = extract_price(t)
                if val is not None:
                    prices.append(val)

            mrp = None
            item_price = None

            # 🔹 Reliable cart price rule
            for i in range(len(prices) - 1):
                if prices[i] > prices[i + 1] and prices[i] <= 200:
                    mrp = prices[i]
                    item_price = prices[i + 1]
                    break

            if item_price:
                print(f"✅ MRP: ₹{mrp} | PRICE: ₹{item_price}")

                if item_price <= TARGET_PRICE:
                    send_telegram(
                        f"🚨 Instamart Price Alert\n"
                        f"CREATED BY @SPIDERYASHU\n\n"
                        f"Item price: ₹{item_price}\n"
                        f"MRP: ₹{mrp}\n"
                        f"Target: ₹{TARGET_PRICE}"
                    )

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print("⚠️ Error:", e)
            time.sleep(CHECK_INTERVAL)
