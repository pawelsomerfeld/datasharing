# Czytnik Uwagi

Prototyp zadania do behawioralnego pomiaru uwagi w czytaniu. Zamiast pytać badanego,
czy trudno mu się skupić, rejestruje, co robi jego uwaga podczas zwykłego czytania —
linia po linii, w milisekundach.

**To nie jest test diagnostyczny.** Narzędzie nie zostało znormalizowane ani zwalidowane.
Sekcja „Ograniczenia" niżej wyjaśnia, dlaczego to nie jest formalność.

```
czytnik-uwagi/
├── index.html                  # kompletne zadanie, jeden plik, bez zależności
└── analysis/score_session.py   # niezależny scoring logu + budowanie norm
```

Uruchomienie: otwórz `index.html` w przeglądarce. Wszystko liczy się lokalnie,
nic nie wychodzi do sieci poza krojami pisma z Google Fonts (przy pracy offline
zadziałają kroje zastępcze).

---

## Skąd ten pomysł

Klasyczne komputerowe zadania do ADHD (CPT, TOVA, QbTest) mierzą coś, czego badany
nigdy nie robi w życiu: przez 15 minut wciska klawisz, kiedy na ekranie pojawi się
litera. Dają dobre wskaźniki, ale kosztem trafności ekologicznej i przy dużej
podatności na „zmobilizuję się, bo to test".

Czytanie jest inne. Jest czynnością, którą badany wykonuje codziennie, ma naturalne
tempo, którego nie da się długo udawać, i — co najważniejsze — **samo tempo czytania
jest ciągłym pomiarem uwagi**. Każde naciśnięcie spacji to jeden punkt pomiarowy.
78 linii to 78 czasów reakcji zebranych bez ani jednej sztucznej próby.

Do tego dochodzi rzecz, której CPT nie potrafi: można sprawdzić, czy badany
**rozumiał**, co czytał, i zestawić to z tempem. Szybkie czytanie przy niskim
rozumieniu to zupełnie inny profil kliniczny niż wolne czytanie przy niskim
rozumieniu, a oba dają identyczny wynik „słaba uwaga" w skali samoopisowej.

## Co dokładnie się dzieje

Sesja zaczyna się od **bloku próbnego** — ośmiu linii z jedną wplecioną bezsensowną
i jednym powiadomieniem — zakończonego informacją zwrotną. Pierwsze naciśnięcia spacji
mierzą naukę interfejsu, a nie uwagę; blok próbny przenosi tę naukę poza pomiar,
a przy okazji pokazuje badanemu, czego właściwie ma szukać. Nie wchodzi do żadnego
wskaźnika, ale trafia do pliku wyjściowego jako `practiceLines`.

Potem trzy teksty popularnonaukowe po 26 linii. Prezentacja **samosterowana, jedna linia
naraz** (self-paced reading, wariant niekumulacyjny) — badany sam decyduje, kiedy
przejść dalej, więc czas linii to czysty czas przetwarzania.

Materiał istnieje w **dwóch formach równoległych**, dobranych parami co do dziedziny
i budowy:

| | Forma A | Forma B |
|---|---|---|
| ocean / geologia | Bałtyk | Wieczna zmarzlina |
| nawigacja zwierząt | Nawigacja pszczół | Wędrówki węgorza |
| historia technologii | Historia papieru | Historia szkła |

Obie mają po 78 linii, 9 linii bez sensu, 6 powiadomień, 6 sond i 12 pytań;
średnia długość linii to 70 i 67 znaków. Bez drugiej formy retest jest niewykonalny —
osoba, która przeszła sesję raz, wie już, gdzie są linie absurdalne. Przy większej
próbie warto kontrbalansować: połowa badanych A→B, połowa B→A.

W tekst wplecione są cztery niezależne kanały pomiarowe:

| Kanał | Mechanika | Co mierzy |
|---|---|---|
| **Czas linii** | spacja przewija dalej | zmienność uwagi w czasie |
| **Linie bez sensu** | 3 na tekst, gramatyczne ale semantycznie absurdalne; reakcja klawiszem `X` | czy tekst jest przetwarzany, czy tylko przewijany |
| **Sondy myśli** | przerwanie: kategoria myśli, potem ocena wciągnięcia 1–5 | samoopis uwagi, do skonfrontowania z czasami |
| **Powiadomienia** | karty odwzorowujące systemowe: macOS, Windows 11, komunikator, baner mobilny, pasek postępu | koszt zakłócenia, tempo powrotu, orientacja wzroku |
| **Linie zatrzymane** | 2 na tekst, tekst widoczny, ale przejść dalej nie wolno | hamowanie reakcji prepotentnej, tolerancja czekania |
| **Ciekawostki z przynętą** | 2 na tekst, w powierzchni czytania, wolno je otworzyć | dobrowolne porzucenie zadania, pomyłka co do źródła |

