# tests/test_reflex.py
# Automated Test Suite for Reflex Delivery Synchronization & Verification Platform

import unittest
import json
import sys
import os

# Add directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app import app
import db

class TestReflexPrototype(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        db.reset_db()

    def test_01_create_delivery_order(self):
        """Retailer staff logs a new delivery request."""
        payload = {
            "retailer_name": "Luthuli Electronics Mart",
            "customer_name": "David Ndung'u",
            "customer_phone": "0722998877",
            "dropoff_address": "CBD, Kimathi Street, Eagle House",
            "item_desc": "HP EliteBook 840 G6 Laptop",
            "order_value_kes": 48000
        }
        res = self.client.post('/api/orders', json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['order']['status'], 'PENDING_DISPATCH')
        self.assertIsNotNone(data['order']['otp_code'])
        self.assertRegex(data['order']['otp_code'], r'^\d{4}$')

    def test_02_dispatcher_unassigned_queue(self):
        """Dispatcher views queue of unassigned orders and available riders."""
        res = self.client.get('/api/dispatch/unassigned')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['unassigned_orders']), 1)
        self.assertGreaterEqual(len(data['available_riders']), 1)

    def test_03_dispatcher_assign_order(self):
        """Dispatcher assigns order to rider."""
        payload = {"order_id": "ORD-501", "rider_id": "RDR-01"}
        res = self.client.post('/api/dispatch/assign', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['order']['status'], 'ASSIGNED')
        self.assertEqual(data['order']['assigned_rider_id'], 'RDR-01')

    def test_04_duplicate_assignment_guard(self):
        """Re-assigning an already assigned order is blocked."""
        self.client.post('/api/dispatch/assign', json={"order_id": "ORD-501", "rider_id": "RDR-01"})
        res2 = self.client.post('/api/dispatch/assign', json={"order_id": "ORD-501", "rider_id": "RDR-02"})
        self.assertEqual(res2.status_code, 400)
        data = res2.get_json()
        self.assertFalse(data['success'])
        self.assertIn("already in state 'ASSIGNED'", data['error'])

    def test_05_rider_pickup_flow(self):
        """Rider confirms package pickup from shop."""
        self.client.post('/api/dispatch/assign', json={"order_id": "ORD-501", "rider_id": "RDR-01"})
        res = self.client.post('/api/riders/pickup', json={"order_id": "ORD-501", "rider_id": "RDR-01"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['order']['status'], 'PICKED_UP')
        self.assertIsNotNone(data['order']['picked_up_at'])

    def test_06_invalid_otp_rejection(self):
        """Rider attempts delivery with wrong Customer OTP and is rejected."""
        self.client.post('/api/dispatch/assign', json={"order_id": "ORD-501", "rider_id": "RDR-01"})
        self.client.post('/api/riders/pickup', json={"order_id": "ORD-501", "rider_id": "RDR-01"})
        res = self.client.post('/api/riders/deliver', json={"order_id": "ORD-501", "rider_id": "RDR-01", "otp_code": "0000"})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data['success'])
        self.assertIn("Invalid Customer OTP PIN", data['error'])

    def test_07_valid_otp_delivery_success(self):
        """Rider enters correct Customer OTP and delivery is marked DELIVERED."""
        self.client.post('/api/dispatch/assign', json={"order_id": "ORD-501", "rider_id": "RDR-01"})
        self.client.post('/api/riders/pickup', json={"order_id": "ORD-501", "rider_id": "RDR-01"})
        correct_otp = db.get_order_by_id("ORD-501")["otp_code"]
        res = self.client.post('/api/riders/deliver', json={"order_id": "ORD-501", "rider_id": "RDR-01", "otp_code": correct_otp})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['order']['status'], 'DELIVERED')
        self.assertIsNotNone(data['order']['delivered_at'])

    def test_08_order_tracking_audit_trail(self):
        """Retailer and customer view complete audit trail of the order."""
        self.client.post('/api/dispatch/assign', json={"order_id": "ORD-501", "rider_id": "RDR-01"})
        self.client.post('/api/riders/pickup', json={"order_id": "ORD-501", "rider_id": "RDR-01"})
        correct_otp = db.get_order_by_id("ORD-501")["otp_code"]
        self.client.post('/api/riders/deliver', json={"order_id": "ORD-501", "rider_id": "RDR-01", "otp_code": correct_otp})

        res = self.client.get('/api/orders/ORD-501/tracking')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['order']['status'], 'DELIVERED')
        self.assertGreaterEqual(len(data['audit_trail']), 3)

    def test_09_busy_rider_assignment_blocked(self):
        """Dispatcher cannot assign a second delivery to a rider who is already BUSY."""
        # 1. Assign first order to RDR-01 -> RDR-01 becomes BUSY
        res1 = self.client.post('/api/dispatch/assign', json={"order_id": "ORD-501", "rider_id": "RDR-01"})
        self.assertEqual(res1.status_code, 200)

        # 2. Attempt to assign second order (ORD-502) to same rider (RDR-01) -> Must be BLOCKED
        res2 = self.client.post('/api/dispatch/assign', json={"order_id": "ORD-502", "rider_id": "RDR-01"})
        self.assertEqual(res2.status_code, 400)
        data = res2.get_json()
        self.assertFalse(data['success'])
        self.assertIn("already BUSY", data['error'])

    def test_10_phone_validation_max_10_digits(self):
        """Phone number with more than 10 digits or non-numeric characters is rejected."""
        # Case A: More than 10 digits (11 digits)
        payload_too_long = {
            "retailer_name": "Luthuli Electronics Mart",
            "customer_name": "Samuel Kamau",
            "customer_phone": "07123456789",  # 11 digits
            "dropoff_address": "Westlands, Nairobi",
            "item_desc": "Tablet",
            "order_value_kes": 20000
        }
        res_long = self.client.post('/api/orders', json=payload_too_long)
        self.assertEqual(res_long.status_code, 400)
        self.assertIn("cannot exceed 10 digits", res_long.get_json()['error'])

        # Case B: Non-numeric phone
        payload_non_digit = {
            "retailer_name": "Luthuli Electronics Mart",
            "customer_name": "Samuel Kamau",
            "customer_phone": "07123ABCDE",
            "dropoff_address": "Westlands, Nairobi",
            "item_desc": "Tablet",
            "order_value_kes": 20000
        }
        res_char = self.client.post('/api/orders', json=payload_non_digit)
        self.assertEqual(res_char.status_code, 400)
        self.assertIn("numbers only", res_char.get_json()['error'])

    def test_11_customer_name_minimum_two_names(self):
        """Customer name must contain at least two names (first and last name)."""
        # Case A: Single name (rejected)
        payload_single = {
            "retailer_name": "Luthuli Electronics Mart",
            "customer_name": "Wanjiku",  # Only 1 name
            "customer_phone": "0712345678",
            "dropoff_address": "Westlands, Nairobi",
            "item_desc": "Tablet",
            "order_value_kes": 20000
        }
        res_single = self.client.post('/api/orders', json=payload_single)
        self.assertEqual(res_single.status_code, 400)
        self.assertIn("at least two names", res_single.get_json()['error'])

        # Case B: Full two names (accepted)
        payload_valid = {
            "retailer_name": "Luthuli Electronics Mart",
            "customer_name": "Wanjiku Mwangi",
            "customer_phone": "0712345678",
            "dropoff_address": "Westlands, Nairobi",
            "item_desc": "Tablet",
            "order_value_kes": 20000
        }
        res_valid = self.client.post('/api/orders', json=payload_valid)
        self.assertEqual(res_valid.status_code, 201)
        self.assertTrue(res_valid.get_json()['success'])

if __name__ == '__main__':
    unittest.main()
