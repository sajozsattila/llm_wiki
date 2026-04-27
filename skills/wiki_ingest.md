# Skill: Wiki Betöltés

## Cél

Nyers bemenet átalakítása strukturált wiki tudássá.

## Lépések

1. Ellenőrizd, hogy léteznek-e releváns oldalak a `/wiki/` mappában
2. Ha IGEN:

   * Frissítsd a meglévő oldalakat
   * Olvassz össze új információkat
   * Frissítsd a `updated` időbélyeget
   * Állítsd be a `confidence` értéket
3. Ha NEM:

   * Hozz létre új oldalt a 'wiki/_meta/schema.md' séma alapján

## Kinyerési szabályok

* Atomikus fogalmak kinyerése
* Duplikáció kerülése
* Nagy témák felbontása több oldalra
* Építsd be minden információt a nyers dokumentumokból

## Írási szabályok

* Töltsd ki az összes kötelező szakaszt
* Adj hozzá linkeket a kapcsolódó oldalakhoz
* Adj hozzá forrásokat a frontmatterben + Források szakaszban
* **YAML szigorú idézés**: Az összes string érték a frontmatterben DUPLA IDÉZŐJELBEN kell legyen
  - `tags: ["statisztika", "delta-modszer"]`
  - `sources: ["Sajó Zsolt Attila"]`
  - Escape: `"` → `\"`, `\` → `\\`

## Confidence pontozás

* 0.9–1.0 → jól megalapozott tény
* 0.6–0.8 → valószínűleg helyes
* 0.3–0.5 → bizonytalan
* <0.3 → spekulatív

## Kimenet

* Csak markdown fájlokat írj a `/wiki/` mappába
* Frissítés preferálása létrehozás helyett