Kanały pasywne, o których badany nie myśli: powroty do poprzedniej linii (`←`),
przejścia szybsze niż fizycznie możliwe do przeczytania, czas trzymania klawisza,
utrata fokusu okna. Na końcu każdego tekstu — cztery pytania o treść.

Czas: 12–18 minut, tryb skrócony ok. 5.

## Co odciąga od tekstu

Powiadomienie systemowe jest bodźcem nienaturalnym z dwóch powodów naraz: badany wie,
że jest sfingowane, i każemy mu je ignorować. W prawdziwym czytaniu nikt niczego nie
zabrania — odciąga cię **coś ciekawszego na tej samej stronie**, i wolno ci tam pójść.

Dlatego gniazdo dystraktora można wypełnić jednym z trzech:

| Tryb | Co się pojawia | Co mierzy |
|---|---|---|
| **Ciekawostki** *(domyślny)* | pudełko „polecane” w powierzchni czytania, wolno je otworzyć | dobrowolne porzucenie zadania, kontaminacja pamięci |
| Powiadomienia systemowe | karty w rogu ekranu, badany ma je ignorować | koszt przerwania i tempo powrotu |
| Naprzemiennie | pierwsze gniazdo w tekście, drugie w rogu | oba naraz |

Liczba zdarzeń jest w każdym trybie ta sama, więc harmonogram i walidator się nie zmieniają.

### Przynęta, czyli pomyłka co do źródła

To jest najmocniejszy pomiar w całym narzędziu. Każda ciekawostka niesie **konkretne,
prawdopodobnie brzmiące twierdzenie sprzeczne z tekstem** — i to twierdzenie wraca potem
jako jedna z odpowiedzi w pytaniu o treść.

Tekst mówi, że pełna wymiana wód Bałtyku zajmuje około trzydziestu lat. Ciekawostka obok
głosi: „Wąskie cieśniny duńskie działają jak dysza: cała objętość wymienia się w niecałe
trzy lata”. Pytanie na końcu ma wśród odpowiedzi „Około trzech lat”.

Wybranie jej **nie jest zwykłym brakiem wiedzy.** To dowód, że badany zapamiętał
dystraktor jako źródło — pomyłka co do źródła, nie luka w pamięci. Dokładnie ta sytuacja,
w której coś było na tyle ciekawsze od tekstu, że zajęło jego miejsce w odpowiedzi.

Rozdziela to dwie porażki, które w zwykłym teście rozumienia wyglądają identycznie:

- **„nie zapamiętałem tekstu”** — błędy rozłożone po opcjach, przy trzech dystraktorach
  około 33% z nich trafiłoby w przynętę przypadkiem;
- **„zapamiętałem dystraktor zamiast tekstu”** — błędy skupione na przynęcie, wyraźnie
  powyżej 33%.

Dlatego panel podaje obie liczby: odsetek pytań z wybraną przynętą oraz udział przynęt
wśród samych błędnych odpowiedzi. Druga kontroluje ogólny poziom rozumienia.

Trzeci wskaźnik to **koszt kontaminacji**: różnica rozumienia między pytaniami
z przynętą a pytaniami bez niej, w obrębie tej samej osoby i tej samej sesji.

### Sprostowanie jest obowiązkowe

Twierdzenia w ciekawostkach są nieprawdziwe. Zostawienie badanego z fałszywą wiedzą nie
jest dopuszczalne, niezależnie od tego, jak dobrym jest to wskaźnikiem — dlatego po sesji
panel wyników pokazuje sekcję **Sprostowanie**: każde pokazane twierdzenie obok tego,
jak jest naprawdę. Ten ekran należy pokazać badanemu.

### Dwie decyzje projektowe

**Otwarcie ciekawostki nie jest złamaniem instrukcji.** Badany dostaje wprost informację,
że wolno je czytać i że nie ma tu dobrej ani złej decyzji. Bez tego mierzylibyśmy
posłuszeństwo, a nie uwagę. Dlatego odsetek otwarć i czas spędzony w ciekawostkach to
miary dobrowolnego porzucenia zadania, a nie błędy.

