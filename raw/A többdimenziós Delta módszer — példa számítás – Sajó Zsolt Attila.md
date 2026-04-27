### **[Sajó Zsolt Attila](https://sajozsattila.home.blog/)**

# A többdimenziós Delta módszer példa számítás

[sajzsoltattila](https://sajozsattila.home.blog/author/sajzsoltattila/) [Statisztika](https://sajozsattila.home.blog/category/statisztika/) 12th március 202015th október 2020 5 Minutes *Egy korábbi bejegyzésben megnéztük a többdimenziós Delta módszer [\(https://sajozsattila.home.blog/2020/03/11/tobbdimenzios-delta-modszer/\)](https://sajozsattila.home.blog/2020/03/11/tobbdimenzios-delta-modszer/) általános számítását. Ebben a posztban a kedvenc többparaméterű eloszlásunkon, a Gaussian-on fogom bemutatni, hogyan végezzük el a számítást.*

Legyen X egy normál eloszlás, aminek a két paramétere és . Sajnos nem tudjuk közvetlenül megfigyelni ezt a X valószínűségi változót, hanem helyette egy Y változót figyelünk meg. Erre igaz, hogy: [1](#page-4-0)

(1) 
$$Y = 2 \cdot X + 5$$

A kérdés, amire választ keresünk: Mi az és ?

Ugye itt két paramétert kell megbecsülnünk, amik nem egyeznek meg a megfigyelt (Y) változó átlagával. Ennek megfelelően a többdimenziós Delta módszert kell alkalmaznunk.

Kezdjük a Maximum likelihood számítással az Y-ra nézve. Mivel egy Gaussian eloszlás lineáris módosítása szintén egy Gaussian lesz, így tudjuk, hogy Y normál. Innen megoldhatjuk magunk vagy csak egyszerűen kinézhetjük a Wikipédiáról, hogy:

$$\hat{\mu}_Y = \bar{y} = \frac{1}{n} \sum_{i=1}^n y_i$$

$$\hat{\tau}_Y = \frac{1}{n} \sum_{i=1}^n (y_i - \bar{y})^2$$

Szintén szükségünk lesz mindkét MLE becslés Varianciájára. Ha lusták vagyunk akkor ezt is kinézhetjük a Wikipédiáról:

$$I(\mu, \tau) = \begin{bmatrix} \frac{1}{\tau_Y} & 0\\ 0 & \frac{1}{2\tau_Y^2} \end{bmatrix}$$

Ezek után végre elkezdhetjük a Delta módszert. Kezdjük először a -ek meghatározásával. Mivel két darab paramétert keresünk , vagyis *k* =2 , ez egy két dimenziós vektor lesz. Mik lesznek ezek? Ezek a függvények azt fejezik ki, hogy az egyes paraméterek, hogy változnak az Y-ban alkalmazott átalakítás következményeként.

Az elvárt érték linearitása miatt tudjuk, hogy az E[Y] megegyezik az E[X] egyszerű lineáris transzformációjával, szóval:

(5) 
$$E[Y] = 2 \cdot E[X] + 5$$

Amit ha átrendezünk akkor meg is kapjuk a -ra vonatkozó -et:

(6) 
$$g_1(x) = g_{\mu}(x) = \frac{E[Y] - 5}{2}$$

A szórásnégyzet tulajdonságai alapján az is tudjuk, hogy:

$$Var(Y) = 2^2 Var(X)$$

Amit átrendezve meg is van a második :

(8) 
$$g_2(x) = g_\tau(x) = \frac{Var(Y)}{4}$$

Tehát összegezve:

$$g(x) = \begin{bmatrix} \frac{E[Y] - 5}{2} \\ \frac{Var(Y)}{4} \end{bmatrix} = \begin{bmatrix} \frac{\mu_Y - 5}{2} \\ \frac{\tau_Y}{4} \end{bmatrix}$$

Most nézzük a -et. Mint tudjuk, egy *k* x *d* dimenziós mátrix lesz az eredmény. Mivel esetünkben csak egy dimenziós a minta adatok, így *d* = 1. Vagyis:

(10) 
$$\nabla g(x) = \begin{bmatrix} \frac{\partial}{\partial E[Y]} \frac{E[Y] - 5}{2} \\ \frac{\partial}{\partial Var(Y)} \frac{Var(Y)}{4} \end{bmatrix} = \begin{bmatrix} \frac{1}{2} \\ \frac{1}{4} \end{bmatrix}$$

Már csak a paraméterbecslés a lesz, ezért csak a konfidencia tartományának számítása maradt. Ez pedig a Delta módszer alapján:

$$\Sigma = \begin{bmatrix} \frac{1}{2} \\ \frac{1}{4} \end{bmatrix}^T \cdot \begin{bmatrix} \frac{1}{\tau_Y} & 0 \\ 0 & \frac{1}{2\tau_Y^2} \end{bmatrix}^{-1} \cdot \begin{bmatrix} \frac{1}{2} \\ \frac{1}{4} \end{bmatrix} = \frac{\tau_Y}{4} + \frac{\tau_Y^2}{8}$$
(11)

Amit már csak osztanunk kell a mintavételek számával, hogy megkapjuk a konkrét konfidencia tartományokat. Vegyük észre, hogy az végső összeadás első tagja a becslésének szórása lesz, míg a második tag a -é.

Teszteljük!

```
     import numpy as np
     from scipy import stats
     import matplotlib.pyplot as plt
     # valos paraméterek
     mu = 30
     sigma2 = 4
     n = 10000
     # 
     y_mle_mu = []
     y_mle_sigma2 = []
     x_mle_mu = []
     x_mle_sigma2 = []
     # megismételjük a mintavételt 5000x
     for j in range(5000):
         # mintavétel
         x = np.random.normal(mu, sigma2**0.5, n)
         y = 2*x+5
         y_mle_mu.append( np.mean(y) )
         y_mle_sigma2.append( np.sum( np.power(y-y_mle_mu[-1],2) )/n )
         x_mle_mu.append( (y_mle_mu[-1]-5)/2 )
         x_mle_sigma2.append( y_mle_sigma2[-1]/4 )
     # Ábra
     %matplotlib qt
     from matplotlib import rc
     plt.clf()
     plt.rc('text', usetex=True)
     plt.rc('font', family='serif')
     plt.rcParams['text.latex.unicode'] = True
     plt.subplot(1,2,1)
     plt.hist(x_mle_mu, label="Becsült $\mu$", density=True)
     # a delta módszer által elvárt eloszálása a becsült paraméternek
     # bins
     binamount = 200
     step = (max(x_mle_mu)-min(x_mle_mu))/binamount
     bins = [ min(x_mle_mu)+s*step for s in range(binamount+2) ]
     normalpdf = stats.norm.pdf(bins, mu, np.sqrt( 1/4 * np.mean(y_mle_sigma2)/n ))
     plt.plot(bins, normalpdf, label="Becslés elvárt eloszlása")
     plt.legend()
     plt.title("Átlag")
     plt.subplot(1,2,2)
     plt.hist(x_mle_sigma2, label="Becsült $\sigma^2$", density=True)
     # a delta módszer által elvárt eloszálása a becsült paraméternek
     step = (max(x_mle_sigma2)-min(x_mle_sigma2))/binamount
     bins = [ min(x_mle_sigma2)+s*step for s in range(binamount+2) ]
     normalpdf = stats.norm.pdf(bins, sigma2, np.sqrt( (1/8)* np.mean(y_mle_sigma2)**2/n ))
     plt.plot(bins, normalpdf, label="Becslés elvárt eloszlása")
     plt.title("Szórásnégyzet")
     plt.legend()
     plt.show()
```

[Úgy néz ki jól dolgoztunk. Ha akarjuk még futtathatunk egy Kolmogorov–Smirnov](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test) (https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov\_test) tesztet is: [2](#page-4-0)

```
     alpha = 0.05
     mu_elutasit = 0
     sigma2_elutasit = 0
     teszt_szam = 1000
     for _ in range(teszt_szam):
         expected_mu__becsles_eloszlas = np.random.normal(mu, np.sqrt( 1/4*4*sigma2/n ), len(x_mle_mu) )
         _, pval =stats.ks_2samp(x_mle_mu, expected_mu__becsles_eloszlas)
         if pval < alpha:
             mu_elutasit += 1
         expected_sigma2__becsles_eloszlas = np.random.normal(sigma2, np.sqrt( 1/8*(4*sigma2)**2/n ), len(x_mle_sigma2) )
         _, pval = stats.ks_2samp(x_mle_sigma2, expected_sigma2__becsles_eloszlas)
         if pval < alpha:
             sigma2_elutasit += 1
     if mu_elutasit/teszt_szam <= alpha:
         print("Elfogadjuk Delta módszer eredményét")
     else:
         print("Elutasítjuk a Delta módszer eredményét")
```

Ami szintén megerősíti a módszert.

## <span id="page-4-0"></span>Lábjegyzet

- 1. A szórás négyzetet fogom jelölni ebben a bejegyzésben, azért, hogy egyértelmű legyen, hogy a varianciát akarjuk becsülni és nem a -t.
- 2. Azért ezzel vigyázzunk! Az egyoldali Kolmogorov–Smirnov [\(https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov\\_test\)](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test) egyáltalán nem használható (https://stackoverflow.com/questions/7903977/implementing-a[kolmogorov-smirnov-test-in-python-scipy/7904652#comment9662498\\_7904652\) ilyen](https://stackoverflow.com/questions/7903977/implementing-a-kolmogorov-smirnov-test-in-python-scipy/7904652#comment9662498_7904652) tesztre, és a kétoldali is csak több ezres *n* esetén.

### **Címke:**

[Centrális határeloszlás-tétel](https://sajozsattila.home.blog/tag/centralis-hatareloszlas-tetel/), [Delta módszer](https://sajozsattila.home.blog/tag/delta-modszer/), [Fisher információ](https://sajozsattila.home.blog/tag/fisher-informacio/), [Lineáris algebra](https://sajozsattila.home.blog/tag/linearis-algebra/), [példa számítás,](https://sajozsattila.home.blog/tag/pelda-szamitas/) [Ronald Fisher](https://sajozsattila.home.blog/tag/ronald-fisher/)

## Közzétéve: sajzsoltattila
