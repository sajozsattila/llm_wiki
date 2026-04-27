---
id: "tobbdimenzios-centralis-hatareloszlas-tetel"
type: concept
tags: ["statisztika", "cht", "normalis-eloszlas", "linearis-algebra"]
created: 2026-04-27
updated: 2026-04-27
confidence: 0.9
sources: ["Sajó Zsolt Attila: A többdimenziós Centrális határeloszlás-tétel"]
stale: false
---

# Többdimenziós centrális határeloszlás-tétel

## TL;DR

A többdimenziós centrális határeloszlás-tétel (CLT) kimondja, hogy véletlenszerű vektorok átlaga többdimenziós normál eloszláshoz tart, ahol a kovariancia mátrix játsza a szórásnégyzet szerepét.

## Leírás

A centrális határeloszlás-tétel (CHT/CLT) több dimenzióban is érvényes: a megfigyeléseinket $d$ dimenziós vektoroknak tekintjük.

### A tétel megfogalmazása

$$\sqrt{n}(\bar{X} - \mu) \xrightarrow[n \to \infty]{d} N_d(0, \Sigma)$$

Vagy standardizált alakban:

$$\sqrt{n} \cdot \Sigma^{-1/2} \cdot (\bar{X} - \mu) \xrightarrow[n \to \infty]{d} N_d(0, I_d)$$

Ahol:
- $\mu$: a valós populáció átlaga
- $\bar{X}$: a mintaátlag (d dimenziós vektor)
- $n$: megfigyelések száma
- $N_d$: d dimenziós normál eloszlás
- $\Sigma$: kovariancia mátrix
- $I_d$: d dimenziós egységmátrix

### Kovariancia mátrix

A $\Sigma^{-1/2}$ értéke teljesíti, hogy:

$$\Sigma^{-1/2} \cdot \Sigma^{-1/2} = \Sigma^{-1}$$

Mivel a kovariancia mátrix pozitív definit, ez a feltétel mindig teljesíthető.

### Példa alkalmazás

Legyen $X_1, X_2, \ldots X_n$ n darab d dimenziós i.i.d. megfigyelés, és $Y=v^T\cdot X$ egy lineáris transzformáció.

Ekkor:
- $E[Y] = v^T \cdot E[X]$
- $Var(Y) = v^T \cdot \Sigma_X \cdot v$

És a CLT alapján:

$$\sqrt{n}(\bar{Y} - v^T \cdot E[X]) \xrightarrow[n \to \infty]{d} N_d(0, v^T \cdot \Sigma_X \cdot v)$$

## Kapcsolódó oldalak

* kapcsolodik: [[Többdimenziós Delta módszer példa számítás]]
* kapcsolodik: [[Robusztus Bayes lineáris regresszió]]
* forrás: [[Loss függvény]]

## Példák

Ha $v\in\mathbb{R}_d$ egy vektor, és minden X értéket ugyanazzal a vektorral módosítunk, a lineáris transzformáció után is érvényes marad a CLT.

## Források

* Sajó Zsolt Attila: A többdimenziós Centrális határeloszlás-tétel
* Wikipedia: Multivariate normal distribution
* Wikipedia: Central limit theorem

## Megjegyzések

* Ha a szórás 0, akkor a kovariancia mátrix singuláris lehet, ezek extrém esetek.
* A $\Sigma^{-1/2}$ keresése során a mátrix pozitív definitségét használjuk ki.
