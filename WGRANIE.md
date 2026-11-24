# Tomdar-Meble - wgranie nowej strony na tomdar-meble.pl

Strona jest statyczna (HTML + CSS + JS + zdjęcia WebP) z jednym skryptem PHP do formularza. Działa na każdym hostingu z Apache i PHP 5.4+ (obecny hosting HITME / Neofusion obsługuje Quick.Cms, więc PHP jest).

- Paczka do wgrania: `C:\Users\Admin\Downloads\Tomdar_strona\paczka\` (to samo w `tomdar-paczka.zip`)
- Źródła i generator: `_src\` (`python -I buduj.py` odbudowuje `paczka\` i `docs\`, `obrazy.py` przygotowuje zdjęcia)
- Wersja testowa do odbioru: https://wylinka-podglad.pl/tomdar-strona/ (noindex, formularz tylko pokazowy)

## 1. Przed wgraniem (po otrzymaniu FTP / panelu hostingu)

1. Zalogować się do panelu HITME (dane od klienta lub z agencji Neofusion zapisać od razu w `klienci/_DOSTEPY_KLIENTOW.md`, loguje się user).
2. **Kopia starej strony**: pobrać przez FTP cały katalog strony (Quick.Cms: `index.php`, `files/`, `templates/`, `database/`, `core/`...) do `Tomdar_strona\_kopia_quickcms_RRRRMMDD\`. Nic nie kasować na serwerze, dopóki kopia nie jest na dysku.
3. Sprawdzić wersję PHP w panelu (zalecane 8.x; skrypt działa od 5.4).
4. Sprawdzić tagi: stara strona NIE ma żadnych tagów Google/Meta (sprawdzone 13.11.2026 curl-em: brak GTM, GA4, Ads, Pixel, meta weryfikacji GSC). Nie ma czego przenosić. Jeśli klient poda konto Google Analytics lub Search Console, dodać tag po zgodzie (Consent Mode v2) i rozszerzyć baner cookies.

## 2. Wgranie

1. Starą stronę przenieść na serwerze do katalogu `_stara_quickcms/` (albo usunąć po zrobieniu kopii) - szczególnie stary `index.php`, bo `DirectoryIndex` w nowym `.htaccess` wskazuje `index.html`, ale stary plik nie powinien zostać dostępny.
2. Wgrać **całą zawartość** folderu `paczka\` do katalogu głównego domeny (public_html / www / katalog domeny tomdar-meble.pl), razem z plikami ukrytymi:
   - `.htaccess` (przekierowania, cache, nagłówki),
   - `_limity/.htaccess` (blokada katalogu liczników formularza).
3. Uprawnienia: katalog `_limity/` musi być zapisywalny przez PHP (zwykle 755 wystarcza; jeśli formularz zgłasza błąd zapisu - 775). Skrypt sam utworzy tam `_sekret.php` i pliki liczników.

## 3. Formularz (wyslij.php)

- Wysyła zapytania funkcją PHP `mail()` na **tomdar.meble@gmail.com**, jako HTML w kolorach marki (bez przycisków), z załącznikiem (1 plik do 10 MB: JPG/PNG/WEBP/HEIC/PDF) i `Reply-To` na adres klienta. Klient dostaje neutralne potwierdzenie (bez cytowania treści).
- Ochrona przed spamem: ukryte pole-pułapka, podpisany znacznik czasu (min. 3 s), sprawdzanie Origin, limit 5 zapytań/h i 12/dobę z jednej sieci oraz 40/dobę łącznie, sprawdzanie sygnatury pliku.
- Nadawca (`From`) to `formularz@tomdar-meble.pl` (stała `NADAWCA` na górze `wyslij.php`). Najlepiej założyć taką skrzynkę w panelu HITME (albo zmienić stałą na istniejącą skrzynkę w domenie) - wtedy Gmail nie wrzuca maili do spamu. Sprawdzić też rekord SPF domeny (powinien obejmować serwer HITME).
- Jeśli serwer nie wysyła maili (`mail()` wyłączone): podmienić w HTML `action="../wyslij.php"` na FormSubmit (`https://formsubmit.co/tomdar.meble@gmail.com`) - wymaga jednorazowego kliknięcia linku aktywacyjnego, który FormSubmit wyśle na skrzynkę klienta; w `app.js` wysyłka idzie na `f.action`, więc działa bez innych zmian (FormSubmit przyjmuje załączniki).
- Test lokalny 13.11.2026: `php -S` + zmienna `TOMDAR_MAIL_DO_PLIKU` (zapis .eml zamiast wysyłki) - wysyłka z załącznikiem przeszła, mail i potwierdzenie poprawnie zbudowane.
- **Po wgraniu**: wysłać 1 zapytanie testowe (najpierw ze zmienioną stałą `ODBIORCA` na odrobimy@gmail.com, sprawdzić wygląd i załącznik, potem przywrócić tomdar.meble@gmail.com), kliknąć formularz na telefonie i komputerze.

