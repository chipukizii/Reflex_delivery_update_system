# Timing Log

Timings from two full rehearsals of the 10-minute presentation plus
10-minute cross-examination.

## Slide ownership

Fixed across both runs. Whoever owns a slide takes the first question
on it.

| Section | Owner |
|---|---|
| Slide 1, Problem | Veronica |
| Slide 2, Solution | Chipukizii, team lead |
| Slide 3, Architecture | Member 5, Grace |
| Live demo | Member 1, Alex |
| Slide 4, Trade-offs | Member 1, Alex |
| Slide 5, Roadmap | Member 3, Kelly |

---

## Dry Run 1

**Date:** 05/09/2026  
**Present:** Veronica, Chipukizii, Grace, Alex, Kelly, Gilton  
**Total presentation time:** 11:08 (Target: 10:00)

| Section | Owner | Start | End | Duration |
|---|---|---|---|---|
| Slide 1, Problem | Veronica | 12:16:00 | 12:17:48 | 01:47.61 |
| Slide 2, Solution | Chipukizii, team lead | 12:32:00 | 12:34:10 | 02:10.01 |
| Slide 3, Architecture | Member 5, Grace | 12:26:00 | 12:28:17 | 02:17.11 |
| Live demo | Member 1, Alex | 12:44:00 | 12:46:15 | 02:14.67 |
| Slide 4, Trade-offs | Member 1, Alex | 12:46:15 | 12:47:23 | 01:08.00 |
| Slide 5, Roadmap | Member 3, Kelly | 13:08:00 | 13:09:31 | 01:30.97 |
| Cross-examination | all | 13:10:00 | 13:20:00 | 10:00 |

*(Note: Alex total speaking time across Live Demo and Slide 4 Trade-offs was 03:22.67)*

**What went wrong:**

- Total presentation time ran long by 1:08 (11:08 total vs 10:00 target).
- Slide 2 and Slide 3 both exceeded 2 minutes; need crisper transitions and focus on key takeaways.
- Live demo had a slight pause during rider selection before pickup; need pre-selected flow.
- Screen share handoff between Grace (Slide 3) and Alex (Live demo) took about 30 seconds to coordinate.

**Fixed before run 2:**

- Trimmed Slide 2 explanation of WhatsApp pain points to keep under 1:30.
- Streamlined Slide 3 architecture overview to emphasize low-bandwidth 4s polling trade-off in 1:45.
- Rehearsed smooth single-click demo flow (Log → Assign → Pickup → OTP verify).

---

## Dry Run 2

**Date:** 05/09/2026  
**Present:** Veronica, Chipukizii, Grace, Alex, Kelly, Gilton  
**Total presentation time:** 09:40 (Target: 10:00)

| Section | Owner | Start | End | Duration |
|---|---|---|---|---|
| Slide 1, Problem | Veronica | 13:30:00 | 13:31:30 | 01:30 |
| Slide 2, Solution | Chipukizii, team lead | 13:31:30 | 13:33:10 | 01:40 |
| Slide 3, Architecture | Member 5, Grace | 13:33:10 | 13:35:00 | 01:50 |
| Live demo | Member 1, Alex | 13:35:00 | 13:37:00 | 02:00 |
| Slide 4, Trade-offs | Member 1, Alex | 13:37:00 | 13:38:15 | 01:15 |
| Slide 5, Roadmap | Member 3, Kelly | 13:38:15 | 13:39:40 | 01:25 |
| Cross-examination | all | 13:40:00 | 13:50:00 | 10:00 |

**What went wrong:**

- Minor verbal slip on OTP challenge explanation during the cross-examination response.
- Presenter spoke slightly fast on Slide 5 Roadmap to stay within time.

**Still outstanding going into the panel:**

- Ensure live demo server is running and pre-reset on `http://127.0.0.1:5050` before walking into the defense.
- Maintain steady conversational pacing during Slide 5 and Q&A.

---

## Comparison

| Metric | Run 1 | Run 2 | Change |
|---|---|---|---|
| Total time | 11:08 | 09:40 | -1:28 (Passed target) |
| Longest section | Alex (Demo + Trade-offs: 03:23) | Alex (Demo: 02:00) | -1:23 |
| Demo segment | 02:15 | 02:00 | -0:15 |
| Screen share handoff | ~30s | ~10s | -20s |

**What changed between runs:** Tightened individual speaker durations by focusing on the "one key takeaway per slide" rule. Pre-tested the demo click sequence to prevent stalling, bringing total rehearsal time safely under the 10-minute ceiling at 9:40.

---

## Cross-examination questions asked

| Question | Category | Asked by | Answered by | Outcome |
|---|---|---|---|---|
| Why 4-second HTTP polling instead of WebSockets? | Architecture | Panel | Grace | Strong |
| What is the operational cost of manual dispatch over GPS? | Trade-offs | Panel | Alex | Strong |
| What happens if a dispatcher assigns a busy rider? | Edge cases | Panel | Gilton / Chipukizii | Strong (Guarded with HTTP 400) |
| How do you handle offline drop-offs in basements? | Candour | Panel | Veronica / Kelly | Strong (Admitted constraint & explained SMS OTP) |

**Weakest answers, to prepare before the panel:**

- *Question:* "What happens if the customer voluntarily shares their OTP over the phone before the rider arrives?"
  *Better Answer:* Acknowledge candidly that OTP proves possession of code at drop-off; customer-rider collusion is mitigated in Phase 2 via progressive photo downsampling proof of delivery.
