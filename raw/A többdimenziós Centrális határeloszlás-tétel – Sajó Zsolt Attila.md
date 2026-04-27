#### **[Sajó Zsolt Attila](https://sajozsattila.home.blog/)**

# A többdimenziós Centrális határeloszlás-tétel

[sajzsoltattila](https://sajozsattila.home.blog/author/sajzsoltattila/) [Statisztika](https://sajozsattila.home.blog/category/statisztika/) 17th április 202014th április 2020 2 Minutes *[Egy korábbi bejegyzésben \(https://sajozsattila.home.blog/2019/05/09/centralis-hatareloszlas-tetel](https://sajozsattila.home.blog/2019/05/09/centralis-hatareloszlas-tetel-statisztika-lapok/)statisztika-lapok/) láttuk a Centrális határeloszlás-tétel (CHT) alapjait. Most egy kicsit tovább visszük ezt és megnézzük mi a helyzet több dimenzió esetén.*

Több dimenzió esetén a megfigyeléseinket felfoghatjuk vektoroknak is, mi is ezt fogjuk tenni. Ha így teszünk – nem túl nagy logikai ugrással – úgy tekinthetünk a CHT-ra mint véletlenszerű vektorok átlagára vonatkozó tételre.

Ennek megfelelően az előző bejegyzésben szereplő (3)-ast felírhatjuk így:

(1) 
$$\sqrt{n}(\bar{X} - \mu) \xrightarrow[n \to \infty]{d} N_d(0, \Sigma)$$

És a (4)-est pedig mint:

(2) 
$$\sqrt{n} \cdot \Sigma^{-1/2} \cdot (\bar{X} - \mu) \xrightarrow[n \to \infty]{d} N_d(0, I_d)$$

Ahol:

- a
- a valós populáció átlag
- *d* dimenziójú egységmátrix [\(https://hu.wikipedia.org/wiki/Egys%C3%A9gm%C3%A1trix\)](https://hu.wikipedia.org/wiki/Egys%C3%A9gm%C3%A1trix)
- a mintaátlag
- megfigyelések száma
- d dimenziójú normál eloszlás [\(https://en.wikipedia.org/wiki/Multivariate\\_normal\\_distribution\)](https://en.wikipedia.org/wiki/Multivariate_normal_distribution)

Ebből az egészből egyedül a értéke igényel egy kis figyelmet. Látni kell, hogy a egy *d* x *d* dimenziójú mátrix lesz amire igaz, hogy:

(3) 
$$\Sigma^{-1/2} \cdot \Sigma^{-1/2} = \Sigma^{-1}$$

Ez a szerencsénk, mivel Covariance mátrixról beszélünk, tudjuk, hogy az értéke mindig pozitív, tehát a fenti feltétel mindig igaz.

### Példa

Nézzük a következő esetet: van n darab d dimenziós i.i.d megfigyelésünk az X eloszlásból. Nevezzük őket  $X_1, X_2, \ldots X_n$ -nek. Ezeknek a megfigyeléseknek az átlaga egy szintén d dimenziós vektor a E[X] vagy másképpen  $\mu_X$ .

Legyen Y ennek az X-nek a függvénye, mégpedig:  $Y=v^T\cdot X$ . Ahol v egy vektor, amire igaz, hogy  $v\in\mathbb{R}_d$ . Vagyis a különböző dimenziók irányában nem feltétlen egyforma a transzformációnk, de minden X értéket ugyanazzal a vektorral módosítunk. Ennek megfelelően az átlaga:

$$_{(4)} \quad E[Y] = v^T \cdot E[X]$$

A szórásnégyzete pedig a lineáris algebrának megfelelően felírva: <sup>2</sup>

(5) 
$$Var(Y) = v^T \cdot \Sigma_X \cdot v$$

A Centrális határeloszlás-tétel alapján ilyenkor az Y-re igaz, hogy:

(6) 
$$\sqrt{n}(\bar{Y} - v^T \cdot E[X]) \xrightarrow[n \to \infty]{d} N_d(0, v^T \cdot \Sigma_X \cdot v)$$

## <span id="page-1-0"></span>Lábjegyzet

- 1. Na jó, nem mindig. Ha a szórás 0 akkor nem, de ezek extrém esetek.
- 2. Ugye a  $Var(a \cdot X) = a^2 \cdot Var(X)$ . Ami ha vektorformában írjuk fel:  $a^T \cdot Var(X) \cdot v$

#### Címke:

Centrális határeloszlás-tétel, CLT,

Normál eloszlás

# Közzétéve: sajzsoltattila
