# backend/app.py
# Reflex Delivery Synchronization Service — API Server & Live Interactive Simulation
# OWNER: Member 2

import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import db

# Set static folder pointing to frontend/static
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'))
app = Flask(__name__, static_folder=static_dir, static_url_path='/static')
CORS(app)

# Serve the 3-column live interactive demo dashboard
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


# ---- Retailer Persona Endpoints ----

@app.route('/api/orders', methods=['GET'])
def list_orders():
    """List all orders or filter by status."""
    status = request.args.get('status')
    orders = db.get_all_orders()
    if status:
        orders = [o for o in orders if o['status'].upper() == status.upper()]
    return jsonify({'success': True, 'count': len(orders), 'orders': orders})


import re

@app.route('/api/orders', methods=['POST'])
def create_delivery_request():
    """Retailer staff logs a new delivery request."""
    data = request.get_json() or {}
    required_fields = ['customer_name', 'customer_phone', 'dropoff_address', 'item_desc']
    for field in required_fields:
        val = data.get(field)
        if not val or not str(val).strip():
            return jsonify({'success': False, 'error': f"Missing required field: '{field}'"}), 400

    # 1. Full Name Validation: Must take at least two names (first and last name)
    customer_name = str(data.get('customer_name', '')).strip()
    name_parts = customer_name.split()
    if len(name_parts) < 2 or any(len(p) < 2 for p in name_parts):
        return jsonify({
            'success': False,
            'error': "Customer name must include at least two names (e.g. First and Last name)."
        }), 400

    # 2. Phone Number Validation: Max 10 digits, numeric only (e.g. 0712345678)
    customer_phone = str(data.get('customer_phone', '')).strip()
    if not customer_phone.isdigit():
        return jsonify({
            'success': False,
            'error': "Phone number must contain numbers only."
        }), 400
    if len(customer_phone) > 10:
        return jsonify({
            'success': False,
            'error': f"Phone number cannot exceed 10 digits. Received {len(customer_phone)} digits."
        }), 400
    if len(customer_phone) < 10:
        return jsonify({
            'success': False,
            'error': f"Phone number must be a valid 10-digit number (e.g. 0712345678). Received {len(customer_phone)} digits."
        }), 400

    # 3. Address and Description Validation
    dropoff_address = str(data.get('dropoff_address', '')).strip()
    if len(dropoff_address) < 5:
        return jsonify({'success': False, 'error': "Delivery address must be at least 5 characters long."}), 400

    item_desc = str(data.get('item_desc', '')).strip()
    if len(item_desc) < 3:
        return jsonify({'success': False, 'error': "Item description must be at least 3 characters long."}), 400

    order = db.create_order(
        retailer_name=data.get('retailer_name', 'Luthuli Electronics Mart'),
        customer_name=customer_name,
        customer_phone=customer_phone,
        dropoff_address=dropoff_address,
        item_desc=item_desc,
        order_value_kes=data.get('order_value_kes', 0)
    )
    return jsonify({
        'success': True,
        'message': f"Delivery request {order['id']} created. Awaiting dispatch.",
        'order': order
    }), 201


@app.route('/api/orders/<order_id>/tracking', methods=['GET'])
def get_order_tracking(order_id):
    """Real-time tracking view for Retailer and Customer."""
    order = db.get_order_by_id(order_id)
    if not order:
        return jsonify({'success': False, 'error': f"Order '{order_id}' not found"}), 404

    logs = db.get_audit_logs(order_id)
    rider = db.get_rider_by_id(order.get('assigned_rider_id')) if order.get('assigned_rider_id') else None

    return jsonify({
        'success': True,
        'order': order,
        'assigned_rider': rider,
        'audit_trail': logs
    })


# ---- Dispatcher Persona Endpoints ----

