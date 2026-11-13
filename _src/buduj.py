# Generator strony Tomdar-Meble (statyczne HTML).
# python -I buduj.py  ->  ../paczka (produkcja, tomdar-meble.pl)  i  ../docs (wersja testowa GitHub Pages, noindex)
import os, json, shutil, html, datetime

TU = os.path.dirname(os.path.abspath(__file__))
KORZEN = os.path.dirname(TU)
Z = json.load(open(os.path.join(TU, 'zdjecia.json'), encoding='utf-8'))
DZIS = datetime.date.today().isoformat()

TEL1, TEL1H = '501 156 315', 'tel:+48501156315'
TEL2, TEL2H = '607 884 191', 'tel:+48607884191'
MAIL = 'tomdar.meble@gmail.com'
ADR1, ADR2 = 'ul. Graniczna 15', '05-503 Głosków-Letnisko'
MAPA = ('https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d36009.393287737235!2d20.9480643259755!3d52.038161803626245'
        '!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x47192fe28761645b%3A0x59948791d65186ff'
        '!2sGraniczna+15%2C+05-503+G%C5%82osk%C3%B3w-Letnisko!5e0!3m2!1spl!2spl!4v1484831036089')
TRASA = 'https://www.google.com/maps/dir/?api=1&amp;destination=Graniczna+15%2C+05-503+G%C5%82osk%C3%B3w-Letnisko'

KOLEJNOSC = ['kuchnie', 'szafy', 'salon', 'lazienki', 'schody', 'tapicerowane', 'stoly', 'regaly']
OPIS_KAT = {
    'kuchnie': 'Nowoczesne wyspy, klasyczne fronty ramowe, blaty z kamienia i panele ze szkła.',
    'szafy': 'Pod skosem, pod schodami i we wnękach, z oświetleniem i wygodnym wnętrzem.',
    'salon': 'Ściany RTV, witryny i komody, od klasycznych po nowoczesne.',
    'lazienki': 'Szafki podumywalkowe, zabudowy pralek, toaletki i lustra w ramach.',
    'schody': 'Drzwi wewnętrzne przylgowe i bezprzylgowe, schody i ściany wykończone drewnem.',
    'tapicerowane': 'Łóżka z tapicerowanym zagłówkiem, siedziska, panele ścienne i szafki nocne.',
    'stoly': 'Blaty z drewna na stalowych podstawach, stoły do jadalni i stoliki.',
    'regaly': 'Regały na książki, biblioteki domowe i podświetlane wnęki.',
}
OPIS_KAT_DLUGI = {
    'kuchnie': 'Kuchnię projektujemy pod konkretne pomieszczenie: od klasycznych frontów ramowych w drewnie, przez białe zabudowy z wyspą, po nowoczesne wyspy w okładzinie o fakturze kamienia. Łączymy płytę i drewno z blatami z kamienia, szkłem i stalą.',
    'szafy': 'Szafy wnękowe, garderoby i zabudowy przedpokoi robimy pod każdy wymiar, także pod skosem dachu i pod schodami, gdzie gotowe meble się nie zmieszczą. Wnętrze dzielimy na półki, drążki i szuflady, a na życzenie dodajemy oświetlenie.',
    'salon': 'Zabudowy ścian z miejscem na telewizor, witryny, komody i szafki RTV. Wykonujemy je zarówno w stylu klasycznym, z frontami frezowanymi i patyną, jak i w prostej, nowoczesnej formie.',
    'lazienki': 'Zabudowy łazienkowe: szafki pod umywalkę, zabudowy pralek, toaletki i lustra w ramach.',
    'schody': 'Wykonujemy drzwi wewnętrzne przylgowe i bezprzylgowe, drewniane schody i balustrady oraz okładziny ścian z drewna i forniru, w których drzwi mogą być niemal niewidoczne.',
    'tapicerowane': 'W naszej stolarni można zamówić meble tapicerowane: łóżka z wysokim zagłówkiem, siedziska w przedpokoju, miękkie panele ścienne oraz pasujące do nich szafki nocne i komody.',
    'stoly': 'Stoły z litego drewna na stalowych podstawach, stoły do jadalni i kuchni, stoliki kawowe z drewna i szkła.',
    'regaly': 'Biblioteki domowe od podłogi po sufit, regały połączone z zabudową kuchenną i podświetlane wnęki na książki i dekoracje.',
}
KAT_KROTKO = {'kuchnie': 'Kuchnie', 'szafy': 'Szafy i garderoby', 'salon': 'Salon i RTV', 'lazienki': 'Łazienki',
              'schody': 'Schody i drzwi', 'tapicerowane': 'Tapicerowane', 'stoly': 'Stoły i blaty', 'regaly': 'Regały'}

TRYBY = {
    'prod': {'out': os.path.join(KORZEN, 'paczka'), 'url': 'https://tomdar-meble.pl/', 'robots': 'index,follow', 'test': False},
    'test': {'out': os.path.join(KORZEN, 'docs'), 'url': 'https://disaster26.github.io/tomdar-strona/', 'robots': 'noindex,nofollow', 'test': True},
}

