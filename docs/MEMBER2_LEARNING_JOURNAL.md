# Member 2 – Learning Journal
## Reflex Readiness Sprint

**Name:** Gilton Koech
**Role:** Member 2 – Backend API Developer
**Date:** 26/08/2026

---

## What I Learned

### 1. Understanding the Role of the API Layer

My job as Member 2 was to build the **API Gateway** — the bridge between the frontend dashboard and the backend logic. All communication between the browser and the server passes through my file, `backend/app.py`.

I structured `app.py` into four clear sections:

```
app.py
├── App Bootstrap        → Flask setup, CORS, static folder config
├── Retailer Endpoints   → POST /api/orders, GET /api/orders, GET /api/orders/<id>/tracking
├── Dispatcher Endpoints → GET /api/dispatch/unassigned, POST /api/dispatch/assign
├── Rider Endpoints      → GET /api/riders/<id>/tasks, POST /api/riders/pickup, POST /api/riders/deliver
└── System Utilities     → POST /api/system/reset
```

Each section maps to exactly one persona, making the code clean and easy to walk through during the live presentation.

---

### 2. How Flask Routes Work

I learned how to use **Flask decorators** to define REST endpoints. A decorator like `@app.route()` registers a URL and the HTTP method it responds to:

```python
@app.route('/api/orders', methods=['POST'])
def create_delivery_request():
    data = request.get_json() or {}
    ...
    return jsonify({'success': True, 'order': order}), 201
```

Key things I understood:
- `methods=['GET']` — route only responds to read requests (fetching data)
- `methods=['POST']` — route accepts submitted data (creating orders, assigning riders)
- `jsonify()` — converts a Python dictionary into a proper JSON HTTP response
- The number at the end (e.g. `201`) is the **HTTP status code** — `201` means "Created", `400` means "Bad Request", `404` means "Not Found"

---

### 3. Input Validation and Error Handling

One of the most critical things I built was **field validation** before passing data further. If a retailer submits a form without a customer name or address, my endpoint rejects it immediately with a clear error:

```python
required_fields = ['customer_name', 'customer_phone', 'dropoff_address', 'item_desc']
for field in required_fields:
    if not data.get(field):
        return jsonify({'success': False, 'error': f"Missing required field: '{field}'"}), 400
```

This pattern taught me:
- **Never trust incoming data** — always validate before processing
- Return `400 Bad Request` for missing or invalid input
- Return `404 Not Found` when a resource (order or rider) doesn't exist
- Every response includes a `success: True/False` field so the frontend knows how to react

---

### 4. Handling Three Different Personas Through One Server

A key insight I gained was that a single Flask server can serve multiple types of users through different endpoint groups. My API handles three completely different personas — each through their own set of routes:

**Retailer** (shop counter tablet):
```python
@app.route('/api/orders', methods=['GET'])      # View all orders
@app.route('/api/orders', methods=['POST'])     # Log a new delivery
@app.route('/api/orders/<order_id>/tracking')   # Track a specific order
```

**Dispatcher** (control cockpit):
```python
@app.route('/api/dispatch/unassigned', methods=['GET'])  # View open queue
@app.route('/api/dispatch/assign', methods=['POST'])     # Assign rider to order
```

**Rider** (budget Android phone):
```python
@app.route('/api/riders/<rider_id>/tasks', methods=['GET'])  # View my tasks
@app.route('/api/riders/pickup', methods=['POST'])           # Confirm pickup
@app.route('/api/riders/deliver', methods=['POST'])          # Submit OTP to deliver
```

---

### 5. CORS and Why It Is Essential

I learned what **CORS (Cross-Origin Resource Sharing)** is and why we needed it:

```python
from flask_cors import CORS
CORS(app)
```

Without this one line, the browser blocks all `fetch()` requests from the frontend to the backend — even when both run on the same machine — because they operate on different origins. Adding `CORS(app)` tells the browser: *"This server accepts requests from any origin."* This is essential for the demo dashboard to communicate with the Flask server.

---

### 6. Serving the Frontend From Within Flask

A key architectural choice I implemented was serving the HTML dashboard **directly from the Flask server**, so the team only runs one process during the presentation:

```python
static_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')
)
app = Flask(__name__, static_folder=static_dir, static_url_path='/static')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')
```

Visiting `http://127.0.0.1:5050` now loads the full 3-column dashboard — no separate web server or hosting needed during the live demo.

---

### 7. The Demo Reset Endpoint

I built a special utility endpoint specifically for the live presentation:

```python
@app.route('/api/system/reset', methods=['POST'])
def reset_system():
    db.reset_db()
    return jsonify({'success': True, 'message': 'System state reset to baseline seed data.'})
```

This allows the team to **instantly wipe all orders and reset riders back to AVAILABLE** with one click between demo runs. If the panel asks us to run the demo again, we press Reset and start fresh without restarting the server.

---

## Challenges Faced

### Challenge 1: Not Knowing Which HTTP Status Code to Return

