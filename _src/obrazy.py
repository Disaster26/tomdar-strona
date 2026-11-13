# Przygotowanie zdjęć realizacji Tomdar-Meble ze starej strony (Quick.Cms).
# Użycie: python -I obrazy.py <katalog_surowych_jpg>
# Każde zdjęcie: sprawdzenie sygnatury, obrót wg EXIF, odcięcie pomarańczowej daty aparatu,
# delikatna korekta jasności/kontrastu, zapis jako nowy WebP bez metadanych.
import sys, os, json
from PIL import Image, ImageOps, ImageEnhance

RAW = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
os.makedirs(OUT, exist_ok=True)

# numer pliku w katalogu surowym -> opis (alt)
KAT = {
 'kuchnie': ('Kuchnie na wymiar', [
  ('081', 'Kuchnia z frontami ramowymi w drewnie i bieli, czarny blat i szklany panel'),
  ('000', 'Otwarta kuchnia z wyspą i zabudową w salonie, łukowa wnęka nad zabudową'),
  ('004', 'Wyspa kuchenna z hokerami i chłodziarką do wina, zabudowa przy drzwiach'),
  ('003', 'Biały blat wyspy z chłodziarką do wina w podstawie'),
  ('005', 'Wysuwane szuflady wyspy kuchennej z organizerami'),
  ('054', 'Kuchnia z wyspą w okładzinie o fakturze kamienia, wysoka zabudowa z lodówką'),
  ('055', 'Ciemna wyspa kuchenna z czarnym blatem przy ceglanej ścianie'),
  ('056', 'Narożnik wyspy kuchennej w okładzinie imitującej kamień'),
  ('012', 'Biała kuchnia z wyspą i wysoką zabudową z piekarnikami'),
  ('013', 'Biała wyspa z czarnym blatem i szufladami'),
  ('041', 'Kuchnia w kształcie litery L z frontami ramowymi w drewnie'),
  ('042', 'Wysokie szafy kuchenne z frontami ramowymi w drewnie i bieli'),
  ('044', 'Wysoka zabudowa z lodówką side by side i piekarnikami w czerni'),
  ('043', 'Zabudowa kuchenna z lodówką i okrągłym czarnym stołem'),
  ('063', 'Zabudowa kuchenna pod oknem z czarnym blatem i frontami ramowymi'),
  ('046', 'Klasyczna biała kuchnia z kamiennym blatem i łukowymi oknami'),
  ('053', 'Szuflady z drewnianymi przegródkami w klasycznej kuchni'),
  ('060', 'Wysuwany kamienny blat roboczy w klasycznej zabudowie'),
  ('038', 'Biała zabudowa kuchenna pod oknem z drewnianym blatem'),
 ]),
 'szafy': ('Szafy, garderoby i zabudowy', [
  ('067', 'Szafa pod skosem z podświetlonym wnętrzem i szufladami'),
  ('068', 'Garderoba pod skosem z drążkiem i oświetleniem LED'),
  ('069', 'Szafa pod skosem z półkami na ubrania i podświetleniem'),
  ('066', 'Wysoka szafa w przedpokoju z tapicerowanym siedziskiem'),
  ('052', 'Wnęka z tapicerowanym siedziskiem i szafą w przedpokoju'),
  ('051', 'Szafa wnękowa pod skosem z czarnymi uchwytami'),
  ('057', 'Szafa w zabudowie pod schodami w jasnym dekorze drewna'),
  ('079', 'Garderoba z półkami i drążkami w dekorze drewna'),
  ('080', 'Otwarta garderoba z półkami i drążkami w fornirze'),
  ('037', 'Szafa z drzwiami przesuwnymi i półkami obok'),
  ('001', 'Szafa w przedpokoju z otwartą wnęką i lustrem'),
  ('029', 'Szafa pod skosem w szarym wykończeniu o fakturze betonu'),
  ('030', 'Uchwyty w kształcie dłoni na szarych frontach szafy'),
  ('031', 'Szuflady z mosiężnymi uchwytami w kształcie dłoni'),
  ('034', 'Szafa pod skosem w jasnym, patynowanym wykończeniu'),
  ('035', 'Fragment zabudowy pod skosem z komodą'),
  ('036', 'Rzeźbiony uchwyt na jasnym froncie szafy'),
 ]),
 'salon': ('Zabudowy salonu i RTV', [
  ('006', 'Ściana TV z płytą o wzorze kamienia, niska szafka i podświetlona witryna'),
  ('064', 'Klasyczna zabudowa salonu z witryną i półkami w drewnie'),
  ('070', 'Klasyczna biała zabudowa z telewizorem we wnęce'),
  ('071', 'Biała zabudowa z ukrytym telewizorem i drewnianą wnęką'),
  ('074', 'Biała zabudowa ściany z telewizorem i półkami'),
  ('076', 'Ściana z frontów w fornirze z wnęką na telewizor'),
  ('065', 'Długa biała szafka RTV z szufladami'),
  ('009t', 'Komoda RTV w ciemnym fornirze z szufladami'),
 ]),
 'lazienki': ('Łazienki', [
  ('002', 'Łazienka z szafką podumywalkową, lustrem z podświetleniem i zabudową pralki'),
  ('016', 'Biała wisząca szafka łazienkowa z drewnianym uchwytem'),
  ('014', 'Zaokrąglona szafka pod umywalkę z lustrem w ramie'),
  ('072', 'Długa zabudowa łazienkowa z szufladami w stylu klasycznym'),
  ('073', 'Toaletka z lustrami w klasycznej łazience'),
 ]),
 'schody': ('Schody, drzwi i okładziny', [
  ('049', 'Drewniane schody i drzwi w okładzinie z fornirowanych paneli'),
  ('050', 'Ściana w drewnianej okładzinie z ukrytymi drzwiami przy schodach'),
  ('048', 'Drzwi z przeszkleniem w ciemnej drewnianej okładzinie'),
  ('047', 'Białe drzwi dwuskrzydłowe z szybami'),
  ('017', 'Drewniane schody zabiegowe z okładziną ściany'),
  ('018', 'Drewniana zabudowa korytarza i drzwi przy schodach'),
  ('019', 'Okładzina ściany z drewna przy schodach'),
  ('020', 'Korytarz z drzwiami wewnętrznymi i drewnianą podłogą'),
  ('021', 'Drewniane schody prowadzące na piętro'),
  ('058', 'Drewniana balustrada schodów z tralkami'),
  ('022', 'Biała balustrada z drewnianą poręczą'),
  ('024', 'Białe schody z ciemnymi stopniami'),
  ('075', 'Panele ścienne z drewna z podświetleniem LED'),
 ]),
 'tapicerowane': ('Meble tapicerowane i sypialnie', [
  ('082', 'Łóżko z wysokim tapicerowanym zagłówkiem i szafkami nocnymi'),
  ('007', 'Sypialnia z tapicerowanymi panelami ściennymi i szafą'),
  ('025', 'Łóżko z tapicerowaną ramą i zagłówkiem pod skosem'),
  ('027', 'Tapicerowany zagłówek łóżka z szafkami nocnymi'),
  ('028', 'Zagłówek łóżka obity szarą tkaniną'),
  ('026', 'Szafka nocna w szarym wykończeniu przy łóżku'),
  ('032', 'Lustro w tapicerowanej ramie w sypialni'),
  ('033', 'Komoda z szufladami w jasnym, patynowanym wykończeniu'),
  ('023', 'Łóżko z szufladami w podstawie'),
  ('008t', 'Łóżko z tapicerowanym zagłówkiem'),
  ('015', 'Szafka nocna obita jasną tkaniną'),
 ]),
 'stoly': ('Stoły i blaty', [
  ('061', 'Stół z dębowego blatu z czarną stalową wstawką i podstawą'),
  ('062', 'Długi dębowy stół do jadalni z krzesłami'),
  ('077', 'Dębowy stół na stalowych płozach'),
  ('078', 'Blat stołu z drewna z czarnym pasem stali'),
  ('040', 'Okrągły czarny stół na stalowej podstawie w kuchni'),
  ('011', 'Stolik kawowy z drewna i szkła'),
  ('010t', 'Stolik kawowy z drewnianą ramą i szklanym blatem'),
 ]),
 'regaly': ('Biblioteki i regały', [
  ('039', 'Regał na książki od podłogi po sufit przy kuchni'),
  ('045', 'Biblioteka połączona z zabudową kuchenną'),
  ('059', 'Podświetlana wnęka z półkami'),
 ]),
}

