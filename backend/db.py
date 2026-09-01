# reflex_prototype/db.py
# Data access layer for Reflex Delivery Synchronization Service

import time

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