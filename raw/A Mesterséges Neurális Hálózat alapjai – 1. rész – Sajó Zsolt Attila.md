#### **[Sajó Zsolt Attila](https://sajozsattila.home.blog/)**

Gépi tanulás és néhány más dolog

☰ **Menü**

# A Mesterséges Neurális Hálózat alapjai – 1. rész

[sajzsoltattila](https://sajozsattila.home.blog/author/sajzsoltattila/) [Gépi tanulás](https://sajozsattila.home.blog/category/gepi-tanulas/) 26th július 20193rd október 2019 7 Minutes *Napjaink igen felkapott elnevezéseinek egyike minden bizonnyal a Mesterséges Neurális Hálózat (MNH), avagy Artificial Neural Networks (ANN). Ami jórészt annak köszönhető, hogy e technológiának a mindennapi életben való alkalmazásai az emberek egy jelentős részét lenyűgözi. Az MNH az alapja sok arcfelismerő, képfeldolgozó megoldásnak, a Google-fordítónak vagy a Facebookhirdetés optimalizációjának, hogy csak néhányat említsek. Mai posztomban a legegyszerűbb MNH-t, az un. Feedforward* [\(https://en.wikipedia.org/wiki/Feedforward\\_neural\\_network\)](https://en.wikipedia.org/wiki/Feedforward_neural_network)*-típust törekszem egy kicsit részletesében bemutatni.*

Kezdjük a neurális hálózat részeivel! Ehhez rajzoltam egy diagramot:

Elsőre talán bonyolultnak látszik, de valójában nagyon egyszerű. Ha jól megnézzük a fenti ábrát, láthatjuk, hogy csupán két fajta objektumból épül fel:

- a körök az úgynevezett neuronok. Ezek végzik a számítást.
- a nyilak a neuronok közötti kapcsolatokat jelölik. A fenti ábrán minden neuron kapcsolódik minden neuronhoz a következő rétegben. Ezt az elrendezést "teljesen csatolt" rendszernek nevezzük. (Van olyan eset is, amikor ez nem így van. Ilyenkor "részlegesen csatolt" a rendszer, de a mi példánk nem ilyen.)

Az alapelemek nem véletlenszerűen helyezkednek el a térben, hanem rétegekbe rendezve.

#### Három rétegtípusról beszélhetünk:

- Bemeneti réteg gondolom, senkit nem lepek meg, ha azt mondom, hogy a megfigyelt adatok itt érkeznek a hálózatba. Ebből a rétegből jobbára csak egy van (a kivételekkel most nem foglalkozunk). A rétegben elhelyezkedő neuronok mind egy-egy tulajdonságot, megfigyelési dimenziót jelölnek.
- Rejtett réteg a számítások helye. Ennek a rétegnek a célja modellezni a bemeneti rétegben feltüntetett tulajdonságok kapcsolatát. (A fenti példában egy rejtett réteg van, de voltaképpen akármennyi követheti egymást, akár elhagyhatjuk is ezt a réteget.)
- Kimeneti réteg beszédes neve szerint ez az utolsó réteg, az MNH eredményének helye.

### Most nézzük a többi kifejezést az ábrán:

- az *n* tulajdonság megfigyelt értéke
- a rejtett réteg neuronjára jellemző eltolás

- a bemeneti és a rejtett réteg közötti kapcsolatokhoz rendelt súlyok. Az indexek a rétegeknek megfelelő neuronokat jelölik. Pl: a bementi réteg 1. neuronját köti össze a rejtett réteg 2. neuronjával.
- a rejtett réteg aktivációs függvénye. Erről később lesz szó. Most csak azt vegyük észre, hogy a réteg összes neuronján megegyezik.
- az aktivációs függvény az előző réteg kimenetéből és a súlyokból számolt bemenete.
- a kimeneti réteg neuronjára jellemző eltolás.
- a rejtett és a kimeneti réteg közötti kapcsolatok súlyai. Az indexelés ugyanazon az elven működik, mint a -nél.
- a kimeneti réteg aktivációs függvénye, hasonlóan a rejtett réteghez, a rétegen belül minden neuronon ugyanaz.
- a kimeneti réteg aktivációs függvényének bemenete.
- a hálózat végső eredménye.

Most, hogy ismerjük a MNH részeit, nézzük, hogyan mozog az adat a rendszeren belül. Ehhez idézzük fel, hogy minden felügyelettel végrehajtott tanulás lényegében három részből áll:

- 1. Alkalmazzuk a már meglévő ismereteinket egy megfigyelésen, azaz az eddigi ismereteink alapján kiszámoljuk, hogy mi lehet a megfigyelés eredménye.
- 2. Összevetjük az előző lépésben kiszámított eredményt a tényleges eredménnyel. Ha a kettő [nem egyezik meg, akkor kalkuláljuk az eltérés mennyiségét és irányát. Lényegében Loss](https://sajozsattila.home.blog/2019/04/03/statisztika-alapok-a-loss-fuggveny/) kalkulációt (https://sajozsattila.home.blog/2019/04/03/statisztika-alapok-a-lossfuggveny/) végzünk.
- 3. Korrigáljuk az ismereteinket, annak megfelelően, hogy mekkora és milyen az előző pontban kiszámított hiba.

A Feedforward-típusú MNH első lépését nevezzük Lejátszásnak (Forward propagation), a másodikat a Hibaszámításnak, míg az utolsót a Visszajátszásnak (Back propagation). Gondolom, senkit se lepek meg, ha elárulom, hogy a lejátszás során az adatok a Bemeneti réteg felől a Kimeneti réteg felé haladnak. Az első ábrám ezt a lépést szemlélteti. Ezzel szemben a Visszajátszás során az ellenkező irányba haladunk:

Most, hogy ismerjük a hálózat alapvető felépítését, nézzük meg, mi a konkrét kivitelezése az egyes lépéseknek.

### Lejátszás — Előrejelzés

Mint fentebb említettem, az összes számítás a neuronokban történik. De mit is csinál egy [neuron? Lényegében hipersíkokat \(https://sajozsattila.home.blog/2019/06/19/hipersik](https://sajozsattila.home.blog/2019/06/19/hipersik-linearis-algebra-pythonban/)linearis-algebra-pythonban/)állít elő. Magát a konkrét számítást, amit végez, így lehetne megjeleníteni:

A fenti ábra a j rejtett rétegbeli neuron működését szemlélteti, de minden, nem a Bemeneti rétegben elhelyezkedő neuron ugyanígy működik. Első lépésben összeadja a bemeneti adatok súlyozott értekét. Ez lesz a . Vegyük észre, hogy van egy bemeneti érték, ami mindig 1, ez az eltolás. Vagyis:

$$z_j = w_{0j} + \sum_{i=1}^n x_i w_{ij}$$

Majd ezen a -én alkalmazza a aktivációs függvényt. És ezzel kész is van. A függvény kimeneti értéke már megy is a neuron kimenetére. Miért kell az aktivációs függvény? Azért használjuk, hogy a lineárisan nem elválasztható feladatokat is meg tudjunk oldani.

Hogy ne csak elméletben legyünk képesek megoldani ezt a feladatot, számszerűsítsük a fenti modellt, valahogy így:

Mivel elég kusza lett volna, ha minden számot feltűntetek a fenti ábrán, csak néhány értéket ábrázoltam. A teljes kezdeti állapot legyen a következő:

$$x = \begin{bmatrix} 0,05\\0,1 \end{bmatrix}$$

$$w = \begin{bmatrix} 0,15 & 0,25 & 0,35 \\ 0,45 & 0,55 & 0,65 \\ 0,75 & 0,85 & 0,95 \end{bmatrix}$$

$$v = \begin{bmatrix} 0, 2 & 0, 3 & 0, 4 & 0, 5 \\ 0, 6 & 0, 7 & 0, 8 & 0, 9 \end{bmatrix}$$

Nézzük az első neuront a Rejtett rétegben. Ennek a értéke az (1) alapján:

$$(5)$$
  $z_1 = 1 \cdot 0, 35 + 0, 05 \cdot 0, 25 + 0, 1 \cdot 0, 35 = 0, 1975$ 

Aki egy kicsit járatos a lineáris algebrában, az már biztosan rájött, hogy nem kell minden neuront külön-külön kiszámítanunk, hanem a számítást rétegenként egyszerre elvégezhetjük:

```
1
2
3
4
    import numpy as np
    # megfigyelés
    x = np.array([.05, .1])
```

```
5
 6
 7
 8
 9
10
11
12
13
14
     # rejtet réteg súlyai
     w = np.array([[.25,.35],[.55, .65],[.85, .95]])
     # rejtett réteg eltolás
     w0 = np.array([[.15],[.45],[.75]])
     # rejtett rétek z érték
     z = (np.concatenate((w0, w), axis=1))@np.insert(x,0,1,axis=0)
```

Aminek az eredménye:

$$z = \begin{bmatrix} 0.1975 \\ 0.5425 \\ 0.8875 \end{bmatrix}$$

A következő lépésben át kell engednünk ezt az eredményt a rejtett réteg aktivációs függvényén. Ez a 3. ábra szerint, egy függvény. Vagyis:

$$f_r(z) = 1 - \frac{2}{e^{2z} + 1}$$

Ugye, ez az első neuron esetén:

$$f_r(z_1) = 1 - \frac{2}{e^{2z_1} + 1} \approx 0.194972$$

A teljes rejtett rétegre:

```
1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
     class Tanh():
         def run(self, x):
             return 1-(2/(np.exp(2*x)+1))
         def derivate(self, x):
             return 4*np.exp(2*x)/(np.exp(2*x)+1)**2
     # rejtett réteg aktivációs függvény
     f_r = Tanh()
     # rejtett réteg kimenet
     o_r = f_r.run(z)
```

Az eredmény pedig:

$$o_r = \begin{bmatrix} 0.19497153 \\ 0.49487804 \\ 0.71015674 \end{bmatrix}$$

A Rejtett réteget be is fejeztük. Most ismételjük meg ugyanezeket a lépéseket a Kimeneti rétegben. A lépések ugyanezek, az egyetlen különbség, hogy az aktivációs függvény ReLU lesz:

$$f_k(u) = max(0, u)$$

Ne is húzzuk az időt, nézzük mi a Kimeneti réteg eredménye:

```
1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13
14
15
16
17
     class ReLU():
         def run(self, x):
             return np.maximum(0,x)
         def derivate(self, x):
             x[x0] = 1
             return x
     # kimeneti réteg súlyai
     v = np.array([[0.3,0.4,0.5],[0.7,0.8,0.9]])
     # kimeneti rétek eltolása
     v0 = np.array([[.2],[.6]])
     # kimeneti réteg
     u = (np.concatenate((v0, v), axis=1))@np.insert(o_r,0,1,axis=0)
     f_k = ReLU()
     o = f_k.run(u)
```

Aminek az eredményei:

$$u = \begin{bmatrix} 0.81152104 \\ 1.77152357 \end{bmatrix}$$

Mind a két szám pozitív, így nem meglepő módon a ReLU aktivációs függvény nem változtat rajtuk:

$$o = \begin{bmatrix} 0.81152104 \\ 1.77152357 \end{bmatrix}$$

Végére is értünk a Lejátszási szakasznak.

A következő lépésben meg kell néznünk, hogy mekkora hibát követtünk el, és a beállításokat ennek megfelelően kell frissítenünk. Ezt fogjuk a következő blogbejegyzésben [\(https://sajozsattila.home.blog/2019/07/31/mesterseges-neuralis-halozat-alapjai-2-resz/\)](https://sajozsattila.home.blog/2019/07/31/mesterseges-neuralis-halozat-alapjai-2-resz/) megtárgyalni.

### Irodalom

- 1. Assaad Moawad: Neural networks and back-propagation explained in a simple way [\(https://medium.com/datathings/neural-networks-and-backpropagation-explained-in-a](https://medium.com/datathings/neural-networks-and-backpropagation-explained-in-a-simple-way-f540a3611f5e)simple-way-f540a3611f5e)
- 2. Matt Mazur: A Step by Step Backpropagation Example [\(https://mattmazur.com/2015/03/17/a-step-by-step-backpropagation-example/\)](https://mattmazur.com/2015/03/17/a-step-by-step-backpropagation-example/)
- 3. John McGonagle, George Shaikouski, Christopher Williams, Andrew Hsu, Jimin Khim: [Backpropagation \(https://brilliant.org/wiki/backpropagation/\)](https://brilliant.org/wiki/backpropagation/)

#### **Címke:**

[Mesterséges Neurális Hálózat](https://sajozsattila.home.blog/tag/mesterseges-neuralis-halozat/)

### Közzétéve: sajzsoltattila

*[sajzsoltattila összes bejegyzése](https://sajozsattila.home.blog/author/sajzsoltattila/)*

## "A Mesterséges Neurális Hálózat alapjai – 1. rész" bejegyzéshez 4 hozzászólás

Visszajelzés: [Mesterséges Neurális Hálózat alapjai – 2. rész – Sajó Zsolt Attila](https://sajozsattila.home.blog/2019/07/31/mesterseges-neuralis-halozat-alapjai-2-resz/)

[Szerkesztés](https://sajozsattilahome.wordpress.com/wp-admin/comment.php?action=editcomment&c=130) |

Visszajelzés: Ismétlődő [Neurális Hálózat – Sajó Zsolt Attila](https://sajozsattila.home.blog/2019/11/25/ismetlodo-neuralis-halozat/) [Szerkesztés](https://sajozsattilahome.wordpress.com/wp-admin/comment.php?action=editcomment&c=692) |

[Visszajelzés: Hosszú munkamemóriájú Neurális Hálózat Kerassal — 2. rész – Sajó Zsolt](https://sajozsattila.home.blog/2019/12/06/hosszu-munkamemoriaju-neuralis-halozat-kerassal-2-resz/)

Attila [Szerkesztés](https://sajozsattilahome.wordpress.com/wp-admin/comment.php?action=editcomment&c=697) |

Visszajelzés: [Konvolúciós Neurális Hálózat – 2. rész – Sajó Zsolt Attila](https://sajozsattila.home.blog/2021/06/01/konvolucios-neuralis-halozat-2-resz/) [Szerkesztés](https://sajozsattilahome.wordpress.com/wp-admin/comment.php?action=editcomment&c=809) |

[WordPress.com ingyen](https://wordpress.com/?ref=footer_website)[es honlap vagy saját honlap létrehozása.](https://wordpress.com/advertising-program-optout/) Do Not Sell or Share My Personal Information (készítette: [Raam Dev](http://raamdev.com/)).