**Przynęta liczy się tylko wtedy, gdy ciekawostka faktycznie się pokazała.** W trybie
samych powiadomień pytania są zwyczajne, a wskaźniki przynęty w ogóle się nie pojawiają.

Osobna uwaga na przyszłość: w paradygmatach dezinformacji fałszywa treść działa
najsilniej, gdy pojawia się **po** materiale oryginalnym. Tutaj gniazda dystraktora są
w stałych miejscach, więc część przynęt wyprzedza fakt, któremu przeczy. Wersja
z przynętami wyłącznie po fakcie byłaby mocniejsza i wymaga jedynie przesunięcia gniazd.

## Powiadomienia

Pięć stylów odwzorowujących układ, ruch i hierarchię prawdziwych powiadomień: jasna
rozmyta karta w prawym górnym rogu, ciemna karta z przyciskami akcji w prawym dolnym,
karta komunikatora z awatarem i wskaźnikiem pisania, baner zjeżdżający z góry ekranu
oraz pasek postępu pobierania. Ikony są rysowane od zera — chodzi o wierność formy,
nie o cudze znaki towarowe.

**Treść jest drugim parametrem.** Dwa zestawy do wyboru, oba zapisywane w pliku wyniku:

- **Neutralne** — suche komunikaty informacyjne (spotkanie, przelew, aktualizacja).
- **Wciągające** *(domyślne)* — luka informacyjna (wiadomość urwana w pół zdania:
  „muszę Ci coś powiedzieć, ale nie tutaj”), niejasność społeczna („Nowy komentarz pod
  Twoim wpisem: «A jednak to nie do końca tak, jak…»”) i drobna presja czasu
  („pozostało 8 sekund”). To są chwyty, które realnie przyciągają uwagę mocniej
  niż suchy komunikat.

Celowo **nie ma tu fałszywych alarmów bankowych ani zdrowotnych.** Badany bywa
pacjentem i nie wolno go straszyć dla zwiększenia siły efektu — sfingowane ostrzeżenie
o nieautoryzowanej transakcji podniosłoby wskaźniki i byłoby nadużyciem.

**Natarczywość jest parametrem badania, nie ustawieniem estetycznym.** Trzy poziomy
zapisują się w pliku wyniku, więc da się je utrzymać stałe albo celowo nimi manipulować
między grupami:

| Poziom | Kart na zdarzenie | Czas życia | Dźwięk |
|---|---|---|---|
| Łagodny | 1 | 3,5 s | nie |
| Standardowy | 1 | 5 s | nie |
| Natarczywy *(domyślny)* | 2, druga po 650 ms | 7 s | tak |

Silniejszy bodziec da większy efekt, ale grozi sufitem i oddala zadanie od zwykłego
czytania. Dlatego wybór jest jawny, a nie zaszyty na stałe.

Sygnał dźwiękowy jest generowany na miejscu, bez plików. To najsilniejszy z bodźców,
ale jego **głośność zależy od sprzętu i nie jest standaryzowana** — przy porównaniach
między osobami albo używaj go wszędzie, albo nigdzie.

Dwie rzeczy, które to zmusiło do zmierzenia:

- **Najazd kursorem.** Orientacja uwagi bez decyzji o kliknięciu. Zdarza się o rząd
  wielkości częściej niż kliknięcie, więc różnicuje znacznie lepiej. Rejestrowany jest
  też czas do najazdu.
- **Dostarczone kontra zaplanowane.** Karta znika, gdy badany przechodzi do kolejnej
  linii, więc bardzo szybkie czytanie może wyprzedzić drugą kartę. Gdyby to zostawić
  bez pomiaru, dawka bodźca zależałaby po cichu od tempa czytania. Panel pokazuje
  stosunek wprost, żeby ta resztka zależności była widoczna w danych.

Przycisk **Pokaż przykłady** na ekranie startowym odpala wszystkie style naraz;
podgląd nie trafia do logu.

## Podgląd materiału

Przycisk **Podgląd materiału** pokazuje badaczowi wszystkie teksty obu form wraz
z częścią próbną, z zaznaczonymi liniami bez sensu, powiadomieniami i miejscami sond,
oraz pytania z zaznaczonymi poprawnymi odpowiedziami. Wcześniej trzeba było czytać
źródło. Nie pokazuj tego ekranu badanemu.

## Metryczka

