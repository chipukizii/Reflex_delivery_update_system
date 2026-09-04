# Member 3 – Learning Journal
## Reflex Readiness Sprint

**Name:** Kelly Wanjiru
**Role:** Member 3 – Frontend Developer
**Date:** 26/08/2026

### What I Learned

#### 1. Understanding the Frontend Architecture
- The UI uses a Single Page Application (SPA) approach
- Three personas (Retailer, Dispatcher, Rider) share the same page
- View switching is controlled by `switchView()` function
- Executive View shows all three personas side-by-side for live demos

#### 2. HTTP Polling vs WebSockets
- Reflex uses 4-second polling to save battery on rider devices
- The `fetchState()` function pulls updates from the backend
- This is a deliberate trade-off (Trade-Off #3 in the design)
- Polling consumes under 5MB of data per 10-hour shift

#### 3. State Synchronization Flow
- All three personas sync from the same backend state
- Orders move through: PENDING_DISPATCH → ASSIGNED → PICKED_UP → DELIVERED
- OTP verification is handled by the rider panel
- The system uses concurrency guards to prevent double-assignment

#### 4. Live Demo Preparation
- The Executive Defense View shows all three personas simultaneously
- I added a demo instructions banner to guide the presentation flow
- The demo flow is: Log Delivery → Assign → Pickup → Deliver with OTP

### Challenges Faced

#### Challenge 1: Understanding the View Switcher Logic
- **Issue:** I didn't initially understand how `switchView()` controlled which panels were visible
- **Fix:** I traced through the code and saw how it toggles `display: none/block`
- **Learning:** `display: none` hides elements, `display: flex` shows them

#### Challenge 2: Git Remote Issues
- **Issue:** I pushed to the wrong repository (`git-test` instead of `reflex-delivery-system`)
- **Fix:** I changed the remote URL and created a clean branch from `main`
- **Learning:** Always check `git remote -v` before pushing

#### Challenge 3: Creating a Pull Request
- **Issue:** "entirely different commit histories" error
- **Fix:** Created a fresh branch from the correct `main`
- **Learning:** Always start from the correct `main` when creating a PR

### Time Spent

| Activity | Time |
|----------|------|
| Understanding code | 1.5 hours |
| Adding demo banner | 30 minutes |
| Fixing Git issues | 1 hour |
| Testing | 30 minutes |
| Writing journal | 30 minutes |
| **Total** | **4 hours** |

### Key Takeaways
1. Git remotes matter – always check where you're pushing
2. Executive View is the best mode for live presentations
3. 4-second polling is a deliberate trade-off for battery life
4. The demo flow should be practiced until smooth

### Next Steps
- Practice the live demo script
- Prepare for cross-examination questions
- Review trade-off log for defense preparation