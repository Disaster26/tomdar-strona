<?php
/* Formularz zapytań TOMDAR-MEBLE - wysyłka z serwera strony funkcją mail() (bez usług zewnętrznych).

   POST z formularza (multipart/form-data): imie, telefon, email, mebel, wiadomosc, plik (opcjonalnie), zgoda, _z, strona_www (pułapka).
   GET ?znacznik=1 -> {"z":"<czas>.<podpis>"} - znacznik czasu podpisany HMAC (formularz pobiera go przy pierwszym kliknięciu).
   Z JS (Accept: application/json) odpowiedź JSON {"success":true|false,"komunikat":...}, bez JS prosta strona HTML.

   Zabezpieczenia: tylko POST/GET, limit rozmiaru, Origin musi być tomdar-meble.pl (gdy przeglądarka go wysyła),
   znacznik czasu (min. 3 s, max. 2 h, jednorazowy) albo - bez JS - zgodny Origin, pułapka strona_www,
   walidacja pól, limit zgłoszeń z jednej sieci (5/h, 12/dobę) i łącznie (40/dobę), załącznik: 1 plik do 10 MB,
   tylko JPG/PNG/WEBP/HEIC/PDF ze sprawdzeniem sygnatury. Potwierdzenie do klienta: neutralne, bez cytowania treści,
   max 1 na adres na dobę i 10 na godzinę łącznie.

   Sekret HMAC i liczniki: katalog _limity (zablokowany w .htaccess); sekret tworzy się sam przy pierwszym uruchomieniu.
   Tryb testowy (tylko lokalnie): zmienna środowiskowa TOMDAR_MAIL_DO_PLIKU=<katalog> -> zamiast mail() zapis .eml,
   dopuszczony Origin http://localhost. Zgodność: PHP 5.4 - 8.x. */

define('ODBIORCA', 'tomdar.meble@gmail.com');           // tu przychodzą zapytania
define('NADAWCA', 'formularz@tomdar-meble.pl');         // From (adres w domenie strony - patrz WGRANIE.md)
define('NADAWCA_NAZWA', 'Strona tomdar-meble.pl');
define('FIRMA', 'Tomdar-Meble');
define('TELEFON', '501 156 315');
define('DOMENY', '#^https?://(www\.)?tomdar-meble\.pl(:\d+)?$#');
define('LIMIT_H', 5);
define('LIMIT_D', 12);
define('LIMIT_GLOBALNY_D', 40);
define('LIMIT_POTW_H', 10);
define('MAX_PLIK', 10 * 1024 * 1024);
define('MAX_ZADANIE', 11 * 1024 * 1024);
define('ZNACZNIK_MIN', 3);
define('ZNACZNIK_MAX', 7200);

date_default_timezone_set('Europe/Warsaw');
header('X-Robots-Tag: noindex');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');
if (function_exists('header_remove')) header_remove('X-Powered-By');

$DEV = (string) getenv('TOMDAR_MAIL_DO_PLIKU');
$METODA = isset($_SERVER['REQUEST_METHOD']) ? $_SERVER['REQUEST_METHOD'] : '';
$JSON = (isset($_SERVER['HTTP_ACCEPT']) && stripos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false) || isset($_GET['znacznik']);

function wez($t, $k, $d = '') { return (is_array($t) && isset($t[$k])) ? $t[$k] : $d; }
function h($s) { return htmlspecialchars((string) $s, ENT_QUOTES, 'UTF-8'); }
function losowe($n) {
    if (function_exists('random_bytes')) { try { return random_bytes($n); } catch (Exception $e) {} }
    if (function_exists('openssl_random_pseudo_bytes')) return openssl_random_pseudo_bytes($n);
    $b = ''; for ($i = 0; $i < $n; $i++) $b .= chr(mt_rand(0, 255)); return $b;
}
function rowne($a, $b) {
    if (function_exists('hash_equals')) return hash_equals((string) $a, (string) $b);
    if (strlen($a) !== strlen($b)) return false;
    $r = 0; for ($i = 0; $i < strlen($a); $i++) $r |= ord($a[$i]) ^ ord($b[$i]); return $r === 0;
}
function kod($k) {
    if (function_exists('http_response_code')) { http_response_code($k); return; }
    header('HTTP/1.1 ' . $k . ' Status', true, $k);
}
function odpowiedz($ok, $k, $komunikat) {
    global $JSON;
    kod($k);
    if ($JSON) {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(array('success' => $ok, 'komunikat' => $komunikat));
        exit;
    }
    header('Content-Type: text/html; charset=utf-8');
    echo '<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
       . '<meta name="robots" content="noindex"><title>' . ($ok ? 'Wysłano' : 'Nie wysłano') . ' - ' . FIRMA . '</title></head>'
       . '<body style="margin:0;padding:40px 16px;background:#EEF0F2;font:17px/1.6 Arial,sans-serif;color:#141414">'
       . '<main style="max-width:560px;margin:0 auto;background:#fff;border-top:6px solid #FDC506;padding:28px 24px">'
       . '<p style="margin:0 0 18px;font-weight:bold">' . h($komunikat) . '</p>'
       . '<p style="margin:0"><a href="/" style="color:#141414">Wróć na stronę ' . FIRMA . '</a></p></main></body></html>';
    exit;
}

