#### **[Sajó Zsolt Attila](https://sajozsattila.home.blog/)**

# A Hosszú Munkamemóriájú Neurális Hálózat

[sajzsoltattila](https://sajozsattila.home.blog/author/sajzsoltattila/) [Gépi tanulás](https://sajozsattila.home.blog/category/gepi-tanulas/) 1st november 20196th november 2019 5 Minutes *Nem olyan régen szó volt a Mesterséges Neurális Hálózatok [\(https://sajozsattila.home.blog/tag/mesterseges-neuralis-halozat/\)](https://sajozsattila.home.blog/tag/mesterseges-neuralis-halozat/) egy sorozatokra kifejlesztett változatáról, az Ismétlődő Neurális Hálózatról (https://sajozsattila.home.blog/2019/08/28/ismetlodo[neuralis-halozat/\). Amint említettük, ez a típus hatványozottan szenved az Elt](https://sajozsattila.home.blog/2019/08/28/ismetlodo-neuralis-halozat/)űnő Gradiens Problémától. Ennek a nehézségnek a megoldására született meg a "Hosszú Munkamemóriájú" (HMM, angolul: Long short-term memory) Neurális Hálózat. Mai bejegyzésünkben ezt megvizsgáljuk meg.*

[A HMM mai formája 1997 és 2000 között született meg Sepp Hochreiter](https://en.wikipedia.org/wiki/Sepp_Hochreiter) [\(https://en.wikipedia.org/wiki/Sepp\\_Hochreiter\), Jürgen Schmidhuber](https://en.wikipedia.org/wiki/J%C3%BCrgen_Schmidhuber) [\(https://en.wikipedia.org/wiki/J%C3%BCrgen\\_Schmidhuber\) és Felix Gers](https://en.wikipedia.org/wiki/Felix_Gers) (https://en.wikipedia.org/wiki/Felix\_Gers) munkája során. Érdemes megemlíteni, hogy Hochreiter volt az aki először definiálta az Eltűnő Gradiens Problémát. [1](#page-7-0)

A 2010-es évek végére az HMM igazi sikersztori lett. Sajnos csak 2016-os adatokat találtam, de ezek szerint 3 évvel ezelőtt olyan jól ismert és használt alkalmazásokban használták, mint a Google Translate, az iPhone "Quicktype" funkciója, a Siri vagy az Amazon Alexa.

A HMM szoros rokonságban áll az Ismétlődő Neurális Hálózattal, sokszor annak egy altípusának tekintik. Itt is egyesével dolgozzuk fel a megfigyeléseket: [2](#page-7-0)

Ami eltérő: az a hálózat felépítése; a zöld dobozok sora. Ez nem egy egyszerű Feed Forward Hálózat, hanem egy sokkal összetettebb rendszer:

Amint látható, az egy tanh aktivációs függvény helyett itt két tanh és három sigmoid függvényünk is van. A rendszert négy részre oszthatjuk:

Nézzük mit is csinálnak ezek a részek részletesebben.

#### Cella állapot

In medias res, kezdjük a cella állapottal! Ez a rész kicsit olyan, mint egy futószalag, ami az információt kis módosítással szállítja az egyik megfigyeléstől a másik felé. Szerintem ez a legérdekesebb része a koncepciónak. Vegyük észre, hogy itt úgy tudunk információt továbbítani a különféle megfigyelések között, hogy azokat nem küldjük többszörösen át az aktivációs függvényen. Ez az, aminek a segítségével a HMM megoldja az Eltűnő Gradiens Problémát. A Felejtés kapuja és a Bemeneti kapuk arra szolgálnak, hogy az adatokat helyezzenek fel vagy vegyenek le erről a futószalagról:

Valamelyest előreszaladva a cella állapot végső értékét így számoljuk:

$$(1) \quad C_t = f_t \circ C_{t-1} + i_t \circ \tilde{C}_t$$

#### Ahol:

- az új cella állapot
- a felejtés kapujának kimenete, lsd. Felejtés kapuja
- a korábbi cella állapot
- a bemeneti kapu eredménye, lsd. Bemeneti kapu
- a tangh aktivációs függvény eredménye, lsd: Bemeneti kapu
- a [Hadamard-szorzat \(https://hu.wikipedia.org/wiki/Hadamard-szorzat\)](https://hu.wikipedia.org/wiki/Hadamard-szorzat) jele

### Felejtés kapuja

Ennek a misztikusan hangzó nevű résznek a dolga eldönteni, hogy korábbi cella állapotok közül mennyi információt őrzünk meg, illetve felejtünk el. Mivel ez egy sigmoid függvény, a kimeneti értéke 0 és 1 között van, azaz minél kisebb a kimenet annál kevésbé fogjuk a későbbiekben figyelembe venni az adott információt:

A számítása ennek megfelelőn:

(2) 
$$f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f)$$

Ahol:

- a felejtés kapujának eredménye
- a felejtés kapujának súlyai
- a korábbi rejtett állapot
- a jelenlegi megfigyelés
- a felejtés kapujának eltolása

#### Bemeneti kapu

Ez a kapu annak eldöntésére szolgál, hogy menyi információt őrizzünk meg a jelenlegi megfigyelésből. A sigmoid eldönti: mi fontos, mi nem, míg a tanh kiszámítja a cella állapot frissítésének értékét:

A fentieknek megfelelően a bementi kapu eredményének számítása:

(3) 
$$i_t = \sigma(W_i \cdot [h_{t-1}, x_t] + b_i)$$

Ahol:

- a bementi kapu eredménye
- a bemeneti kapu súlyai
- a bemeneti kapu eltolása

Az aktivációs függvény pedig a szokásos:

(4) 
$$\tilde{C}_t = \tanh(W_c \cdot [h_{t-1}, x_t] + b_c)$$

Ahol:

- a javasolt állapot a -re
- az aktivációs függvény súlyai
- az aktivációs függvény eltolása

### Kimenti kapu

Ez a réteg dönti el, hogy a következő megfigyelés esetén mi legyen a Rejtett állapot. Ezt az állapotot használjuk előrejelzésre is.

A kimeneti kapu eredményének számítása:

(5) 
$$o_t = \sigma(W_o \cdot [h_{t-1}, x_t] + b_o)$$

Ahol:

- a kimeneti kapu eredménye
- a kimeneti kapu súlyai
- a kimeneti kapu eltolása

Végül pedig a végső Rejtett állapot:

$$h_t = o_t \circ \tanh(C_t)$$

### Naiv Python Lejátszás

Végezetül nézzünk meg egy egyszerű Python implementációt a HMM lejátszás szakaszára:

```
     import numpy as np
     # kezdeti sulyok
     wf = np.array([0,0])
     bf = -100
     wi=np.array([0,100])
     bi = 100
     wo=np.array([0,100])
     bo = 0
     wc = np.array([-100,50])
     bc = 0
     # sigmoid függvény
     def sigmoid(x):
         return 1/(1+np.exp(-x))
     # LSTM cella
     #   attr:
     #       x -- igazából [ h_{t-1}, x]
     def lstmcell(x, ct):
         # felejtés kapuja
         ft = sigmoid(np.dot(wf, x)+bf)
         # bemeneti kapu
         it = sigmoid(np.dot(wi, x)+bi)
         # kimeneti kapu
         ot = sigmoid(np.dot(wo, x)+bo)
         # cella állapot
         ct = ft*ct+it * np.tanh(np.dot(wc, x)+bc)
         # rejtett állapot
         ht = ot*np.tanh(ct)
         return ht, ct
     # megfigyelések
     xs = np.array([0, 0, 1, 1, 1, 0])
     # kezdeti rejtett állapot
     htx = [0]
     # kezdeti cella állapot
     ctx = np.array([0])
     # eredmény
     result = []
     # végiglépkedünk a megfigyeléseken
     for i in xs:
         htx.append(i)
         htx, ctx = lstmcell(np.array(htx), ctx)
         htx = htx.tolist()
         htx[0] = htx[0]
         result.append(htx[0])
     # eredmény
     print(result)
```

### Végszó

A fentiekben megnéztük, hogyan működik egy tipikus HMM, de mint mindennek a Mesterséges Neurális Hálózatok területén, ennek is több változata alakult ki. A konkrét könyvtárak alkalmazása során érdemes átolvasni a dokumentációt, hogy lássuk, mennyiben tipikus az adott megvalósítás.

#### <span id="page-7-0"></span>Lábjegyzet

- 1. S. Hochreiter: Untersuchungen zu dynamischen neuronalen Netzen. Diploma thesis, Institut f. Informatik, Technische Univ. Munich, 1991.
- 2. Mint a Ismétlődő Neurális Hálózat esetén ebben a bejegyzésben is Michael Nguyen [Illustrated Guide to LSTM's and GRU's \(https://towardsdatascience.com/illustrated-](https://towardsdatascience.com/illustrated-guide-to-lstms-and-gru-s-a-step-by-step-explanation-44e9eb85bf21)

[guide-to-lstms-and-gru-s-a-step-by-step-explanation-44e9eb85bf21\)](https://towardsdatascience.com/illustrated-guide-to-lstms-and-gru-s-a-step-by-step-explanation-44e9eb85bf21) munkájának ábráit használom.

#### Irodalom

- [Christopher Olah: Understanding LSTM Networks \(http://colah.github.io/posts/2015-08-](http://colah.github.io/posts/2015-08-Understanding-LSTMs/?source=post_page-----37e2f46f1714----------------------) Understanding-LSTMs/?source=post\_page-----37e2f46f1714----------------------)
- Michael Nguyen: Illustrated Guide to LSTM's and GRU's: A step by step explanation [\(https://towardsdatascience.com/illustrated-guide-to-lstms-and-gru-s-a-step-by-step](https://towardsdatascience.com/illustrated-guide-to-lstms-and-gru-s-a-step-by-step-explanation-44e9eb85bf21)explanation-44e9eb85bf21)
- Shi Yan: Understanding LSTM and its diagrams [\(https://medium.com/mlreview/understanding-lstm-and-its-diagrams-37e2f46f1714\)](https://medium.com/mlreview/understanding-lstm-and-its-diagrams-37e2f46f1714)

#### **Címke:**

[Hosszú munkamemóriájú](https://sajozsattila.home.blog/tag/hosszu-munkamemoriaju/), Ismétlődő [Neurális Hálózat](https://sajozsattila.home.blog/tag/ismetlodo-neuralis-halozat/), [Mesterséges Neurális Hálózat](https://sajozsattila.home.blog/tag/mesterseges-neuralis-halozat/)

## Közzétéve: sajzsoltattila
