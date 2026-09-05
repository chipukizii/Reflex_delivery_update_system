# Member 2 – Learning Journal
## Reflex Readiness Sprint

**Name:** [Your Name]
**Role:** Member 2 – Backend API Developer
**Date:** 26/08/2026

---

## What I Learned

### 1. Understanding the Backend API Architecture

The backend uses a **two-file separation of concerns**:

- `backend/db.py` (Member 1) handles all data and business logic
- `backend/app.py` (my file) acts as the **API Gateway** — receiving HTTP requests from the frontend and routing them to the correct logic in `db.py`

My file (`app.py`) is structured into **four persona-specific sections**:

```
app.py
├── App Bootstrap        → Flask setup, CORS, static folder config
├── Retailer Endpoints   → POST /api/orders, GET /api/orders, GET /api/orders/<id>/tracking
├── Dispatcher Endpoints → GET /api/dispatch/unassigned, POST /api/dispatch/assign
├── Rider Endpoints      → GET /api/riders/<id>/tasks, POST /api/riders/pickup, POST /api/riders/deliver
└── System Utilities     → POST /api/system/reset
```

Each group of endpoints serves exactly one persona, keeping the code clean and easy to navigate during live presentations.

---

### 2. How REST API Endpoints Work in Flask

I learned how to use **Flask decorators** to define REST routes. A decorator like `@app.route()` tells Flask which URL triggers which function:

```python
@app.route('/api/orders', methods=['POST'])
def create_delivery_request():
    data = request.get_json() or {}
    ...
    return jsonify({'success': True, 'order': order}), 201
```

Key things I understood:
- `methods=['GET']` means the route only responds to read requests
- `methods=['POST']` means the route accepts data submissions (creating orders, assigning riders)
- `jsonify()` converts a Python dictionary into a proper JSON HTTP response
- The number at the end (e.g. `201`) is the **HTTP status code** — `201` means "Created", `400` means "Bad Request", `404` means "Not Found"

---

### 3. Input Validation and Error Handling

One of the most important things I implemented was **field validation** before passing data to the database layer. If a retailer submits a form without a customer name or phone number, the API rejects it immediately with a clear error message:

```python
required_fields = ['customer_name', 'customer_phone', 'dropoff_address', 'item_desc']
for field in required_fields:
    if not data.get(field):
        return jsonify({'success': False, 'error': f"Missing required field: '{field}'"}), 400
```

This pattern taught me:
- **Never trust incoming data** — always validate before processing
- Return `400 Bad Request` for user/input errors
- Return `404 Not Found` when a requested resource doesn't exist
- Every response has a `success: True/False` flag so the frontend knows how to react

---

### 4. Connecting the API Layer to the Database Layer

My file (`app.py`) does **not** store any data itself. It delegates everything to `db.py` by calling its functions:

```python
# app.py calls db.py functions directly
success, msg, order = db.assign_order_to_rider(order_id, rider_id)
if not success:
    return jsonify({'success': False, 'error': msg}), 400
return jsonify({'success': True, 'message': msg, 'order': order})
```

This separation means:
- `app.py` only handles **HTTP concerns** (parsing requests, returning responses)
- `db.py` handles **business logic** (state transitions, OTP verification, concurrency guards)
- If the database rejects an assignment (e.g. order already assigned), `app.py` passes that error directly to the frontend as an HTTP 400

---

### 5. CORS and Why It Matters

I learned what **CORS (Cross-Origin Resource Sharing)** is and why we needed it:

```python
from flask_cors import CORS
CORS(app)
```

Without this single line, the browser would block all fetch requests from the frontend to the backend because they run on different "origins" (even on the same machine). Adding `CORS(app)` tells the browser: **"This server accepts requests from any origin"** — essential for our demo dashboard.

---

### 6. Serving the Frontend from the Backend

A key design choice I understood was how we serve the HTML dashboard **from within the Flask server**, eliminating the need for a separate web server:

```python
static_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')
)
app = Flask(__name__, static_folder=static_dir, static_url_path='/static')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')
```

This means visiting `http://127.0.0.1:5050` in a browser loads the full 3-column dashboard — no separate server or hosting needed during the demo.

---

### 7. The System Reset Endpoint (Demo Tool)

I built a special endpoint specifically for the live demo:

```python
@app.route('/api/system/reset', methods=['POST'])
def reset_system():
    db.reset_db()
    return jsonify({'success': True, 'message': 'System state reset to baseline seed data.'})
```

This allows us to **instantly wipe all orders and reset riders to AVAILABLE** between demo runs during the presentation — so if we need to run the demo a second time for the panel, one click restores everything to a clean starting state.

---

## Challenges Faced

### Challenge 1: Understanding How `app.py` and `db.py` Communicate

