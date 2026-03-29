# Interviewer Grading Rubric

**For internal use only — do not share with candidates.**

---

## Seniority Benchmarks

Use this to calibrate your hiring decision after reviewing the candidate's PR.

---

## Scoring

Each category is scored 0–3. Total max = **21 points**.

| Score | Meaning |
|---|---|
| 3 | Excellent — exceeds expectations, shows depth |
| 2 | Good — meets expectations, correct and clear |
| 1 | Partial — attempted but incomplete or shallow |
| 0 | Missing or fundamentally wrong |

---

## Category 1 — Bug Fixes (max 9 pts, 3 per sub-group)

### Backend Bugs (B1–B4) — max 3 pts

| Score | What the candidate did |
|---|---|
| 3 | Found all 4. Explained root causes with math/spec/docs. Fixed B3 correctly end-to-end (async def + await in callers). Called out B4 as a spec violation AND a security risk. |
| 2 | Found 3–4. Fixed them correctly but explanations were shallow (e.g. "used wrong key" without checking the API docs). B3 fix swapped libraries but didn't explain the event loop. |
| 1 | Found 2–3. Missed B3 or described it as "just use httpx". Missed B4 entirely or treated it as a preference, not a security issue. |
| 0 | Found 1 or fewer. Did not fix the KeyError (B2) which is the most visible crash. |

**Key signals:**
- B3 is the senior filter — understanding that `requests.get()` in an `async def` blocks the event loop separates mid from senior
- B4 is the security filter — a candidate who doesn't know CORS spec has gaps in web fundamentals
- B1 is the reasoning filter — can they derive the correct formula from first principles?

---

### Frontend Bugs (B5–B8) — max 3 pts

| Score | What the candidate did |
|---|---|
| 3 | Found all 4. B5 fix follows the same pattern as `PortfolioSummary.tsx` (or better). B6 explanation covers closure semantics and why the dep array matters. Both instances of B7 fixed. |
| 2 | Found 3–4. B6 was fixed (dep array) but explanation was "React told me to add it" without understanding why. B5 fetch works but missing error or loading state. |
| 1 | Found 2–3. Fixed visual bugs (B7, B8) but missed B5 or B6. Or: fixed B5 but the fetch has no error handling. |
| 0 | Only found B7/B8 (the obvious visual ones). Did not fix B5 or B6. |

**Key signals:**
- B6 (stale closure) is the React depth filter — a senior knows *why* the dep array exists, not just that eslint complained
- B5 with proper loading/error/finally is a professionalism signal
- Missing B8 (CSS) after fixing B5 suggests they didn't test the UI end-to-end

---

### PR Communication for Bugs — max 3 pts

| Score | What the candidate wrote |
|---|---|
| 3 | Each bug has: file + line + root cause + fix + why the fix is correct. Reads like a production incident writeup. |
| 2 | Most bugs documented but some are shallow ("changed X to Y" without explaining why Y is correct). |
| 1 | List of changes without root causes. Reads like a changelog, not an explanation. |
| 0 | No PR description or just "fixed bugs". |

---

## Category 2 — Flaky Tests (max 3 pts)

| Score | What the candidate did |
|---|---|
| 3 | Correctly identified all 3 flaky tests and their root causes. Test 1: `time.sleep()` blocks event loop + threshold too tight. Test 2: ratio is env-sensitive. Test 3: recognized it's NOT flaky now but becomes flaky when a naive cache is added. Fixed all without weakening assertions. |
| 2 | Fixed Test 1 and Test 2. Didn't notice Test 3 or just ran it and said "this one passed". |
| 1 | Ran tests, said "these are flaky", widened all thresholds or added `pytest.mark.skip`. Weakened the assertions. |
| 0 | Did not run the tests. Or: deleted the test file. |

**Key signals:**
- Test 3 insight (it surfaces race conditions in a naive cache) is the strongest senior signal in the entire challenge — it requires connecting the code review concern (rate limiting) to the test suite
- Widening all thresholds = junior instinct. Fixing the root cause = senior instinct.

---

## Category 3 — New Feature: Search Bar (max 3 pts)

| Score | What the candidate built |
|---|---|
| 3 | Case-insensitive search by name and symbol. Empty state. No extra state (filter is derived, not stored). Works with both mock and real data. Styled to match. Clean, minimal code. |
| 2 | Works correctly but minor issues: case-sensitive, no empty state, or a separate `filteredCoins` state that's kept in sync with `setCoins` (unnecessary). |
| 1 | Partially works — filters by name only, or has a bug with special characters, or breaks when API data loads. |
| 0 | Not implemented or non-functional. |

**Key signals:**
- Storing `filteredCoins` as state (instead of deriving it) is a React anti-pattern — reveals whether the candidate thinks in derived state
- UX details (empty state, placeholder text, clearing) show product thinking

---

## Category 4 — Code Review (max 3 pts)

| Score | What the candidate raised |
|---|---|
| 3 | At least 3 real production concerns beyond the 8 bugs. Examples: no rate limiting on CoinGecko calls, `requests` still in requirements.txt, no error boundary in React, `--reload` in Dockerfile (dev-only flag), no retry logic, no input validation on API endpoints, portfolio holdings are hardcoded with no persistence. |
| 2 | 2 real concerns, or 3 concerns but one is just restating a known bug. |
| 1 | Only restates the 8 bugs. No original observations. |
| 0 | No code review section. |

**Key signals:**
- Rate limiting concern = backend architecture awareness
- Error boundary concern = React production awareness
- `--reload` in Dockerfile = DevOps / deployment awareness
- These are the "5+ years" signals — juniors fix what's broken, seniors see what's missing

---

## Total Score → Seniority Level

| Total | Level | Hiring signal |
|---|---|---|
| 19–21 | **Staff / Senior+** | Exceptional. Hire fast, don't let them wait. |
| 15–18 | **Senior** | Strong hire. Knows the why, not just the what. |
| 11–14 | **Mid-Senior** | Solid hire. Gaps in depth but good instincts. Discuss in debrief. |
| 7–10 | **Mid-level** | Borderline. Good at following patterns, weak on first principles. |
| 4–6 | **Junior** | Found the easy bugs, missed the hard ones. Not ready for senior role. |
| 0–3 | **No hire** | Did not engage with the challenge meaningfully. |

---

## Live Debrief Questions

Use these to pressure-test the PR. A candidate who can't answer these for their own fixes is likely copy-pasting.

**On B3 (async):**
- "What actually happens to other requests while `requests.get()` is running?"
- "What's the difference between `run_in_executor` and using `httpx`?"
- "If you had 100 concurrent users, what would the latency look like before and after your fix?"

**On B4 (CORS):**
- "Why does the browser reject wildcard + credentials specifically?"
- "Does this bug affect requests from `localhost:5173`? Why or why not?"
- "How would you configure this for production with multiple frontend origins?"

**On B6 (useEffect):**
- "Walk me through what happens when the user changes the dropdown to 5s."
- "Why does adding `refreshInterval` to the dep array fix it?"
- "What would `useCallback` change here, if anything?"

**On flaky tests:**
- "What's the difference between `time.sleep()` and `asyncio.sleep()` in an async context?"
- "Why is a ratio assertion unreliable across environments?"
- "When would Test 3 actually fail? Can you write code that would cause it to fail?"

**On code review:**
- "You mentioned rate limiting. How would you implement a server-side cache for this?"
- "What happens if CoinGecko is down for 5 minutes? How would you handle that?"