// ---------------------------------------------------------------- katalog limitów i sekret
function katalog() {
    global $DEV;
    $k = getenv('TOMDAR_KATALOG_LIMITOW');
    if (!$k) $k = __DIR__ . '/_limity';
    if (!is_dir($k)) @mkdir($k, 0750, true);
    return $k;
}
function sekret() {
    static $s = null;
    if ($s !== null) return $s;
    $p = katalog() . '/_sekret.php';
    if (is_file($p)) { $s = (string) include $p; if (strlen($s) >= 32) return $s; }
    $s = bin2hex(losowe(32));
    @file_put_contents($p, "<?php return '" . $s . "';\n", LOCK_EX);
    return $s;
}
function siec() {
    $ip = (string) wez($_SERVER, 'REMOTE_ADDR', '0.0.0.0');
    if (strpos($ip, ':') !== false) {                  // IPv6 -> sieć /64
        $b = @inet_pton($ip);
        if ($b !== false) return bin2hex(substr($b, 0, 8));
    }
    return $ip;
}
function z_plikiem($nazwa, $fn) {                      // licznik JSON z blokadą
    $p = katalog() . '/' . $nazwa;
    $f = @fopen($p, 'c+');
    if (!$f) return true;                              // brak zapisu - nie blokujemy klienta
    flock($f, LOCK_EX);
    $tresc = stream_get_contents($f);
    $dane = json_decode($tresc ? $tresc : '{}', true);
    if (!is_array($dane)) $dane = array();
    $wynik = $fn($dane);
    ftruncate($f, 0); rewind($f); fwrite($f, json_encode($dane)); fflush($f);
    flock($f, LOCK_UN); fclose($f);
    return $wynik;
}

// ---------------------------------------------------------------- Origin
$origin = (string) wez($_SERVER, 'HTTP_ORIGIN', '');
$originOk = $origin !== '' && (preg_match(DOMENY, $origin) || ($DEV !== '' && preg_match('#^http://(localhost|127\.0\.0\.1)(:\d+)?$#', $origin)));
if ($origin !== '' && !$originOk) odpowiedz(false, 403, 'Wiadomość odrzucona.');

// ---------------------------------------------------------------- GET: znacznik czasu
if ($METODA === 'GET' && isset($_GET['znacznik'])) {
    $t = (string) time();
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(array('z' => $t . '.' . substr(hash_hmac('sha256', 'tomdar|' . $t . '|' . siec(), sekret()), 0, 40)));
    exit;
}
if ($METODA !== 'POST') { header('Allow: GET, POST'); odpowiedz(false, 405, 'Ten adres przyjmuje tylko wiadomości z formularza.'); }

$dl = (int) wez($_SERVER, 'CONTENT_LENGTH', 0);
if ($dl > MAX_ZADANIE || (empty($_POST) && $dl > 0)) odpowiedz(false, 413, 'Załącznik jest za duży (maksymalnie 10 MB). Wyślij mniejszy plik albo prześlij go e-mailem na ' . ODBIORCA . '.');

