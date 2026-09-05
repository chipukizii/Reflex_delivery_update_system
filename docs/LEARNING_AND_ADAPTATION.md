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

### Key Learning

The most useful thing I learned was that a passing test suite proves less than it appears to. Every one of my eight tests passed against an OTP generator that produced a literal string instead of a number, because the tests only checked that an OTP existed and then submitted that same value back to itself. Nothing asserted the shape of what was generated. I added a format assertion afterwards, but the lesson is that assertions have to test the property you actually care about, not the presence of a field.

Code review also changed my approach twice. It caught that I was generating a delivery verification code with random, which is predictable, when an OTP is a credential and belongs in secrets. And it caught that I was writing the OTP itself into the audit log, putting the credential in plaintext in a record any caller can read. Both were things I would not have found by testing, because neither breaks anything.

### Contribution Evidence

Implemented backend/db.py: in-memory store, seed reset, four-state order machine, guarded transitions, OTP generation and verification, audit logging. Wrote tests/test_reflex.py, eleven tests covering the lifecycle and the state guards. Authored docs/TRADE_OFF_LOG.md, nine entries, four of them co-authored with Member 5. Reviewed and merged Member 4's styling branch.

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

## Member 5: Technical Documentation

# REFLEX Delivery Synchronization Platform

## Personal Learning and Adaptation

My assigned responsibility in the REFLEX project was **project documentation**. My main task was to understand the system well enough to document its architecture, technical decisions, and limitations clearly.

### What I Learned

Through this responsibility, I learned how to:

* Read and understand an existing codebase.
* Translate technical implementation into simple documentation.
* Create and explain a system architecture.
* Document technical trade-offs and explain why decisions were made.
* Identify the difference between what the system currently does and what is planned for the future.
* Keep documentation consistent with the actual implementation.

### How I Adapted

Initially, I focused mainly on describing the system. As I reviewed the code, I learned that documentation must reflect **what is actually implemented**, not what we intended to build.

I therefore adapted the documentation by:

* Simplifying technical explanations.
* Correcting assumptions that were not supported by the code.
* Clearly separating current MVP features from future improvements.
* Making the architecture and trade-offs easier for a non-technical audience to understand.

### Key Lesson

> **Good documentation is not just describing a system; it is understanding the system well enough to explain it accurately and simply.**

### Initial Understanding

My responsibility was to handle the frontend styling and theming of the Reflex delivery synchronization platform. I understood that the interface needed to support the three main personas — retailer staff, dispatcher, and rider — while remaining clear, responsive, and easy to use on different screen sizes.

My main focus was `frontend/static/styles.css`, including the dashboard layout, dark/light themes, forms, buttons, order cards, status indicators, OTP banner, and the rider's mobile interface.

### Implementation Approach

I started by defining reusable CSS variables for the application's colours, backgrounds, borders, text, status states, OTP elements, and shadows. I created both dark-theme defaults and light-theme overrides so the interface could switch between themes consistently.

I then implemented the main three-column dashboard layout and added a single-view layout for individual personas. I styled the persona cards, headers, forms, inputs, select fields, and action buttons to create a consistent visual structure.

For delivery tracking, I added distinct status pills for `PENDING_DISPATCH`, `ASSIGNED`, `PICKED_UP`, and `DELIVERED`. This makes the current state of an order easier to identify at a glance.

I also implemented the OTP banner using a distinct background, dashed border, and monospace font. For the rider interface, I created a mobile phone frame effect to reflect the intended budget Android smartphone experience.

Finally, I added responsive CSS rules for tablet and mobile screen sizes. This allowed the three-column layout to collapse into a single-column layout on smaller screens and adjusted spacing, buttons, headers, and the rider frame accordingly.

### Adaptation and Learning

During implementation, I had to think beyond simply making the page look good and consider how the styling would work with the existing HTML structure and different personas. I learned the importance of using CSS variables and reusable classes because they make theme changes and future adjustments much easier.

I also learned how responsive design can be handled using CSS Grid and media queries rather than creating completely separate layouts for different devices.

### Testing and Validation

I reviewed the implemented CSS against the assigned styling requirements, checking that the required theme variables, dashboard grid, persona cards, forms, buttons, status badges, OTP banner, rider mobile frame, and responsive breakpoints were included.

I also resolved a CSS conflict when preparing my branch for the pull request by retaining my frontend styling changes while resolving the difference with the `main` branch.

## Member 5: QA Testing and Technical Documentation

## Team-Level Adaptations

## Final Validation
