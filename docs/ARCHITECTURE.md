# REFLEX Delivery Synchronization Platform

## Technical & Project Management Architecture

**Project:** REFLEX Delivery Synchronization Platform
**Sprint:** Readiness Sprint
**Architecture Style:** Modular Monolith
**Backend:** Python + Flask
**Frontend:** HTML, CSS, JavaScript
**Data Layer:** In-memory data store for MVP
**Communication:** REST API + HTTP polling
**Authentication/Proof:** Order-specific OTP verification


# 1. Architecture Overview

REFLEX is designed as a simple delivery synchronization platform that connects three users:

1. **Retailer Staff** – creates delivery orders.
2. **Dispatcher** – assigns available riders.
3. **Field Rider** – picks up and delivers orders using an OTP.

The main goal of the architecture is to keep **one source of truth for delivery status**.

The frontend displays information and sends requests, while the backend controls the delivery rules and status changes.

### Main delivery lifecycle

```text
PENDING_DISPATCH
        ↓
    ASSIGNED
        ↓
    PICKED_UP
        ↓
    DELIVERED
```

The backend prevents users from skipping or repeating invalid stages.

---

# 2. High-Level Technical Architecture

```text
┌───────────────────────────────┐
│           USERS               │
│                               │
│ Retailer | Dispatcher | Rider │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│          FRONTEND             │
│        HTML/CSS/JavaScript    │
│                               │
│ • Persona switching           │
│ • Order creation              │
│ • Dispatcher controls         │
│ • Rider delivery controls     │
│ • Status display              │
└───────────────┬───────────────┘
                │ HTTP/REST
                ▼
┌───────────────────────────────┐
│          FLASK API            │
│                               │
│ • Receives requests            │
│ • Validates input              │
│ • Calls business logic         │
│ • Returns JSON responses       │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       BUSINESS / STATE        │
│          ENGINE               │
│                               │
│ • Order lifecycle             │
│ • Rider assignment            │
│ • OTP verification            │
│ • Delivery validation         │
│ • Audit events                │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│          DATA LAYER           │
│                               │
│ Orders | Riders | Audit Logs  │
│        In-memory MVP          │
└───────────────────────────────┘
```

---

# 3. Technical Components

## 3.1 Frontend

The frontend is a lightweight web interface built with:

* HTML
* CSS
* JavaScript

It provides different views for the three REFLEX personas.

### Responsibilities

The frontend:

* displays available orders;
* allows retailer staff to create orders;
* allows dispatchers to assign riders;
* allows riders to update delivery progress;
* displays the current order status;
* sends requests to the Flask API;
* periodically requests updated state from the backend.

The frontend does **not** decide whether a delivery transition is valid.

That responsibility belongs to the backend.

---

## 3.2 Backend API

The backend uses **Flask** to expose REST API endpoints.

The API acts as the communication layer between the frontend and the business logic.

Examples of operations include:

```text
POST /api/orders
```

Creates a new delivery order.

```text
POST /api/riders/assign
```

Assigns an available rider to an order.

```text
POST /api/riders/pickup
```

Moves an assigned order to pickup.

```text
POST /api/riders/deliver
```

Verifies the OTP and completes the delivery.

The API returns JSON responses so that the frontend can update the interface.

---

# 4. Business Logic and State Management

The main business rules are kept in the backend data/state layer.

This is important because users should not be able to directly change an order from one status to another.

For example:

```text
PENDING_DISPATCH → DELIVERED
```

is not allowed.

The expected sequence is:

```text
PENDING_DISPATCH
        ↓
    ASSIGNED
        ↓
    PICKED_UP
        ↓
    DELIVERED
```

The backend checks the current status before allowing a transition.

### Example

If an order is already assigned, another assignment request is rejected.

If an order has not been picked up, it cannot be marked as delivered.

This makes the backend the **source of truth for delivery state**.

---

# 5. Rider Assignment

The dispatcher is responsible for assigning riders in the MVP.

The current approach is intentionally simple:

