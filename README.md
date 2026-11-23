# Dwukierunkowa synchronizacja kontaktów

Dwa lokalne serwery Flask przechowują kontakty w osobnych bazach SQLite. Ręczna synchronizacja przesyła zmiany między serwerami przez REST. Demonstracja wymaga Pythona 3 i trzech okien PowerShell otwartych w katalogu projektu.

## Uruchomienie w Windows

**Okno 1 — przygotowanie środowiska i start systemu A**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py --port 5000 --db system_a.db
```

**Okno 2 — start systemu B**

```powershell
.\.venv\Scripts\python.exe app.py --port 5001 --db system_b.db
```

## Demonstracja w oknie 3

Oba serwery pozostają uruchomione. Poniższe polecenie definiuje w trzecim oknie skrót do demonstracji.

```powershell
function demo($krok) { .\.venv\Scripts\python.exe demo.py $krok }
```

Przy pierwszym uruchomieniu, na pustych bazach, kolejne kroki dają następujące wyniki. Każde polecenie pokazuje stan obu systemów przed synchronizacją i po niej.

| Krok | Polecenie | Oczekiwany wynik |
|---|---|---|
| 1. Import z CSV | `demo import` | Po imporcie A ma 5 kontaktów, B ma 0. Po synchronizacji oba mają po 5. |
| 2. Zmiana w A | `demo a-do-b` | Telefon Anny zmienia się w A na 111. Po synchronizacji w B również widnieje 111. |
| 3. Zmiana w B | `demo b-do-a` | Telefon Anny zmienia się w B na 222. Po synchronizacji w A również widnieje 222. |
| 4. Konflikt | `demo konflikt` | A ma numer 333, B ma 444. Oba numery pozostają zachowane, a w terminalu i w pliku `sync.log` pojawia się „Konflikt kontaktu 1”. |

Skrypt demonstracyjny korzysta z tych samych poleceń, które można uruchomić oddzielnie: `.\.venv\Scripts\python.exe import_csv.py` (sam import) oraz `.\.venv\Scripts\python.exe sync.py` (sama synchronizacja). Zatrzymanie serwerów: Ctrl+C w oknach 1 i 2.

**Zakres na 3.0** obejmuje import CSV do SQLite, pomijanie istniejących identyfikatorów i obsługę błędów pliku oraz bazy. **Zakres na 4.0** obejmuje dwukierunkową synchronizację przez REST z kluczem API, obsługę błędów danych i sieci oraz logowanie. Plik `sync_state.json` przechowuje ostatnią wspólną wersję każdego kontaktu, na podstawie której skrypt rozpoznaje zmiany i konflikty.