STRONY = [
    # (ścieżka, klucz menu, title, description)
    ('', 'start', 'Tomdar-Meble - meble na wymiar, kuchnie, szafy i schody | Głosków-Letnisko, Piaseczno',
     'Pracownia stolarska Tomdar-Meble: kuchnie, szafy, garderoby, schody, drzwi, stoły i meble tapicerowane na wymiar. Głosków-Letnisko pod Piasecznem.'),
    ('oferta/', 'oferta', 'Oferta - kuchnie, szafy, schody i drzwi na wymiar | Tomdar-Meble',
     'Kuchnie, szafy i garderoby, zabudowy łazienek i salonu, schody, drzwi przylgowe i bezprzylgowe, stoły i meble tapicerowane na wymiar. Drewno, kamień, szkło i stal.'),
    ('realizacje/', 'realizacje', 'Realizacje - zdjęcia mebli na wymiar | Tomdar-Meble',
     'Galeria realizacji pracowni Tomdar-Meble: kuchnie, szafy pod skosem, garderoby, schody, drzwi, łóżka tapicerowane, stoły i regały wykonane na wymiar.'),
    ('o-nas/', 'o-nas', 'O pracowni - stolarnia Dariusza Skorupskiego i Tomasza Pliszki | Tomdar-Meble',
     'Tomdar-Meble to pracownia stolarska w Głoskowie-Letnisku prowadzona przez dwóch wspólników. Ponad 20 lat doświadczenia w obróbce drewna i meblach na wymiar.'),
    ('kontakt/', 'kontakt', 'Kontakt - Tomdar-Meble, Głosków-Letnisko | tel. 501 156 315',
     'Zapytaj o wycenę mebli na wymiar: tel. 501 156 315 lub 607 884 191, tomdar.meble@gmail.com. Pracownia: ul. Graniczna 15, 05-503 Głosków-Letnisko.'),
    ('polityka-prywatnosci/', 'polityka', 'Polityka prywatności i cookies | Tomdar-Meble',
     'Zasady przetwarzania danych osobowych i plików cookies na stronie tomdar-meble.pl.'),
]
MENU = [('oferta/', 'oferta', 'Oferta'), ('realizacje/', 'realizacje', 'Realizacje'), ('o-nas/', 'o-nas', 'O pracowni'), ('kontakt/', 'kontakt', 'Kontakt')]

e = html.escape


def badge():
    src = open(os.path.join(TU, 'badge.html'), encoding='utf-8').read()
    return src


def img(R, z, cls='', lazy=True, sizes=None):
    a = f' class="{cls}"' if cls else ''
    return (f'<img{a} src="{R}img/{z["src"]}" alt="{e(z["alt"])}" width="{z["w"]}" height="{z["h"]}"'
            + (' loading="lazy" decoding="async"' if lazy else '') + '>')


def logo_defs():
    return '''<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <symbol id="logo" viewBox="0 0 240 100">
      <path d="M3 3H221V58M3 3V73H186" fill="none" stroke="#FDC506" stroke-width="6"/>
      <text x="15" y="55" font-family="Montserrat,Arial,sans-serif" font-weight="700" font-size="43" textLength="176" lengthAdjust="spacingAndGlyphs" fill="currentColor">TOMDAR</text>
      <text x="147" y="68" font-family="Montserrat,Arial,sans-serif" font-weight="500" font-size="12" fill="currentColor">Meble</text>
      <g fill="currentColor"><use href="#krzeslo-ksztalt"/></g>
    </symbol>
    <g id="krzeslo-ksztalt">
      <path d="M203 21.5c10-1.6 22-1.6 33 0l-.4 4.2c-10.6-1.4-21.6-1.4-32.2 0z"/>
      <path d="M204 24h3.2l-.6 40h-3.2zM210.6 25h2.4l-.3 39h-2.4zM216.6 24.6h2.4v39.4h-2.4zM222.6 24.8h2.4l.3 39.2h-2.4zM232.2 23.6h3.4l-1.8 76.4h-3.4z"/>
      <path d="M188 62.5h46.8v5.4l-44.6 2.4z"/>
      <path d="M191 69.6h3.6l-1.8 29.4h-3.4zM204.6 68.8h3l.3 22h-2.8z"/>
    </g>
    <symbol id="tel" viewBox="0 0 20 20"><path d="M5.2 2.5 7.6 5c.4.4.4 1 .1 1.4L6.4 8c1 2.2 3.4 4.6 5.6 5.6l1.6-1.3c.4-.3 1-.3 1.4.1l2.5 2.4c.4.4.4 1.1 0 1.5l-1.4 1.4c-.6.6-1.5.8-2.3.5C8.6 16.4 3.6 11.4 1.8 6.2c-.3-.8-.1-1.7.5-2.3L3.7 2.5c.4-.4 1.1-.4 1.5 0Z" fill="currentColor"/></symbol>
  </defs>
</svg>'''


def naglowek(R, klucz):
    def link(p, k, n, mob=False):
        akt = ' class="akt" aria-current="page"' if k == klucz else ''
        return f'<a href="{R}{p}"{akt}>{n}</a>'
    nav = '\n      '.join(link(*m) for m in MENU)
    navm = '\n      '.join(link(*m) for m in MENU)
    cta = '#kontakt' if klucz == 'start' else f'{R}kontakt/#formularz'
    return f'''<header class="top" id="top">
  <div class="top-in">
    <a class="logo" href="{R or './'}" aria-label="Tomdar-Meble - strona główna"><svg viewBox="0 0 240 100" aria-hidden="true"><use href="#logo"/></svg></a>
    <nav class="nav" aria-label="Główna">
      {nav}
    </nav>
    <a class="top-tel" href="{TEL1H}"><svg aria-hidden="true"><use href="#tel"/></svg><span class="top-tel-num">{TEL1}</span><span class="top-tel-kr">Zadzwoń</span></a>
    <button class="burger" type="button" aria-expanded="false" aria-controls="menu-mob" aria-label="Otwórz menu"><span></span><span></span><span></span></button>
  </div>
  <div class="menu-mob" id="menu-mob" hidden>
    <nav aria-label="Menu mobilne">
      <a href="{R or './'}"{' class="akt" aria-current="page"' if klucz == 'start' else ''}>Strona główna</a>
      {navm}
    </nav>
    <div class="menu-mob-kontakt">
      <a class="btn" href="{cta}">Zapytaj o wycenę</a>
      <p>Dariusz Skorupski <a href="{TEL1H}">{TEL1}</a><br>Tomasz Pliszka <a href="{TEL2H}">{TEL2}</a></p>
    </div>
  </div>
</header>'''


