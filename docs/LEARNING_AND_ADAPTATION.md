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

## Member 4: Frontend Styling and Theming

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
