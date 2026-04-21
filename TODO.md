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

### Two-tier wiki: concept pages and chunk pages

#### The problem with the current raw fallback

Right now the wiki has two disconnected layers:

```
Concept pages  (wiki/*.md)    ← agent navigates these
Raw files      (raw/*.md)     ← agent only touches these in the RAW_FALLBACK node
```

`RAW_FALLBACK` is a hack to bridge this gap: when the concept pages don't contain
enough detail, the agent switches to a completely different mechanism — extracting
headings from raw files, asking the LLM which sections are relevant, then reading
those sections. This is fragile and hard to maintain.

#### The solution: chunks as first-class wiki pages

Segment every raw source document by its Markdown heading hierarchy. Each segment
becomes a **chunk page** — a normal wiki page that the agent navigates to like any
other, but whose content is the raw source text rather than a human- or
Claude-written summary.

```
Concept pages  (wiki/*.md)       ← agent navigates these
Chunk pages    (wiki/*.md)       ← agent navigates these too
```

The graph becomes fully connected. `RAW_FALLBACK` is no longer needed.

#### Chunk page format

Each chunk page is a leaf node — it has content but links only back to its parent
document summary page:

```markdown
# FABF v8 – 12.3. pont: Szankciók

**Összefoglalás**: A FABF v8 feltételek szankciókra vonatkozó rendelkezései.
**Forrás dokumentum**: AHE_43501_8_FABF_FINAL.md
**chunk_id**: 47
**Típus**: forrás-szegmens
**Utolsó frissítés**: 2026-04-21

---

[raw section text here]

## Kapcsolodó oldalak
- [[ahe-43501-8-fabf]]
```

Naming convention: `<document-slug>-chunk-<zero-padded-id>.md`
e.g. `ahe-43501-8-fabf-chunk-047.md`

#### Graph shape with chunks

Concept pages link down to chunk pages. Chunk pages link back up to their document
summary page. This creates a clear hub-and-spoke structure per document:

```
[[allianz-szakmavedelem]]
    └──► [[ahe-43501-8-fabf]]               (document summary page)
              ├──► [[ahe-43501-8-fabf-chunk-001]]   (raw section, leaf)
              ├──► [[ahe-43501-8-fabf-chunk-012]]
              └──► [[ahe-43501-8-fabf-chunk-047]]
```

#### How the agent changes

`PageMeta` gains an `is_chunk: bool` flag. The agent should not stop navigation
until at least one chunk page has been visited — raw detail is always in the chunks,
not in the concept pages.

`FRONTIER_BUILDER` scores chunk pages higher when no chunk has been visited yet,
steering navigation toward the raw text when needed. Once a chunk is reached, the
normal `DONE` / continue decision applies.

`RAW_FALLBACK` is removed entirely. What it did is now handled by normal graph
navigation.

#### Ingest workflow change

When Claude Code ingests a new source document it must:

1. Segment the raw file by Markdown heading hierarchy
2. Assign a `chunk_id` to each segment (sequential, stable across re-ingests)
3. Create one chunk page per segment in `wiki/`
4. Add links from the document summary page to all its chunk pages
5. Update `wiki/index.md` (chunk pages can be listed under their parent document)

### Updated subgraph flow

With chunk pages in place `RAW_FALLBACK` is removed. The flow becomes:

```
ENTRY ──► READ ──► FRONTIER_BUILDER ──► NAVIGATOR ──┐
           ▲         (scores chunk pages             │
           │          higher if none visited yet)    │
           └─────────────────────────────────────────┘ (if not DONE)
                                         │
                                       DONE
                                         │
                                    SYNTHESIZE
                                         │
                                  CONFIDENCE_CHECK
                                    │         │
                               SUFFICIENT  INSUFFICIENT
                                    │         │
                                   END      END
                                        (no more fallback —
                                         chunks are in the graph)
```