def stopka(R, klucz):
    cta = '#kontakt' if klucz == 'start' else f'{R}kontakt/#formularz'
    return f'''<footer class="stopka">
  <div class="wrap stopka-in">
    <div class="stopka-firma">
      <svg class="stopka-logo" viewBox="0 0 240 100" aria-hidden="true"><use href="#logo"/></svg>
      <p>TOMDAR-MEBLE s.c.<br>Dariusz Skorupski, Tomasz Pliszka<br>{ADR1}, {ADR2}<br>NIP 952-214-00-87</p>
    </div>
    <div class="stopka-kol">
      <p class="stopka-h">Kontakt</p>
      <p><a href="{TEL1H}">{TEL1}</a> Dariusz<br><a href="{TEL2H}">{TEL2}</a> Tomasz<br><a href="mailto:{MAIL}">{MAIL}</a></p>
    </div>
    <nav class="stopka-kol" aria-label="Stopka">
      <p class="stopka-h">Strona</p>
      <a href="{R}oferta/">Oferta</a><a href="{R}realizacje/">Realizacje</a><a href="{R}o-nas/">O pracowni</a><a href="{R}kontakt/">Kontakt</a>
    </nav>
  </div>
  <div class="wrap stopka-dol">
    <span>&copy; <span data-rok>{datetime.date.today().year}</span> Tomdar-Meble</span>
    <span class="stopka-pr"><a href="{R}polityka-prywatnosci/">Polityka prywatności</a><button type="button" class="link-btn" data-cookies-ustawienia>Ustawienia cookies</button></span>
    {badge()}
  </div>
</footer>

<div class="mob" id="mob" aria-hidden="true">
  <a href="{TEL1H}" class="mob-tel" tabindex="-1"><svg aria-hidden="true"><use href="#tel"/></svg>Zadzwoń</a>
  <a href="{cta}" class="mob-cta" tabindex="-1">Zapytaj o wycenę</a>
</div>

<dialog class="lb" id="lb" aria-label="Powiększone zdjęcie">
  <figure class="lb-fig"><img src="data:," alt=""><figcaption><span class="lb-opis"></span><span class="lb-licz"></span></figcaption></figure>
  <button type="button" class="lb-x" aria-label="Zamknij">Zamknij</button>
  <button type="button" class="lb-n lb-prev" aria-label="Poprzednie zdjęcie"><span class="strz-l"></span></button>
  <button type="button" class="lb-n lb-next" aria-label="Następne zdjęcie"><span class="strz-p"></span></button>
</dialog>

<div class="ck" id="ck" role="dialog" aria-labelledby="ck-t" aria-live="polite" hidden>
  <div class="ck-in">
    <p class="ck-t" id="ck-t">Pliki cookies</p>
    <p>Strona używa niezbędnych plików cookies oraz mapy Google, która może zapisywać własne pliki cookies. Szczegóły w <a href="{R}polityka-prywatnosci/#cookies">polityce prywatności</a>.</p>
    <div class="ck-opcje" hidden>
      <label><input type="checkbox" checked disabled> Niezbędne (zawsze aktywne)</label>
      <label><input type="checkbox" data-ck-mapa checked> Mapa Google na stronie</label>
    </div>
    <div class="ck-akcje">
      <button type="button" class="btn btn-ck" data-ck="wszystkie">Akceptuję wszystkie</button>
      <button type="button" class="btn btn-ck2" data-ck="niezbedne">Tylko niezbędne</button>
      <button type="button" class="link-btn" data-ck="ustawienia">Ustawienia</button>
      <button type="button" class="btn btn-ck2" data-ck="zapisz" hidden>Zapisz wybór</button>
    </div>
  </div>
</div>'''


def karuzela(R, slug, ile=5, cls='kar'):
    zd = Z[slug]['zdjecia'][:ile]
    imgs = '\n            '.join(img(R, z, lazy=(i > 0 or True)) for i, z in enumerate(zd))
    return f'''<div class="{cls}" data-kar>
          <div class="kar-tor" tabindex="0" aria-label="Zdjęcia: {e(Z[slug]['nazwa'])}, przesuń w bok">
            {imgs}
          </div>
        </div>'''


def karty_oferty(R):
    out = []
    for s in KOLEJNOSC:
        n = len(Z[s]['zdjecia'])
        out.append(f'''      <article class="kat">
        {karuzela(R, s, 5)}
        <h3><a href="{R}realizacje/#{s}">{e(Z[s]['nazwa'])}</a></h3>
        <p>{e(OPIS_KAT[s])}</p>
        <a class="kat-link" href="{R}realizacje/#{s}">Zobacz realizacje ({n})</a>
      </article>''')
    return '\n'.join(out)


def tor(R, lista, grupa, nazwa):
    el = []
    for z in lista:
        pion = ' real-w' if z['h'] > z['w'] * 1.05 else ''
        el.append(f'<button class="real{pion}" type="button" data-grupa="{grupa}">{img(R, z)}</button>')
    return '\n    '.join(el)


def galeria_sekcja(R, s, i):
    zd = Z[s]['zdjecia']
    n = len(zd)
    tlo = ' sek-szara' if i % 2 == 0 else ''
    return f'''<section class="sek gal{tlo}" id="{s}" aria-labelledby="h-{s}">
  <div class="wrap">
    <div class="sek-glowa sek-glowa-rzad">
      <div>
        <h2 class="h-rama" id="h-{s}">{e(Z[s]['nazwa'])}</h2>
        <p>{e(OPIS_KAT[s])}</p>
      </div>
      <div class="tor-nav">
        <span class="tor-licz" aria-live="polite">1 / {n}</span>
        <div class="tor-strz">
          <button type="button" class="strz" data-strz="-1" aria-label="Poprzednie zdjęcia"><span class="strz-l"></span></button>
          <button type="button" class="strz" data-strz="1" aria-label="Następne zdjęcia"><span class="strz-p"></span></button>
        </div>
      </div>
    </div>
  </div>
  <div class="real-tor" data-tor tabindex="0" aria-label="Galeria: {e(Z[s]['nazwa'])}, przewiń w bok lub kliknij zdjęcie, aby powiększyć">
    {tor(R, zd, s, Z[s]['nazwa'])}
  </div>
</section>'''


