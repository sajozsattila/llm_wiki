---
id: "loss-fuggveny"
type: concept
tags: ["statisztika", "loss-fuggveny", "optimalizalas"]
created: 2026-04-27
updated: 2026-04-27
confidence: 0.9
sources: ["Sajó Zsolt Attila: A Loss függvény – statisztika alapok"]
stale: false
---

# Loss függvény

## TL;DR

A loss függvény egy olyan mérőszám, amely megmondja, mennyire illeszkedik egy modell az adatokra; minél nagyobb az értéke, annál rosszabb a modell.

## Leírás

A loss függvényt optimalizációs problémák megoldására alkalmazzák annak eldöntésére, melyik modell illeszkedik legjobban a mintavételi pontokra.

### Működési elv

A modell pontoktól való távolságainak összege adja a loss értéket. Minél nagyobb ez a szám, annál rosszabb a modell, mivel annál távolabb van a pontoktól. A távolság mindig pozitív (nem különbség!).

### Gyakori loss függvények

- **Mean squared error**: a távolság négyzetét használja, érzékeny a kiugró adatokra
- **Abszolút loss**: a puszta távolságot méri, de nem deriválható
- **Huber loss**: kombinálja a kettőt; 0 közelében folytonos és deriválható, robusztus a kiugró értékekkel szemben

### Objektív függvény

Az objektív függvény egy olyan függvény, amit minimalizálni vagy maximalizálni szeretnénk. A loss függvény az objektív függvények alcsoportja.

További objektív függvények:
- **Reward function** (jutalom)
- **Profit function** (haszon)
- **Fitness function** (fitnesz)
- **Likelihood függvény** (statisztikában gyakran maximalizálandó)

A maximalizálás és minimalizálás ugyanaz a probléma: ha egy függvényt, amit maximalizálni akarunk, megszorzunk -1-gyel, akkor minimalizációs probléma lesz belőle.

### Kapcsolat a lineáris regresszióval

A lineáris legkisebb négyzetek regresszió során a rendszer kipróbál lineáris modelleket, és a legkisebb loss értékűt választja ki.

## Kapcsolódó oldalak

* kapcsolodik: [[Robusztus Bayes lineáris regresszió]]
* kapcsolodik: [[Mesterséges neurális hálózat alapjai]]
* kapcsolodik: [[Túlillesztés]]

## Példák

Három modell összehasonlítása 20 adatponton:
- Modell A: összesített távolság = 68.09
- Modell B: összesített távolság = 28.09
- Modell C: összesített távolság = 27.29

Legjobb modell: C (legalacsonyabb loss).

## Források

* Sajó Zsolt Attila: A Loss függvény – statisztika alapok
* Wikipedia: Mean squared error
* Wikipedia: Huber loss
* Wikipedia: Loss function
* Wikipedia: Likelihood function

## Megjegyzések

* A közgazdaságtanban "cost függvénynek" is nevezik, utalva arra, hogy a költséget alacsonyan szeretnénk tartani.
* A cost függvény néha a loss kiterjesztéseként használatos: loss + büntetés a bonyolult modellért.