```text
New Order
    ↓
Dispatcher sees order
    ↓
Dispatcher selects available rider
    ↓
Backend validates assignment
    ↓
Order becomes ASSIGNED
```

This avoids introducing GPS tracking and routing complexity during the readiness sprint.

The architecture can later be extended with automated rider selection based on:

* GPS location;
* rider workload;
* delivery distance;
* estimated travel time.

---

# 6. Delivery Verification

REFLEX uses an OTP as the delivery confirmation mechanism.

The basic flow is:

```text
Order Created
      ↓
OTP Generated
      ↓
Rider Picks Up Order
      ↓
Customer Provides OTP
      ↓
Backend Verifies OTP
      ↓
Order Marked DELIVERED
```

An incorrect OTP is rejected.

The current MVP implements the OTP verification mechanism but does **not** include a production SMS provider.

A future version can connect the OTP generation process to an SMS service.

---

# 7. Data Architecture

The readiness sprint uses an **in-memory data store** rather than a production database.

The main data structures represent:

```text
Orders
Riders
Audit Events
```

This decision keeps the prototype small and easy to demonstrate within the sprint.

### Important limitation

Because the data is stored in memory, it is not suitable for production use.

Restarting the application can clear the current application state.

### Production direction

A production version should replace the in-memory layer with a persistent relational database such as PostgreSQL or MySQL.

---

# 8. Synchronization

The frontend periodically requests the latest delivery state from the backend.

The current MVP uses HTTP polling.

```text
Frontend
    │
    │ Request latest state
    ▼
Flask API
    │
    │ Current state
    ▼
Frontend
```

Polling was selected because it is easier to implement and understand for the readiness sprint.

A future version could use:

* Server-Sent Events (SSE);
* WebSockets;
* event-driven messaging.

These would be considered if real-time requirements increase.

---

# 9. Error and Edge-Case Handling

The backend validates important delivery actions.

Examples include:

| Situation                        | Expected Behaviour |
| -------------------------------- | ------------------ |
| Assign an already assigned order | Reject request     |
| Deliver before pickup            | Reject request     |
| Wrong OTP                        | Reject request     |
| Wrong rider attempts delivery    | Reject request     |
| Invalid order ID                 | Return error       |
| Invalid delivery transition      | Reject request     |

This prevents the frontend from creating inconsistent delivery states.

---

# 10. Audit Trail

REFLEX records important delivery events during the MVP.

Examples include:

```text
ORDER_CREATED
RIDER_ASSIGNED
ORDER_PICKED_UP
DELIVERY_COMPLETED
```

The audit trail helps demonstrate what happened during the delivery lifecycle.

For production, these records should be stored in a persistent database with stronger controls around integrity, retention, and access.

---

# 11. Security Considerations

The MVP focuses on the core delivery workflow rather than full production security.

Current protections include:

* backend validation of state transitions;
* OTP verification;
* rider/order validation;
* rejection of invalid actions;
* controlled API operations.

Production improvements would include:

* user authentication;
* role-based access control;
* HTTPS;
* secure OTP delivery;
* rate limiting;
* encrypted sensitive data;
* persistent audit logging.

---

# 12. Technical Trade-Offs

The team deliberately chose simplicity for the readiness sprint.

| Decision        | Chosen Approach                 | Reason                       |
| --------------- | ------------------------------- | ---------------------------- |
| Architecture    | Modular monolith                | Easier to build and explain  |
| Database        | In-memory                       | Fast MVP development         |
| Dispatch        | Manual                          | Avoid GPS/routing complexity |
| Delivery proof  | OTP                             | Simple and lightweight       |
| Synchronization | HTTP polling                    | Simple implementation        |
| Frontend        | Lightweight SPA-style interface | Low overhead                 |
| Backend         | Flask                           | Small and easy to develop    |

These decisions are appropriate for a **proof-of-approach MVP**, but some would need to change before production deployment.

---

# 13. Project Management Architecture

REFLEX was developed using an Agile Scrum approach.

The team worked as a small cross-functional pod with clearly divided responsibilities.

### Scrum structure

