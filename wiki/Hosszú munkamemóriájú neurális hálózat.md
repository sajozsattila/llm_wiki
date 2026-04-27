---
id: "lstm"
type: concept
tags: ["neurális hálózat", "lstm", "rnn", "deep-learning"]
created: 2026-04-27
updated: 2026-04-27
confidence: 0.9
sources: ["Sajó Zsolt Attila: A Hosszú Munkamemóriájú Neurális Hálózat"]
stale: false
---

# Hosszú munkamemóriájú neurális hálózat

## TL;DR

Az LSTM (Long Short-Term Memory) egy speciális, az eltűnő gradiens problémát megoldó ismétlődő neurális hálózat, amely cellaállapotával hosszú távú információt képes megőrizni.

## Leírás

Az LSTM a Mesterséges Neurális Hálózatok egyik sikeres változata, amelyet 1997-2000 között Sepp Hochreiter, Jürgen Schmidhuber és Felix Gers fejlesztett ki. Hochreiter definiálta először az eltűnő gradiens problémát (vanishing gradient problem), amelyre az LSTM jelent megoldást.

Az LSTM az Ismétlődő Neurális Hálózat (RNN) altípusaként a megfigyeléseket egyesével dolgozza fel, de a hagyományos RNN-nel ellentétben négy összetett részből áll:

### Cella állapot

A cella állapot egy futószalag-szerű struktúra, amely az információt kis módosítással szállítja a megfigyelések között anélkül, hogy többszörös átvitel történne az aktivációs függvényeken. Ez oldja meg az eltűnő gradiens problémát.

A cella végső értéke:

$$(1) \quad C_t = f_t \circ C_{t-1} + i_t \circ \tilde{C}_t$$

Ahol:
- $C_t$: az új cella állapot
- $f_t$: a felejtés kapujának kimenete
- $C_{t-1}$: a korábbi cella állapot
- $i_t$: a bemeneti kapu eredménye
- $\tilde{C}_t$: a tanh aktivációs függvény eredménye
- $\circ$: a Hadamard-szorzat jele

### Felejtés kapuja

Eldönti, hogy a korábbi cella állapotok közül mennyi információt őrzünk meg. A sigmoid függvény (0-1 közötti kimenet) határozza meg, mennyire vesszük figyelembe az adott információt:

$$f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f)$$

### Bemeneti kapu

A jelenlegi megfigyelésből mennyi információt őriz meg. A sigmoid eldönti mi fontos, a tanh kiszámítja a cella állapot frissítését:

$$i_t = \sigma(W_i \cdot [h_{t-1}, x_t] + b_i)$$

$$\tilde{C}_t = \tanh(W_c \cdot [h_{t-1}, x_t] + b_c)$$

### Kimeneti kapu

Eldönti, mi legyen a következő rejtett állapot (ez használható előrejelzésre):

$$o_t = \sigma(W_o \cdot [h_{t-1}, x_t] + b_o)$$

$$h_t = o_t \circ \tanh(C_t)$$

### Alkalmazások

A 2010-es évek végére az LSTM széles körben elterjedt: Google Translate, iPhone Quicktype, Siri, Amazon Alexa.

## Kapcsolódó oldalak

* kapcsolodik: [[Mesterséges neurális hálózat alapjai]]
* kapcsolodik: [[Túlillesztés]]
* forrás: [[Loss függvény]]

## Példák

Egyszerű Python implementáció (naiv lejátszás):

```python
import numpy as np

def sigmoid(x):
    return 1/(1+np.exp(-x))

def lstmcell(x, ct):
    ft = sigmoid(np.dot(wf, x)+bf)
    it = sigmoid(np.dot(wi, x)+bi)
    ot = sigmoid(np.dot(wo, x)+bo)
    ct = ft*ct+it * np.tanh(np.dot(wc, x)+bc)
    ht = ot*np.tanh(ct)
    return ht, ct
```

## Források

* Sajó Zsolt Attila: A Hosszú Munkamemóriájú Neurális Hálózat
* Christopher Olah: Understanding LSTM Networks
* Michael Nguyen: Illustrated Guide to LSTM's and GRU's
* Shi Yan: Understanding LSTM and its diagrams

## Megjegyzések

* Az LSTM-nek több változata is létezik; a könyvtárak dokumentációját érdemes áttanulmányozni a konkrét implementáció előtt.