Przed startem zbierany jest kod badanego (pole wymagane) oraz współzmienne: wiek,
wykształcenie, długość snu, kofeina, leki wpływające na uwagę i ewentualne rozpoznanie.

Kod jest wymagany nie z pedanterii — bez niego nie da się połączyć dwóch sesji tej samej
osoby, a więc retest, o który cały ten projekt się opiera, jest niewykonalny. Pole ma
przyjmować pseudonim, nie imię i nazwisko.

Pozostałe pola to bezpośrednia odpowiedź na ograniczenie opisane niżej: niewyspanie,
kofeina i leki dają ten sam profil co ADHD. Jeśli ich nie zbierzesz, nie da się o wyniku
powiedzieć nic sensownego. **Odpowiedzi o sen, leki i rozpoznanie to dane o zdrowiu** —
plik wyjściowy staje się przez nie danymi szczególnej kategorii w rozumieniu art. 9 RODO
i wymaga takiej ochrony jak reszta dokumentacji badania.

## Zbieranie danych z wielu osób

Każda zakończona sesja zapisuje się automatycznie w `localStorage` przeglądarki — badacz,
który zapomni pobrać plik, nie traci danych. Ekran startowy pokazuje licznik zebranych
sesji i trzy przyciski:

- **Pobierz wszystkie (JSON)** — komplet z pełnymi logami zdarzeń, do analizy skryptem
- **Pobierz tabelę (CSV)** — jeden wiersz na sesję, metryczka plus wszystkie wskaźniki,
  gotowe do wczytania w R, Pythonie, JASP-ie, jamovi czy SPSS-ie
- **Wyczyść** — z potwierdzeniem

CSV używa przecinka jako separatora i kropki dziesiętnej, czyli konwencji, którą czytają
wszystkie wymienione programy. Excel z polską lokalizacją potraktuje go jako jedną kolumnę —
tam użyj importu z jawnym wskazaniem separatora, a nie dwukliku.

Zapis jest lokalny dla przeglądarki i profilu. Wyczyszczenie danych witryny albo praca
w oknie prywatnym go likwiduje, dlatego pobieraj komplet po każdej serii badań.
Jeśli miejsce się skończy, panel po sesji powie o tym wprost, zamiast po cichu zgubić dane.

## Co z modeli ADHD to zadanie faktycznie dotyka

Uczciwa mapa. Nie jest to deklaracja trafności — narzędzie wciąż nie jest zwalidowane —
tylko wskazanie, który konstrukt ma tu jakąkolwiek reprezentację pomiarową.

| Konstrukt | Reprezentacja w zadaniu | Ocena |
|---|---|---|
| Zmienność wewnątrzosobnicza czasów reakcji | τ, ogon odporny, współczynnik zmienności, pasmo 0,03–0,07 Hz | mocna — to jest rdzeń narzędzia |
| Odpływanie myślami, interferencja sieci spoczynkowej | sondy dwuetapowe, wykrywanie bezsensu, korelacja rozrzutu z samoopisem | mocna |
| Podatność na dystrakcję i powrót do zadania | koszt powiadomienia, reszty na kolejnych liniach, najazd kursorem | średnia |
| Hamowanie reakcji prepotentnej | linie zatrzymane, błędy komisji | średnia — to jest no-go, nie stop-signal |
| Nietolerancja czekania, awersja do odroczenia | tolerancja czekania, naciśnięcia w oknie zatrzymania | średnia |
| Spadek czujności w czasie | nachylenie tempa względem pozycji w sesji | słaba — 78 linii to krótka sesja |
| Korekta po błędzie | zwolnienie na linii po fałszywym alarmie lub błędzie komisji | słaba — mało zdarzeń |
| Impulsywność wyboru, dyskontowanie odroczenia | **brak** | wymaga osobnego zadania |
| Impulsywność refleksyjna, decyzja na zbyt małych danych | **brak** | wymaga osobnego zadania |
| Kontaminacja pamięci treścią konkurencyjną | przynęty w ciekawostkach, udział przynęt wśród błędów | mocna — bezpośredni dowód zachowaniowy |
| Dobrowolne porzucenie zadania | odsetek otwartych ciekawostek, czas w nich spędzony | średnia |
| Wrażliwość na wzmocnienie | **brak** | wymagałaby bloku z informacją zwrotną |
| Nadruchliwość | **brak** | wymaga pomiaru ruchu, nie klawiatury |

Trzy zastrzeżenia, których nie wolno pominąć:

