from sqlalchemy.orm import Session

from app.models import Product

_PRODUCTS = [
    # Accessories
    {
        "name": "Wireless Keyboard",
        "description": "Compact wireless keyboard with backlit keys and 3-device Bluetooth pairing.",
        "category": "Accessories",
        "price_cents": 4999,
        "currency": "usd",
    },
    {
        "name": "USB-C Hub",
        "description": "7-in-1 USB-C hub with HDMI 4K, USB 3.0, SD card reader, and 100W PD pass-through.",
        "category": "Accessories",
        "price_cents": 3499,
        "currency": "usd",
    },
    {
        "name": "Laptop Stand",
        "description": "Adjustable aluminium laptop stand with six height settings and non-slip base.",
        "category": "Accessories",
        "price_cents": 2999,
        "currency": "usd",
    },
    {
        "name": "Webcam HD",
        "description": "1080p webcam with built-in noise-cancelling microphone and auto-focus.",
        "category": "Accessories",
        "price_cents": 5999,
        "currency": "usd",
    },
    {
        "name": "Desk Lamp",
        "description": "LED desk lamp with adjustable colour temperature, USB charging port, and touch control.",
        "category": "Accessories",
        "price_cents": 3999,
        "currency": "usd",
    },
    {
        "name": "Cable Management Kit",
        "description": "20-piece cable management kit including clips, sleeves, and velcro ties.",
        "category": "Accessories",
        "price_cents": 1499,
        "currency": "usd",
    },
    # Electronics
    {
        "name": "Noise-Cancelling Headphones",
        "description": "Over-ear headphones with active noise cancellation, 30-hour battery, and foldable design.",
        "category": "Electronics",
        "price_cents": 14999,
        "currency": "usd",
    },
    {
        "name": "Portable Charger 20000mAh",
        "description": "Slim 20000mAh power bank with dual USB-A and USB-C outputs plus 22.5W fast charging.",
        "category": "Electronics",
        "price_cents": 3999,
        "currency": "usd",
    },
    {
        "name": "Bluetooth Speaker",
        "description": "Waterproof portable Bluetooth speaker with 360° sound and 24-hour playtime.",
        "category": "Electronics",
        "price_cents": 7999,
        "currency": "usd",
    },
    {
        "name": "Smart Plug",
        "description": "Wi-Fi smart plug with energy monitoring, scheduling, and voice assistant compatibility.",
        "category": "Electronics",
        "price_cents": 1999,
        "currency": "usd",
    },
    {
        "name": "LED Strip Lights",
        "description": "5-metre RGB LED strip with app control, music sync, and adhesive backing.",
        "category": "Electronics",
        "price_cents": 2499,
        "currency": "usd",
    },
    # Peripherals
    {
        "name": "Mechanical Keyboard",
        "description": "Tenkeyless mechanical keyboard with Cherry MX switches and per-key RGB lighting.",
        "category": "Peripherals",
        "price_cents": 9999,
        "currency": "usd",
    },
    {
        "name": "Ergonomic Mouse",
        "description": "Vertical ergonomic mouse with adjustable DPI, silent clicks, and USB receiver.",
        "category": "Peripherals",
        "price_cents": 3499,
        "currency": "usd",
    },
    {
        "name": "Wrist Rest",
        "description": "Memory foam wrist rest with non-slip base, sized for full-size keyboards.",
        "category": "Peripherals",
        "price_cents": 1999,
        "currency": "usd",
    },
    {
        "name": "USB Microphone",
        "description": "Cardioid condenser USB microphone with mute button and headphone monitoring jack.",
        "category": "Peripherals",
        "price_cents": 8999,
        "currency": "usd",
    },
    {
        "name": "Monitor Light Bar",
        "description": "Clip-on LED monitor light bar with auto-dimming and asymmetric lighting to reduce glare.",
        "category": "Peripherals",
        "price_cents": 4499,
        "currency": "usd",
    },
]


def seed_products(session: Session) -> None:
    if session.query(Product).count() == 0:
        session.add_all([Product(**p) for p in _PRODUCTS])
        session.commit()
