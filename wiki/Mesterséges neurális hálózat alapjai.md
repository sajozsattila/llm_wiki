---
id: "mesterseges-neuralis-halozat-alapjai"
type: concept
tags: ["neurális hálózat", "ann", "feedforward", "gepi-tanulas"]
created: 2026-04-27
updated: 2026-04-27
confidence: 0.9
sources: ["Sajó Zsolt Attila: A Mesterséges Neurális Hálózat alapjai – 1. rész"]
stale: false
---

# Mesterséges neurális hálózat alapjai

## TL;DR

A Feedforward típusú Mesterséges Neurális Hálózat (ANN) teljesen csatolt rétegekből álló rendszer, amely a lejátszás (forward propagation), hibaszámítás és visszajátszás (back propagation) lépésekkel tanul.

## Leírás

A Mesterséges Neurális Hálózat (MNH/ANN) napjaink felkapott technológiája, amely arcfelismerésre, képfeldolgozásra, fordításra és hirdetésoptimalizálásra is használatos.

### Felépítés

A hálózat két alapelemre épül:
- **Neuronok**: végzik a számítást (körök)
- **Kapcsolatok**: a neuronok közötti összeköttetések (nyilak), teljesen csatolt rendszerben minden neuron kapcsolódik a következő réteg összes neuronjához

### Rétegek

1. **Bemeneti réteg**: a megfigyelt adatok érkeznek ide, minden neuron egy tulajdonságot/jellemzőt jelöl
2. **Rejtett réteg**: a számítások helye, modellezi a bemeneti tulajdonságok kapcsolatát (tetszőleges számú lehet, akár el is hagyható)
3. **Kimeneti réteg**: az MNH végső eredményének helye

### Neuronszámítás

Egy neuron működése:

$$z_j = w_{0j} + \sum_{i=1}^n x_i w_{ij}$$

Majd alkalmazzuk az aktivációs függvényt: $f(z_j)$

Az aktivációs függvény lehetővé teszi a lineárisan nem elválasztható feladatok megoldását.

### Tanulás lépései

Minden felügyelt tanulás három részből áll:
1. **Lejátszás (Forward propagation)**: meglévő ismeretek alkalmazása egy megfigyelésen
2. **Hibaszámítás**: az eredmény összevetése a tényleges értékkel, Loss kalkuláció
3. **Visszajátszás (Back propagation)**: az ismeretek korrigálása a hiba alapján

### Aktivációs függvények példák

- **tanh**: $f_r(z) = 1 - \frac{2}{e^{2z} + 1}$
- **ReLU**: $f_k(u) = max(0, u)$

## Kapcsolódó oldalak

* kapcsolodik: [[Hosszú munkamemóriájú neurális hálózat]]
* kapcsolodik: [[Loss függvény]]
* kapcsolodik: [[Túlillesztés]]
* forrás: [[Hipersík]]

## Példák

Python példa a lejátszásra (numpy-val):

```python
import numpy as np

# megfigyelés
x = np.array([.05, .1])
# rejtett réteg súlyai
w = np.array([[.25,.35],[.55, .65],[.85, .95]])
w0 = np.array([[.15],[.45],[.75]])
# z érték számítása
z = (np.concatenate((w0, w), axis=1))@np.insert(x,0,1,axis=0)
```

## Források

* Sajó Zsolt Attila: A Mesterséges Neurális Hálózat alapjai – 1. rész
* Assaad Moawad: Neural networks and back-propagation explained in a simple way
* Matt Mazur: A Step by Step Backpropagation Example
* John McGonagle et al.: Backpropagation

## Megjegyzések

* A 2. rész tárgyalja a hibaszámítást és visszajátszást.
* Az aktivációs függvényeknek van deriváltja is, amely a visszajátszásnál szükséges.
