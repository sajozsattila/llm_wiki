# Skill: Wiki Lekérdezés

## Cél

A felhasználói lekérdezések megválaszolása a wiki használatával, **minimális késleltetés és token-használat** mellett, a helyesség megőrzése közben.

---

## Alapstratégia

A munkát áthelyezni: lekérdezési időből → előre kiszámított tudásba.

Prioritási sorrend:

1. Előre kiszámított válaszok (leggyorsabb)
2. Összefoglalók (olcsó útválasztás)
3. Teljes oldalak (drága, korlátozott)

---

## Kemény Korlátozások

* MAX betöltendő oldal: **3**
* MAX bejárási mélység: **2**
* Összefoglalók előtérbe helyezése teljes tartalom helyett
* SOHA ne olvasd végig végig a teljes wikit

---

## 0. lépés — Lekérdezés Normalizálása

* Szándék kinyerése
* Kulcs entitások / koncepciók azonosítása
* 3–5 keresőkulcsszó generálása

---

## 1. lépés — Válasz Gyorsítótár Ellenőrzése (FAQ Réteg)

Keresés itt:
`/wiki/answers/`

Ha van egyező vagy hasonló kérdés:

* Add vissza az előre kiszámított választ
* Gyorsan ellenőrizd a relevanciát
* ÁLLJ MEG

---

## 2. lépés — Gyors Útválasztás (Olcsó Átmenet)

Csak itt KERESS:

* Frontmatter
* `## Lekérési Összefoglaló`
* `_index.md` (ha létezik)

NE olvass teljes oldalakat.

Válassz:

* Top **2–4 jelölt oldal**

Kiválasztási kritériumok:

* Kulcsszó egyezés
* Címke egyezés
* Magas `confidence`
* Alacsony `stale`
* Magas `centrality` (ha elérhető)

---

## 3. lépés — Felületes Olvasás (Lusta Kiterjesztés)

A kiválasztott oldalakból, csak ezt OLVASD:

* TL;DR
* Kulcs Pontok
* Kapcsolatok

Még NE olvass teljes oldalt.

Ha a válasz elegendő:

* Generálj választ
* ÁLLJ MEG

---

## 4. lépés — Mély Olvasás (Korlátozott)

Ha szükséges:

* Töltsd be a teljes tartalmat max **3 oldalról**

Prioritizálás:

1. Legmagasabb relevancia
2. Legmagasabb confidence
3. Leginkább kapcsolódó oldalak

Opcionális:

* Kövesd a linkeket (`[[...]]`) de CSAKA egy ugrásnyit

---

## 5. lépés — Válasz Szintetizálása

* Kombinálj információt a kiválasztott oldalakból
* A teljesség helyett a konzisztenciát részesítsd előnyben
* Oldd fel a kisebb konfliktusokat, ha lehetséges

---

## 6. lépés — Hiányok Kezelése

Ha hiányzik az információ:

* Mondd: "Nincs a wikiben"
* Javasolj betöltést:

  * Új oldal
  * Meglévő oldal frissítése

---

## 7. lépés — Opcionális Gyorsítótár Írás

Ha:

* A lekérdezés valószínűleg ismétlődik
* A válasz több lépéses következtetést igényelt

Akkor:

* Hozz létre új fájlt itt: `/wiki/answers/`

Tartalmazza:

* Kérdés
* Válasz
* Forrás oldalak

---

## Kimeneti Szabályok

* Légy tömör
* Hivatkozz oldalnevekre (pl. [[LLM Wiki]])
* NE hallucinálj
* Részesítsd előnyben a strukturált válaszokat

---

## Teljesítmény Heurisztikák

* 2 jó oldalt részesíts előnyben 5 közepesnél
* Kerüld a mély bejárási láncokat
* Kerüld a nagy oldalak betöltését, hacsak nem szükséges
* Állj meg korán, ha a confidence elegendő

---

## Kerülendő Hibamódok

* A teljes wiki végigolvasása
* Túl sok oldal betöltése
* Gyorsítótárban lévő válaszok figyelmen kívül hagyása
* Túl sok link bejárása
* Ismert válaszok újraszámolása

---

## Mentális Modell

Te nem dokumentumokat keresel.

Te vagy:
→ egy lekérdezés **előre kiszámított tudásgráfon** keresztül történő útválasztása

Cél:
→ találd meg a legrövidebb utat a válaszhoz

(Vége a fájlnak - összesen 185 sor)