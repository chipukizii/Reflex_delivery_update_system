# backend/db.py
# Data access layer for Reflex Delivery Synchronization Service

import time
import random
import copy

# In-memory database tables
import copy

_RIDER_SEED = {
    "RDR-01": {"id": "RDR-01", "name": "Kipchoge Mwangi", "phone": "+254711223344", "status": "AVAILABLE", "active_orders": []},
    "RDR-02": {"id": "RDR-02", "name": "Juma Omondi", "phone": "+254722334455", "status": "AVAILABLE", "active_orders": []},
    "RDR-03": {"id": "RDR-03", "name": "Faith Chebet", "phone": "+254733445566", "status": "AVAILABLE", "active_orders": []}
}

_ORDERS = {}
_RIDERS = {}
_AUDIT_LOGS = []


def reset_db():
    """Reset database to default seed state for clean testing and demos."""
    global _ORDERS, _RIDERS, _AUDIT_LOGS
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
    _RIDERS = copy.deepcopy(_RIDER_SEED)
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
    order_id = None
    for _ in range(50):
        candidate = f"ORD-{random.randint(503, 999)}"
        if candidate not in _ORDERS:
            order_id = candidate
            break
    if order_id is None:
        return None

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

def assign_order_to_rider(order_id, rider_id):
    """Dispatcher assigns an order to a rider, guarded by order state."""

    order_id = str(order_id).upper()
    rider_id = str(rider_id).upper()

    order = get_order_by_id(order_id)
    rider = get_rider_by_id(rider_id)

    if not order:
        return False, "Order not found", None
    if not rider:
        return False, "Rider not found", None
    if order["status"] != "PENDING_DISPATCH":
        return False, f"Order is already in state '{order['status']}'", None

    order["status"] = "ASSIGNED"
    order["assigned_rider_id"] = rider_id
    if order_id not in rider["active_orders"]:
        rider["active_orders"].append(order_id)
    rider["status"] = "BUSY"

    _AUDIT_LOGS.append({
        "order_id": order_id,
        "actor": "DISPATCHER",
        "action": f"Assigned order to {rider['name']} ({rider_id})",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    return True, "Assigned successfully", order

def rider_pickup_order(order_id, rider_id):
    """Rider confirms pickup of parcel from retailer."""

    order_id = str(order_id).upper()
    rider_id = str(rider_id).upper()

    order = get_order_by_id(order_id)
    if not order:
        return False, "Order not found", None
    if order["assigned_rider_id"] != rider_id:
        return False, "Order is not assigned to this rider", None
    if order["status"] != "ASSIGNED":
        return False, f"Cannot pickup order in state '{order['status']}'", None

    order["status"] = "PICKED_UP"
    order["picked_up_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

    _AUDIT_LOGS.append({
        "order_id": order_id,
        "actor": f"RIDER:{rider_id}",
        "action": "Package picked up from shop; in transit to customer",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    return True, "Picked up successfully", order

def verify_and_deliver_order(order_id, rider_id, input_otp):
    """Rider delivers package and enters customer 4-digit OTP code for instant proof-of-delivery."""

    order_id = str(order_id).upper()
    rider_id = str(rider_id).upper()

    order = get_order_by_id(order_id)
    if not order:
        return False, "Order not found", None
    if order["assigned_rider_id"] != rider_id:
        return False, "Order is not assigned to this rider", None
    if order["status"] != "PICKED_UP":
        return False, f"Order must be in PICKED_UP state before delivery. Current state: '{order['status']}'", None

    # OTP Verification check
    if str(input_otp).strip() != str(order["otp_code"]).strip():
        _AUDIT_LOGS.append({
            "order_id": order_id,
            "actor": f"RIDER:{rider_id}",
            "action": "FAILED_DELIVERY_ATTEMPT: Invalid OTP entered",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        return False, "Invalid Customer OTP PIN. Verification failed.", None

    order["status"] = "DELIVERED"
    order["delivered_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

    # Release rider
    rider = get_rider_by_id(rider_id)
    if rider and order_id in rider["active_orders"]:
        rider["active_orders"].remove(order_id)
    if rider and len(rider["active_orders"]) == 0:
        rider["status"] = "AVAILABLE"

    _AUDIT_LOGS.append({
        "order_id": order_id,
        "actor": f"RIDER:{rider_id}",
        "action": "DELIVERED: Verified via Customer OTP",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    return True, "Delivered successfully with verified Proof-of-Delivery", order

    