def formularz(R, test):
    akcja = '#' if test else f'{R}wyslij.php'
    opcje = ''.join(f'<option>{o}</option>' for o in ['Kuchnia', 'Szafa lub garderoba', 'Zabudowa salonu lub RTV', 'Zabudowa łazienki',
                                                       'Schody lub drzwi', 'Meble tapicerowane', 'Stół lub blat', 'Regał lub biblioteka', 'Inny mebel'])
    return f'''<form class="form" id="formularz" action="{akcja}" method="post" enctype="multipart/form-data" data-tryb="{'test' if test else 'prod'}" data-znacznik="{R}wyslij.php?znacznik=1">
      <h3 class="form-h">Zapytanie o wycenę</h3>
      <label>Imię i nazwisko<input name="imie" autocomplete="name" required minlength="2" maxlength="100"></label>
      <div class="form-2">
        <label>Telefon<input name="telefon" type="tel" autocomplete="tel" inputmode="tel" maxlength="30"></label>
        <label>E-mail<input name="email" type="email" autocomplete="email" maxlength="120"></label>
      </div>
      <p class="form-pod">Podaj telefon lub e-mail, abyśmy mogli odpowiedzieć.</p>
      <label>Co chcesz zamówić?
        <select name="mebel">{opcje}</select>
      </label>
      <label>Wiadomość<textarea name="wiadomosc" rows="4" maxlength="5000" required placeholder="np. kuchnia w kształcie litery L, ok. 3,2 x 2,4 m"></textarea></label>
      <label class="plik">Projekt, szkic lub zdjęcie wnętrza (opcjonalnie, do 10 MB)<input type="file" name="plik" accept="image/jpeg,image/png,image/webp,image/heic,.heic,application/pdf"></label>
      <div class="hp" aria-hidden="true"><label>Strona firmy<input name="strona_www" tabindex="-1" autocomplete="off"></label></div>
      <input type="hidden" name="_z" value="">
      <label class="zgoda"><input type="checkbox" name="zgoda" value="tak" required> <span>Zgadzam się na przetwarzanie moich danych w celu odpowiedzi na zapytanie. Zasady w <a href="{R}polityka-prywatnosci/">polityce prywatności</a>.</span></label>
      <button class="btn" type="submit">Wyślij zapytanie</button>
      <p class="form-info" role="status" aria-live="polite"></p>
    </form>'''


def kontakt_sekcja(R, test, h_tag='h2', id_='kontakt'):
    return f'''<section class="sek sek-kontakt" id="{id_}">
  <div class="wrap kontakt">
    <div class="kontakt-dane">
      <{h_tag} class="h-rama">Opowiedz nam o swoim meblu</{h_tag}>
      <p>Napisz, co chcesz zamówić i jakie masz wymiary. Jeśli masz projekt, szkic albo zdjęcie wnętrza, dołącz je do wiadomości. Możesz też po prostu zadzwonić.</p>
      <dl class="dane">
        <div><dt>Telefon</dt><dd><a href="{TEL1H}">{TEL1}</a> Dariusz Skorupski<br><a href="{TEL2H}">{TEL2}</a> Tomasz Pliszka</dd></div>
        <div><dt>E-mail</dt><dd><a href="mailto:{MAIL}">{MAIL}</a></dd></div>
        <div><dt>Pracownia</dt><dd>{ADR1}<br>{ADR2}<br><a href="{TRASA}" target="_blank" rel="noopener">Wyznacz trasę</a></dd></div>
        <div><dt>Firma</dt><dd>TOMDAR-MEBLE s.c.<br>Dariusz Skorupski, Tomasz Pliszka<br>NIP 952-214-00-87</dd></div>
      </dl>
    </div>
    {formularz(R, test)}
  </div>
  <div class="mapa" data-mapa>
    <iframe title="Mapa dojazdu: ul. Graniczna 15, Głosków-Letnisko" src="{MAPA}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
    <div class="mapa-zast" hidden>
      <p><b>Pracownia Tomdar-Meble</b><br>{ADR1}, {ADR2}</p>
      <p>Mapa Google jest wyłączona w ustawieniach cookies.</p>
      <p><a class="btn" href="{TRASA}" target="_blank" rel="noopener">Wyznacz trasę</a> <button type="button" class="link-btn" data-ck-wlacz-mape>Pokaż mapę</button></p>
    </div>
  </div>
</section>'''


def materialy(R):
    z = Z['kuchnie']['zdjecia'][6]
    return f'''<section class="sek sek-mat" id="materialy">
  <div class="wrap mat">
    <figure class="mat-foto">{img(R, z)}</figure>
    <div class="mat-tekst">
      <h2 class="h-rama">Drewno, kamień, szkło i stal w jednym meblu</h2>
      <p>Nie trzymamy się jednego stylu ani jednego materiału. Pomagamy dobrać połączenie, które będzie dobrze wyglądać i długo służyć.</p>
      <div class="mat-listy">
        <div><h3>Materiały</h3><p>płyty MDF, płyty laminowane, drewno, kamień, szkło, stal kwasowa</p></div>
        <div><h3>Wykończenia</h3><p>lakierowanie, patynowanie, oklejanie i wiele innych technik</p></div>
        <div><h3>Style</h3><p>prowansalski, rustykalny, industrialny, nowoczesny</p></div>
      </div>
      <p class="mat-proj">Współpracujemy z projektantami wnętrz, więc pomożemy przy całej aranżacji pomieszczenia albo tylko przy jej części.</p>
    </div>
  </div>
</section>'''


def naglowek_strony(R, h1, lead, z, okruszki):
    return f'''<section class="ph">
  <figure class="ph-foto">{img(R, z, lazy=False)}</figure>
  <div class="ph-in">
    <nav class="okruszki" aria-label="Jesteś tutaj"><a href="{R or './'}">Strona główna</a><span aria-hidden="true">/</span><span aria-current="page">{okruszki}</span></nav>
    <div class="rama rama-ph">
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>
    </div>
  </div>
</section>'''


