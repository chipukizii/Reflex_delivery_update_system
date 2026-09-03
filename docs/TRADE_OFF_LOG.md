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