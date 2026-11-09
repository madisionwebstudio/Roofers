<?php
/**
 * Roofrs — form handler for /free-preview/ and /contact/.
 *
 * - POST only, same-origin check
 * - Honeypot (fax_number) + minimum fill time: bots get a fake "success"
 * - Rate limit: 5 submissions per 15 minutes per IP (file-based)
 * - Validates and sanitizes every field (no header injection)
 * - Emails the lead to TO_EMAIL and appends a CSV copy OUTSIDE public_html
 * - Answers JSON for fetch() requests, or a 303 redirect for plain form posts
 *
 * Settings come from config.json via tools/build.py. You can also edit the
 * constants below directly on the server.
 */
declare(strict_types=1);

const TO_EMAIL   = '';
const FROM_EMAIL = '';      // must be a mailbox on your own domain, e.g. forms@yourdomain.com
const SITE_HOST  = '[DOMAIN]';
const BRAND      = 'Roofrs';
const RATE_MAX   = 5;
const RATE_WINDOW = 900;               // seconds
const MIN_FILL_SECONDS = 3;
const CONSENT_TEXT = 'I agree to be contacted by phone, text and email about my request. Reply STOP to opt out.';

// Private folder one level ABOVE public_html (not reachable from the web).
$PRIVATE_DIR = dirname(__DIR__) . '/form-leads';

function respond(bool $ok, string $error = '', int $code = 200): void {
    $wantsJson = stripos($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json') !== false;
    if ($wantsJson) {
        http_response_code($code);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($ok ? ['ok' => true, 'redirect' => '/thank-you/'] : ['ok' => false, 'error' => $error]);
    } elseif ($ok) {
        header('Location: /thank-you/', true, 303);
    } else {
        http_response_code($code);
        header('Content-Type: text/html; charset=utf-8');
        echo '<!doctype html><meta charset="utf-8"><title>Form error</title><p style="font:18px system-ui;max-width:600px;margin:60px auto">'
            . htmlspecialchars($error) . ' <a href="javascript:history.back()">Go back</a></p>';
    }
    exit;
}

function clean(string $key, int $max = 200): string {
    $v = $_POST[$key] ?? '';
    if (!is_string($v)) return '';
    $v = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $v) ?? '';
    $v = trim(preg_replace('/[\r\n]+/', ' ', $v) ?? '');
    return mb_substr($v, 0, $max);
}

function clean_multiline(string $key, int $max = 2000): string {
    $v = $_POST[$key] ?? '';
    if (!is_string($v)) return '';
    $v = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $v) ?? '';
    return mb_substr(trim($v), 0, $max);
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Allow: POST');
    respond(false, 'Method not allowed.', 405);
}

// Same-origin check (Origin header if present, else Referer)
$origin = $_SERVER['HTTP_ORIGIN'] ?? ($_SERVER['HTTP_REFERER'] ?? '');
if ($origin !== '') {
    $host = parse_url($origin, PHP_URL_HOST) ?: '';
    $selfHost = preg_replace('/:\d+$/', '', (string) ($_SERVER['HTTP_HOST'] ?? ''));
    $allowed = array_filter([SITE_HOST, 'www.' . SITE_HOST, $selfHost]);
    if (!in_array($host, $allowed, true)) respond(false, 'Request blocked.', 403);
}

// Honeypot + timing: pretend success so bots don't retry
$ts = (int) ($_POST['_ts'] ?? 0);
if (clean('fax_number') !== '' || ($ts > 0 && ((int) (microtime(true) * 1000) - $ts) < MIN_FILL_SECONDS * 1000)) {
    respond(true);
}

// Rate limit per IP
$ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
$rateDir = is_dir($PRIVATE_DIR) || @mkdir($PRIVATE_DIR, 0750, true) ? $PRIVATE_DIR : sys_get_temp_dir();
$rateFile = $rateDir . '/rate-' . hash('sha256', $ip . BRAND) . '.json';
$hits = array_filter((array) json_decode((string) @file_get_contents($rateFile), true), fn($t) => is_int($t) && $t > time() - RATE_WINDOW);
if (count($hits) >= RATE_MAX) respond(false, 'Too many submissions — please wait 15 minutes or message us on WhatsApp.', 429);
$hits[] = time();
@file_put_contents($rateFile, json_encode(array_values($hits)), LOCK_EX);