def cta_pas(R):
    return f'''<section class="cta-pas">
  <div class="wrap cta-pas-in">
    <p class="cta-pas-t">Masz wymiary albo projekt? Przygotujemy wycenę.</p>
    <div class="cta-pas-a"><a class="btn btn-duzy" href="{R}kontakt/#formularz">Zapytaj o wycenę</a><a class="cta-tel" href="{TEL1H}">{TEL1}</a></div>
  </div>
</section>'''


# ---------------------------------------------------------------- treści stron
def tresc_start(R, t):
    wyr = []
    for s, i in [('kuchnie', 1), ('schody', 0), ('kuchnie', 4), ('szafy', 0), ('tapicerowane', 1), ('salon', 0),
                 ('stoly', 0), ('kuchnie', 9), ('schody', 2), ('regaly', 0), ('lazienki', 0), ('szafy', 6)]:
        wyr.append(Z[s]['zdjecia'][i])
    z_prac = Z['kuchnie']['zdjecia'][15]
    return f'''<section class="hero" id="start">
  <figure class="hero-foto">
    <picture>
      <source media="(max-width:760px)" srcset="{R}img/hero-tel.webp" width="900" height="946">
      <img src="{R}img/hero.webp" alt="Kuchnia na wymiar z frontami ramowymi w drewnie i bieli, czarny blat i szklany panel" width="1900" height="946" fetchpriority="high">
    </picture>
  </figure>
  <div class="hero-in">
    <div class="rama">
      <h1>Meble na wymiar, które wychodzą poza ramy</h1>
      <p class="lead">Kuchnie, szafy, garderoby, schody, drzwi i&nbsp;meble tapicerowane. Projektujemy i&nbsp;wykonujemy je w naszej stolarni w&nbsp;Głoskowie-Letnisku pod Piasecznem.</p>
      <div class="hero-akcje"><a class="btn btn-duzy" href="#kontakt">Zapytaj o wycenę mebli</a></div>
    </div>
  </div>
</section>

<section class="sek sek-oferta" id="oferta">
  <div class="wrap">
    <div class="sek-glowa">
      <h2 class="h-rama">Co robimy w naszej stolarni</h2>
      <p>Każdy mebel powstaje pod konkretne wnętrze i wymiar. Łączymy drewno z płytą, kamieniem, szkłem i stalą, a styl dobieramy do domu: od prowansalskiego po nowoczesny.</p>
    </div>
    <div class="oferta">
{karty_oferty(R)}
    </div>
    <p class="oferta-dop">Wykonujemy też zabudowy biurowe oraz meble do obiektów użyteczności publicznej. <a href="{R}oferta/">Pełna oferta</a></p>
  </div>
</section>

<section class="sek sek-real" id="realizacje">
  <div class="wrap">
    <div class="sek-glowa sek-glowa-rzad">
      <div><h2 class="h-rama">Z naszej pracowni</h2></div>
      <div class="tor-nav">
        <span class="tor-licz" aria-live="polite">1 / {len(wyr)}</span>
        <div class="tor-strz">
          <button type="button" class="strz" data-strz="-1" aria-label="Poprzednie zdjęcia"><span class="strz-l"></span></button>
          <button type="button" class="strz" data-strz="1" aria-label="Następne zdjęcia"><span class="strz-p"></span></button>
        </div>
      </div>
    </div>
  </div>
  <div class="real-tor" data-tor tabindex="0" aria-label="Wybrane realizacje, przewiń w bok lub kliknij zdjęcie, aby powiększyć">
    {tor(R, wyr, 'wybrane', 'Wybrane realizacje')}
  </div>
  <div class="wrap"><a class="kat-link real-wiecej" href="{R}realizacje/">Wszystkie realizacje ({sum(len(v['zdjecia']) for v in Z.values())} zdjęć)</a></div>
</section>

{materialy(R)}

<section class="sek sek-prac" id="pracownia">
  <div class="wrap prac">
    <div class="prac-tekst">
      <h2 class="h-rama">Stolarnia prowadzona przez dwóch wspólników</h2>
      <p>Tomdar-Meble to pracownia stolarska Dariusza Skorupskiego i Tomasza Pliszki. Doświadczenie w obróbce drewna zbieramy od ponad 20 lat i wciąż inwestujemy w nowe maszyny i narzędzia.</p>
      <p>Każde zlecenie prowadzimy osobiście, od pierwszej rozmowy do ostatniego detalu. Nie korzystamy z pobieżnych, niesprawdzonych technik, bo mebel ma służyć przez długie lata.</p>
      <blockquote class="cytat"><p>Jedyne, co nas w życiu ogranicza, to nasza wyobraźnia.</p></blockquote>
      <div class="osoby">
        <p><b>Dariusz Skorupski</b><a href="{TEL1H}">{TEL1}</a></p>
        <p><b>Tomasz Pliszka</b><a href="{TEL2H}">{TEL2}</a></p>
      </div>
      <a class="kat-link" href="{R}o-nas/">Więcej o pracowni</a>
    </div>
    <figure class="prac-foto">{img(R, z_prac)}</figure>
  </div>
</section>

{kontakt_sekcja(R, t['test'])}'''