**Issue:** I initially returned `200 OK` for everything, including error responses. This confused the frontend because it could not tell success from failure.

**Fix:** I researched standard HTTP status code meanings and applied them correctly:
- `200 OK` → Successful read
- `201 Created` → New order successfully created
- `400 Bad Request` → Missing fields or invalid input
- `404 Not Found` → Order or rider ID does not exist

**Learning:** HTTP status codes are part of the API contract. The frontend's `fetch()` logic reads the status code to decide what to display to the user.

---

### Challenge 2: Understanding the Assignment Error Response

**Issue:** I was unsure what to do when the dispatcher tried to assign an order that was already assigned. I did not know whether to handle this in `app.py` or whether the system handled it automatically.

**Investigation:** I traced the request flow and saw that the assignment logic returns a `success=False` flag along with an error message when the order is in the wrong state. My endpoint correctly surfaces this back to the frontend:

```python
success, msg, order = db.assign_order_to_rider(order_id, rider_id)
if not success:
    return jsonify({'success': False, 'error': msg}), 400
```

**Learning:** The API layer's job is to pass errors up correctly — not to solve business logic itself. Returning the right HTTP code and error message is what matters.

---

### Challenge 3: The Rider ID Casing Bug

**Issue:** During testing, fetching tasks for rider `rdr-01` returned zero results even though rider `RDR-01` had active orders assigned.

**Fix:** I found that the rider ID comparison in the tasks endpoint was case-sensitive. I added `.upper()` to normalize the incoming rider ID:

```python
assigned_orders = [
    o for o in all_orders
    if o.get('assigned_rider_id') == rider_id.upper()
]
```

**Learning:** Always normalize string inputs before comparing them. A lowercase `rdr-01` from the URL and an uppercase `RDR-01` in the data store are not equal in Python.

---

### Challenge 4: Staging Only My File in Git

**Issue:** When I ran `git status`, I saw other members' files listed as modified and almost staged them all by accident using `git add .`

**Fix:** I staged only my assigned file explicitly:

```bash
git add backend/app.py
git commit -m "feat(api): implement REST endpoints and error handlers - Member 2"
git push origin main
```

**Learning:** Always use `git add <specific-file>` in a shared team repository. `git add .` stages every changed file regardless of ownership, which breaks other members' work.

---

## Time Spent

| Activity | Time |
|:---|:---|
| Understanding the API layer's role | 1 hour |
| Writing all 10 REST endpoints in `app.py` | 1.5 hours |
| Manually testing endpoints with the browser | 45 minutes |
| Debugging CORS and static file path | 30 minutes |
| Fixing the rider ID casing bug | 20 minutes |
| Fixing git staging issue | 15 minutes |
| Writing this journal | 30 minutes |
| **Total** | **4 hours 50 minutes** |

---

## Key Takeaways

1. **The API layer is a bridge** — it routes and validates HTTP requests; it does not hold business logic.
2. **HTTP status codes are part of the contract** — always return the correct code so the frontend can react appropriately.
3. **Input validation at the API layer is non-negotiable** — never let incomplete or malformed data pass through.
4. **CORS must be enabled** for browser-to-server communication to work, even on localhost.
5. **Normalize string inputs** — `rdr-01` and `RDR-01` are different strings in Python; always call `.upper()` or `.lower()` before comparing IDs.
6. **`git add <file>` not `git add .`** — always stage only your assigned file in a shared team repository.
7. **The reset endpoint is a presentation tool** — it lets the team run the live demo multiple times cleanly without restarting the server.

---

## API Endpoint Summary (What I Built)

| Endpoint | Method | Persona | What It Does |
|:---|:---|:---|:---|
| `/` | GET | Everyone | Serves the live dashboard HTML |
| `/api/orders` | GET | Retailer | Lists all orders with optional status filter |
| `/api/orders` | POST | Retailer | Creates a new delivery request |
| `/api/orders/<id>/tracking` | GET | Retailer | Returns real-time order status and audit trail |
| `/api/dispatch/unassigned` | GET | Dispatcher | Returns open orders and available riders |
| `/api/dispatch/assign` | POST | Dispatcher | Assigns a rider to a specific order |
| `/api/riders/<id>/tasks` | GET | Rider | Returns tasks assigned to a specific rider |
| `/api/riders/pickup` | POST | Rider | Confirms parcel pickup at the shop |
| `/api/riders/deliver` | POST | Rider | Submits customer OTP to complete delivery |
| `/api/system/reset` | POST | Demo Tool | Resets all data to clean seed state |

---

## Next Steps

- [ ] Practice explaining each endpoint to the panel in under 30 seconds
- [ ] Prepare defense for: *"Why Flask over Django or FastAPI?"*
- [ ] Rehearse the demo flow while Member 4 drives the live dashboard
- [ ] Prepare answer for: *"What happens if the backend crashes mid-delivery?"*
- [ ] Review Trade-Off log to support Member 5's architecture slides
