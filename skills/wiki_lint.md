# Skill: Wiki Ellenőrzés

## Cél

A wiki minőségének és konzisztenciájának fenntartása.

## Ellenőrzések

### 1. Strukturális érvényesség

* Van frontmatter?
* A kötelező mezők jelen vannak?
* Érvényes típusok?

### 2. Konzisztencia

* Ellentmondásos állítások az oldalak között
* Duplikált fogalmak

### 3. Linkelés

* Árvák (bejövő link nélküli oldalak)
* Hibás linkek

### 4. Frissesség

* Régi oldalak → `stale: true` jelölés

### 5. Confidence

* Alacsony confidence-jű oldalak jelölése

### 6. YAML Formátum

* Az összes string érték duplas idézőjelben
* Nincs escape-eletlen kettőspont az értékekben
* Érvényes YAML szintaxis (parseolható)

## Műveletek

* Összefűzés javaslata
* Frissítés javaslata
* Ellentmondások jelölése
* Elavult tartalom jelölése

## Kimenet

* Problémák listája
* Javasolt javítások