## 4. Przekierowania 301 ze starych adresów (Quick.Cms) - w `.htaccess`

| Stary adres | Nowy adres |
|---|---|
| `/?o-nas,1`, `/index.php` | `/` |
| `/?oferta,3` | `/oferta/` |
| `/?galeria,37` | `/realizacje/` |
| `/?kontakt,2`, `/?wycena,28` | `/kontakt/` |
| `/?sLang=pl`, inne `/?nazwa,ID` | `/` |
| `/files/...` (stare zdjęcia, Google Grafika), `/images/banner*.jpg` | `/realizacje/` |
| `/templates/`, `/core/`, `/database/`, `admin.php` | 410 Gone |
| `/oferta` bez ukośnika itd. | z ukośnikiem |
| `www.tomdar-meble.pl` | `tomdar-meble.pl` |

Sprawdzenie po wgraniu (powinno dać 301 i właściwy `Location`):
```
curl -sI "http://tomdar-meble.pl/?oferta,3"
curl -sI "http://tomdar-meble.pl/?galeria,37"
curl -sI "http://tomdar-meble.pl/?kontakt,2"
curl -sI "http://tomdar-meble.pl/files/meble-1.jpg"
curl -sI "http://www.tomdar-meble.pl/"
```

## 5. SSL i https

Obecnie certyfikat na tomdar-meble.pl jest wystawiony na inną nazwę (przeglądarka ostrzega). Kolejność:
1. W panelu HITME włączyć darmowy certyfikat Let's Encrypt dla `tomdar-meble.pl` i `www.tomdar-meble.pl` (zwykle "SSL" / "Certyfikaty" przy domenie).
2. Sprawdzić `curl -sI https://tomdar-meble.pl/` (200, bez błędu certyfikatu) i to samo dla www.
3. Dopiero wtedy w `.htaccess` odkomentować blok "1. HTTPS i adres bez www" (5 linii z `# Rewrite...`) i usunąć/zakomentować przekierowanie www na http pod nim. Opcjonalnie włączyć nagłówek HSTS (sekcja 6).
4. Adresy kanoniczne, sitemap i dane strukturalne już wskazują `https://tomdar-meble.pl/`.

## 6. Po wgraniu - lista kontrolna

- [ ] Wszystkie podstrony 200: `/`, `/oferta/`, `/realizacje/`, `/o-nas/`, `/kontakt/`, `/polityka-prywatnosci/`, nieistniejący adres -> 404 z naszą stroną.
- [ ] `https://tomdar-meble.pl/_limity/` -> 403, `/wyslij.php` (GET) -> 405.
- [ ] Formularz: wysyłka testowa jak w pkt 3, na telefonie i komputerze.
- [ ] Baner cookies: "Tylko niezbędne" chowa mapę (adres + "Wyznacz trasę"), "Ustawienia cookies" w stopce otwiera baner ponownie.
- [ ] Google Search Console: dodać właściwość `https://tomdar-meble.pl/` (weryfikacja przez DNS u HITME albo plik HTML w katalogu głównym), zgłosić `sitemap.xml`, poprosić o indeksowanie strony głównej.
- [ ] Profil Firmy w Google (jeśli klient ma): podmienić link na https://tomdar-meble.pl/.
- [ ] Stopka: znak "wykonanie: Wylinka" (gekon) jest w każdej podstronie - zgodnie z § 8 ust. 4 umowy.
- [ ] Zamknąć zlecenie w planerze i dodać realizację na wylinka.pl.

## 7. Zmiany treści

Treści i lista zdjęć są w `_src\buduj.py` (teksty) i `_src\zdjecia.json` (kategorie, opisy zdjęć). Nowe zdjęcia klienta: dopisać do `KAT` w `_src\obrazy.py` (katalog surowych plików jako argument), uruchomić `python -I obrazy.py <katalog>`, potem `python -I buduj.py` i wgrać `paczka\img\` oraz zmienione `index.html`.
