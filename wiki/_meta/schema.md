# Wiki Page Template

---

id: <unique_id>
type: concept | entity | project | note
tags: ["statisztika", "delta-modszer"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: 0.0-1.0
sources: ["Sajó Zsolt Attila", "Wikipedia"]
stale: false
---

## YAML Strict Quoting Rules

**Hungarian text contains `:` characters, so ALL string values MUST use double quotes:**

- `tags: ["statisztika", "delta-modszer"]` ✓
- `tags: [statisztika, delta-modszer]` ✗ (will fail)

- `sources: ["Sajó Zsolt Attila: Delta módszer"]` ✓
- `sources: [Sajó Zsolt Attila - Delta módszer]` ✗

**Escaping inside strings:**
- `"` → `\"`
- `\` → `\\`
- `:` at end of value is OK, but safer to quote

# <Cím>

## TL;DR

<rövid leírás>

## Leírás

<teljes leírás>


## Kapcsolódó oldalak

* kapcsolodik: [[Other Page]]
* forrás: [[Other Page]]
* ellenmond: [[Other Page]]

## Példák

<opcionális>

## Források

* <források listája>

## Megjegyzések

<opcionális, lábjegyzetek>

