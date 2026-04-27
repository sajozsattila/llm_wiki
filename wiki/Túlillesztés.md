---
id: "tulillesztes"
type: concept
tags: ["gepi-tanulas", "overfitting", "regularization", "neurális hálózat"]
created: 2026-04-27
updated: 2026-04-27
confidence: 0.9
sources: ["Sajó Zsolt Attila: A túlillesztés problémája"]
stale: false
---

# Túlillesztés

## TL;DR

A túlillesztés (overfitting) akkor lép fel, amikor a modell megtanulja a tréning adatok minden apró különbségét, beleértve a zajt is, így képtelen általánosítani a nem látott adatokra.

## Leírás

Minden statisztikai elemzés és modell a világ egyszerűsítése. Mivel a teljes világot leírni annyi információt igényelne, mint maga a világ, a modell csak a lényeges mintázatokat tudja megragadni.

### A probléma lényege

A megfigyeléseket két csoportra osztjuk:
- **Tréning adatok**: ezek alapján tanítjuk a modellt
- **Teszt adatok**: ezekkel mérjük a modell teljesítményét

Az emberi elme és a gépi tanulás kiváló mintázatkereső, de túl jók: gyakran ott is összefüggést vélnek felfedezni, ahol nincs. A túlillesztés során a modell "specializálódik" a tréning adatokra, megtanulja a képzelt mintázatokat is.

### Tünetek

A loss függvény folyamatosan csökken a tréning adatokon, de a teszt adatokon romlik a teljesítmény.

### Megoldások

- **Regularization**: az összetettebb modellek büntetése az egyszerűekkel szemben
- **Dropout réteg**: neurális hálózatokban speciális réteg a túlillesztés ellen
- **Több adat**: minél több adat áll rendelkezésre, annál nehezebb a nem létező mintázatokat megtanulni

## Kapcsolódó oldalak

* kapcsolodik: [[Mesterséges neurális hálózat alapjai]]
* kapcsolodik: [[Loss függvény]]
* kapcsolodik: [[Hosszú munkamemóriájú neurális hálózat]]

## Példák

Mély Feed Forward Neurális Hálózat 15 mintán, 200 epoch:
- 4 rejtett réteg (méretek: 30, 45, 60, 75 neuron)
- Tréning: a loss folyamatosan csökken
- Teszt: a loss növekszik (tipikus túlillesztés)

A valós modell: $y = \beta_0 + x \cdot \beta_1 + x^2 \cdot \beta_2 + x^3 \cdot \beta_3$ binominális klasszifikációval.

## Források

* Sajó Zsolt Attila: A túlillesztés problémája
* Will Koehrsen: Overfitting vs. Underfitting: A Complete Example
* Wikipedia: Overfitting

## Megjegyzések

* Angolul: overfitting
* A Regularization-ról és Dropout rétegről külön bejegyzések lesznek a blogon
* A túlillesztés akkor is előfordulhat, ha a zaj szerencsétlen elrendeződése miatt trendszerűséget vélünk felfedezni