**No-go to nie stop-signal.** Linie zatrzymane sygnalizują zakaz od początku ekspozycji,
więc mierzą powstrzymanie reakcji jeszcze niezainicjowanej. Czas hamowania reakcji już
uruchomionej (SSRT) to inny wskaźnik i oba potrafią się rozjeżdżać. Kto potrzebuje SSRT,
potrzebuje procedury schodkowej, a nie tego zadania.

**Tempo zdarzeń jest ustawiane przez badanego.** W modelach energetyczno-poznawczych
deficyty ujawniają się najmocniej przy bardzo wolnym i bardzo szybkim tempie prezentacji,
a zadanie samosterowane pozwala badanemu ustawić sobie tempo wygodne. To osłabia część
efektów i jest ceną, jaką płacimy za trafność ekologiczną. Wersja z narzuconym tempem
byłaby innym zadaniem, bliższym klasycznemu CPT.

**Dwutorowość jest reprezentowana asymetrycznie.** Tor wykonawczy ma tu kilka wskaźników,
tor motywacyjny w zasadzie jeden — tolerancję czekania. Do pełnego obrazu trzeba dołożyć
dyskontowanie odroczenia, co jest osobnym, krótkim zadaniem i naturalnym kolejnym krokiem.

## Linie zatrzymane: hamowanie i czekanie

Po kilkudziesięciu liniach naciśnięcie spacji jest reakcją wyćwiczoną i automatyczną.
Linia zatrzymana wymaga jej wstrzymania: pod tekstem pojawia się napis „Poczekaj”,
a linia przechodzi sama. Naciśnięcia w tym oknie to błędy komisji.

Trzy decyzje projektowe, które o tym decydują:

**Okno jest indywidualizowane** — własne tempo badanego razy długość linii, plus 2,2 s.
Dzięki temu obciążenie hamowaniem jest porównywalne u osoby czytającej szybko i wolno.
Tempo liczone jest na bieżąco z linii już przeczytanych, dlatego pierwsza linia
zatrzymana nie może wypaść wcześniej niż ósma w tekście — walidator tego pilnuje.

**Nie ma odliczania i to jest celowe.** Znajomość momentu zakończenia czyni czekanie
łatwym. To niepewność co do tego, kiedy wolno zareagować, wywołuje reakcje przedwczesne
i o nią tu chodzi.

**Czas linii zatrzymanej nie jest czasem czytania**, bo został narzucony przez zadanie,
a nie wybrany przez badanego. Takie linie wypadają z serii czasów, z regresji i ze
wszystkich wskaźników zmienności. Pozycja w regresji pozostaje jednak globalna: linia
zatrzymana zajmuje czas sesji, nawet jeśli nie wnosi czasu czytania.

Wskaźniki: odsetek linii z naciśnięciem (błędy komisji), łączna liczba naciśnięć
(wielokrotne dobijanie to inny wzorzec niż jedno wcześniejsze naciśnięcie) oraz
tolerancja czekania — jaka część okna zdążyła minąć przed pierwszym naciśnięciem.

## Wskaźniki i dlaczego akurat te

Kluczowa decyzja: **nie interesuje nas średnie tempo, tylko rozrzut i jego struktura
w czasie**. Średnie tempo czytania zależy głównie od kompetencji językowej i
wykształcenia. Rozrzut wokół własnej średniej — znacznie mniej.

Wszystkie czasy są najpierw resztami z regresji `czas linii ~ liczba znaków + pozycja
w sesji`, co usuwa wpływ długości linii i efektu wprawy/zmęczenia.

**τ (tau)** — składowa wykładnicza rozkładu ex-Gaussa, estymowana metodą momentów.
To „ogon" nietypowo wolnych linii. W literaturze o czasach reakcji w ADHD τ jest
konsekwentnie tym parametrem, który różnicuje grupy, podczas gdy μ (tempo bazowe)
często nie.

Estymator momentowy ma jednak wadę: przy rozkładzie bez prawostronnej skośności nie ma
rozwiązania. Narzędzie zwraca wtedy **`null`, a nie zero** — i tak też pokazuje to panel,
razem z wartością skośności. Zero wyglądałoby jak bardzo dobry wynik, co jest dokładnie
odwrotne do prawdy: to brak wyniku.

**Ogon odporny** — dlatego obok τ stoi wskaźnik nieparametryczny: `(P90 − mediana)` reszt
podzielone przez medianę czasu linii. Mierzy to samo zjawisko, nigdy się nie degeneruje
i nie zależy od tego, jak szybko ktoś czyta. Jeśli τ jest nieokreślone, to jest wskaźnik,
który należy czytać.

