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
            "customer_phone": "+254722998877",
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

if __name__ == '__main__':
    unittest.main()
