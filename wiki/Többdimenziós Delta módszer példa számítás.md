---
id: "tobbdimenzios-delta-modszer-pelda-szamitas"
type: concept
tags: ["statisztika", "delta-modszer", "fisher-informacio", "linearis-algebra"]
created: 2026-04-27
updated: 2026-04-27
confidence: 0.9
sources: ["Sajó Zsolt Attila: A többdimenziós Delta módszer példa számítás"]
stale: false
---

# Többdimenziós Delta módszer példa számítás

## TL;DR

A Delta módszer segítségével számolható a paraméterbecslések aszimptotikus eloszlása, amikor a megfigyelt változó lineáris transzformációján keresztül próbálunk becsülni eredeti paramétereket.

## Leírás

A példában egy normál eloszlás ($X$) két paraméterét ($\mu$ és $\tau = \sigma^2$) szeretnénk becsülni, de csak egy $Y = 2 \cdot X + 5$ transzformált változót figyelhetünk meg.

### Maximum Likelihood becslés (Y-ra)

Mivel Y is normál eloszlású:

$$\hat{\mu}_Y = \bar{y} = \frac{1}{n} \sum_{i=1}^n y_i$$

$$\hat{\tau}_Y = \frac{1}{n} \sum_{i=1}^n (y_i - \bar{y})^2$$

Fisher információs mátrix:

$$I(\mu, \tau) = \begin{bmatrix} \frac{1}{\tau_Y} & 0\\ 0 & \frac{1}{2\tau_Y^2} \end{bmatrix}$$

### Delta módszer lépései

1. **g függvények meghatározása**:

$$g_1(x) = g_{\mu}(x) = \frac{\mu_Y - 5}{2}$$

$$g_2(x) = g_\tau(x) = \frac{\tau_Y}{4}$$

Vektorként:

$$g(x) = \begin{bmatrix} \frac{\mu_Y - 5}{2} \\ \frac{\tau_Y}{4} \end{bmatrix}$$

2. **Gradiens számítása** ($k=2$, $d=1$):

$$\nabla g(x) = \begin{bmatrix} \frac{1}{2} \\ \frac{1}{4} \end{bmatrix}$$

3. **Aszimptotikus kovariancia**:

$$\Sigma = \begin{bmatrix} \frac{1}{2} \\ \frac{1}{4} \end{bmatrix}^T \cdot \begin{bmatrix} \frac{1}{\tau_Y} & 0 \\ 0 & \frac{1}{2\tau_Y^2} \end{bmatrix}^{-1} \cdot \begin{bmatrix} \frac{1}{2} \\ \frac{1}{4} \end{bmatrix} = \frac{\tau_Y}{4} + \frac{\tau_Y^2}{8}$$

## Kapcsolódó oldalak

* kapcsolodik: [[Többdimenziós centrális határeloszlás-tétel]]
* kapcsolodik: [[Robusztus Bayes lineáris regresszió]]
* forrás: [[Loss függvény]]

## Példák

Szimuláció (n=10000, 5000 ismétlés):
- Valós $\mu = 30$, $\sigma^2 = 4$
- Becslés elvárt eloszlása: normál, szórás = $\sqrt{\frac{1}{4} \cdot \frac{4\sigma^2}{n}}$
- Kolmogorov-Smirnov teszt megerősíti a Delta módszer helyességét

## Források

* Sajó Zsolt Attila: A többdimenziós Delta módszer példa számítás
* Wikipedia: Delta method
* Wikipedia: Fisher information

## Megjegyzések

* A $\tau$ jelöli a szórásnégyzetet (varianciát), hogy egyértelmű legyen: nem a szórásnégyzetgyököt becsüljük
* Kétoldali Kolmogorov-Smirnov teszt csak nagy n esetén megbízható
* Az egyoldali KS teszt nem használható ilyen célra
