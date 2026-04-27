---
id: "robusztus-bayes-linearis-regresszio"
type: concept
tags: ["statisztika", "bayes", "linearis-regresszio", "robusztus", "stan"]
created: 2026-04-27
updated: 2026-04-27
confidence: 0.9
sources: ["Sajó Zsolt Attila: A Robusztus Bayes lineáris regresszió"]
stale: false
---

# Robusztus Bayes lineáris regresszió

## TL;DR

A robusztus Bayes lineáris regresszió a Student t-eloszlást használja a zaj modellezésére (nem normális eloszlást feltételez), a Bayes megközelítés pedig lehetővé teszi a paraméterek valószínűségi eloszlásának meghatározását.

## Leírás

A lineáris regresszió alapképlettel:

$$(1) \quad y = \alpha + \beta x + \epsilon$$

Hagyományos esetben a zaj ($\epsilon$) normál eloszlású, 0 átlaggal:

$$(2) \quad y = N(\alpha + \beta x, \sigma)$$

### Problémák és megoldásuk

**Probléma 1: Nem normál eloszlású zaj**

A kiugró értékekkel szemben robusztusabb a Student t-eloszlás használata:

$$(3) \quad y = T(\alpha + \beta x, \sigma, \nu)$$

Ahol:
- $T$: Student t-eloszlás
- $\sigma$: arányossági tényező
- $\nu$: szabadsági fok (ahogy csökken, nő a farokterület, növelve a robusztusságot)

**Probléma 2: Rövid idősor**

A Bayes analízis megoldja, mivel nemcsak a legvalószínűbb paramétereket adja, hanem az összes lehetséges megoldás valószínűségét is. Minél hosszabb a megfigyelés, annál megbízhatóbb az eredmény.

### STAN implementáció

A STAN egy C++-ban írt nyelv Bayes statisztikához, amelyhez létezik Python interfész (PySTAN 3.x).

A modellben:
- Likelihood: Student t-eloszlás
- Priors: nem informatív priorok a paramétereken

## Kapcsolódó oldalak

* kapcsolodik: [[Loss függvény]]
* kapcsolodik: [[Többdimenziós centrális határeloszlás-tétel]]
* forrás: [[Többdimenziós Delta módszer példa számítás]]

## Példák

LTE átjátszó tornyok DL Throughput elemzése 10 napos adatsoron:

- Béta paraméter: -0,0002 és +0,00005 között
- 0-nál nagyobb béta valószínűsége: 4,2%
- Kolmogorov-Smirnov teszt a normál eloszlás ellen: p = 1,13e-05 (elutasítva)
- Kolmogorov-Smirnov teszt Student t ellen: p = 0,778 (elfogadva)

## Források

* Sajó Zsolt Attila: A Robusztus Bayes lineáris regresszió
* Adrian Baez-Ortega: Robust Bayesian linear regression with Stan in R
* Solomon Kurz: Robust Linear Regression with Student's t-Distribution
* Cliburn Chan et al.: Computational Statistics in Python

## Megjegyzések

* A STAN kód a PySTAN 3.8.0 verziójával kompatibilis (frissítve 2024.01)
* A Student t-eloszlás farokterülete vastagabb, mint a normál eloszlásé, ezért robusztusabb
* A Q-Q ábra és Kolmogorov-Smirnov teszt segít ellenőrizni a modell illeszkedését
