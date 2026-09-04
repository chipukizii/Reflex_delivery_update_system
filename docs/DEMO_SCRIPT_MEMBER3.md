# Member 3 – Live Demo Script
## Reflex Readiness Sprint

**Speaker:** Member 3 (Kelly Wanjiru)
**Timing:** 4:30 – 6:00 (1.5 minutes for live demo)
**View Mode:** All 3 Personas (Executive Defense View)

---

## Opening Line

"Let us see Reflex work live on one screen. In the Executive Defense View, all three personas are displayed simultaneously."

---

## Step 1: Log a Delivery (Retailer Panel)

**Action:** Ensure "All 3 Personas" view is active

**Action:** Click "Log Delivery Request" on the Retailer panel

**Script:**
"On the left, our retailer is logging a delivery: a JBL Flip 6 Speaker worth KES 14,500 going to Upperhill. When I click 'Log Delivery Request', notice the order is instantly created with ID ORD-501 and an authentic Customer OTP PIN."

---

## Step 2: Assign the Order (Dispatcher Panel)

**Action:** In the dispatcher panel, select "Kipchoge Mwangi" (RDR-01) and click "Assign"

**Script:**
"In the center column, the Dispatcher Cockpit immediately shows ORD-501 in the unassigned queue. The dispatcher selects rider Kipchoge Mwangi and clicks 'Assign'. Kipchoge's status flips to BUSY, and our concurrency guard prevents any duplicate assignment."

---

## Step 3: Pick Up the Order (Rider Panel)

**Action:** In the Rider panel, click "Confirm Package Pickup"

**Script:**
"On the right column, Kipchoge's mobile app receives the task. He arrives at the shop and clicks 'Confirm Package Pickup'. Notice the retailer's screen on the left automatically updates to PICKED UP."

---

## Step 4: Deliver with OTP

**Action:** Enter the OTP (shown on the retailer's screen) in the rider's OTP input field

**Action:** Click "Verify & Deliver"

**Script:**
"Kipchoge arrives at the drop-off in Upperhill. If he enters the wrong PIN '0000', Reflex rejects the delivery instantly. When the customer provides their real OTP, Reflex verifies the PIN, marks the order DELIVERED, logs the timestamp in the immutable audit trail, and frees Kipchoge for his next job."

---

## Closing Line

"This demonstrates Reflex's complete lifecycle: Pending Dispatch → Assigned → Picked Up → Delivered, with full audit trail and OTP verification."

---

## Timing Breakdown

| Step | Duration |
|------|----------|
| Opening | 10 seconds |
| Step 1: Log Delivery | 20 seconds |
| Step 2: Assign Order | 20 seconds |
| Step 3: Pickup | 20 seconds |
| Step 4: Deliver with OTP | 30 seconds |
| Closing | 10 seconds |
| **Total** | **1 minute 50 seconds** |