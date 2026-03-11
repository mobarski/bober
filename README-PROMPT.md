ZADANIE: rozwiń poniższy dokument, dopracuj, skup się na ergonomii przekazywania wiedzy
KONTEKST: uworzenie pliku README tego projektu do publikacji na github
JĘZYK: angielski
STYL: bez nadęcia, zwięźle (szanujemy czas czytelnika), krótkie przykłady
OUTPUT: README.md

# Bober

Ciasna pętla agentyczna / harness w stylu Ralpha i trochę Autoresearch.
Po co: wykonywalna specyfikacja / program w markdown.

Niecałe 200 linii kodu = łatwe zrozumienie i audyt.

Dodane kilka kluczowych (moim zdaniem) mechanizmów:
- kilka rozmiarów modeli do różnych zadań
- słowa kluczowe przerwania pętli (opcjonalne)
- twardy limit iteracji
- proste wywołanie bo konfiguracja w pliku
- odrobina obserwowalności poprzez JSONL
- podobieństwo do unixowych procesów: stdin, stdout, stderr + skutki uboczne

Ograniczenia:
- na razie może używać tylko "Cursor CLI" jako agenta (bo prostsza implementacja)
- brak równoległego wywołania agentów (aby uprościć synchronizację)

# Użycie

`bober plan inbox/task1.md`
`bober loop inbox/task1.md 20`

`bober plan inbox/task1.md --version mk2`
`bober loop inbox/task1.md 20 --version mk2`

# Skąd nazwa

- memiczne polskie zwierze
- budowniczy

# Instalacja- zrównoleglanie prac

`uv tool install git+https://github.com/mobarski/bober`