**Issue:** I initially tried to write database logic directly in `app.py`, duplicating what Member 1 had in `db.py`.

**Fix:** I re-read the separation of concerns in the README and understood that `app.py` should only call `db.py` functions — never duplicate them. I refactored my endpoints to import and call `db` directly.

**Learning:** In a layered architecture, each layer has one job. The API layer routes and validates; the data layer stores and enforces rules.

---

### Challenge 2: HTTP Status Codes — Which Code for Which Situation?

**Issue:** I initially returned `200 OK` for everything, including errors. This confused the frontend because it couldn't tell success from failure.

**Fix:** I studied the standard HTTP status code meanings and applied them correctly:
- `200 OK` → Successful read (GET)
- `201 Created` → Successful creation (POST order)
- `400 Bad Request` → Validation failure or invalid state transition
- `404 Not Found` → Order or rider ID doesn't exist in the system

**Learning:** HTTP status codes are part of the API contract. The frontend's fetch logic reads the status code to decide how to display results to the user.

---

### Challenge 3: The Duplicate Assignment Race Condition

**Issue:** I wondered what would happen if two dispatchers tried to assign the same order at exactly the same time through my `/api/dispatch/assign` endpoint.

**Investigation:** I traced the call to `db.assign_order_to_rider()` and found that Member 1's state machine guard handles it:

```python
# Inside db.py (Member 1's code)
if order["status"] != "PENDING_DISPATCH":
    return False, f"Order is already in state '{order['status']}'", None
```

My endpoint correctly passes this failure back as `HTTP 400`:

```python
success, msg, order = db.assign_order_to_rider(order_id, rider_id)
if not success:
    return jsonify({'success': False, 'error': msg}), 400
```

**Learning:** The API layer and the database layer work as a team. My job was to correctly surface the error that Member 1's code produced — not to solve concurrency myself.

---

### Challenge 4: Git Commit Scope

**Issue:** When I ran `git status`, I saw other members' files had also changed and I almost staged them all accidentally.

**Fix:** I staged only my file explicitly:
```bash
git add backend/app.py
git commit -m "feat(api): implement REST endpoints and error handlers - Member 2"
git push origin main
```

**Learning:** Always use `git add <specific-file>` instead of `git add .` when working in a shared repository with multiple members.

---

## Time Spent

| Activity | Time |
|:---|:---|
| Reading and understanding `db.py` (Member 1's layer) | 1 hour |
| Writing all 10 REST endpoints in `app.py` | 1.5 hours |
| Testing endpoints manually with browser / curl | 45 minutes |
| Debugging CORS and static file serving | 30 minutes |
| Fixing git staging issue | 15 minutes |
| Writing this journal | 30 minutes |
| **Total** | **4.5 hours** |

---

## Key Takeaways

1. **The API layer is the bridge** — it connects the frontend's HTTP calls to the backend's business logic without holding any logic of its own.
2. **HTTP status codes are part of the contract** — always return the correct code so the frontend can react correctly.
3. **Input validation at the API layer saves the database** — never let garbage data reach `db.py`.
4. **CORS must be enabled** for browser-to-server communication to work, even on localhost.
5. **`git add <file>` not `git add .`** — always stage only your assigned file in a shared team repo.
6. **The reset endpoint is a presentation superpower** — it lets the team run the live demo multiple times cleanly without restarting the server.

---

## API Endpoint Summary (What I Built)

| Endpoint | Method | Who Uses It | What It Does |
|:---|:---|:---|:---|
| `/` | GET | Everyone | Serves the dashboard HTML |
| `/api/orders` | GET | Retailer | Lists all orders (optional status filter) |
| `/api/orders` | POST | Retailer | Creates a new delivery request |
| `/api/orders/<id>/tracking` | GET | Retailer | Returns real-time status + audit trail |
| `/api/dispatch/unassigned` | GET | Dispatcher | Returns open orders + available riders |
| `/api/dispatch/assign` | POST | Dispatcher | Assigns a rider to an order |
| `/api/riders/<id>/tasks` | GET | Rider | Returns tasks assigned to a specific rider |
| `/api/riders/pickup` | POST | Rider | Confirms parcel pickup at the shop |
| `/api/riders/deliver` | POST | Rider | Submits customer OTP to complete delivery |
| `/api/system/reset` | POST | Demo Tool | Resets all data to clean seed state |

---

## Next Steps

- [ ] Practice explaining each endpoint to the panel in under 30 seconds
- [ ] Prepare defense for: *"Why Flask over Django or FastAPI?"*
- [ ] Review Trade-Off #1 (Manual Dispatch) to support Member 5's slides
- [ ] Rehearse the demo flow as Member 4 drives the live dashboard
- [ ] Prepare answer for: *"What happens if the backend crashes mid-delivery?"*
