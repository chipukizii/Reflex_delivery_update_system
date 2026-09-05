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

## Member 4: Frontend Styling and Theming

## Member 5: QA Testing and Technical Documentation

## Team-Level Adaptations

## Final Validation