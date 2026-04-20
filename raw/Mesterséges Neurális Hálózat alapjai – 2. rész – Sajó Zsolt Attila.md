#### **[Sajó Zsolt Attila](https://sajozsattila.home.blog/)**

Gépi tanulás és néhány más dolog

☰ **Menü**

# Mesterséges Neurális Hálózat alapjai – 2. rész

[sajzsoltattila](https://sajozsattila.home.blog/author/sajzsoltattila/) [Gépi tanulás](https://sajozsattila.home.blog/category/gepi-tanulas/) 31st július 20193rd október 2019 8 Minutes *Az előző részben (https://sajozsattila.home.blog/2019/07/26/mesterseges-neuralis-halozat-alapjai-1 [resz/\) átnéztük, a Neurális Hálózat részeit és a lejátszási szakaszt. Most folytassuk a Hibaszámítássa](https://sajozsattila.home.blog/2019/07/26/mesterseges-neuralis-halozat-alapjai-1-resz/)l és a Visszajátszással*! 

## Hibaszámítás

Az előző részben, a lejátszás végén kaptunk egy előrejelzést a bemeneti adatok alapján. A konkrét példánk esetében ez így alakult:

$$o = \begin{bmatrix} 0.81152104 \\ 1.77152357 \end{bmatrix}$$

Mivel felügyelettel végrehajtott tanulást végzünk ismerjük a bemeneti adatok tényleges eredményét. Semmi akadálya tehát, hogy összevessük ezt az eredményt az MNH előrejelzésével. Nem meglepő, hogy a kettő különbsége lesz az előrejelzés hibája. Több módon számíthatjuk ezt az értéket, az egyetlen megkötés, hogy részekben deriválható legyen. A legegyszerűbb, és amit itt mi is alkalmazunk, a négyzetes hiba:

(2) 
$$E = \frac{(y-o)^2}{2}$$

Ahol:

- a Hiba
- a valós eredmény

Számítsuk is ki a korábbi példán, legyen mondjuk a tényleges eredmény:

$$y = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$$

Ennek megfelelően a Hiba:

```
1
2
3
4
    y = np.array([0,1])
    e = 0.5*(y-o)**2
    print("Teljes hiba: ", sum(e))
```

Aminek az eredménye:

$$E = \begin{bmatrix} 0.3292832\\ 0.29762431 \end{bmatrix}$$

Ezzel a lépéssel készek is vagyunk. Most már csak tanulnunk kell a tévedésből, ez lesz a Visszajátszás.

# Visszajátszás

Ebben a lépésben frissítjük a Hálózat beállításait annak megfelelően, hogy mekkora részben járultak hozzá az előző lépésben számított Hibához. Ezt a frissítést most visszafelé haladva hajtjuk végre a rendszeren. Vagyis az adatáramlás így alakul:

Hogy miért visszafelé tesszük ezt ? Ennek számítástechnikai oka van, amit majd lentebb bemutatok.

De mit is frissítünk konkrétan? Ha valaki odafigyelt, akkor nyilvánvaló a számára, hogy az MNH-nak csupán egyetlen része nem fixen meghatározott: a súlyok. A visszajátszás során ezeket állítjuk. Ugye, így szabályozzuk, hogy az előző rétegben az egyes tulajdonságoknak mekkora szerepük legyen az adott neuron kimeneti értékében.

Most nézzük magát a konkrét számítást! Ez egy minimalizációs probléma: azt szeretnénk, hogy a Hiba minél kisebb legyen. És a Hiba ott a legkisebb, ahol a deriváltja nulla. Legalábbis elméletileg. A gyakorlatban lehetségesek olyan lokális minimumok, amelyek kielégítik ezt a feltételt, és mégsem a legjobb megoldások. Amint azt a nevük is mutatja, csak lokálisan a legjobbak. Ezt mindig tartsuk az észben! A MNH csupán azt garantálja, hogy a lokális minimumot megtaláljuk, de azt nem, hogy ez valóban a legjobb megoldás a lehetséges megoldások végtelenjében.

### A kimeneti réteg súlyainak hibája

Térjünk vissza a számításra! Az első lépésben azt nézzük meg, hogy a Kimeneti réteg egyes súlyainak mekkora szerepük volt a Hibában. Ezt az értéket fogjuk gradiensnek nevezni. Hogy ezt kiszámoljuk, deriválnunk kell a Hibát az egyes súlyokra. Nézzünk egy konkrét példát, a súlyt:

$$\frac{\partial E_{o_1}}{\partial v_{11}}$$

Vegyük észre, hogy a csak egyetlen egy hibához, a hibájához járul hozzá. Az teljesen független tőle. Ugye, a (2)-ben nem szerepel a , tehát ez a parciális deriválás nem lesz egy lépésben elvégezhető művelet. A láncszabályt

[\(https://hu.wikipedia.org/wiki/L%C3%A1ncszab%C3%A1ly\)h](https://hu.wikipedia.org/wiki/L%C3%A1ncszab%C3%A1ly)asználva vissza kell fejtenünk az egyenletet a keresett súlyig. Először is írjuk fel a Hibát, úgy, hogy lássuk a keresett elemet:

(6) 
$$E = 0.5 \cdot (y - f_k(v_p o_r))^2$$

Most már látjuk a súlyokat. Úgyhogy felírhatjuk a parciális deriváltak sorát. Először deriváljuk a -t az -hez tartozó hibából:

$$\frac{\partial E_{op}}{\partial o_p} = o_p - y_p$$

Lépjünk egyel visszább, most az -ból a -t. Ez egy kicsit trükkösebb, mivel a ReLU nem deriválható egy az egyben, csak két részben: külön eset ha u kisebb, mint 0 és külön eset, ha nagyobb.

$$\frac{\partial f_k(u_p)}{\partial u_p} = \begin{cases} 1 & \text{ha } u_p > 1\\ 0 & \text{ha } u_p <= 0 \end{cases}$$

És a következőben már meg is érkeztünk a -hoz. Vegyük észre, hogy itt a deriváltnál szintén két lehetőség van: 1 ha az eltolásra deriválunk, és 1 ha bármelyik másra:

$$\frac{\partial u_p}{\partial v_{mp}} = \begin{cases} o_r & \text{ha } p > 0\\ 1 & \text{ha } p = 0 \end{cases}$$

A fentieknek megfelelően a Hiba -ra számolt részderiváltja:

$$_{(10)} \quad \frac{\partial E_{o_1}}{\partial v_{11}} = \frac{\partial E_{o_1}}{\partial o_1} \cdot \frac{\partial f_k(u_1)}{\partial u_1} \cdot \frac{\partial u_1}{\partial v_{11}}$$

Ami behelyettesítve:

$$\frac{\partial E_{o_1}}{\partial v_{11}} = (o_1 - y_1) \cdot 1 \cdot o_r = 0, 1582235$$

Ez azt fejezi ki, hogy mekkora részben felelős a a Hibáért. Mivel csökkenteni akarjuk a hibát, ezért az így kapott eredményt ki kell vonnunk a jelenleg beállított súlyból, hogy a következő alkalommal jobb eredményt kapjunk. Ennek megfelelően a frissített súly így alakul:

$$v_{11} = v_{11} - \eta \frac{\partial E_{o_1}}{\partial v_{11}}$$

Ahol:

 [— a tanulási ráta. Erre most nem térek ki, maradjunk annyiban, hogy gradient descent](https://en.wikipedia.org/wiki/Gradient_descent) (https://en.wikipedia.org/wiki/Gradient\_descent)tanulást alkalmazunk.

Gondolom, már mindenki rájött, hogy a lejátszáshoz hasonlóan, ezt se kell egyesével számolni a neuronokra. Rétegenként is elvégezhetjük egyszerű lineáris algebrával:

$$1 \mid v_{gradient} = np.insert(o_r, 0, 1, axis=0) * ((o-y)*f_k.derivate(u)$$

Ami ebben a példában:

$$\frac{\partial E}{\partial v_{mp}} = \begin{bmatrix} 0,81152104 & 0,1582235 & 0,40160394 & 0,57630714 \\ 0,77152357 & 0,15042513 & 0,38181007 & 0,54790266 \end{bmatrix}$$

Most már csak frissíteni kell ezzel az értékkel a kimeneti réteg súlyait a (12)-nek megfelelően. De mielőtt ez megtennénk számoljuk ki a Rejtett réteg súlyainak gradienseit. Ajánlott előszőr minden gradienst kiszámolni és csak utána frissíteni az összes súlyt. Miért? Mindjárt kiderül.

#### A Rejtett réteg súlyainak hibája

Az alapvető eljárás ugyanaz lesz itt is mint a Kimeneti réteg esetében, azzal az eltéréssel, hogy itt még visszább kell fejteni a láncszabály segítségével. Ami még megbonyolítja az életünket, az az, hogy a Rejtett rétegben nem csak 1 irányból érkezik az adat, hanem a Kimeneti rétegben lévő minden neurontól. Nézzük például a súlyt:

A fenti ábrán pirossal jelöltem, honnan származnak az információk, amelyeket ennek a súlynak a frissítésére használunk. Egyértelmű a különbség a Kimeneti réteghez képest. Ott a neuronokra csak egy irányból érkezett információ, ezzel szemben a Rejtett rétegben az előző rétegben lévő minden neuron befolyásolja, hogy milyen módon frissítjük a súlyt. Ennek megfelelően a -nak megfelelő parciális derivált a következő lesz:

$$\frac{\partial E}{\partial w_{11}} = \frac{\partial E}{\partial o_{r1}} \cdot \frac{\partial f_r(z_1)}{\partial z_1} \cdot \frac{\partial z_1}{\partial w_{11}}$$

Ahol:

$$_{ullet}$$
  $O_{r1}$  — a Rejtett réteg 1. neuronjának kimenete

Vegyük észre, hogy menyire hasonlít ez a (10). egyenletre. Számítása is hasonló lesz, csak az első részderivált okozhat némi problémát. Ez a rész arra válaszol, hogy összességében mekkora hibát generált ez a súly a következő rétegen. Vagyis:

$$\frac{\partial E}{\partial o_r} = \frac{\partial E_{o_1}}{\partial o_{r1}} + \frac{\partial E_{o_2}}{\partial o_{r1}}$$

Hogyan valósítsuk meg ezt a gyakorlati életben? Úgy, hogy a Visszajátszás során minden előző rétegben kiszámoljuk, ezt az értéket, és csak ezt passzoljuk vissza az előző rétegnek. Ez a magyarázata annak, amiért nem frissítjük a súlyokat egyből, amint kiszámoljuk a hibájukat. Ha így tennénk az összeadás elemei megváltoznának.

Az összeadásban szereplő elemeket meg így általánosíthatjuk:

$$\frac{\partial E_{op}}{\partial o_{rm}} = \frac{\partial E_{op}}{\partial o_p} \cdot \frac{\partial f_r(u_p)}{\partial u_p} \cdot \frac{\partial u_p}{\partial v_{mp}}$$

Pythonban:

1 elozo\_retek\_hiba = np.sum(v\*((o-y)\*f\_k.derivate(u)).reshape(1,-1).T, axis=0)

A Kimeneti rétegben megismert módon számíthatjuk ennek a rétegnek a hibáit is:

1 | w\_gradient = np.insert(x,
$$0$$
,1,axis= $0$ ) \* ( elozo\_retek\_hiba \* f\_r. $\alpha$ 

A konkrét számtani példánál maradva az eredmény pedig a következő:

$$\frac{\partial E}{\partial w_{mp}} = \begin{bmatrix} 0,75373805 & 0,0376869 & 0,07537381 \\ 0,71116975 & 0,03555849 & 0,07111697 \\ 0,54531045 & 0,02726552 & 0,05453104 \end{bmatrix}$$

### A Súlyok frissítése

Most már, hogy ismerjük az össze súly hibáját, nyugodtan frissíthetjük őket a (12)-nak megfelelően:

```
1
2
3
4
5
    eta = 0.002
    v = v-eta*v_gradient[:,1:] 
    v0 = (v0.T - eta*v_gradient[:,0]).T 
    w = w-eta*w_gradient[:,1:]
    w0 = (w0.T - eta*w_gradient[:,0]).T
```

Aminek megfelelően az új súlyok a következők lesznek:

$$w = \begin{bmatrix} 0,14849252 & 0,24992463 & 0,34984925 \\ 0,44857766 & 0,54992888 & 0,64985777 \\ 0,74890938 & 0,84994547 & 0,94989094 \end{bmatrix}$$

$$v = \begin{bmatrix} 0,19837696 & 0,29968355 & 0,39919679 & 0,49884739 \\ 0,59845695 & 0,69969915 & 0,79923638 & 0,89890419 \end{bmatrix}$$

## Befejezés

Ezzel készen is vagyunk. Átnéztük a MNH alapvető lépéseit és elemeit. Napjainkban már persze egy rakás szoftver könyvtár elérhető MNH megvalósítására, és általában azokat használjuk a gyakorlati életben. Viszont, ha anélkül használunk valamit, hogy valóban értenénk a működését, fennáll a veszélye annak, hogy az "mágiává" válik. Sokszor mint valami Delphoi orákulumot kezelik a Neurális Hálózatokat. Ami sajnos magával hozza a rossz felhasználásokat is. Ez a lehetőség maga is megérne egy újabb bejegyzést, de nem részletezem, hanem végszó gyanánt álljon itt két fontos megjegyzés:

- 1. Minden MNH annyit ér, amennyit az adat, amivel tanítjuk.
- 2. Csak a lokális legjobb válasz megtalálása garantált.

#### **Címke:**

[Mesterséges Neurális Hálózat](https://sajozsattila.home.blog/tag/mesterseges-neuralis-halozat/)

## Közzétéve: sajzsoltattila

*[sajzsoltattila összes bejegyzése](https://sajozsattila.home.blog/author/sajzsoltattila/)*

# "Mesterséges Neurális Hálózat alapjai – 2. rész" bejegyzéshez 2 hozzászólás

Visszajelzés: [A Mesterséges Neurális Hálózat alapjai – 1. rész – Sajó Zsolt Attila](https://sajozsattila.home.blog/2019/07/26/mesterseges-neuralis-halozat-alapjai-1-resz/)

[Szerkesztés](https://sajozsattilahome.wordpress.com/wp-admin/comment.php?action=editcomment&c=141) |

Visszajelzés: Ismétlődő [Neurális Hálózat – Sajó Zsolt Attila](https://sajozsattila.home.blog/2019/11/25/ismetlodo-neuralis-halozat/) [Szerkesztés](https://sajozsattilahome.wordpress.com/wp-admin/comment.php?action=editcomment&c=693) |

[WordPress.com ingyenes honlap vagy saját honlap létrehozása](https://wordpress.com/?ref=footer_website)[.](https://wordpress.com/advertising-program-optout/) Do Not Sell or Share My Personal Information (készítette: [Raam Dev](http://raamdev.com/)).