// ---------------------------------------------------------------- pułapka i znacznik
if (trim((string) wez($_POST, 'strona_www')) !== '') odpowiedz(true, 200, 'Dziękujemy, zapytanie zostało wysłane.');   // bot: udajemy sukces
$z = (string) wez($_POST, '_z');
$teraz = time();
$zOk = false;
if (preg_match('/^(\d{9,11})\.([0-9a-f]{40})$/', $z, $m)) {
    $wiek = $teraz - (int) $m[1];
    $zOk = rowne(substr(hash_hmac('sha256', 'tomdar|' . $m[1] . '|' . siec(), sekret()), 0, 40), $m[2]) && $wiek >= ZNACZNIK_MIN && $wiek <= ZNACZNIK_MAX;
    if ($zOk) {
        $zOk = z_plikiem('zuzyte.json', function (&$d) use ($z, $teraz) {
            foreach ($d as $k => $t) if ($t < $teraz - ZNACZNIK_MAX) unset($d[$k]);
            $k = sha1($z);
            if (isset($d[$k])) return false;
            $d[$k] = $teraz; return true;
        });
    }
}
if (!$zOk && !$originOk) odpowiedz(false, 403, 'Formularz wysłano zbyt szybko albo strona była otwarta zbyt długo. Odśwież stronę i spróbuj ponownie albo zadzwoń: ' . TELEFON . '.');

// ---------------------------------------------------------------- pola
function pole($k, $max) {
    $v = (string) wez($_POST, $k);
    $v = str_replace("\0", '', $v);
    if (function_exists('mb_substr')) $v = mb_substr($v, 0, $max, 'UTF-8'); else $v = substr($v, 0, $max * 2);
    return trim($v);
}
function linia($s) { return trim(preg_replace('/[\r\n\t]+/', ' ', $s)); }
$imie = linia(pole('imie', 100));
$tel = linia(pole('telefon', 30));
$email = linia(pole('email', 120));
$mebel = linia(pole('mebel', 60));
$tresc = pole('wiadomosc', 5000);
$MEBLE = array('Kuchnia', 'Szafa lub garderoba', 'Zabudowa salonu lub RTV', 'Zabudowa łazienki', 'Schody lub drzwi', 'Meble tapicerowane', 'Stół lub blat', 'Regał lub biblioteka', 'Inny mebel');
if (!in_array($mebel, $MEBLE, true)) $mebel = 'Inny mebel';
$bledy = array();
if (strlen($imie) < 2) $bledy[] = 'imię i nazwisko';
if ($tel === '' && $email === '') $bledy[] = 'telefon lub e-mail';
if ($tel !== '' && !preg_match('/^[0-9 +()\-\.\/]{7,30}$/', $tel)) $bledy[] = 'numer telefonu';
if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) $bledy[] = 'adres e-mail';
if (strlen($tresc) < 3) $bledy[] = 'treść wiadomości';
if (wez($_POST, 'zgoda') !== 'tak') $bledy[] = 'zgoda na przetwarzanie danych';
if (preg_match_all('#https?://#i', $tresc) > 3) $bledy[] = 'treść (za dużo linków)';
if ($bledy) odpowiedz(false, 422, 'Sprawdź pola: ' . implode(', ', $bledy) . '.');

