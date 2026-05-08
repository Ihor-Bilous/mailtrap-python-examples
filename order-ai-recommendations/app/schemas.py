from dataclasses import dataclass


@dataclass
class OrderItem:
    name: str
    quantity: int
    price: str


@dataclass
class ShippingAddress:
    name: str
    line1: str
    line2: str
    city: str
    state: str
    postal_code: str
    country: str


@dataclass
class OrderData:
    order_id: str
    customer_email: str
    items: list[OrderItem]
    total: str
    shipping_address: ShippingAddress | None


@dataclass
class RecommendedProduct:
    name: str
    description: str
    price: str