def plik(n):
    for f in os.listdir(RAW):
        if os.path.splitext(f)[0] == n:
            return os.path.join(RAW, f)
    raise SystemExit('brak ' + n)

SYG = (b'\xff\xd8\xff', b'\x89PNG')

def data_aparatu(im):
    """Zwraca y górnej krawędzi pomarańczowej daty w dolnych 14% kadru albo None."""
    w, h = im.size
    y0 = int(h * 0.86)
    px = im.load()
    wiersze = []
    for y in range(y0, h):
        n = 0
        for x in range(int(w * 0.35), w, 2):
            r, g, b = px[x, y]
            if r > 200 and 70 < g < 175 and b < 90 and r - g > 70:
                n += 1
        if n >= 3:
            wiersze.append(y)
    if len(wiersze) >= 4:
        return min(wiersze)
    return None

wynik = {}
for slug, (nazwa, lista) in KAT.items():
    elem = []
    for i, (n, alt) in enumerate(lista, 1):
        p = plik(n)
        with open(p, 'rb') as fh:
            if not fh.read(4).startswith(SYG):
                raise SystemExit('zła sygnatura ' + p)
        im = Image.open(p)
        im = ImageOps.exif_transpose(im).convert('RGB')
        y = None if n.endswith('t') else data_aparatu(im)
        if y is not None:
            im = im.crop((0, 0, im.width, max(int(im.height * 0.8), y - 6)))
        im = ImageOps.autocontrast(im, cutoff=0.5, preserve_tone=True)
        im = ImageEnhance.Color(im).enhance(1.04)
        maly = n.endswith('t')
        nazwa_pl = f'{slug}-{i:02d}.webp'
        if im.width > 1600:
            im.thumbnail((1600, 1600), Image.LANCZOS)
        im.save(os.path.join(OUT, nazwa_pl), 'WEBP', quality=80, method=6)
        elem.append({'src': nazwa_pl, 'w': im.width, 'h': im.height, 'alt': alt, 'maly': maly, 'zrodlo': n, 'data_odcieta': y is not None})
    wynik[slug] = {'nazwa': nazwa, 'zdjecia': elem}

# hero: pełna i mobilna wersja banera z kuchnią
b = ImageOps.autocontrast(Image.open(plik('081')).convert('RGB'), cutoff=0.5, preserve_tone=True)
b.save(os.path.join(OUT, 'hero.webp'), 'WEBP', quality=78, method=6)
m = b.crop((int(b.width * 0.30), 0, int(b.width * 0.30) + 900, b.height))
m.save(os.path.join(OUT, 'hero-tel.webp'), 'WEBP', quality=78, method=6)
og = b.resize((1200, int(b.height * 1200 / b.width)), Image.LANCZOS)
og = og.crop((0, (og.height - 630) // 2, 1200, (og.height - 630) // 2 + 630))
og.save(os.path.join(OUT, 'og.jpg'), 'JPEG', quality=84, optimize=True)

json.dump(wynik, open(os.path.join(os.path.dirname(OUT), 'zdjecia.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(sum(len(v['zdjecia']) for v in wynik.values()), 'zdjęć;', 'data odcięta:', [e['zrodlo'] for v in wynik.values() for e in v['zdjecia'] if e['data_odcieta']])