def tresc_oferta(R, t):
    wiersze = []
    for i, s in enumerate(KOLEJNOSC):
        n = len(Z[s]['zdjecia'])
        wiersze.append(f'''    <article class="of-w{' of-w-odw' if i % 2 else ''}" id="oferta-{s}">
      {karuzela(R, s, 6, 'kar kar-of')}
      <div class="of-t">
        <h2 class="h-rama">{e(Z[s]['nazwa'])}</h2>
        <p>{e(OPIS_KAT_DLUGI[s])}</p>
        <a class="kat-link" href="{R}realizacje/#{s}">Zobacz realizacje ({n})</a>
      </div>
    </article>''')
    w = '\n'.join(wiersze)
    return f'''{naglowek_strony(R, 'Meble na wymiar z naszej stolarni', 'Każdego rodzaju obróbka drewna: od kuchni i szaf, przez schody i drzwi, po meble tapicerowane. Zawsze pod konkretne wnętrze i wymiar.', Z['kuchnie']['zdjecia'][5], 'Oferta')}

<section class="sek sek-intro">
  <div class="wrap intro">
    <p class="intro-lead">Wykonujemy zabudowy kuchenne, łazienkowe i biurowe, garderoby, biblioteki oraz zabudowy innych pomieszczeń mieszkalnych i obiektów użyteczności publicznej. Robimy drzwi wewnętrzne przylgowe i bezprzylgowe, a w naszej stolarni można też zamówić meble tapicerowane.</p>
    <ul class="intro-lista">
      {''.join(f'<li><a href="#oferta-{s}">{e(Z[s]["nazwa"])}</a></li>' for s in KOLEJNOSC)}
    </ul>
  </div>
</section>

<section class="sek sek-of">
  <div class="wrap of">
{w}
  </div>
</section>

{materialy(R)}

{cta_pas(R)}'''


def tresc_realizacje(R, t):
    chips = ''.join(f'<a href="#{s}">{KAT_KROTKO[s]} <span>{len(Z[s]["zdjecia"])}</span></a>' for s in KOLEJNOSC)
    sekcje = '\n\n'.join(galeria_sekcja(R, s, i) for i, s in enumerate(KOLEJNOSC))
    razem = sum(len(v['zdjecia']) for v in Z.values())
    return f'''{naglowek_strony(R, 'Realizacje z naszej pracowni', f'{razem} zdjęć mebli wykonanych na wymiar. Przesuń galerię palcem lub myszą, kliknij zdjęcie, aby je powiększyć.', Z['schody']['zdjecia'][0], 'Realizacje')}

<nav class="chips" aria-label="Rodzaje mebli">
  <div class="chips-in">{chips}</div>
</nav>

{sekcje}

{cta_pas(R)}'''


def tresc_onas(R, t):
    return f'''{naglowek_strony(R, 'Pracownia, która nie boi się wyzwań', 'Tomdar-Meble to stolarnia w Głoskowie-Letnisku prowadzona przez dwóch wspólników: Dariusza Skorupskiego i Tomasza Pliszkę.', Z['kuchnie']['zdjecia'][15], 'O pracowni')}

<section class="sek sek-prac">
  <div class="wrap prac">
    <div class="prac-tekst">
      <h2 class="h-rama">Ponad 20 lat przy obróbce drewna</h2>
      <p>Tomdar-Meble to pracownia stolarska z dużym doświadczeniem. Ponad 20 lat pracy z drewnem pozwala nam stale doskonalić umiejętności, a każde zlecenie traktujemy osobiście.</p>
      <p>Dbamy tak samo o ogólny wygląd mebla, jak o każdy szczegół i najmniejszy detal. Nie wyróżniamy jednego kierunku: wykonujemy meble w stylu prowansalskim, rustykalnym i industrialnym, a także nowoczesne, eleganckie zabudowy. Nie ma dla nas rzeczy niemożliwych.</p>
      <p>Inwestujemy w nowoczesne zaplecze maszynowe i narzędzia. Nie akceptujemy pobieżnych, niesprawdzonych technik, na które zawód stolarza nie może sobie pozwolić.</p>
      <blockquote class="cytat"><p>Jedyne, co nas w życiu ogranicza, to nasza wyobraźnia.</p></blockquote>
    </div>
    <figure class="prac-foto">{img(R, Z['schody']['zdjecia'][1])}</figure>
  </div>
</section>

<section class="sek sek-szara">
  <div class="wrap">
    <div class="sek-glowa"><h2 class="h-rama">Na czym nam zależy</h2></div>
    <div class="wartosci">
      <article><span class="w-nr">01</span><h3>Trwałość</h3><p>Dobre materiały i sprawdzone technologie wykonania to meble, które służą przez długie lata.</p></article>
      <article><span class="w-nr">02</span><h3>Meble, o jakich marzysz</h3><p>Nie boimy się wyzwań, dlatego tworzymy meble dokładnie takie, jakie wymarzyli sobie nasi klienci.</p></article>
      <article><span class="w-nr">03</span><h3>Wygląd i wygoda</h3><p>Łączymy cechy użytkowe i estetyczne, dzięki czemu nasze meble tworzą niebanalny klimat wnętrza.</p></article>
    </div>
  </div>
</section>

<section class="sek sek-osoby">
  <div class="wrap">
    <div class="sek-glowa"><h2 class="h-rama">Wspólnicy</h2><p>Każde zlecenie traktujemy osobiście. Zadzwoń bezpośrednio do jednego z nas.</p></div>
    <div class="wspolnicy">
      <div class="wsp"><h3>Dariusz Skorupski</h3><a href="{TEL1H}">{TEL1}</a></div>
      <div class="wsp"><h3>Tomasz Pliszka</h3><a href="{TEL2H}">{TEL2}</a></div>
      <div class="wsp"><h3>E-mail</h3><a href="mailto:{MAIL}">{MAIL}</a></div>
    </div>
  </div>
</section>

{materialy(R)}

{cta_pas(R)}'''


def tresc_kontakt(R, t):
    return f'''{naglowek_strony(R, 'Kontakt i wycena', 'Zadzwoń albo napisz, co chcesz zamówić. Odpowiemy i umówimy się na rozmowę o szczegółach.', Z['szafy']['zdjecia'][0], 'Kontakt')}

{kontakt_sekcja(R, t['test'], 'h2', 'kontakt')}'''