**Moc pasma 0,03–0,07 Hz** — udział wolnych, mniej więcej 20–30-sekundowych oscylacji
w całej zmienności tempa. Odpowiada opisom uwagi, która nie tyle się potyka, co
faluje. Traktuj jako przybliżenie: próbkowanie jest z natury nierównomierne (kolejne
linie mają różne czasy trwania), więc odstępy zastępujemy średnim czasem linii.
To wystarcza do porównań między badanymi, ale nie jest estymatorem widma.

**d′ wykrywania bezsensu** — teoria detekcji sygnału na dziewięciu liniach absurdalnych
w sesji. Sześć, jak było w pierwszej wersji, nie wystarcza do rzetelności nadającej się
do retestu; dziewięć to kompromis — przy większym zagęszczeniu zadanie przestaje być
czytaniem, a staje się polowaniem na absurdy, co zmienia samo zachowanie, które mierzymy.
Trafienie liczy się też, gdy reakcja padła jedną linię później (typowe: badany
przechodzi dalej, po czym się orientuje); taka linia jest wtedy wyłączona z puli
fałszywych alarmów. Niskie d′ **przy szybkim tempie** jest sygnałem czytania bez
kodowania treści.

**Walidacja wewnętrzna** — rozrzut czasów w czterech liniach przed sondą, na którą
badany odpowiedział „poza tekstem", podzielony przez ten sam rozrzut przed sondą
„przy treści tekstu". Wartość powyżej 1 znaczy, że wskaźnik obiektywny zapowiadał
to, co badany zaraz zaraportował. Jest to pojedynczy najważniejszy wynik w całym
narzędziu: sprawdza, czy pomiar w ogóle łapie to zjawisko, o które nam chodzi,
**w obrębie jednej osoby**, bez potrzeby grupy kontrolnej.

## Sonda: co i dlaczego zostało zmienione

Pierwsza wersja pytała, gdzie był umysł, i dawała pięć opcji, wśród których dwie
rozdzielały odpływanie na „wiedziałem o tym" i „zorientowałem się dopiero teraz".
To rozróżnienie ma sens w literaturze, ale badany w połowie czytania nie potrafi go
zrobić wiarygodnie — wymaga introspekcji nad własną metaświadomością sprzed sekundy.
Doszło do tego, że opcje były sformułowane czasownikami w pierwszej osobie, więc każda
niosła końcówkę rodzajową do wybrania w trakcie zadania.

Obecna wersja ma dwa kroki:

**Krok 1 — kategoria.** Pięć wyrażeń rzeczownikowych, bez czasowników, a więc bez
końcówek rodzajowych, każde z krótkim przykładem pod spodem:

| Odpowiedź | Kategoria |
|---|---|
| Przy treści tekstu | przy zadaniu |
| Przy czymś zupełnie innym | odpływanie myślami |
| Przy samym badaniu | myśli o wykonaniu zadania |
| Przy czymś na ekranie albo w otoczeniu | bodziec zewnętrzny |
| Nigdzie — w głowie było pusto | pustka |

Kategoria bodźca zewnętrznego jest nowa i konieczna: bez niej powiadomienia nie miały
gdzie zapisać się w samoopisie, więc trafiały do worka „odpływanie", z którym nie mają
wiele wspólnego.

**Krok 2 — stopień.** „Na ile udało się wciągnąć w tekst przez ostatnią minutę?",
skala 1–5. Pomiar ciągły obok kategorycznego: łatwiejszy do udzielenia i mocniejszy
statystycznie niż samo „odpłynąłem albo nie".

## Rozkład zdarzeń jest sprawdzany automatycznie

Manipulacje nie mogą na siebie nachodzić: linia bez sensu, która wypada w oknie powrotu
po powiadomieniu albo tuż po sondzie, jest stracona dla obu pomiarów naraz — jej czas
odzwierciedla wtedy zakłócenie, a nie wykrywanie absurdu.

Przy każdym uruchomieniu `validateForms()` sprawdza cały materiał i wypisuje zastrzeżenia
na ekranie wstępnym oraz w konsoli:

- bezsens w oknie `[d, d+3]` po powiadomieniu w linii `d`
- bezsens albo powiadomienie na linii bezpośrednio po sondzie
- dwa bezsensy bliżej niż 3 linie od siebie, dwa powiadomienia bliżej niż 4
- indeksy poza zakresem tekstu, zła liczba bezsensów lub pytań
- różna łączna liczba linii między formami

