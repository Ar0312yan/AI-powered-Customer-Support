import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

CHANNELS = ["chat", "email", "web"]
PRODUCTS = [
    "Running Shoes", "Wireless Headphones", "Yoga Mat", "Coffee Maker",
    "Laptop Bag", "Sunglasses", "Watch", "Backpack", "Water Bottle", "Desk Lamp"
]
COUNTRIES = ["US", "UK", "CA", "AU", "DE", "IN", "FR", "SG", "BR", "MX"]
RESOLUTIONS = ["resolved", "pending", "escalated", "closed"]

CATEGORIES = {
    "delivery_delay": {
        "weight": 0.24,
        "sentiments": ["frustrated", "frustrated", "dissatisfied", "neutral"],
        "messages": [
            "My order was supposed to arrive {days} days ago and still nothing. Tracking hasnt updated at all.",
            "Where is my package? Ordered {days_ago} days ago and no movement since it left the warehouse.",
            "I paid for express shipping and my order is already {days} days late.",
            "Order still hasnt arrived. Its been {days_ago} days. Can someone help.",
            "Package stuck at facility for {days} days now. No updates from your side.",
        ],
        "replies": [
            "Really sorry about the delay. I flagged your order as priority with our logistics team. You should get an update within a few hours. If it still doesnt move I will process a refund right away.",
            "There was an unexpected hold at the distribution center. Its back in transit now and should reach you in 2 business days. I added a store credit for the trouble.",
            "I opened a trace with the carrier. If delivery cant be confirmed soon I will arrange a replacement or full refund, your choice.",
        ]
    },
    "wrong_item": {
        "weight": 0.19,
        "sentiments": ["frustrated", "dissatisfied", "dissatisfied", "neutral"],
        "messages": [
            "Got completely the wrong item. Ordered {product} and received something else.",
            "My order arrived but its not what I ordered at all.",
            "Wrong size and wrong color. This is the second time this happened.",
            "Received an incorrect item in my order.",
        ],
        "replies": [
            "Please keep the wrong item, no need to return it. I placed a new order for the correct {product} and it will ship today. Tracking number coming within the hour.",
            "A prepaid return label is heading to your email and I expedited the correct order. Also adding a discount for the inconvenience.",
        ]
    },
    "payment_failed": {
        "weight": 0.16,
        "sentiments": ["neutral", "dissatisfied", "frustrated", "neutral"],
        "messages": [
            "Payment keeps getting declined but my card works fine everywhere else. Error {error_code}.",
            "Checkout is failing every time. Just want to place my order.",
            "Tried three different cards and none work on your site.",
            "Getting a payment error at the last step.",
        ],
        "replies": [
            "Error {error_code} is usually a security flag from the payment processor. Try clearing your browser cache and using incognito. If it still fails I can process the order manually.",
            "There was a temporary issue with our payment gateway today. It has been fixed so please try again. Still failing? Send me your order details and I will sort it.",
        ]
    },
    "refund_not_received": {
        "weight": 0.14,
        "sentiments": ["neutral", "dissatisfied", "frustrated", "neutral"],
        "messages": [
            "Returned my order {days_ago} days ago and still no refund. Return was confirmed received.",
            "Where is my refund? Been over two weeks since you got my return.",
            "Still waiting on ${amount}. This is taking too long.",
            "No refund after {days_ago} days. Starting to get worried.",
        ],
        "replies": [
            "Your refund of ${amount} was processed. Bank transfers take 5 to 10 business days. Should be there very soon.",
            "The refund got stuck in a processing queue which I have now cleared. It will reflect in your account within 3 business days.",
        ]
    },
    "account_login": {
        "weight": 0.10,
        "sentiments": ["neutral", "dissatisfied", "neutral", "neutral"],
        "messages": [
            "Cant log into my account. Reset my password twice and still getting an error.",
            "Account seems locked and I have not done anything unusual.",
            "Password reset email is not arriving. Checked spam already.",
            "Says my email doesnt exist but I have been ordering from you for years.",
        ],
        "replies": [
            "Triggered a fresh password reset email manually. Should arrive in a few minutes. Check spam just in case.",
            "Your account was auto-locked after an unusual login attempt. I have unlocked it and sent a reset link.",
        ]
    },
    "product_quality": {
        "weight": 0.09,
        "sentiments": ["dissatisfied", "frustrated", "dissatisfied", "neutral"],
        "messages": [
            "The {product} stopped working after just {days} days.",
            "Very disappointed. Looks nothing like the photos on the website.",
            "Arrived damaged. Packaging was fine so it happened before shipping.",
            "Already falling apart after one week.",
        ],
        "replies": [
            "A replacement is shipping today at no cost. You do not need to return the defective item.",
            "I processed a full refund. Should be there in 5 to 7 business days. Want a replacement instead? Just say so.",
        ]
    },
    "cancellation": {
        "weight": 0.08,
        "sentiments": ["neutral", "neutral", "neutral", "satisfied"],
        "messages": [
            "Need to cancel my order please. It hasnt shipped yet.",
            "Can you cancel my recent order? Ordered by mistake.",
            "Please cancel before it ships.",
        ],
        "replies": [
            "Done. Cancelled and refund of ${amount} is on its way. Back in your account within 5 business days.",
            "No problem. Cancelled and refunded ${amount}. Let me know if you need anything else.",
        ]
    },
}


def weighted_choice(items, weights):
    return random.choices(items, weights=weights, k=1)[0]


def random_date():
    start = datetime.now() - timedelta(days=90)
    delta = timedelta(
        days=random.randint(0, 90),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    return start + delta


def generate_ticket(index):
    category = weighted_choice(
        list(CATEGORIES.keys()),
        [v["weight"] for v in CATEGORIES.values()]
    )
    cat = CATEGORIES[category]
    product = random.choice(PRODUCTS)
    days = random.randint(2, 14)
    days_ago = random.randint(5, 20)
    amount = round(random.uniform(15, 350), 2)
    error_code = f"ERR_{random.randint(100, 999)}"
    dt = random_date()

    msg = random.choice(cat["messages"]).format(
        product=product, days=days, days_ago=days_ago,
        amount=amount, error_code=error_code
    )
    reply = random.choice(cat["replies"]).format(
        product=product, amount=amount, error_code=error_code
    )
    sentiment = random.choice(cat["sentiments"])
    frustration_map = {
        "frustrated": random.randint(7, 10),
        "dissatisfied": random.randint(4, 6),
        "neutral": random.randint(2, 4),
        "satisfied": random.randint(1, 3)
    }

    return {
        "ticket_id": f"TKT-{str(index).zfill(5)}",
        "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
        "customer_id": f"CUST-{random.randint(1000, 50000)}",
        "channel": weighted_choice(CHANNELS, [0.55, 0.32, 0.13]),
        "message": msg,
        "agent_reply": reply,
        "product": product,
        "order_value": amount,
        "customer_country": random.choice(COUNTRIES),
        "resolution_status": weighted_choice(RESOLUTIONS, [0.58, 0.22, 0.12, 0.08]),
        "category": category,
        "sentiment": sentiment,
        "frustration_score": frustration_map[sentiment],
    }


def generate(rows=10000, output="data/tickets.csv"):
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "ticket_id", "timestamp", "customer_id", "channel", "message",
        "agent_reply", "product", "order_value", "customer_country",
        "resolution_status", "category", "sentiment", "frustration_score"
    ]
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for i in range(1, rows + 1):
            writer.writerow(generate_ticket(i))
    print(f"Generated {rows} tickets -> {output}")


if __name__ == "__main__":
    generate()