def tresc_polityka(R, t):
    return f'''<section class="sek sek-tekst">
  <div class="wrap tekst">
    <nav class="okruszki okruszki-j" aria-label="Jesteś tutaj"><a href="{R or './'}">Strona główna</a><span aria-hidden="true">/</span><span aria-current="page">Polityka prywatności</span></nav>
    <h1 class="h-rama">Polityka prywatności i cookies</h1>
    <p class="tekst-data">Obowiązuje od {datetime.date.today().strftime('%d.%m.%Y')}</p>

    <h2>1. Administrator danych</h2>
    <p>Administratorem danych osobowych jest TOMDAR-MEBLE s.c. Dariusz Skorupski, Tomasz Pliszka, {ADR1}, {ADR2}, NIP 952-214-00-87. Kontakt w sprawie danych: <a href="mailto:{MAIL}">{MAIL}</a>, tel. <a href="{TEL1H}">{TEL1}</a>.</p>

    <h2>2. Jakie dane i w jakim celu</h2>
    <p>Przetwarzamy dane, które podajesz w formularzu kontaktowym, w wiadomości e-mail lub podczas rozmowy telefonicznej: imię i nazwisko, numer telefonu, adres e-mail, treść wiadomości oraz dołączone pliki (np. projekt lub zdjęcie wnętrza). Dane wykorzystujemy wyłącznie po to, aby odpowiedzieć na zapytanie, przygotować wycenę i wykonać zamówienie.</p>
    <p>Podstawą prawną jest art. 6 ust. 1 lit. b RODO (działania przed zawarciem i w celu wykonania umowy) oraz art. 6 ust. 1 lit. f RODO (nasz prawnie uzasadniony interes, czyli odpowiedź na wiadomość i obrona przed roszczeniami). Podanie danych jest dobrowolne, ale bez nich nie możemy odpowiedzieć.</p>

    <h2>3. Jak długo przechowujemy dane</h2>
    <p>Dane z zapytań przechowujemy przez czas potrzebny do odpowiedzi i ewentualnej realizacji zamówienia, a potem przez okres przedawnienia roszczeń lub tak długo, jak wymagają tego przepisy podatkowe i rachunkowe. Zapytania, które nie zakończyły się zamówieniem, usuwamy najpóźniej po 12 miesiącach.</p>

    <h2>4. Odbiorcy danych</h2>
    <p>Dane mogą trafić do firm, które obsługują nas technicznie: dostawcy hostingu strony i poczty e-mail (wiadomości z formularza trafiają na skrzynkę w usłudze Gmail firmy Google) oraz biura rachunkowego. Nie sprzedajemy danych i nie przekazujemy ich w celach marketingowych. W związku z korzystaniem z usług Google dane mogą być przekazywane poza Europejski Obszar Gospodarczy na podstawie standardowych klauzul umownych lub decyzji Komisji Europejskiej.</p>

    <h2>5. Twoje prawa</h2>
    <p>Masz prawo dostępu do swoich danych, ich sprostowania, usunięcia, ograniczenia przetwarzania, przenoszenia oraz wniesienia sprzeciwu. Możesz też złożyć skargę do Prezesa Urzędu Ochrony Danych Osobowych (ul. Stawki 2, 00-193 Warszawa). Aby skorzystać z praw, napisz na <a href="mailto:{MAIL}">{MAIL}</a>.</p>

    <h2 id="cookies">6. Pliki cookies</h2>
    <p>Strona nie używa narzędzi analitycznych ani reklamowych. Korzystamy z:</p>
    <ul>
      <li><b>pamięci przeglądarki (localStorage)</b> - zapisujemy w niej wyłącznie Twój wybór dotyczący cookies (na 12 miesięcy), aby baner nie pojawiał się przy każdej wizycie;</li>
      <li><b>mapy Google</b> osadzonej na stronie głównej i w zakładce Kontakt - dostawca, Google Ireland Ltd., może zapisywać własne pliki cookies i otrzymuje Twój adres IP. Zasady Google: <a href="https://policies.google.com/privacy?hl=pl" target="_blank" rel="noopener">policies.google.com/privacy</a>.</li>
    </ul>
    <p>Jeśli wybierzesz „Tylko niezbędne”, mapa Google nie będzie wyświetlana, a w jej miejscu pojawi się adres i link do wyznaczenia trasy. Swój wybór możesz zmienić w każdej chwili przyciskiem „Ustawienia cookies” w stopce strony. Pliki cookies możesz też usunąć lub zablokować w ustawieniach przeglądarki.</p>

    <h2>7. Zmiany polityki</h2>
    <p>O zmianach tej polityki poinformujemy, publikując jej nową wersję na tej stronie.</p>
  </div>
</section>'''


TRESCI = {'start': tresc_start, 'oferta': tresc_oferta, 'realizacje': tresc_realizacje, 'o-nas': tresc_onas,
          'kontakt': tresc_kontakt, 'polityka': tresc_polityka}


