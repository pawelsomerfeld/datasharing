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
| **Sondy myśli** | przerwanie z pytaniem „gdzie był Twój umysł?", 5 opcji | samoopis odpływania, do skonfrontowania z czasami |
| **Dystraktory** | atrapy powiadomień systemowych w rogu ekranu | koszt zakłócenia i tempo powrotu |

Kanały pasywne, o których badany nie myśli: powroty do poprzedniej linii (`←`),
przejścia szybsze niż fizycznie możliwe do przeczytania, czas trzymania klawisza,
utrata fokusu okna. Na końcu każdego tekstu — cztery pytania o treść.

Czas: 12–18 minut, tryb skrócony ok. 5.

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
badany odpowiedział „odpłynąłem", podzielony przez ten sam rozrzut przed sondą
„byłem przy tekście". Wartość powyżej 1 znaczy, że wskaźnik obiektywny zapowiadał
to, co badany zaraz zaraportował. Jest to pojedynczy najważniejszy wynik w całym
narzędziu: sprawdza, czy pomiar w ogóle łapie to zjawisko, o które nam chodzi,
**w obrębie jednej osoby**, bez potrzeby grupy kontrolnej.

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

**Wersja mobilna.** Wymaga zastąpienia klawiatury dotknięciem i pogodzenia się
z gorszą precyzją czasową. Do wskaźników opartych na rozrzucie to prawdopodobnie
wystarczy, do opóźnienia wykrycia raczej nie.
