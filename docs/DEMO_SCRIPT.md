# Reflex Demo Script

Live walkthrough of one delivery, from request to verified drop-off.

**Driver:** Member 1 (Alex), shares screen for this segment only
**Target runtime:** 3 minutes
**View mode:** All 3 Personas, for the entire demo

## Before the demo starts

Complete these before sharing your screen.

1. Start the server: `python3 backend/app.py`
2. Open `http://127.0.0.1:5050` in the browser
3. Confirm the view selector is on **All 3 Personas**
4. Set browser zoom so all three columns fit without scrolling
5. Restart the server to reset the database if a rehearsal was just run
6. Close or move the terminal off the shared screen

**Constraint:** stay in All 3 Personas view throughout. Switching view
modes breaks the layout until the page is refreshed.

**Constraint:** the database must be reset between rehearsals, or
ORD-501 will already be DELIVERED and the flow will not run.

## Step 1: Retailer logs a delivery request

**Do:** In the Retailer column, enter:

| Field | Value |
|---|---|
| Customer name | Wanjiku Mwangi |
| Phone | +254700112233 |
| Drop-off address | Upperhill, KMA Centre, 4th Floor |
| Item description | JBL Flip 6 Bluetooth Speaker |
| Parcel value (KES) | 14500 |

Click **Log Delivery Request**.

**Say:** "A retailer logs the delivery in one form. The system issues an
order ID and a four-digit customer OTP. Note that OTP, the rider will
need it at the door."

**Watch for:** the order appears in the Dispatcher queue within 4
seconds, with nobody refreshing the page.

## Step 2: Dispatcher assigns a rider

**Do:** In the Dispatcher column, find ORD-501, select **RDR-01
Kipchoge Mwangi** from the rider dropdown, click **Assign**.

**Say:** "The dispatcher sees every unassigned order and every available
rider in one queue. Assignment is manual. We did not build routing
logic, and that is a deliberate trade-off we will come back to."

**Watch for:** status moves to ASSIGNED, the order appears in the Rider
column, and the rider's status changes to BUSY.

## Step 3: Rider confirms pickup

**Do:** In the Rider column, click **Confirm Pickup** on ORD-501.

**Say:** "The rider confirms collection from the shop. The order cannot
skip this step. Delivery is blocked until pickup is recorded."

**Watch for:** status becomes PICKED_UP and a pickup timestamp appears.

## Step 4: Failed delivery attempt

**Do:** In the Rider column, enter OTP `0000` and click **Verify and
Deliver**.

**Say:** "The rider enters the code the customer gives them at the door.
This one is wrong, so the delivery is rejected and the order stays in
PICKED_UP."

**Watch for:** the rejection message, and that the status does not
change.

## Step 5: Successful delivery

**Do:** Read the correct OTP from the order card, enter it, click
**Verify and Deliver**.

**Say:** "With the correct code the delivery completes. The order is
marked DELIVERED and the rider is released back to available."

**Watch for:** status DELIVERED, a delivery timestamp, and the rider
returning to AVAILABLE.

## Step 6: Audit trail

**Do:** Open the tracking view for ORD-501.

**Say:** "Every state change is recorded, including the failed attempt.
If a delivery is disputed later, the record shows a wrong code was
entered before the correct one. The trail captures failures, not just
the happy path."

**Watch for:** the FAILED_DELIVERY_ATTEMPT entry sitting between pickup
and delivery.

## Handoff

**Into the demo:** Member 5 finishes Slide 3, then hands over with a
line naming what the demo will show.

**Out of the demo:** Member 1 ends on the audit trail and moves straight
into Slide 4, since the trade-offs slide is owned by the same presenter.

## If something breaks

| Problem | Action |
|---|---|
| Server not responding | Restart it, narrate the state machine from Slide 3 while it comes back |
| Order not appearing | Wait one poll cycle, 4 seconds, before clicking again |
| Layout breaks | Refresh the page. Do not switch view modes |
| Wrong state reached | Restart the server to reset the database, resume from Step 1 |
| Demo will not start at all | Fall back to Slide 3 and walk the state machine verbally, say plainly that the demo failed |
