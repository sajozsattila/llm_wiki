#### Sajó Zsolt Attila

# A túlillesztés problémája

å sajzsoltattila ► Gépi tanulás, Statisztika ② 2nd január 20202nd január 2020 

Minutes

A mai bejegyzésben egy olyan problémáról fogunk beszélni, ami minden statisztikai elemzés szenved. Sőt igazából tovább mennék, valamibe, amitől rengetek ember is szenved.

## Általánosítás vs. Specializáció

Minden modell a világ valamilyen szintű egyszerűsítése, aminek egyszerű számítástechnikai oka van: ahhoz, hogy a világot a teljesen részleteiben leírjuk annyi információ kellene tárolnunk mint maga a világ. Ez meg egyértelműen lehetetlen.

Vagyis a tanulmányozott rendszereinknek mindig van egy része, amit nem vagyunk képesek megmagyarázni. Amikor modellt építünk, a rendelkezésünkre álló információból ki kell választanunk azt, amit a modell le tud írni és amit nem. A kérdés, hogy tehetjük ezt meg?

A bevett gyakorlat erre, hogy a megfigyeléseinket két csoportba osztjuk: tréning és teszt adatokra. A tréning adatok ami alapján létrehozzuk, tanítjuk a modellünk, a teszt ami segítségével mérjük a modell teljesítményét.

Az emberi elme, és az általunk létrehozott gépi tanulás igen erős mintázatok keresésében. Annyira jó, hogy gyakran ott is összefüggéseket vél felfedezni, ahol nincs. Ennek tipikus esete, mikor túlhajtjuk a tréning adatok elsajátítását. Vagyis megtanulunk minden apró különbséget a tréning adatokon belül.: képzelt mintázatokat fedezünk fel benne, és ezeket beépítjük a modellünkbe. Úgy is mondhatnák, hogy specializálódunk a tréning adatok megoldására. Ezzel az a probléma, hogy amikor a tréning alatt nem látott esetet fogunk észlelni, akkor nem fogjuk tudni azt a helyén kezelni, vagyis nem tudunk általánosítani. Ezt a problémát nevezzük a túlillesztés problémájának.

Erre fogunk most egy példát nézni egy Feed Forward Neurális Hálózaton.

### Az igaz rendszer

Szintetikus megfigyelések esetén abban a kényelmes helyzetben vagyunk, hogy ismerjük az igazi modellt, amiből a megfigyelések származnak. Az esetünkben ez egy binominális klasszifikációs modell lesz, amiben a két osztály határát a következő polinom egyenlet adja meg:

$$(1) \quad y = \beta_0 + x \cdot \beta_1 + x^2 \cdot \beta_2 + x^3 \cdot \beta_3$$

Vegyünk néhány mintát:

```
     import numpy as np
     b = np.random.rand(4)
     x = np.linspace(-10,10,5000)
     y = b[0]+x*b[1]+np.power(x,2)*b[2]+np.power(x,3)*b[3]
     n = 750
     minta_x = x.copy()
     zaj = np.random.normal(0, 50, n)
     np.random.shuffle(minta_x)
     minta_x = minta_x[:n]
     minta_y = b[0]+minta_x*b[1]+np.power(minta_x,2)*b[2]+np.power(minta_x,2)*b[3]+zaj
     osztaly = [ 1 if z >= 0 else -1 for z in zaj ]
```

### Példa túlillesztésre

A túlillesztés szemléltetéséhez 15 megfigyeléssel fogok magas epoch számmal tanítani egy mély Feed Forward Neurális Hálózatot. Először kiválasztok 15 mintavételt:

```
   trainsize = 15
   train_X = np.array([ list(i) for i in zip(minta_x, minta_y) ][:trainsize])
   train_y = np.array([ [0,1] if c == 1 else [1,0] for c in osztaly[:trainsize] ])
   test_X = np.array([ list(i) for i in zip(minta_x, minta_y) ][trainsize:])
   test_y = np.array([ [0,1] if c == 1 else [1,0] for c in osztaly[trainsize:] ])
```

Majd definiálok egy 4 rejtett rétegű Neurális Hálózatot Keras-sal, és tanítom:

```
    from keras.models import Sequential
    from keras.layers import Dense
    from keras.models import Sequential
    from keras.layers import Dense
    model = Sequential()
    model.add(Dense(trainsize*2, activation = 'relu', input_dim=2))
    model.add(Dense(trainsize*3, activation = 'relu'))
    model.add(Dense(trainsize*4, activation = 'relu'))
    model.add(Dense(trainsize*5, activation = 'relu'))
    model.add(Dense(2, activation = 'softmax'))
    model.compile(loss='binary_crossentropy', optimizer='adam')
    history = model.fit(train_X, train_y, batch_size=1, epochs=200, validation_data=(test_X,test_y))
```

Nézzük, hogy alakul a modell teljesítménye a teszt és a tréning adatokon:

A fenti ábra egy elég tipikus ábra túlillesztés esetén. A Loss [\(https://sajozsattila.home.blog/2019/04/03/statisztika-alapok-a-loss-fuggveny\)a](https://sajozsattila.home.blog/2019/04/03/statisztika-alapok-a-loss-fuggveny) tréning adatokon szinte folyamatoson csökken, míg teszt adatokon ezzel ellentétes folyamat figyelhető meg.

### Mit lehet tenni?

Több módon is megpróbálhatjuk elkerülni a fenti problémát:

- Regularization az összetettebb modellek büntetése az egyszerűekkel szemben
- Dropout réteg ez egy speciális réteg Neurális Hálózatokra, lesz róla szó a blogban később
- Több adat minél több az adat, annál nehezebb ott is mintát találni ahol nincs

A [Dropout \(https://sajozsattila.home.blog/2019/09/09/dropout-reteg\)-](https://sajozsattila.home.blog/2019/09/09/dropout-reteg)ról és a [Regularization \(https://sajozsattila.home.blog/2020/01/02/regularization\)-](https://sajozsattila.home.blog/2020/01/02/regularization)ről a későbbiekben lesz szó a blogon.

#### <span id="page-4-0"></span>Lábjegyzet

1. Angolul: overfitting

#### Irodalom

Will Koehrsen: Overfitting vs. Underfitting: A Complete Example [\(https://towardsdatascience.com/overfitting-vs-underfitting-a-complete-example](https://towardsdatascience.com/overfitting-vs-underfitting-a-complete-example-d05dd7e19765)d05dd7e19765)

#### **Címke:**

[Mesterséges Neurális Hálózat,](https://sajozsattila.home.blog/tag/mesterseges-neuralis-halozat/) [Overfitting](https://sajozsattila.home.blog/tag/overfitting/), [Túlillesztés](https://sajozsattila.home.blog/tag/tulillesztes/)

## Közzétéve: sajzsoltattila
