# Trade-Off Log

Weak points we identified in our own build before the panel did, with the
reasoning for accepting each one and what we would change with more time.

## 1. No real concurrency control on assignment

**What it is.** `assign_order_to_rider()` rejects an order that is not in
`PENDING_DISPATCH`, which stops a second dispatcher from taking an order
that is already assigned. That check is not atomic. Two requests arriving
at the same instant can both read `PENDING_DISPATCH` before either writes,
and the second assignment overwrites the first. The guard is sequential,
not concurrent.

**Acceptable because.** The prototype runs single process against an
in-memory store, so there is no genuine parallel write path in the demo.
Adding real locking would have meant either a threading lock that only
holds inside one process, or moving to a database, neither of which
changes what the demo shows.

**With more time.** Move the state check and the write into one atomic
operation: a conditional update that only succeeds if the status is still
`PENDING_DISPATCH`, so the losing request fails rather than overwrites.

## 2. Customer OTP is readable through the order accessors

**What it is.** The OTP lives on the order record, so `get_all_orders()`
and `get_order_by_id()` return it, and it reaches the API response. The
code that proves a delivery happened is visible to anyone who can read
the order.

**Acceptable because.** The demo needs the OTP visible to show the
verification flow end to end, and the prototype has no authentication
layer to scope who may read an order. Removing it mid sprint would have
broken the API layer and the test suite, which both read it.

**With more time.** Strip `otp_code` from every read response and verify
it server side only, so the code never leaves the backend. The customer
would receive it out of band, by SMS.

## 3. All state is in memory and lost on restart

**What it is.** Orders, riders and the audit trail are Python
dictionaries. Restarting the server returns the system to seed state.

**Acceptable because.** The sprint is judged on design reasoning and a
live demo, not persistence. An in-memory store meant every teammate could
run the app with no database setup, which mattered more than durability
over five days.

**With more time.** Move to a real database. The data access layer is
already a single module with function boundaries, so the storage swap
would not reach into the API or frontend.

## 4. Order identifiers are randomly generated from a small range

**What it is.** Order ids are drawn at random from `ORD-503` to `ORD-999`,
a space of 497 values. The generator now retries on collision and refuses
to issue an id rather than overwrite a live order, but the space is still
small and the failure path is not handled by the API.

**Acceptable because.** The demo carries a handful of orders, so the
collision risk is negligible in practice. The retry guard closes the
silent data loss case, which was the part that actually mattered.

**With more time.** Use a sequential counter or a UUID, so ids are unique
by construction and the retry logic disappears.

## 5. Audit trail lives in the same store it describes

**What it is.** `_AUDIT_LOGS` is an ordinary list in the same module as
the orders. Entries are only ever appended by the data layer, but nothing
structurally prevents code from editing or removing them, so the trail is
append only by convention rather than by design.

**Acceptable because.** For a prototype the value of the trail is
demonstrating that every state change is captured, including failed OTP
attempts, and that holds regardless of storage. Tamper resistance is a
production concern that does not change what the demo proves.

**With more time.** Write audit entries to append only storage the
application cannot rewrite, so a delivery record can support a dispute
rather than merely describe one.

## 6. Status updates rely on polling rather than push

**What it is.** The frontend does not receive updates when an order
changes. It re-requests the current state every 4 seconds, so a
dispatcher or retailer sees a change up to one interval after it
happens, and every open browser issues repeated requests whether or not
anything has changed.

**Acceptable because.** Polling needs no persistent connection and no
extra infrastructure, and the lag is not perceptible at the scale of a
demo with a handful of orders. Websockets would have added connection
handling and reconnection logic for a responsiveness gain the panel
would not see.

**With more time.** Push updates over websockets or server sent events,
so a status change reaches every watching client immediately and idle
clients cost nothing.

## 7. Frontend is plain HTML, CSS and JavaScript

**What it is.** The interface is hand written with no framework, so
state lives in the DOM and in ad hoc JavaScript rather than in a single
managed store. Adding screens means adding more of the same by hand.

**Acceptable because.** The application has three persona views and a
small number of forms. A framework would have added a build step and a
learning cost for a team working across five days, without changing what
the interface does.

**With more time.** Move to a framework once the screen count grows,
so view state is managed in one place rather than being reconstructed
from the DOM.

## 8. No authentication or role enforcement

**What it is.** Nothing verifies who is calling the API. The retailer,
dispatcher and rider views are separated in the interface only, so any
caller can hit any endpoint and act as any persona. This is what makes
weak point 2 exploitable: without identity, there is no way to scope who
may read an order and see its OTP.

**Acceptable because.** The sprint was scoped to proving the delivery
workflow. Building login, sessions and role checks would have consumed
the time the workflow itself needed, and the demo runs as a trusted
single operator.

**With more time.** Add authentication and role based access, so a rider
can only act on their own assignments and only the customer receives the
OTP.

## 9. The OTP is never actually delivered to the customer

**What it is.** The system generates a verification code and checks it,
but has no channel to send it. In the demo the code is read from the
order record, which is not how it would reach a customer in reality.

**Acceptable because.** Integrating an SMS provider means credentials,
per message cost and an external dependency that can fail mid demo. The
verification logic is the part being proven, and it is complete and
tested independently of how the code travels.

**With more time.** Send the OTP by SMS when the order is created, so
the customer holds a code the rider has never seen, which is the
property that makes it proof of delivery rather than a shared secret.