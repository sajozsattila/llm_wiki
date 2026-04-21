### In-memory wiki graph

#### The problem it solves

Every time the agent finishes reading a page and needs to decide where to go next,
the current `nav_router` runs this:

```python
for slug in state["visited"]:    # e.g. ["index", "allianz-cegem", "cegem-csomagok"]
    page_text = _read_page(slug) # reads the file from disk — AGAIN
    for link in _extract_links(page_text):
        ...
```

If 5 pages have been visited, it re-reads all 5 files from disk just to get their
links — information it already had the first time it read those pages. On the next
hop it reads them again. **The links don't change between hops.** This is pure waste.

With `MAX_PAGES_PER_QUESTION = 8`, this adds up to:

| Hop | Pages re-read |
|-----|--------------|
| 1st | 1 |
| 2nd | 2 |
| 3rd | 3 |
| ... | ... |
| 7th | 7 |
| **Total** | **up to 28 redundant disk reads per question** |

#### The solution

Build the full adjacency structure **once at startup**, before any question is processed:

```
WikiGraph
├── nodes: dict[slug → PageMeta]          # slug, title, one-line description
├── out_edges: dict[slug → set[slug]]     # wikilinks from each page
└── in_edges: dict[slug → set[slug]]      # reverse index: who links to this page
```

`PageMeta` is extracted once from each page (title line + **Összefoglalás** field).
After that, the router becomes a single set operation — no disk reads at all:

```python
# Before: re-read every visited page on every hop
# After: pure set arithmetic, zero I/O
frontier = set().union(*[out_edges[s] for s in visited]) - visited_set
```

```
WikiGraph construction (once, O(n pages)):

  for each slug in wiki/:
    read page → extract title, summary, outbound [[links]]
    store in nodes, out_edges, in_edges
```

#### Where it is used

The in-memory graph is used in three places:

**1. Router (main benefit)** — frontier computation becomes a set operation instead
of re-reading files. The graph knows the structure; the LLM decides the direction.

**2. Entry node** — instead of sending the raw text of `index.md` to the LLM, send
`PageMeta` summaries for the most relevant nodes. Smaller, more focused prompt.

**3. Frontier ranking** — `in_edges` lets you count how many pages point to each
candidate (in-degree). Pages with high in-degree are the hubs of the wiki and are
probably more relevant than obscure leaf pages. Ranking before the LLM sees the
frontier means the LLM receives the 6 best candidates instead of 12 random ones.

#### What it does not solve

With ~35 pages the wall-clock difference is not dramatic. The real value is
**correctness and separation of concerns**: the graph makes the navigation model

### Scoring candidates for the LLM

Before the LLM picks the next hops, pre-score each frontier node:

| Signal | How | Cost |
|---|---|---|
| In-degree (centrality) | Count entries in `in_edges[slug]` | Free (computed at build time) |
| Keyword overlap | Count question terms appearing in `PageMeta.summary` | O(words) |
| Hop distance | Prefer 1-hop neighbors over 2-hop | Free from graph |

The LLM receives the top 6 candidates (vs. 12 today), ranked, with summaries.
Smaller, better-ordered prompt → more reliable navigation decisions.

explicit in code, unlocks reverse-edge traversal (in-degree ranking), and cleanly
separates what the graph knows (structure) from what the LLM decides (direction).