// Fields
$form = in_array($_POST['form'] ?? '', ['free-preview', 'contact', 'chat'], true) ? $_POST['form'] : 'contact';
$name = clean('name', 100);
$company = clean('company', 120);
$website = clean('website', 200);
$city = clean('city', 100);
$phone = clean('phone', 30);
$email = clean('email', 160);
$logo = in_array($_POST['logo'] ?? '', ['Yes', 'No'], true) ? $_POST['logo'] : '';
$notes = clean_multiline('notes');
$message = clean_multiline('message', $form === 'chat' ? 6000 : 2000);
$allowedServices = ['Replacement', 'Repair', 'Storm/insurance', 'Commercial', 'Gutters', 'Siding'];
$services = array_values(array_intersect((array) ($_POST['services'] ?? []), $allowedServices));
$consent = ($_POST['consent'] ?? '') === 'yes';
$serviceNames = ['web-design' => 'Web design', 'seo' => 'SEO', 'google-ads' => 'Google Ads (PPC)', 'not-sure' => 'Not sure yet'];
$service = $serviceNames[$_POST['service'] ?? ''] ?? '';
// Ad attribution captured by main.js from the landing URL
$attrib = [];
foreach (['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'landing_page'] as $k) {
    $v = clean($k, 200);
    if ($v !== '') $attrib[$k] = $v;
}

$errors = [];
if ($name === '') $errors[] = 'name';
$digits = preg_replace('/\D/', '', $phone) ?? '';
$phoneOk = strlen($digits) >= 10 && strlen($digits) <= 11;
$emailOk = (bool) filter_var($email, FILTER_VALIDATE_EMAIL);
if ($form === 'chat') {
    // Chat leads need a name and at least one way to reach them
    if (!$phoneOk && !$emailOk) $errors[] = 'phone or email';
} else {
    if (!$emailOk) $errors[] = 'email';
    if (!$phoneOk) $errors[] = 'phone';
}
if ($form === 'free-preview') {
    if ($company === '') $errors[] = 'company';
    if ($city === '') $errors[] = 'city and state';
} elseif ($form === 'contact' && $message === '') {
    $errors[] = 'message';
}
if (!$consent) $errors[] = 'contact consent';
if ($errors) respond(false, 'Please check: ' . implode(', ', $errors) . '.', 422);

$time = gmdate('Y-m-d H:i:s') . ' UTC';
$page = clean('page', 200) ?: ($_SERVER['HTTP_REFERER'] ?? '');
$ua = mb_substr((string) ($_SERVER['HTTP_USER_AGENT'] ?? ''), 0, 250);

$lines = [
    'New ' . ($form === 'free-preview' ? 'LEAD: ' . ($service ?: 'free website preview') : ($form === 'chat' ? 'CHAT lead' : 'contact message')) . ' — ' . BRAND,
    str_repeat('-', 48),
    "Service:   " . ($service ?: '—'),
    "Name:      $name",
    "Company:   $company",
    "Phone:     $phone",
    "Email:     $email",
    "City/State: $city",
    "Website:   $website",
    'Services:  ' . implode(', ', $services),
    "Has logo:  $logo",
    '',
    ($form === 'chat' ? 'Chat transcript:' : 'Notes / message:'),
    $notes . $message,
    '',
    str_repeat('-', 48),
    'Consent:   YES — "' . CONSENT_TEXT . '"',
    "Time:      $time",
    "IP:        $ip",
    "Page:      $page",
    'Source:    ' . ($attrib ? implode(' | ', array_map(fn($k, $v) => "$k=$v", array_keys($attrib), $attrib)) : 'direct / unknown'),
    "Browser:   $ua",
];
$body = implode("\n", $lines);

// CSV copy outside public_html — the safety net if email fails
$saved = false;
if (is_dir($PRIVATE_DIR) || @mkdir($PRIVATE_DIR, 0750, true)) {
    $csv = $PRIVATE_DIR . '/leads.csv';
    $new = !file_exists($csv);
    if ($fh = @fopen($csv, 'a')) {
        flock($fh, LOCK_EX);
        if ($new) fputcsv($fh, ['time', 'form', 'service', 'name', 'company', 'phone', 'email', 'city', 'website', 'services', 'logo', 'notes', 'consent', 'ip', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'gclid', 'landing_page']);
        $row = [$time, $form, $service, $name, $company, $phone, $email, $city, $website, implode('|', $services), $logo, $notes . $message, 'yes', $ip,
                $attrib['utm_source'] ?? '', $attrib['utm_medium'] ?? '', $attrib['utm_campaign'] ?? '', $attrib['utm_term'] ?? '', $attrib['gclid'] ?? '', $attrib['landing_page'] ?? ''];
        // neutralize spreadsheet formulas
        $row = array_map(fn($c) => preg_match('/^[=+\-@]/', (string) $c) ? "'" . $c : $c, $row);
        $saved = fputcsv($fh, $row) !== false;
        flock($fh, LOCK_UN);
        fclose($fh);
    }
}

$mailed = false;
if (filter_var(TO_EMAIL, FILTER_VALIDATE_EMAIL)) {
    $from = filter_var(FROM_EMAIL, FILTER_VALIDATE_EMAIL) ? FROM_EMAIL : 'no-reply@' . SITE_HOST;
    $subject = ($form === 'free-preview' ? ($service === 'Google Ads (PPC)' ? 'Google Ads plan: ' : 'Free preview: ') : ($form === 'chat' ? 'Chat lead: ' : 'Contact: ')) . ($company ?: $name) . (isset($attrib['gclid']) ? ' [Google Ads]' : '');
    $subject = '=?UTF-8?B?' . base64_encode(mb_substr($subject, 0, 120)) . '?=';
    $headers = [
        'From: ' . BRAND . ' website <' . $from . '>',
        'Content-Type: text/plain; charset=UTF-8',
    ];
    if ($emailOk) $headers[] = 'Reply-To: ' . $email;
    $mailed = @mail(TO_EMAIL, $subject, $body, implode("\r\n", $headers), '-f' . $from);
}

if (!$mailed && !$saved) {
    respond(false, 'Sorry — our form is not connected yet.', 500);
}
respond(true);
