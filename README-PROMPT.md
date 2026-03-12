ZADANIE: rozwiń poniższy dokument, dopracuj, skup się na ergonomii przekazywania wiedzy
KONTEKST: uworzenie pliku README tego projektu do publikacji na github
JĘZYK: angielski
STYL: bez nadęcia, zwięźle (szanujemy czas czytelnika), krótkie przykłady
OUTPUT: README.md

# Bober

Lekka pętla agentyczna / harness w stylu [ralph](https://github.com/snarktank/ralph) i trochę [autoresearch](https://github.com/karpathy/autoresearch).
Po co: wykonywalna specyfikacja / program w markdown.

Niecałe 200 linii kodu = łatwe zrozumienie i audyt.

Dodane kilka kluczowych (moim zdaniem) mechanizmów:
- kilka rozmiarów modeli do różnych zadań
- słowa kluczowe przerwania pętli (opcjonalne)
- twardy limit iteracji
- proste wywołanie bo konfiguracja w pliku
- odrobina obserwowalności poprzez JSONL
- podobieństwo do unixowych procesów:
  - stdin = path (kod programu w markdown)
  - stdout = outpath (plik wykonania w markdown)
  - stderr = logpath (jsonl z logami z agenta)
  - zmiany w innych plikach jako skutki uboczne
- łatwa produkcja wielu wariantów z jednego wejścia

Ograniczenia:
- na razie może używać tylko "Cursor CLI" jako agenta (bo prostsza implementacja)
- brak równoległego wywołania agentów (aby uprościć synchronizację)

# Użycie

`bober init`

`bober plan inbox/task1.md`
`bober loop inbox/task1.md 20`

`bober plan inbox/task1.md --variant mk2`
`bober loop inbox/task1.md 20 --variant mk2`

# Konfiguracja

--config option > BOBER_CONFIG env variable > ~/.config/bober/bober.toml > bundled config

# Skąd nazwa

- znane memiczne polskie zwierze (nie linkuj to niczego XD)
- bobry budują rzeczy... i tylko czasem powoduje to podtopienia lub suszę ;)

# Instalacja

`uv tool install git+https://github.com/mobarski/bober`
Trzeba mieć zainstalowany [Cursor CLI](https://cursor.com/cli) i zalogować się w nim na swoje konto.