def jsonld(t, sciezka, tytul_krotki):
    u = t['url']
    firma = {
        '@context': 'https://schema.org', '@type': 'LocalBusiness', '@id': u + '#firma',
        'name': 'Tomdar-Meble', 'legalName': 'TOMDAR-MEBLE s.c. Dariusz Skorupski, Tomasz Pliszka',
        'description': 'Pracownia stolarska: kuchnie, szafy, garderoby, schody, drzwi, stoły i meble tapicerowane na wymiar.',
        'url': u, 'logo': u + 'favicon.svg', 'image': u + 'img/og.jpg',
        'telephone': '+48501156315', 'email': MAIL, 'taxID': '9522140087',
        'address': {'@type': 'PostalAddress', 'streetAddress': 'ul. Graniczna 15', 'postalCode': '05-503',
                    'addressLocality': 'Głosków-Letnisko', 'addressRegion': 'mazowieckie', 'addressCountry': 'PL'},
        'hasMap': 'https://www.google.com/maps/search/?api=1&query=Graniczna+15+05-503+G%C5%82osk%C3%B3w-Letnisko',
        'founder': [{'@type': 'Person', 'name': 'Dariusz Skorupski', 'telephone': '+48501156315'},
                    {'@type': 'Person', 'name': 'Tomasz Pliszka', 'telephone': '+48607884191'}],
        'knowsAbout': ['meble na wymiar', 'kuchnie na wymiar', 'szafy wnękowe', 'garderoby', 'schody drewniane',
                       'drzwi bezprzylgowe', 'meble tapicerowane', 'stoły z drewna'],
    }
    out = [firma]
    if sciezka:
        out.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Strona główna', 'item': u},
            {'@type': 'ListItem', 'position': 2, 'name': tytul_krotki, 'item': u + sciezka}]})
    return '\n'.join('<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + '</script>' for o in out)


KROTKIE = {'oferta/': 'Oferta', 'realizacje/': 'Realizacje', 'o-nas/': 'O pracowni', 'kontakt/': 'Kontakt', 'polityka-prywatnosci/': 'Polityka prywatności'}


def strona(t, sciezka, klucz, tytul, opis, tresc_html=None, status404=False):
    R = '../' * sciezka.count('/')
    if status404:
        R = '/' if not t['test'] else '/tomdar-strona/'
    can = t['url'] + sciezka
    tresc = tresc_html if tresc_html is not None else TRESCI[klucz](R, t)
    preload = f'<link rel="preload" href="{R}img/hero.webp" as="image" media="(min-width:761px)">\n<link rel="preload" href="{R}img/hero-tel.webp" as="image" media="(max-width:760px)">' if klucz == 'start' else ''
    ld = '' if status404 else jsonld(t, sciezka, KROTKIE.get(sciezka, ''))
    canon = '' if status404 else f'<link rel="canonical" href="{can}">'
    robots = 'noindex,nofollow' if (t['test'] or status404) else t['robots']
    styl_badge = open(os.path.join(TU, 'badge_style.html'), encoding='utf-8').read()
    return f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="{robots}">
<title>{e(tytul)}</title>
<meta name="description" content="{e(opis)}">
{canon}
<meta name="theme-color" content="#FFFFFF">
<meta property="og:type" content="website">
<meta property="og:locale" content="pl_PL">
<meta property="og:site_name" content="Tomdar-Meble">
<meta property="og:title" content="{e(tytul)}">
<meta property="og:description" content="{e(opis)}">
<meta property="og:url" content="{can}">
<meta property="og:image" content="{t['url']}img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<link rel="preload" href="{R}fonts/montserrat-latin.woff2" as="font" type="font/woff2" crossorigin>
{preload}
<link rel="stylesheet" href="{R}style.css?v={WERSJA}">
<link rel="icon" href="{R}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{R}favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="{R}apple-touch-icon.png">
{styl_badge}
{ld}
</head>
<body class="s-{klucz}">
<a class="skip" href="#tresc">Przejdź do treści</a>
{logo_defs()}
{naglowek(R, klucz)}
<main id="tresc">
{tresc}
</main>
{stopka(R, klucz)}
<script src="{R}app.js?v={WERSJA}" defer></script>
</body>
</html>
'''


def tresc_404(R):
    return f'''<section class="sek sek-tekst">
  <div class="wrap tekst t404">
    <h1 class="h-rama">Nie ma takiej strony</h1>
    <p>Strona mogła zostać przeniesiona po zmianie wyglądu serwisu. Zobacz <a href="{R}realizacje/">realizacje</a>, <a href="{R}oferta/">ofertę</a> albo wróć na <a href="{R}">stronę główną</a>.</p>
    <p><a class="btn" href="{R}kontakt/">Kontakt z pracownią</a></p>
  </div>
</section>'''


WERSJA = datetime.datetime.now().strftime('%m%d%H%M')


def buduj(tryb):
    t = TRYBY[tryb]
    out = t['out']
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    for sciezka, klucz, tytul, opis in STRONY:
        d = os.path.join(out, sciezka)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(strona(t, sciezka, klucz, tytul, opis))
    R404 = '/' if not t['test'] else '/tomdar-strona/'
    with open(os.path.join(out, '404.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(strona(t, '', '404', 'Nie znaleziono strony | Tomdar-Meble', 'Strona nie istnieje.', tresc_404(R404), status404=True))
    # zasoby
    for n in ['style.css', 'app.js', 'favicon.svg', 'favicon.ico', 'apple-touch-icon.png']:
        shutil.copy(os.path.join(TU, n), out)
    shutil.copytree(os.path.join(TU, 'fonts'), os.path.join(out, 'fonts'))
    shutil.copytree(os.path.join(TU, 'img'), os.path.join(out, 'img'))
    if t['test']:
        open(os.path.join(out, 'robots.txt'), 'w', newline='\n').write('User-agent: *\nDisallow: /\n')
        open(os.path.join(out, '.nojekyll'), 'w').write('')
    else:
        open(os.path.join(out, 'robots.txt'), 'w', newline='\n').write(
            'User-agent: *\nDisallow: /wyslij.php\nDisallow: /_limity/\n\nSitemap: https://tomdar-meble.pl/sitemap.xml\n')
        sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for sciezka, klucz, *_ in STRONY:
            pr = '1.0' if not sciezka else ('0.3' if klucz == 'polityka' else '0.8')
            sm.append(f'  <url><loc>{t["url"]}{sciezka}</loc><lastmod>{DZIS}</lastmod><priority>{pr}</priority></url>')
        sm.append('</urlset>')
        open(os.path.join(out, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write('\n'.join(sm) + '\n')
        for n in ['.htaccess', 'wyslij.php']:
            shutil.copy(os.path.join(TU, n), out)
        os.makedirs(os.path.join(out, '_limity'))
        shutil.copy(os.path.join(TU, '_limity.htaccess'), os.path.join(out, '_limity', '.htaccess'))
    print(tryb, '->', out)


if __name__ == '__main__':
    for tr in ('prod', 'test'):
        buduj(tr)
