# reflex_prototype/db.py
# Data access layer for Reflex Delivery Synchronization Service

import time
import random

# In-memory database tables
_ORDERS = {}
_RIDERS = {
    "RDR-01": {"id": "RDR-01", "name": "Kipchoge Mwangi", "phone": "+254711223344", "status": "AVAILABLE", "active_orders": []},
    "RDR-02": {"id": "RDR-02", "name": "Juma Omondi", "phone": "+254722334455", "status": "AVAILABLE", "active_orders": []},
    "RDR-03": {"id": "RDR-03", "name": "Faith Chebet", "phone": "+254733445566", "status": "AVAILABLE", "active_orders": []}
}
_AUDIT_LOGS = []


def reset_db():
    """Reset database to default seed state for clean testing and demos."""
    global _ORDERS, _AUDIT_LOGS
    _ORDERS = {
        "ORD-501": {
            "id": "ORD-501",
            "retailer": "Luthuli Electronics Mart",
            "customer_name": "Samuel Kamau",
            "customer_phone": "+254712345678",
            "dropoff_address": "Westlands, Ring Road Plaza, 3rd Floor",
            "item_desc": "Samsung 43-Inch 4K TV Screen",
            "order_value_kes": 34500,
            "status": "PENDING_DISPATCH",
            "assigned_rider_id": None,
            "otp_code": "8492",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "picked_up_at": None,
            "delivered_at": None
        },
        "ORD-502": {
            "id": "ORD-502",
            "retailer": "Nairobi Central Pharmacy",
            "customer_name": "Amina Hassan",
            "customer_phone": "+254798765432",
            "dropoff_address": "Kilimani, Argwings Kodhek Rd, House 12",
            "item_desc": "Prescription Cold Chain Insulin Pack",
            "order_value_kes": 6200,
            "status": "PENDING_DISPATCH",
            "assigned_rider_id": None,
            "otp_code": "3104",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "picked_up_at": None,
            "delivered_at": None
        }
    }
    _AUDIT_LOGS = [
        {"order_id": "ORD-501", "actor": "RETAILER", "action": "ORDER_CREATED", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")},
        {"order_id": "ORD-502", "actor": "RETAILER", "action": "ORDER_CREATED", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
    ]
    for rider in _RIDERS.values():
        rider["status"] = "AVAILABLE"
        rider["active_orders"] = []


# Initialize seed data on load
reset_db()


def get_all_orders():
    return list(_ORDERS.values())


def get_order_by_id(order_id):
    return _ORDERS.get(order_id.upper())


def get_all_riders():
    return list(_RIDERS.values())


def get_rider_by_id(rider_id):
    return _RIDERS.get(rider_id.upper())


def get_audit_logs(order_id=None):
    if order_id:
        return [log for log in _AUDIT_LOGS if log["order_id"] == order_id.upper()]
    return _AUDIT_LOGS

def create_order(retailer_name, customer_name, customer_phone, dropoff_address, item_desc, order_value_kes):
    """Create a new delivery request by Retailer Staff."""
    order_id = f"ORD-{random.randint(503, 999)}"
    otp = f"{random.randint(1000, 9999)}"

    order = {
        "id": order_id,
        "retailer": retailer_name or "Downtown Retailer",
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "dropoff_address": dropoff_address,
        "item_desc": item_desc,
        "order_value_kes": float(order_value_kes or 0),
        "status": "PENDING_DISPATCH",
        "assigned_rider_id": None,
        "otp_code": otp,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "picked_up_at": None,
        "delivered_at": None
    }
    _ORDERS[order_id] = order
    _AUDIT_LOGS.append({
        "order_id": order_id,
        "actor": "RETAILER",
        "action": f"Created order {order_id} for {customer_name}",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    return order