# Skill: Wiki Query

## Goal

Answer user queries using the wiki with **minimal latency and token usage**, while maintaining correctness.

---

## Core Strategy

Shift work from query-time → precomputed knowledge.

Priority order:

1. Precomputed answers (fastest)
2. Summaries (cheap routing)
3. Full pages (expensive, limited)

---

## Hard Constraints

* MAX pages to fully load: **3**
* MAX traversal depth: **2**
* Prefer summaries over full content
* NEVER scan entire wiki

---

## Step 0 — Normalize Query

* Extract intent
* Identify key entities / concepts
* Generate 3–5 search keywords

---

## Step 1 — Check Answer Cache (FAQ Layer)

Search in:
`/wiki/answers/`

If a matching or similar question exists:

* Return the precomputed answer
* Verify relevance quickly
* STOP

---

## Step 2 — Fast Routing (Cheap Pass)

Search ONLY:

* Frontmatter
* `## Retrieval Summary`
* `_index.md` (if exists)

Do NOT read full pages.

Select:

* Top **2–4 candidate pages**

Selection criteria:

* Keyword match
* Tag match
* High `confidence`
* Low `stale`
* High `centrality` (if available)

---

## Step 3 — Shallow Read (Lazy Expansion)

From selected pages, read ONLY:

* TL;DR
* Key Points
* Relationships

Do NOT read full page yet.

If answer is sufficient:

* Generate response
* STOP

---

## Step 4 — Deep Read (Limited)

If needed:

* Load FULL content of max **3 pages**

Prioritize:

1. Highest relevance
2. Highest confidence
3. Most connected pages

Optional:

* Follow links (`[[...]]`) but ONLY one hop

---

## Step 5 — Synthesize Answer

* Combine information from selected pages
* Prefer consistency over completeness
* Resolve minor conflicts if possible

---

## Step 6 — Handle Gaps

If information is missing:

* Say: "Not in wiki"
* Suggest ingestion:

  * New page
  * Update existing page

---

## Step 7 — Optional Cache Write

If:

* Query is likely to repeat
* Answer required multi-step reasoning

Then:

* Create a new file in `/wiki/answers/`

Include:

* Question
* Answer
* Source pages

---

## Output Rules

* Be concise
* Reference page names (e.g. [[LLM Wiki]])
* Do NOT hallucinate
* Prefer structured answers

---

## Performance Heuristics

* Prefer 2 good pages over 5 mediocre ones
* Avoid deep traversal chains
* Avoid loading large pages unless necessary
* Stop early when confidence is sufficient

---

## Failure Modes to Avoid

* Reading entire wiki
* Loading too many pages
* Ignoring cached answers
* Over-traversing links
* Recomputing known answers

---

## Mental Model

You are not searching documents.

You are:
→ routing a query through a **precomputed knowledge graph**

Goal:
→ find the shortest path to an answer
