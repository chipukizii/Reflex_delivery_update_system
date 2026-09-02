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

### Challenge Encountered
### Adaptation Made
### Testing and Validation
### Key Learning
### Contribution Evidence

## Member 2: Backend API and Integration

## Member 3: Frontend UI and Interaction

## Member 4: Frontend Styling and Theming

## Member 5: QA Testing and Technical Documentation

## Team-Level Adaptations

## Final Validation