@app.route('/api/dispatch/unassigned', methods=['GET'])
def get_unassigned_queue():
    """Dispatcher views unassigned delivery queue."""
    all_orders = db.get_all_orders()
    unassigned = [o for o in all_orders if o['status'] == 'PENDING_DISPATCH']
    riders = db.get_all_riders()
    return jsonify({
        'success': True,
        'unassigned_orders': unassigned,
        'available_riders': riders
    })


@app.route('/api/dispatch/assign', methods=['POST'])
def assign_order():
    """Dispatcher assigns an order to a rider."""
    data = request.get_json() or {}
    order_id = data.get('order_id')
    rider_id = data.get('rider_id')

    if not order_id or not rider_id:
        return jsonify({'success': False, 'error': 'order_id and rider_id are required'}), 400

    # Fleet Guard: Verify rider exists and is NOT currently BUSY
    rider = db.get_rider_by_id(rider_id)
    if not rider:
        return jsonify({'success': False, 'error': f"Rider '{rider_id}' not found"}), 404

    if rider.get('status') == 'BUSY' or len(rider.get('active_orders', [])) > 0:
        return jsonify({
            'success': False,
            'error': f"Cannot assign: Rider {rider['name']} ({rider_id}) is already BUSY with an active delivery."
        }), 400

    success, msg, order = db.assign_order_to_rider(order_id, rider_id)
    if not success:
        return jsonify({'success': False, 'error': msg}), 400

    return jsonify({'success': True, 'message': msg, 'order': order})


# ---- Rider Persona Endpoints ----

@app.route('/api/riders/<rider_id>/tasks', methods=['GET'])
def get_rider_tasks(rider_id):
    """Rider views assigned active delivery tasks."""
    rider = db.get_rider_by_id(rider_id)
    if not rider:
        return jsonify({'success': False, 'error': f"Rider '{rider_id}' not found"}), 404

    all_orders = db.get_all_orders()
    assigned_orders = [o for o in all_orders if o.get('assigned_rider_id') == rider_id.upper()]
    return jsonify({
        'success': True,
        'rider': rider,
        'tasks': assigned_orders
    })


@app.route('/api/riders/pickup', methods=['POST'])
def rider_pickup():
    """Rider confirms physical pickup of the parcel."""
    data = request.get_json() or {}
    order_id = data.get('order_id')
    rider_id = data.get('rider_id')

    if not order_id or not rider_id:
        return jsonify({'success': False, 'error': 'order_id and rider_id are required'}), 400

    success, msg, order = db.rider_pickup_order(order_id, rider_id)
    if not success:
        return jsonify({'success': False, 'error': msg}), 400

    return jsonify({'success': True, 'message': msg, 'order': order})


@app.route('/api/riders/deliver', methods=['POST'])
def rider_deliver():
    """Rider enters Customer SMS OTP PIN to verify drop-off."""
    data = request.get_json() or {}
    order_id = data.get('order_id')
    rider_id = data.get('rider_id')
    raw_otp = data.get('otp_code')

    if not order_id or not rider_id or not raw_otp:
        return jsonify({'success': False, 'error': 'order_id, rider_id, and otp_code are required'}), 400

    # Strip any accidental spaces (e.g. from letter-spacing or spacebar taps)
    clean_otp = str(raw_otp).replace(' ', '').strip()

    success, msg, order = db.verify_and_deliver_order(order_id, rider_id, clean_otp)
    if not success:
        return jsonify({'success': False, 'error': msg}), 400

    return jsonify({'success': True, 'message': msg, 'order': order})


# ---- System Utilities ----

@app.route('/api/system/reset', methods=['POST'])
def reset_system():
    """Reset system state to clean seed data for live demo repetitions."""
    db.reset_db()
    return jsonify({'success': True, 'message': 'System state reset to baseline seed data.'})


if __name__ == '__main__':
    print("\n=======================================================")
    print("  REFLEX: Delivery Synchronization Service Running")
    print("  Live Interactive Dashboard: http://127.0.0.1:5050")
    print("=======================================================\n")
    app.run(port=5050, debug=True)