Jeśli dopisujesz własne teksty do `FORMS`, to jest siatka bezpieczeństwa — źle
rozłożony materiał psuje wyniki po cichu, bez żadnego objawu w interfejsie.

## Progi w panelu wyników są tymczasowe

Etykiety „w normie orientacyjnej / podwyższone / wyraźnie podwyższone" opierają się
na rzędach wielkości z literatury, **nie na normalizacji tego narzędzia**. Są tam po
to, żeby panel dało się czytać, i muszą zostać zastąpione percentylami z własnej próby.

Do tego służy tryb `--norms`:

```bash
python3 analysis/score_session.py sesja.json          # jedna sesja + kontrola zgodności
python3 analysis/score_session.py --norms katalog/    # percentyle, osobno dla każdej formy
python3 analysis/score_session.py sesja.json --json   # do dalszej obróbki
```

Tryb `--norms` rozdziela sesje według formy i liczy percentyle osobno dla każdej.
Zlanie ich w jedną tabelę zakładałoby równoważność form, której nikt jeszcze nie wykazał —
to jest właśnie jedna z rzeczy do sprawdzenia w badaniu normalizacyjnym.

Skrypt to **niezależna implementacja tych samych wzorów** co w przeglądarce. Po
przeliczeniu porównuje wynik z polem `metrics` w pliku JSON i wypisuje `OK` albo listę
rozbieżności. Jeśli kiedykolwiek zobaczysz `ROZBIEŻNOŚCI`, jedna ze stron ma błąd —
to celowy mechanizm kontrolny, nie ozdoba.

Sensowna próba normalizacyjna to minimum 100–150 osób bez rozpoznania, z kontrolą
wieku i wykształcenia, plus osobno grupa z rozpoznaniem postawionym niezależnie.

## Plan walidacji, gdyby to miało być czymś więcej niż demem

1. **Rzetelność i równoważność form** — retest po 2–4 tygodniach na 30 osobach,
   forma A na pierwszym pomiarze u połowy i forma B u drugiej połowy. Daje to naraz
   dwie rzeczy: ICC dla stabilności (τ i współczynnik zmienności powinny przekroczyć 0,7)
   oraz sprawdzenie, czy formy dają zgodne wyniki. Jeśli nie dają, normy muszą
   zostać osobne — dlatego `--norms` od razu je rozdziela.
2. **Trafność zbieżna** — korelacja z Conners CPT 3 (zwłaszcza HRT SE i wariancja),
   z ASRS i z BAARS-IV. Oczekiwane wartości umiarkowane, 0,3–0,5; wyższe byłyby
   podejrzane.
3. **Trafność różnicowa** — porównanie z grupą z depresją i z grupą po nieprzespanej
   nocy. To jest test, na którym większość narzędzi tego typu przegrywa i dlatego
   jest najważniejszy.
4. **Trafność przyrostowa** — czy wskaźniki dokładają cokolwiek do modelu, w którym
   już są ASRS i CPT. Jeśli nie dokładają, narzędzie nie ma racji bytu, niezależnie
   od tego, jak ładnie wygląda panel.
5. **Symulacja** — sprawdzenie, czy da się udać wynik. Instrukcja „udawaj ADHD"
   dla połowy próby. Podejrzewam, że τ da się podnieść świadomie, ale relacja między
   sondami a czasami (walidacja wewnętrzna) już nie.

## Ograniczenia, których nie da się obejść

Ten sam profil — wysokie τ, dużo odpływania, słabe wykrywanie bezsensu — daje
niewyspanie, lęk, depresja, ból przewlekły, niedoczynność tarczycy, leki
przeciwhistaminowe i zwykła nuda. Metryczka zbiera część z tych współzmiennych,
ale zbieranie ich to nie to samo co kontrolowanie — bez grupy porównawczej
z zaburzeniem nastroju wynik i tak nie rozdziela tych możliwości. Zadanie mierzy **stan uwagi w jednej sesji**,
a nie cechę osoby. Rozpoznanie ADHD wymaga wywiadu wobec kryteriów DSM-5 lub ICD-11,
danych z co najmniej dwóch środowisk i potwierdzenia objawów w okresie rozwojowym —
żadnej z tych rzeczy komputer nie zastąpi.