// ---------------------------------------------------------------- załącznik
$zal = null;
if (!empty($_FILES['plik']) && wez($_FILES['plik'], 'error', UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_NO_FILE) {
    $p = $_FILES['plik'];
    if ($p['error'] !== UPLOAD_ERR_OK || $p['size'] > MAX_PLIK || !is_uploaded_file($p['tmp_name'])) {
        odpowiedz(false, 413, 'Nie udało się przyjąć załącznika (maksymalnie 10 MB). Wyślij mniejszy plik albo prześlij go e-mailem na ' . ODBIORCA . '.');
    }
    $nag = (string) file_get_contents($p['tmp_name'], false, null, 0, 16);
    $typ = null;
    if (substr($nag, 0, 3) === "\xFF\xD8\xFF") $typ = array('jpg', 'image/jpeg');
    elseif (substr($nag, 0, 8) === "\x89PNG\r\n\x1a\n") $typ = array('png', 'image/png');
    elseif (substr($nag, 0, 4) === 'RIFF' && substr($nag, 8, 4) === 'WEBP') $typ = array('webp', 'image/webp');
    elseif (substr($nag, 0, 5) === '%PDF-') $typ = array('pdf', 'application/pdf');
    elseif (substr($nag, 4, 4) === 'ftyp' && preg_match('/^(heic|heix|mif1|msf1|hevc)$/', substr($nag, 8, 4))) $typ = array('heic', 'image/heic');
    if (!$typ) odpowiedz(false, 422, 'Załącznik musi być zdjęciem (JPG, PNG, WEBP, HEIC) albo plikiem PDF.');
    $zal = array('nazwa' => 'zalacznik.' . $typ[0], 'typ' => $typ[1], 'dane' => file_get_contents($p['tmp_name']), 'rozmiar' => (int) $p['size']);
}

// ---------------------------------------------------------------- limity
$ip = hash_hmac('sha256', 'ip|' . siec(), sekret());
$wolno = z_plikiem('ip.json', function (&$d) use ($ip, $teraz) {
    foreach ($d as $k => $l) { $d[$k] = array_values(array_filter((array) $l, function ($t) use ($teraz) { return $t > $teraz - 86400; })); if (!$d[$k]) unset($d[$k]); }
    $moje = isset($d[$ip]) ? $d[$ip] : array();
    $godz = count(array_filter($moje, function ($t) use ($teraz) { return $t > $teraz - 3600; }));
    if ($godz >= LIMIT_H || count($moje) >= LIMIT_D) return false;
    $moje[] = $teraz; $d[$ip] = $moje; return true;
});
if (!$wolno) odpowiedz(false, 429, 'Wysłano już kilka zapytań. Spróbuj później albo zadzwoń: ' . TELEFON . '.');
$wolnoG = z_plikiem('globalny.json', function (&$d) use ($teraz) {
    $d = array_values(array_filter($d, function ($t) use ($teraz) { return $t > $teraz - 86400; }));
    if (count($d) >= LIMIT_GLOBALNY_D) return false;
    $d[] = $teraz; return true;
});
if (!$wolnoG) odpowiedz(false, 429, 'Formularz jest chwilowo niedostępny. Zadzwoń: ' . TELEFON . ' albo napisz na ' . ODBIORCA . '.');

// ---------------------------------------------------------------- budowa maili
define('NL', "\r\n");
function zakoduj($s) { return '=?UTF-8?B?' . base64_encode($s) . '?='; }
function granica() { return '=_td_' . bin2hex(losowe(10)); }
function b64($s) { return rtrim(chunk_split(base64_encode($s), 76, NL)) . NL; }
function szkielet($tytul, $srodek) {
    return '<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' . h($tytul) . '</title></head>'
        . '<body style="margin:0;padding:0;background:#EEF0F2">'
        . '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#EEF0F2"><tr><td align="center" style="padding:24px 12px">'
        . '<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;background:#ffffff;border-top:6px solid #FDC506">'
        . '<tr><td style="padding:22px 28px 6px;font:bold 22px/1.2 Arial,Helvetica,sans-serif;color:#000000">'
        . '<span style="display:inline-block;border:3px solid #FDC506;border-right-color:transparent;padding:6px 12px 4px">TOMDAR <span style="font-size:12px;font-weight:normal">Meble</span></span></td></tr>'
        . $srodek
        . '<tr><td style="padding:18px 28px 24px;border-top:1px solid #DADDE1;font:13px/1.6 Arial,Helvetica,sans-serif;color:#4A4D52">'
        . 'TOMDAR-MEBLE s.c. Dariusz Skorupski, Tomasz Pliszka<br>ul. Graniczna 15, 05-503 Głosków-Letnisko<br>'
        . '<a href="tel:+48501156315" style="color:#141414">501 156 315</a> &middot; <a href="tel:+48607884191" style="color:#141414">607 884 191</a> &middot; '
        . '<a href="https://tomdar-meble.pl/" style="color:#141414">tomdar-meble.pl</a></td></tr>'
        . '</table></td></tr></table></body></html>';
}
function wiersz($k, $v) {
    return '<tr><td style="padding:10px 0;border-bottom:1px solid #EEF0F2;width:150px;vertical-align:top;font:bold 14px/1.5 Arial,Helvetica,sans-serif;color:#4A4D52">' . h($k) . '</td>'
         . '<td style="padding:10px 0;border-bottom:1px solid #EEF0F2;font:15px/1.5 Arial,Helvetica,sans-serif;color:#141414">' . $v . '</td></tr>';
}
function wyslij_mail($do, $temat, $naglowki, $tresc) {
    global $DEV;
    if ($DEV !== '') {
        if (!is_dir($DEV)) @mkdir($DEV, 0777, true);
        $plik = rtrim($DEV, '/\\') . '/' . date('Ymd-His') . '-' . bin2hex(losowe(3)) . '.eml';
        return (bool) file_put_contents($plik, 'To: ' . $do . NL . 'Subject: ' . $temat . NL . implode(NL, $naglowki) . NL . NL . $tresc);
    }
    return mail($do, $temat, $tresc, implode(NL, $naglowki));
}

$data = date('d.m.Y, H:i');
$zrodlo = (string) wez($_SERVER, 'HTTP_REFERER', '');
if (!preg_match('#^https?://[^\s<>"]+$#', $zrodlo)) $zrodlo = '';
$telHref = preg_replace('/[^0-9+]/', '', $tel);
if ($telHref !== '' && $telHref[0] !== '+' && strlen($telHref) === 9) $telHref = '+48' . $telHref;
$rows = wiersz('Imię i nazwisko', h($imie))
      . wiersz('Telefon', $tel !== '' ? '<a href="tel:' . h($telHref) . '" style="color:#141414;font-weight:bold">' . h($tel) . '</a>' : '-')
      . wiersz('E-mail', $email !== '' ? '<a href="mailto:' . h($email) . '" style="color:#141414;font-weight:bold">' . h($email) . '</a>' : '-')
      . wiersz('Mebel', h($mebel))
      . wiersz('Załącznik', $zal ? h($zal['nazwa']) . ' (' . round($zal['rozmiar'] / 1024) . ' KB, w załączniku maila)' : 'brak')
      . wiersz('Wysłano', h($data) . ($zrodlo !== '' ? '<br><span style="font-size:13px;color:#4A4D52">' . h($zrodlo) . '</span>' : ''));
$srodek = '<tr><td style="padding:14px 28px 4px;font:bold 20px/1.3 Arial,Helvetica,sans-serif;color:#141414">Nowe zapytanie ze strony</td></tr>'
        . '<tr><td style="padding:6px 28px 4px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">' . $rows . '</table></td></tr>'
        . '<tr><td style="padding:16px 28px 6px;font:bold 14px/1.5 Arial,Helvetica,sans-serif;color:#4A4D52">Wiadomość</td></tr>'
        . '<tr><td style="padding:0 28px 22px"><div style="border-left:5px solid #FDC506;padding:10px 16px;background:#F7F8F9;font:15px/1.6 Arial,Helvetica,sans-serif;color:#141414">' . nl2br(h($tresc)) . '</div>'
        . ($email !== '' ? '<p style="margin:14px 0 0;font:13px/1.5 Arial,Helvetica,sans-serif;color:#4A4D52">Odpowiedź na tę wiadomość trafi na adres klienta.</p>' : '')
        . '</td></tr>';
$html = szkielet('Nowe zapytanie', $srodek);
$tekst = "Nowe zapytanie ze strony tomdar-meble.pl\r\n\r\nImię i nazwisko: $imie\r\nTelefon: " . ($tel !== '' ? $tel : '-') . "\r\nE-mail: " . ($email !== '' ? $email : '-')
       . "\r\nMebel: $mebel\r\nZałącznik: " . ($zal ? $zal['nazwa'] : 'brak') . "\r\nWysłano: $data\r\n\r\nWiadomość:\r\n" . $tresc . "\r\n";

$gA = granica();
$alt = 'Content-Type: multipart/alternative; boundary="' . $gA . '"' . NL . NL
     . '--' . $gA . NL . 'Content-Type: text/plain; charset=UTF-8' . NL . 'Content-Transfer-Encoding: base64' . NL . NL . b64($tekst)
     . '--' . $gA . NL . 'Content-Type: text/html; charset=UTF-8' . NL . 'Content-Transfer-Encoding: base64' . NL . NL . b64($html)
     . '--' . $gA . '--' . NL;
$nag = array('MIME-Version: 1.0', 'From: ' . zakoduj(NADAWCA_NAZWA) . ' <' . NADAWCA . '>', 'Date: ' . date('r'),
             'X-Mailer: tomdar-formularz');
if ($email !== '') $nag[] = 'Reply-To: ' . zakoduj($imie) . ' <' . $email . '>';
if ($zal) {
    $gM = granica();
    $nag[] = 'Content-Type: multipart/mixed; boundary="' . $gM . '"';
    $cialo = '--' . $gM . NL . $alt
           . '--' . $gM . NL . 'Content-Type: ' . $zal['typ'] . '; name="' . $zal['nazwa'] . '"' . NL
           . 'Content-Transfer-Encoding: base64' . NL . 'Content-Disposition: attachment; filename="' . $zal['nazwa'] . '"' . NL . NL
           . b64($zal['dane']) . '--' . $gM . '--' . NL;
} else {
    list($h1, $reszta) = explode(NL . NL, $alt, 2);
    $nag[] = $h1;
    $cialo = $reszta;
}
$temat = zakoduj('Nowe zapytanie ze strony: ' . $mebel . ' - ' . $imie);
if (!wyslij_mail(ODBIORCA, $temat, $nag, $cialo)) {
    error_log('tomdar formularz: mail() zwrócił false');
    odpowiedz(false, 500, 'Nie udało się wysłać wiadomości. Zadzwoń: ' . TELEFON . ' albo napisz na ' . ODBIORCA . '.');
}

// ---------------------------------------------------------------- potwierdzenie dla klienta (neutralne)
if ($email !== '' && $zOk) {
    $adr = hash_hmac('sha256', 'mail|' . strtolower($email), sekret());
    $mozna = z_plikiem('potwierdzenia.json', function (&$d) use ($adr, $teraz) {
        foreach ($d as $k => $t) if ($k !== '_h' && $t < $teraz - 86400) unset($d[$k]);
        $h = isset($d['_h']) ? array_values(array_filter((array) $d['_h'], function ($t) use ($teraz) { return $t > $teraz - 3600; })) : array();
        if (isset($d[$adr]) || count($h) >= LIMIT_POTW_H) { $d['_h'] = $h; return false; }
        $d[$adr] = $teraz; $h[] = $teraz; $d['_h'] = $h; return true;
    });
    if ($mozna) {
        $s2 = '<tr><td style="padding:14px 28px 4px;font:bold 20px/1.3 Arial,Helvetica,sans-serif;color:#141414">Dziękujemy za zapytanie</td></tr>'
            . '<tr><td style="padding:8px 28px 22px;font:15px/1.6 Arial,Helvetica,sans-serif;color:#141414">'
            . '<p style="margin:0 0 12px">Otrzymaliśmy wiadomość wysłaną przez formularz na stronie tomdar-meble.pl. Odezwiemy się najszybciej, jak to możliwe.</p>'
            . '<p style="margin:0">W pilnej sprawie zadzwoń: <a href="tel:+48501156315" style="color:#141414;font-weight:bold">501 156 315</a> (Dariusz Skorupski) lub '
            . '<a href="tel:+48607884191" style="color:#141414;font-weight:bold">607 884 191</a> (Tomasz Pliszka).</p></td></tr>';
        $h2 = szkielet('Dziękujemy za zapytanie', $s2);
        $t2 = "Dziękujemy za zapytanie.\r\n\r\nOtrzymaliśmy wiadomość wysłaną przez formularz na stronie tomdar-meble.pl. Odezwiemy się najszybciej, jak to możliwe.\r\n"
            . "W pilnej sprawie zadzwoń: 501 156 315 (Dariusz Skorupski) lub 607 884 191 (Tomasz Pliszka).\r\n\r\nTOMDAR-MEBLE s.c., ul. Graniczna 15, 05-503 Głosków-Letnisko\r\n";
        $g2 = granica();
        $n2 = array('MIME-Version: 1.0', 'From: ' . zakoduj(FIRMA) . ' <' . NADAWCA . '>', 'Reply-To: ' . ODBIORCA, 'Date: ' . date('r'),
                    'Auto-Submitted: auto-replied', 'Content-Type: multipart/alternative; boundary="' . $g2 . '"');
        $c2 = '--' . $g2 . NL . 'Content-Type: text/plain; charset=UTF-8' . NL . 'Content-Transfer-Encoding: base64' . NL . NL . b64($t2)
            . '--' . $g2 . NL . 'Content-Type: text/html; charset=UTF-8' . NL . 'Content-Transfer-Encoding: base64' . NL . NL . b64($h2)
            . '--' . $g2 . '--' . NL;
        wyslij_mail($email, zakoduj('Tomdar-Meble: otrzymaliśmy zapytanie'), $n2, $c2);
    }
}
odpowiedz(true, 200, 'Dziękujemy, zapytanie zostało wysłane. Odezwiemy się najszybciej, jak to możliwe.');
