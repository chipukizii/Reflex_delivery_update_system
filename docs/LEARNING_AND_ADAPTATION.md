# Learning and Adaptation Log

## Purpose

This log records how each member approached their assigned part of the
Reflex delivery system, what they got wrong or had to change along the
way, and what they learned. One shared file, one section per member, so
the team's reasoning sits in a single place rather than scattered across
separate documents.

## Member 1: Backend Core and Data Engine

### Initial Understanding

The delivery workflow required storing delivery requests, rider
information and status updates. My first task was deciding where that
state lives. I chose an in-memory Python store rather than a database,
because the sprint is judged on the demo and the design reasoning, not
on persistence, and a database would have added setup cost for every
teammate running the app locally. The cost of that choice (state is lost
on restart) is noted in the trade-off log.

### Implementation Approach

Started with the storage tables and read accessors, plus a reset_db()
helper so tests and demos always begin from a known seed state.

Added order creation, then rider assignment. Assignment is where the
first real design question appeared: nothing stopped a second dispatcher
from assigning an order that was already taken, because the function
happily overwrote assigned_rider_id. I added a state check so assignment
only succeeds from PENDING_DISPATCH.

Two issues surfaced in review of the data layer. The first was a real
defect: reset_db() rebuilt orders and audit logs but mutated the rider
table in place, so rider state could leak between test runs. Fixed by
rebuilding riders from a seed template. The second was the customer OTP
being readable through the order accessors. I chose not to change that
mid sprint, because the API and the test suite both depend on reading
it, and recorded it as a trade-off instead.

Completing the workflow raised an ordering question in the delivery
function. A rider can fail delivery for three different reasons: the
order is not theirs, it was never picked up, or the OTP is wrong. I
check them in that order, because the most specific failure a rider can
act on should surface first. Telling someone their OTP is wrong when the
real problem is that they never confirmed pickup would send them looking
in the wrong place.

I also chose to write failed OTP attempts to the audit log rather than
drop them. A delivery that is disputed later is more useful with a
record of how many wrong codes were entered than with silence.

### Testing and Validation

The full suite ran end to end for the first time once the backend was
complete, covering order creation, the dispatcher queue, assignment,
duplicate assignment rejection, pickup, invalid OTP rejection,
successful delivery and the audit trail. I also checked by hand the two
paths the suite does not reach: pickup attempted before assignment, and
delivery attempted before pickup.

## Member 2: Backend API and Integration

## Member 3: Frontend UI and Interaction

### Initial Understanding

I needed to build a dashboard that supports three personas: Retailer, Dispatcher, and Rider. The key requirement was that all three views must sync to the same backend state without requiring a page refresh for each update.

I chose a Single Page Application (SPA) approach with three panels that can be viewed together (Executive View) or individually. The view switching is controlled by the `switchView()` function, which toggles which panels are visible.

### Implementation Approach

Started by understanding the existing `index.html` file and its interaction with the backend API. The three main functions I worked with were:

- `switchView(mode)`: Controls which persona panels are visible
- `fetchState()`: Polls the backend every 4 seconds for updates
- The order flow functions: `createOrder()`, `assignOrder()`, `pickupOrder()`, `deliverOrder()`

The most significant change I made was adding a demo instructions banner above the view switcher to guide presenters through the live demo flow: "DEMO: Click 'Log Delivery' → Assign to Rider → Pickup → Enter OTP."

### Challenges Faced

**Challenge 1: Understanding the View Switcher Logic**
- **Issue:** I didn't initially understand how `switchView()` controlled which panels were visible
- **Fix:** I traced through the code and saw how it toggles `display: none/block` on the persona cards
- **Learning:** `display: none` hides elements, `display: flex` shows them

**Challenge 2: Git Remote Issues**
- **Issue:** I pushed to the wrong repository (`git-test` instead of `reflex-delivery-system`)
- **Fix:** I changed the remote URL using `git remote set-url origin`
- **Learning:** Always check `git remote -v` before pushing

**Challenge 3: Creating a Pull Request**
- **Issue:** I got an "entirely different commit histories" error
- **Fix:** Created a fresh branch from the correct `main`
- **Learning:** Always start from the correct `main` when creating a PR

**Challenge 4: View Mode Bug**
- **Issue:** Switching view modes breaks the layout until you refresh
- **Workaround:** Run the demo in "All 3 Personas" view – it renders fine
- **Learning:** This is a render path issue in `index.html`, not a CSS problem

### What I Learned

1. **Frontend Architecture:** The UI uses a Single Page Application (SPA) approach with three personas sharing the same page. Executive View shows all three side-by-side for live demos.

2. **HTTP Polling vs WebSockets:** Reflex uses 4-second polling to save battery on rider devices. The `fetchState()` function pulls updates from the backend. This is a deliberate trade-off – persistent WebSockets drain budget Android batteries within 4 hours.

3. **State Synchronization:** All three personas sync from the same backend state. Orders move through: PENDING_DISPATCH → ASSIGNED → PICKED_UP → DELIVERED. OTP verification is handled by the rider panel.

4. **Git Best Practices:** Always work on a branch, not `main`. Always check `git remote -v` before pushing. Start from the correct `main` when creating a PR.

### Time Spent

| Activity | Time |
|----------|------|
| Understanding code | 1.5 hours |
| Adding demo banner | 30 minutes |
| Fixing Git issues | 1 hour |
| Testing | 30 minutes |
| Writing documentation | 30 minutes |
| **Total** | **4 hours** |

### Key Takeaways

1. Git remotes matter – always check where you're pushing
2. Executive View is the best mode for live presentations
3. 4-second polling is a deliberate trade-off for battery life
4. The demo flow should be practiced until smooth
5. Always work on a branch, not directly on `main`

## Member 4: Frontend Styling and Theming

## Member 5: QA Testing and Technical Documentation

## Team-Level Adaptations

## Final Validation