Osobne ryzyko: teksty są jawne. Dwie formy wystarczają na jeden retest, ale nie na
serię pomiarów — przy trzecim podejściu badany zna już oba zestawy. Kolejne formy
dopisuje się do obiektu `FORMS`; walidator sprawdzi rozkład, ale nie sprawdzi za Ciebie,
czy pytania nie opierają się na liniach absurdalnych ani czy teksty są porównywalnie
trudne.

Zadanie zakłada sprawne czytanie w języku polskim. U osoby z dysleksją albo czytającej
w drugim języku wskaźniki oparte na czasie będą zawyżone z powodów niemających
z uwagą nic wspólnego.

## Dane osobowe

Wszystkie obliczenia dzieją się w przeglądarce, plik JSON zapisuje się lokalnie.
Nie ma serwera, więc nie ma czego wykradać po drodze. Log zawiera `navigator.userAgent`
i rozdzielczość ekranu — usuń oba przed archiwizacją, o ile ich nie potrzebujesz.

Nowe ryzyko wprowadza automatyczny zapis sesji w `localStorage`. Na **komputerze
współdzielonym** — a taki bywa stanowisko badawcze — kolejni badani mają wtedy dostęp
do metryczek i wyników poprzednich osób przez ekran startowy. Ponieważ te dane
obejmują sen, leki i rozpoznanie, jest to art. 9 RODO. Postępowanie jest proste:
pobierz komplet i wyczyść magazyn po każdej serii, a jeśli badani obsługują stanowisko
sami, prowadź je w oknie prywatnym, gdzie magazyn i tak nie przeżyje zamknięcia karty.

Sam kod badanego jest pseudonimem, nie anonimizacją — klucz łączący kod z osobą
przechowuj osobno od plików wyjściowych.

Uwaga na przyszłość: jeżeli dołożysz moduł eyetrackingu (niżej), wchodzisz w art. 9
RODO — dane biometryczne, szczególna kategoria. Nagranie z kamery nie może wtedy
opuścić urządzenia; z klatek wolno wyprowadzać wyłącznie liczby (kąt spojrzenia,
częstość mrugnięć), a samo wideo musi być odrzucane w tym samym obiegu.
To projektuje się od początku, nie dokłada później.

## Czego tu jeszcze nie ma

**Eyetracking z kamery internetowej.** Kuszące i technicznie wykonalne (WebGazer,
MediaPipe FaceMesh), ale przy typowej kamerze błąd wynosi kilka stopni kątowych —
za dużo, żeby powiedzieć, na którym słowie badany trzyma wzrok. Sensownie policzalne
są za to trzy rzeczy: częstość mrugnięć, odsetek czasu ze wzrokiem poza ekranem
i stabilność pozycji głowy. Ta ostatnia jest ciekawa, bo to tani odpowiednik pomiaru
ruchu w QbTest — komponentu nadruchliwości, którego zadania czysto poznawcze w ogóle
nie dotykają.

**Analiza przeglądania.** Wariant zamiast czytania: zadanie „znajdź odpowiedź na
pytanie" w spreparowanym, lokalnym zbiorze stron, z metryką odejść od celu, głębokości
dygresji i czasu powrotu do pierwotnego zadania. Bliżej realnego życia niż czytanie,
ale trudniejsze do ustandaryzowania — dwie osoby nigdy nie przejdą tej samej ścieżki,
więc porównywalność trzeba budować na miarach grafowych, a nie na czasach.

**Dyskontowanie odroczenia.** Krótkie zadanie wyboru między mniejszą nagrodą teraz
a większą później. Domyka tor motywacyjny modelu dwutorowego, którego to zadanie
prawie nie dotyka. Pięć minut, kilkanaście prób, wynik to jeden parametr k.
To jest najbardziej wartościowe z tego, czego tu nie ma.

**Blok z informacją zwrotną.** W ADHD wykonanie poprawia się nieproporcjonalnie mocno
przy natychmiastowym wzmocnieniu. Jeden tekst z informacją zwrotną po każdym wykryciu
bezsensu, reszta bez, dałby test tej hipotezy wewnątrz osoby. Kłopot w tym, że blok
z wzmocnieniem miesza się z pozycją w sesji i zmęczeniem, więc wymaga kontrbalansowania
kolejności — a to znaczy cztery formy zamiast dwóch.

**Wersja mobilna.** Wymaga zastąpienia klawiatury dotknięciem i pogodzenia się
z gorszą precyzją czasową. Do wskaźników opartych na rozrzucie to prawdopodobnie
wystarczy, do opóźnienia wykrycia raczej nie.
