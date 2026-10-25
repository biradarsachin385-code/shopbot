import os
import re

# Uses your real database when DB_HOST is set, otherwise the sample data
if os.environ.get("DB_HOST"):
    from db_mysql import init_db, search_products, all_products, get_order
else:
    from db import init_db, search_products, all_products, get_order

KEYWORDS = {
    "human":    ["human", "agent", "support", "complaint", "call"],
    "returns":  ["return", "refund", "exchange", "replace", "cancel"],
    "shipping": ["shipping", "delivery", "deliver"],
    "payment":  ["payment", "upi", "cod", "cash on delivery", "card", "pay"],
    "offers":   ["offer", "discount", "coupon", "sale", "deal"],
    "size":     ["size", "fit"],
    "warranty": ["warranty", "guarantee"],
    "catalog":  ["catalog", "catalogue", "all products", "products",
                 "items", "what do you sell", "what do you have"],
    "greeting": ["hi", "hello", "hey", "hii", "namaste"],
    "thanks":   ["thank"],
    "bye":      ["bye", "goodbye"],
}

RESPONSES = {
    "human": "Sure! Our support team will help you. Please use the Help or Contact option in the app.",
    "returns": "Returns are accepted within 7 days of delivery, and refunds take 5-7 working days. To cancel an order, type 'agent' and our team will help.",
    "shipping": "Delivery takes 3-5 business days. Free shipping above ₹999.",
    "payment": "We accept UPI, cards, net banking and Cash on Delivery.",
    "offers": "Check the Offers section in the app for current deals and coupons.",
    "size": "Size details are on each product page. Type 'agent' if you need help choosing.",
    "warranty": "Warranty depends on the product. Please check the product page for details.",
    "greeting": "Hi! 👋 I can help with products, order tracking, shipping, returns and payments.",
    "thanks": "You're welcome! 😊 Anything else?",
    "bye": "Bye! 👋 Happy shopping!",
}

def has(text, words):
    return any(re.search(rf"\b{re.escape(w)}(s|es|ing)?\b", text) for w in words)

def price_range(text):
    """Reads budgets like 'under 2000' or 'above 500'."""
    low = high = None
    m = re.search(r"(?:under|below|less than|upto|up to)\s*(?:rs\.?|₹)?\s*(\d+)", text)
    if m:
        high = int(m.group(1))
    m = re.search(r"(?:above|over|more than)\s*(?:rs\.?|₹)?\s*(\d+)", text)
    if m:
        low = int(m.group(1))
    return low, high

def format_products(items):
    lines = []
    for p in items:
        stock = "In stock" if p["stock"] > 0 else "Out of stock"
        lines.append(f"• {p['name']} - ₹{p['price']:.0f} ({stock})")
    return "\n".join(lines)

def reply(message):
    text = message.lower().strip()

    if has(text, KEYWORDS["human"]):
        return RESPONSES["human"]
    if has(text, KEYWORDS["returns"]):
        return RESPONSES["returns"]

    # products + budget
    low, high = price_range(text)
    price_query = low is not None or high is not None
    items = search_products(text)
    if price_query and not items:
        items = all_products()
    if low is not None:
        items = [p for p in items if p["price"] >= low]
    if high is not None:
        items = [p for p in items if p["price"] <= high]

    if price_query and not items:
        return ("Sorry, I couldn't find any products within that budget. "
                "Try a higher amount, or type 'agent' for help.")

    # order tracking (a budget number is never treated as an order id)
    oid = None if price_query else re.search(r"\b\d{4,}\b", text)
    wants_order = has(text, ["order", "track", "parcel", "package"])

    if not items and (oid or wants_order):
        if not oid:
            return "Sure! Please share your order ID (example: 1001)."
        order = get_order(oid.group())
        if not order:
            return f"I couldn't find order {oid.group()}. Please check the ID."
        return f"Order {order['order_id']}: {order['status']} (expected: {order['eta']})."

    if items:
        return format_products(items)

    # cheapest item
    if has(text, ["cheapest", "cheap", "lowest price"]):
        in_stock = [p for p in all_products() if p["stock"] > 0]
        if in_stock:
            p = min(in_stock, key=lambda x: x["price"])
            return f"Our lowest-priced item in stock: {p['name']} - ₹{p['price']:.0f}"

    # list everything
    if has(text, KEYWORDS["catalog"]):
        return format_products(all_products())

    for intent in ["shipping", "payment", "offers", "size", "warranty",
                   "greeting", "thanks", "bye"]:
        if has(text, KEYWORDS[intent]):
            return RESPONSES[intent]

    return ("Sorry, I didn't get that. Ask me about a product, order status, "
            "shipping, returns or payments, or type 'agent' for a human.")

if __name__ == "__main__":
    init_db()
    while True:
        print("Bot:", reply(input("You: ")))
