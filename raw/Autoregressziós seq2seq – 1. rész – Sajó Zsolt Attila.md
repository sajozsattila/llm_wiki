### **[Sajó Zsolt Attila](https://sajozsattila.home.blog/)**

Gépi tanulás és néhány más dolog

☰ **Menü**

# Autoregressziós seq2seq – 1. rész

[sajzsoltattila](https://sajozsattila.home.blog/author/sajzsoltattila/) [Gépi tanulás](https://sajozsattila.home.blog/category/gepi-tanulas/) 12th szeptember 202412th december 2024 6 Minutes 

*A mai bejegyzésben egy olyan modellel fogunk megismerkedni, amit gyakran használunk hosszabb sorozatok előrejelzésére. A seq2seq (az angol "sequence to sequence" szóból származtatott rövidítés) olyan neurális hálón, pontosabban az Ismétlődő Neurális Hálózaton*

*[\(https://sajozsattila.home.blog/2019/11/25/ismetlodo-neuralis-halozat/\)\(](https://sajozsattila.home.blog/2019/11/25/ismetlodo-neuralis-halozat/)angolul: Recurrent Neural Network) alapuló modell, ami egy változó hosszúságú bemeneti sorozatból egy szintén változó hosszúságú kimeneti sorozatot állít elő. Egy időben elég elterjedt volt a használata a számítógépes [nyelvészetben \(https://sajozsattila.home.blog/tag/szamitogepes-nyelveszet/\), de mára inkább csak](https://sajozsattila.home.blog/tag/szamitogepes-nyelveszet/) idő[sorok \(https://sajozsattila.home.blog/tag/idosorok/\)](https://sajozsattila.home.blog/tag/idosorok/)elemzésére használjuk.*

A seq2seq modellt eredetileg automatizált fordításra dolgozták ki 2014-ben. Mi is a számítógépes nyelvészet irányából fogjuk megközelíteni. Ez segíteni fog abban, hogy megértsük, milyen probléma megoldására született, és ez hogyan befolyásolta a szerkezetét.

## A probléma

Természetes nyelvek gépi fordítása egy viszonylag régi kutatási terület. Az 1950-es években az IBM és az amerikai kormány jelentős pénzösszegeket fordítottak erre a területre, különösképpen az orosz-angol fordításra összpontosítva. Ezek az első modellek egyszerű szabályalapú modellek voltak, de elég gyorsan kiderült, hogy ez nem fog működni. 1966-ban az [ALPAC \(https://en.wikipedia.org/wiki/ALPAC\)](https://en.wikipedia.org/wiki/ALPAC)jelentéssel ez köztudottá vált.

### Hosszabb szünet után a word2vec

[\(https://sajozsattila.home.blog/2020/10/20/word2vec/\)n](https://sajozsattila.home.blog/2020/10/20/word2vec/)yitotta meg az utat a neurális hálókon alapuló gépi fordítások előtt. Ez a modell már viszonylag nagy pontossággal volt képes egyes szavakat más nyelvekre fordítani. Sajnos ennek viszont kis gyakorlati haszna volt. A való életben nagyon ritkán akarunk csak egyetlen szót vagy kifejezést lefordítani. Sokkal inkább mondatoknak és teljes szövegeknek a fordítására van igény. Alapvetően három kihívás áll fenn nagyobb szövegekkel kapcsolatban:

- 1. Bármely, a szónál nagyobb egységet választunk a gépi fordítás alapegységének, annak nem lesz állandó hossza. A mondatok változó mennyiségű szóból épülnek fel, a bekezdések pedig változó mennyiségű mondatból, stb. Értelemszerűen egy egyszerű "Feed Forward" háló ezt nem tudja megoldani. Ezeknek állandó a bemeneti neuronjainak száma, vagyis csak ugyanolyan hosszúságú szövegek kezelésére lennének képesek.
- 2. A fordítás eredményének hossza előre nem ismert, és nem is feltétlenül egyezik meg a bemeneti szöveg hosszával. Például a magyar "Hirdetését olvastam és közlöm önnel, hogy elveszett életkedvének becsületes megtalálója vagyok." mondat 11 szóból áll. Ennek angol fordítása: "I have read your advertisement and I would like to inform you that I am the honest finder of your lost zest for life.", ami viszont 24 szóból tevődik össze.
- 3. A szavak sorrendje információt hordoz. Nem mindegy, hogy Piszkos Fred zárja be Fülig Jimit, vagy fordítva.

Tömören: egy nem ismert hosszúságú bemeneti sorozatból kellene egy szintén nem ismert, eltérő hosszúságú kimenetet előállítani. A seq2seq modell erre vállalkozik. Nézzük meg, hogyan.

## A seq2seq felépítése

A fenti problémák tudatosítása után nem jelent nagy ugrást a gondolat, hogy a Feed Forward háló helyett inkább Ismétlődő Neurális Hálózatot [\(https://sajozsattila.home.blog/2019/11/25/ismetlodo-neuralis-halozat/\)](https://sajozsattila.home.blog/2019/11/25/ismetlodo-neuralis-halozat/) kellene használni. Ez lehetővé teszi számunkra a változó hosszúságú bemeneti adatok kezelését. De miért nem elegendő ez önmagában?

Elméletileg elég lenne, de vegyünk észre valamit. A feladatot két logikus alfeladatra lehetne bontani. Az első részben szeretnénk "megérteni" a bemenetet, a másodikban pedig elkészíteni a kimeneti sorozatot. Felmerül a kérdés, hogy vajon nem lenne-e hatékonyabb, ha két neurális hálót tanítanánk. Specializálva mindegyiket a saját feladatára. Talán nem olyan meglepő, ha azt mondom, hogy igen, hatékonyabb. Két részfeladatra specializált modell együtt általában jobb eredményt ér el mint egy modell, amelynek egyetlen, de komplexebb feladatot kell megoldania. A seq2seq modell lényegében eköré az ötlet köré épül, és két neurális hálóból áll. Nézzük, mi ez a két rész:

*Kódoló-Dekódoló*

A fenti részben a Kódoló (angolul: Encoder) egy olyan háló, ami a bemeneti sorozat megértésére van optimalizálva. Ez a Neurális Háló feldolgozza és tömöríti a bemenetet, majd elkészíti az Összefoglaló Vektort (angolul: Context Vector). Ez a vektor elméletileg tartalmazza az összes információt, ami lényeges a bemeneti sorozatban. Ezt a vektort továbbítjuk a Dekodoló Hálónak (angolul: Decoder), ami így már specializálódhat a kimeneti sorozat elkészítésére.

De sajnos van itt egy probléma. Általában a neurális hálók nem képesek egy sorozatot egy lépésben generálni. Tehát a Dekodoló résznek egyesével kell elkészítenie az elemeket. A 2. problémánál említett példánál maradva, a modellnek először el kell készítenie az "I" kimenetet, a második lépésben a "have"-t, a harmadikban a "read"-et és így tovább. Persze ehhez tudni kellene, mi történt minden esetben előtte. A példánál maradva, valami ilyesmi vislekedést várunk el:

| lé<br>p<br>é<br>s | bemenet                                                                                                                                              | elvárt<br>kimen<br>et |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| 1.                | [ "Hirdetését", "olvastam", "és", "közlöm", "önnek", "hogy", "elveszett",<br>"életkedvének", "becsületes", "megtalálója", "vagyok"]                  | "I"                   |
| 2.                | [ "Hirdetését", "olvastam", "és", "közlöm", "önnek", "hogy", "elveszett",<br>"életkedvének", "becsületes", "megtalálója", "vagyok"] + ["I" ]         | "have<br>"            |
| 3.                | [ "Hirdetését", "olvastam", "és", "közlöm", "önnek", "hogy", "elveszett",<br>"életkedvének", "becsületes", "megtalálója", "vagyok"] + ["I", "have" ] | "read"                |

A fenti példa egy hagyományos Rekurzív módszer

[\(https://sajozsattila.home.blog/2024/09/05/idosor-elorejelzes-hosszabb-idotavra/\)](https://sajozsattila.home.blog/2024/09/05/idosor-elorejelzes-hosszabb-idotavra/), ahol az előző modell kimenetét mindig hozzáadjuk a következő futtatás bemenetéhez (a könnyebb láthatóság kedvéért dőlt betűvel jelöltem ezeket a fenti táblázatban). Ez a lépés az, ami miatt autoregressziós seq2seq-ről beszélünk. Az autoregresszió tulajdonképpen nem más, mint amikor a modell saját maga által generált kimenetét használja fel a bemeneteként a jövőben. (Igen, jogos a feltevés, hogy ha létezik autoregressziós seq2seq, akkor léteznie kell nem autoregressziós változatnak is. Ezek azonban nem olyan elterjedtek, így mi most nem foglalkozunk velük részletesebben.)

A fentieket összefoglalva ilyennek kell elképzelnünk az autoregresszió seq2seq felépítését:

*autoregressziós seq2seq*

Két dolgot érdemes még megjegyezni, ha számítógépes nyelvészetben alkalmazunk seq2seq modellt. Először is, a Dekódoló kimenete egy valószínűség, vagyis hogy megkapjuk a legjobb valós kimeneti szót, egy Softmax réteget kell alkalmaznunk a Dekódoló eredményén.

Másodszor, a bemeneti adatok egy ritka mátrixot

[\(https://hu.wikipedia.org/wiki/Ritka\\_m%C3%A1trix\)](https://hu.wikipedia.org/wiki/Ritka_m%C3%A1trix) eredményeznének természetes nyelveken. Ennek megfelelően valamilyen dimenziócsökkentést kell alkalmaznunk a bemeneti szövegen, és ennek a fordítottját a Dekódoló eredményén. Tehát a modellt még ki kell egészítenünk ezzel:

*neuro-lingvisztikus seq2seq*

Értelemszerűen a fenti kiegészítésekre nincs szükség, ha idősorokkal dolgozunk.

## Végszó

A következő bejegyzésben megnézzük egy példát TensorFlowban a seq2seq modellre idősorokon.

### Irodalom

- 1. Max Brenner: Implementing Seq2Seq Models for Efficient Time Series Forecasting [\(https://medium.com/@maxbrenner-ai/implementing-seq2seq-models-for-efficient-time](https://medium.com/@maxbrenner-ai/implementing-seq2seq-models-for-efficient-time-series-forecasting-88dba1d66187)series-forecasting-88dba1d66187)
- 2. [Harvard University: Introduction to Artificial Intelligence with Python Lecture 6](https://www.youtube.com/watch?v=QAZc9xsQNjQ&list=PLhQjrBD2T381PopUTYtMSstgk-hsTGkVm&index=8) (https://www.youtube.com/watch? v=QAZc9xsQNjQ&list=PLhQjrBD2T381PopUTYtMSstgk-hsTGkVm&index=8)
- 3. freeCodeCamp: A history of machine translation from the Cold War to deep learning [\(//www.freecodecamp.org/news/a-history-of-machine-translation-from-the-cold-war-to](https://www.freecodecamp.org/news/a-history-of-machine-translation-from-the-cold-war-to-deep-learning-f1d335ce8b5/)deep-learning-f1d335ce8b5/)
- 4. Huangwei Wieniawska: Building Seq2Seq LSTM with Luong Attention in Keras for Time [Series Forecasting \(https://levelup.gitconnected.com/building-seq2seq-lstm-with-luong](https://levelup.gitconnected.com/building-seq2seq-lstm-with-luong-attention-in-keras-for-time-series-forecasting-1ee00958decb)attention-in-keras-for-time-series-forecasting-1ee00958decb)
- 5. Kriz Moses: Encoder-Decoder Seq2Seq Models, Clearly Explained!! [\(https://medium.com/analytics-vidhya/encoder-decoder-seq2seq-models-clearly](https://medium.com/analytics-vidhya/encoder-decoder-seq2seq-models-clearly-explained-c34186fbf49b)explained-c34186fbf49b)

### **Címke:**

Idő[sorok](https://sajozsattila.home.blog/tag/idosorok/), Ismétlődő [Neurális Hálózat](https://sajozsattila.home.blog/tag/ismetlodo-neuralis-halozat/), [Mesterséges Neurális Hálózat,](https://sajozsattila.home.blog/tag/mesterseges-neuralis-halozat/) [Számítógépes nyelvészet](https://sajozsattila.home.blog/tag/szamitogepes-nyelveszet/)

Közzétéve: sajzsoltattila

*[sajzsoltattila összes bejegyzése](https://sajozsattila.home.blog/author/sajzsoltattila/)*

## "Autoregressziós seq2seq – 1. rész" bejegyzéshez 2 hozzászólás

Visszajelzés: [Figyelem + Seq2seq TensorFlowban – seq2seq 2. rész – Sajó Zsolt Attila](https://sajozsattila.home.blog/2024/12/12/figyelem-seq2seq-tensorflowban-seq2seq-2-resz/)

[Szerkesztés](https://sajozsattilahome.wordpress.com/wp-admin/comment.php?action=editcomment&c=932) |

Visszajelzés: [MI Ügynök tesztelése és értékelése — 1. rész – Sajó Zsolt Attila](https://sajozsattila.home.blog/2025/07/20/mi-ugynok-tesztelese-es-ertekelese-1-resz/) [Szerkesztés](https://sajozsattilahome.wordpress.com/wp-admin/comment.php?action=editcomment&c=937) |

[WordPress.com ingyen](https://wordpress.com/?ref=footer_website)[es honlap vagy saját honlap létrehozása.](https://wordpress.com/advertising-program-optout/) Do Not Sell or Share My Personal Information (készítette: [Raam Dev](http://raamdev.com/)).