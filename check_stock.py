import os
import requests

ZIP = "92618"  # Irvine
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "iphone-duo-irvine-change-me")

PARTS = {
    "MK1E4LL/A": "Star White 256GB",
    "MK1F4LL/A": "Night Sky 256GB",
    "MK1G4LL/A": "Star White 512GB",
    "MK1H4LL/A": "Night Sky 512GB",
    "MK1J4LL/A": "Star White 1TB",
    "MK1L4LL/A": "Night Sky 1TB",
    "MK1Q4LL/A": "Star White 2TB",
    "MK1R4LL/A": "Night Sky 2TB",
}

def check():
    params = {"pl": "true", "location": ZIP}
    for i, part in enumerate(PARTS.keys()):
        params[f"parts.{i}"] = part

    r = requests.get(
        "https://www.apple.com/shop/retail/pickup-message",
        params=params,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    r.raise_for_status()
    data = r.json()

    available = []
    for store in data.get("body", {}).get("stores", []):
        name = store.get("storeName", "Unknown store")
        for part, info in store.get("partsAvailability", {}).items():
            if info.get("pickupDisplay") == "available":
                available.append(
                    f"{name}: {PARTS.get(part, part)} — {info.get('storePickupQuote') or info.get('pickupSearchQuote') or 'available'}"
                )
    return available

if __name__ == "__main__":
    results = check()
    # Temporary test — remove after confirming it works
    requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data="Test notification from GitHub Actions".encode(), timeout=10)
    if results:
        msg = "iPhone Duo in stock near Irvine!\n\n" + "\n".join(results)
        print(msg)
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode(), timeout=10)
    else:
        print("No stock")