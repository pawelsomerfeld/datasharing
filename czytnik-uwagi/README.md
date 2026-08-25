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

Trzy teksty popularnonaukowe po 26 linii. Prezentacja **samosterowana, jedna linia
naraz** (self-paced reading, wariant niekumulacyjny) — badany sam decyduje, kiedy
przejść dalej, więc czas linii to czysty czas przetwarzania.

W tekst wplecione są cztery niezależne kanały pomiarowe:

| Kanał | Mechanika | Co mierzy |
|---|---|---|
| **Czas linii** | spacja przewija dalej | zmienność uwagi w czasie |
| **Linie bez sensu** | 2 na tekst, gramatyczne ale semantycznie absurdalne; reakcja klawiszem `X` | czy tekst jest przetwarzany, czy tylko przewijany |
| **Sondy myśli** | przerwanie z pytaniem „gdzie był Twój umysł?", 5 opcji | samoopis odpływania, do skonfrontowania z czasami |
| **Dystraktory** | atrapy powiadomień systemowych w rogu ekranu | koszt zakłócenia i tempo powrotu |

Kanały pasywne, o których badany nie myśli: powroty do poprzedniej linii (`←`),
przejścia szybsze niż fizycznie możliwe do przeczytania, czas trzymania klawisza,
utrata fokusu okna. Na końcu każdego tekstu — cztery pytania o treść.

Czas: 12–18 minut, tryb skrócony ok. 5.

## Wskaźniki i dlaczego akurat te

Kluczowa decyzja: **nie interesuje nas średnie tempo, tylko rozrzut i jego struktura
w czasie**. Średnie tempo czytania zależy głównie od kompetencji językowej i
wykształcenia. Rozrzut wokół własnej średniej — znacznie mniej.

Wszystkie czasy są najpierw resztami z regresji `czas linii ~ liczba znaków + pozycja
w sesji`, co usuwa wpływ długości linii i efektu wprawy/zmęczenia.

**τ (tau)** — składowa wykładnicza rozkładu ex-Gaussa, estymowana metodą momentów.
To „ogon" nietypowo wolnych linii. W literaturze o czasach reakcji w ADHD τ jest
konsekwentnie tym parametrem, który różnicuje grupy, podczas gdy μ (tempo bazowe)
często nie. Jeśli w wyniku widzisz `τ = 0`, oznacza to rozkład bez prawostronnej
skośności — u człowieka rzadkie, ale możliwe przy bardzo krótkiej sesji.

**Moc pasma 0,03–0,07 Hz** — udział wolnych, mniej więcej 20–30-sekundowych oscylacji
w całej zmienności tempa. Odpowiada opisom uwagi, która nie tyle się potyka, co
faluje. Traktuj jako przybliżenie: próbkowanie jest z natury nierównomierne (kolejne
linie mają różne czasy trwania), więc odstępy zastępujemy średnim czasem linii.
To wystarcza do porównań między badanymi, ale nie jest estymatorem widma.

**d′ wykrywania bezsensu** — teoria detekcji sygnału na liniach absurdalnych.
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

## Progi w panelu wyników są tymczasowe

Etykiety „w normie orientacyjnej / podwyższone / wyraźnie podwyższone" opierają się
na rzędach wielkości z literatury, **nie na normalizacji tego narzędzia**. Są tam po
to, żeby panel dało się czytać, i muszą zostać zastąpione percentylami z własnej próby.

Do tego służy tryb `--norms`:

```bash
python3 analysis/score_session.py sesja.json          # jedna sesja + kontrola zgodności
python3 analysis/score_session.py --norms katalog/    # P10/P25/mediana/P75/P90 z próby
python3 analysis/score_session.py sesja.json --json   # do dalszej obróbki
```

Skrypt to **niezależna implementacja tych samych wzorów** co w przeglądarce. Po
przeliczeniu porównuje wynik z polem `metrics` w pliku JSON i wypisuje `OK` albo listę
rozbieżności. Jeśli kiedykolwiek zobaczysz `ROZBIEŻNOŚCI`, jedna ze stron ma błąd —
to celowy mechanizm kontrolny, nie ozdoba.

Sensowna próba normalizacyjna to minimum 100–150 osób bez rozpoznania, z kontrolą
wieku i wykształcenia, plus osobno grupa z rozpoznaniem postawionym niezależnie.

## Plan walidacji, gdyby to miało być czymś więcej niż demem

1. **Rzetelność** — retest po 2–4 tygodniach na 30 osobach. τ i współczynnik
   zmienności powinny dać ICC powyżej 0,7. Wskaźniki oparte na 6 zdarzeniach
   (d′, koszt dystraktora) prawdopodobnie nie dadzą i będą wymagały dłuższej wersji.
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
przeciwhistaminowe i zwykła nuda. Zadanie mierzy **stan uwagi w jednej sesji**,
a nie cechę osoby. Rozpoznanie ADHD wymaga wywiadu wobec kryteriów DSM-5 lub ICD-11,
danych z co najmniej dwóch środowisk i potwierdzenia objawów w okresie rozwojowym —
żadnej z tych rzeczy komputer nie zastąpi.

Osobne ryzyko: teksty są jawne. Osoba, która przeszła sesję raz, wie, gdzie są linie
absurdalne. Do retestu potrzeba równoległych zestawów tekstów — struktura pliku na to
pozwala, wystarczy dopisać kolejne pozycje do tablicy `PASSAGES`.

Zadanie zakłada sprawne czytanie w języku polskim. U osoby z dysleksją albo czytającej
w drugim języku wskaźniki oparte na czasie będą zawyżone z powodów niemających
z uwagą nic wspólnego.

## Dane osobowe

Wszystkie obliczenia dzieją się w przeglądarce, plik JSON zapisuje się lokalnie.
Nie ma serwera, więc nie ma czego wykradać. Jeśli zbierasz dane do badania, log
zawiera `navigator.userAgent` i rozdzielczość ekranu — usuń oba przed archiwizacją,
o ile ich nie potrzebujesz.

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