```text
Product Goal
     ↓
Sprint Planning
     ↓
Task Breakdown
     ↓
Parallel Development
     ↓
Integration
     ↓
Testing
     ↓
Demo
     ↓
Review / Retrospective
```

The focus of the sprint was not to build a complete production platform.

The goal was to demonstrate that the core delivery synchronization concept works.

---

# 14. Team Responsibilities

The project was divided into clear areas of ownership.

### Backend

Responsible for:

* API development;
* delivery state management;
* rider assignment;
* OTP verification;
* validation.

### Frontend

Responsible for:

* persona interfaces;
* order creation interface;
* dispatcher interface;
* rider interface;
* status display.

### Testing

Responsible for:

* testing valid workflows;
* testing invalid transitions;
* testing OTP rejection;
* testing rider/order validation.

### Documentation & Architecture

Responsible for:

* architecture documentation;
* trade-off decisions;
* project explanation;
* presentation preparation.

### Integration & Demo

Responsible for:

* connecting components;
* running the complete workflow;
* identifying integration issues;
* preparing the final demonstration.

---

# 15. Definition of Done

A feature is considered complete when:

* the code works;
* the API returns the expected response;
* invalid actions are handled;
* the feature is integrated with the rest of the system;
* relevant tests pass;
* documentation reflects the actual implementation.

This prevents the team from considering a feature complete simply because its code has been written.

---

# 16. Testing Strategy

Testing focuses on the most important business rules.

The test suite covers scenarios such as:

```text
Create order
      ↓
Assign rider
      ↓
Pickup order
      ↓
Verify OTP
      ↓
Complete delivery
```

It also tests failure scenarios such as:

```text
Wrong OTP
Duplicate assignment
Wrong rider
Invalid status transition
```

The purpose is to ensure that the delivery state cannot easily become inconsistent.

---

# 17. Current MVP Limitations

The current readiness-sprint prototype intentionally does not provide:

* production database persistence;
* GPS-based dispatch;
* offline order creation;
* production SMS integration;
* photo proof of delivery;
* production authentication;
* automated routing;
* horizontal scaling.

These are not hidden weaknesses. They are deliberate boundaries of the MVP.

---

# 18. Future Architecture

The system can evolve without completely rewriting the core business logic.

A possible production architecture is:

```text
                    ┌───────────────┐
                    │    Users      │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Web / Mobile  │
                    │   Clients     │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   API Layer   │
                    └───────┬───────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
        Order Service  Dispatch Service  Delivery
                                           Service
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                    ┌───────────────┐
                    │ PostgreSQL DB │
                    └───────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Notifications │
                    │ SMS / Events  │
                    └───────────────┘
```

Possible future capabilities include:

* persistent database storage;
* mobile applications;
* GPS-based dispatch;
* real-time updates;
* SMS integration;
* stronger authentication;
* analytics and reporting;
* automated routing.

---

# 19. Architecture Principles

The REFLEX architecture follows five simple principles:

### 1. Backend owns the state

The frontend displays and requests changes. The backend decides whether changes are allowed.

### 2. Keep the MVP small

Only functionality required to prove the core delivery workflow is included.

### 3. Validate at the source of truth

Important business rules are enforced in the backend rather than relying only on the interface.

### 4. Design for extension

The MVP is intentionally simple, but the major components can later be replaced or expanded.

### 5. Document the real system

Architecture documentation describes what is currently implemented and clearly separates it from future improvements.

---

# 20. Final Architecture Summary

REFLEX uses a **simple modular-monolith architecture** consisting of a lightweight frontend, Flask REST API, backend state-management logic, and an in-memory MVP data layer.

The architecture supports the complete core delivery lifecycle:

```text
CREATE
  ↓
ASSIGN
  ↓
PICK UP
  ↓
VERIFY OTP
  ↓
DELIVER
```

The project-management approach uses Agile Scrum to keep the sprint focused on a demonstrable proof of concept.

The key architectural decision is:

> **Keep the MVP simple enough to build and explain, while keeping the core business logic structured enough to evolve into a production system.**

