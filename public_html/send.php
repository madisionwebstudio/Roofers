<?php
/**
 * Roofrs — form handler for /free-audit/ and /contact/
 *
 * - Accepts POST only
 * - Honeypot + minimum fill-time check (bots)
 * - Rate limit per IP (file-based) and per session
 * - Validates + sanitises every field, strips header-injection characters
 * - Sends a plain-text email with PHP mail()
 * - Returns JSON for fetch() requests, or redirects (303) for normal form posts
 *
 * SETUP: change TO_EMAIL and FROM_EMAIL below. FROM_EMAIL must be an address on
 * your own domain (create it in Hostinger → Emails) or many inboxes will
 * reject the message as spoofed.
 */
declare(strict_types=1);

// ------------------------------------------------------------------ config
const TO_EMAIL        = '[TO_EMAIL]';
const FROM_EMAIL      = 'no-reply@[DOMAIN]';
const SITE_NAME       = 'Roofrs';
const THANK_YOU_URL   = '/thank-you/';
const RATE_MAX        = 5;     // submissions allowed…
const RATE_WINDOW     = 900;   // …per this many seconds, per IP
const MIN_FILL_SECS   = 3;     // faster than this = bot
const USE_ENVELOPE_F  = true;  // pass -f FROM_EMAIL to sendmail (recommended on Hostinger)

// ------------------------------------------------------------------ helpers
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: same-origin');

$wantsJson = (isset($_SERVER['HTTP_ACCEPT']) && stripos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false)
    || (($_SERVER['HTTP_X_REQUESTED_WITH'] ?? '') === 'fetch');

function respond(bool $ok, string $message, array $errors = [], int $status = 200, string $redirect = THANK_YOU_URL): void
{
    global $wantsJson;
    http_response_code($status);
    if ($wantsJson) {
        header('Content-Type: application/json; charset=utf-8');
        header('Cache-Control: no-store');
        echo json_encode(['ok' => $ok, 'message' => $message, 'errors' => (object)$errors, 'redirect' => $ok ? $redirect : null]);
        exit;
    }
    if ($ok) {
        header('Location: ' . $redirect, true, 303);
        exit;
    }
    // No-JS error page
    header('Content-Type: text/html; charset=utf-8');
    $items = '';
    foreach ($errors as $msg) { $items .= '<li>' . htmlspecialchars($msg, ENT_QUOTES, 'UTF-8') . '</li>'; }
    $m = htmlspecialchars($message, ENT_QUOTES, 'UTF-8');
    echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
       . '<meta name="robots" content="noindex"><title>Please check the form — ' . SITE_NAME . '</title>'
       . '<link rel="stylesheet" href="/assets/css/main.css"></head><body><main class="section"><div class="container container--narrow">'
       . '<h1>Almost there.</h1><p class="lede">' . $m . '</p>' . ($items ? '<ul>' . $items . '</ul>' : '')
       . '<p><a class="btn" href="javascript:history.back()">Go back and fix it</a></p></div></main></body></html>';
    exit;
}

/** Single-line field: trim, strip tags and every control char (blocks header injection). */
function line(string $key, int $max = 150): string
{
    $v = isset($_POST[$key]) && is_string($_POST[$key]) ? $_POST[$key] : '';
    $v = strip_tags($v);
    $v = preg_replace('/[\x00-\x1F\x7F]+/u', ' ', $v) ?? '';
    $v = trim(preg_replace('/\s+/u', ' ', $v) ?? '');
    return mb_substr($v, 0, $max, 'UTF-8');
}

/** Multi-line field: keep newlines, strip other control chars. */
function block(string $key, int $max = 3000): string
{
    $v = isset($_POST[$key]) && is_string($_POST[$key]) ? $_POST[$key] : '';
    $v = strip_tags($v);
    $v = str_replace("\r\n", "\n", $v);
    $v = preg_replace('/[\x00-\x09\x0B-\x1F\x7F]+/u', ' ', $v) ?? '';
    return mb_substr(trim($v), 0, $max, 'UTF-8');
}

function client_ip(): string
{
    // REMOTE_ADDR only — forwarded headers are trivially spoofed on shared hosting.
    $ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    return filter_var($ip, FILTER_VALIDATE_IP) ? $ip : '0.0.0.0';
}

// ------------------------------------------------------------------ method
if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'POST') {
    header('Allow: POST');
    respond(false, 'This address only accepts form submissions.', [], 405);
}

// Same-origin check (when the browser sends Origin)
if (!empty($_SERVER['HTTP_ORIGIN']) && !empty($_SERVER['HTTP_HOST'])) {
    $originHost = parse_url($_SERVER['HTTP_ORIGIN'], PHP_URL_HOST);
    $host = preg_replace('/:\d+$/', '', $_SERVER['HTTP_HOST']);
    if ($originHost && strcasecmp($originHost, $host) !== 0) {
        respond(false, 'Request blocked.', [], 403);
    }
}

// ------------------------------------------------------------------ bot checks
// Honeypot: real people never see or fill this field. Pretend success so bots move on.
if (!empty($_POST['fax_number'])) {
    respond(true, 'Thanks.');
}
$ts = isset($_POST['form_ts']) ? (int)$_POST['form_ts'] : 0; // ms, set by JS on page load
if ($ts > 0 && (time() * 1000 - $ts) < MIN_FILL_SECS * 1000) {
    respond(true, 'Thanks.');
}

// ------------------------------------------------------------------ rate limit
if (session_status() === PHP_SESSION_NONE) {
    session_start(['cookie_httponly' => true, 'cookie_samesite' => 'Lax', 'cookie_secure' => !empty($_SERVER['HTTPS'])]);
}
$now = time();
$_SESSION['sends'] = array_values(array_filter($_SESSION['sends'] ?? [], fn($t) => $t > $now - RATE_WINDOW));
if (count($_SESSION['sends']) >= RATE_MAX) {
    respond(false, 'Too many submissions in a short time. Please wait a few minutes, or email us directly.', [], 429);
}

$rateFile = rtrim(sys_get_temp_dir(), '/') . '/roofrs_rl_' . hash('sha256', client_ip() . '|' . __FILE__) . '.json';
$fh = @fopen($rateFile, 'c+');
if ($fh) {
    flock($fh, LOCK_EX);
    $hits = json_decode(stream_get_contents($fh) ?: '[]', true);
    $hits = array_values(array_filter(is_array($hits) ? $hits : [], fn($t) => is_int($t) && $t > $now - RATE_WINDOW));
    if (count($hits) >= RATE_MAX) {
        flock($fh, LOCK_UN); fclose($fh);
        respond(false, 'Too many submissions in a short time. Please wait a few minutes, or email us directly.', [], 429);
    }
    $hits[] = $now;
    ftruncate($fh, 0); rewind($fh); fwrite($fh, json_encode($hits));
    flock($fh, LOCK_UN); fclose($fh);
}

// ------------------------------------------------------------------ fields
$type = line('form_type', 20);
if (!in_array($type, ['audit', 'contact'], true)) {
    respond(false, 'Unknown form.', [], 400);
}

$f = [
    'name'     => line('name', 100),
    'company'  => line('company', 120),
    'website'  => line('website', 200),
    'city'     => line('city', 100),
    'phone'    => line('phone', 30),
    'email'    => line('email', 160),
    'ads'      => line('ads', 20),
    'leads'    => line('leads', 20),
    'plan'     => line('plan', 20),
    'topic'    => line('topic', 40),
    'message'  => block('message', 3000),
    'consent'  => line('consent', 5),
    'page'     => line('page', 200),
];
$errors = [];

if ($f['name'] === '' || mb_strlen($f['name']) < 2)              $errors['name']  = 'Enter your name.';
if (!filter_var($f['email'], FILTER_VALIDATE_EMAIL))              $errors['email'] = 'Enter a valid email address.';
$digits = preg_replace('/\D+/', '', $f['phone']) ?? '';
if ($type === 'audit' || $f['phone'] !== '') {
    if (strlen($digits) === 11 && $digits[0] === '1') $digits = substr($digits, 1);
    if (strlen($digits) !== 10)                                    $errors['phone'] = 'Enter a 10-digit US phone number.';
}
if ($f['website'] !== '') {
    $url = preg_match('#^https?://#i', $f['website']) ? $f['website'] : 'https://' . $f['website'];
    if (!filter_var($url, FILTER_VALIDATE_URL) || !preg_match('/\.[a-z]{2,}/i', (string)parse_url($url, PHP_URL_HOST))) {
        $errors['website'] = 'Enter a website like yourroofing.com, or leave it blank.';
    } else {
        $f['website'] = $url;
    }
}

if ($type === 'audit') {
    if ($f['company'] === '')                                      $errors['company'] = 'Enter your company name.';
    if ($f['city'] === '')                                         $errors['city']    = 'Enter the city and state you work in.';
    if (!in_array($f['ads'], ['Yes', 'No', 'Not sure'], true))     $errors['ads']     = 'Pick one.';
    if (!in_array($f['leads'], ['Under 10', '10-25', '26-50', '51-100', '100+', 'Not sure'], true)) $errors['leads'] = 'Pick a range.';
    if (!in_array($f['plan'], ['', 'starter', 'growth', 'premium'], true)) $f['plan'] = '';
} else {
    if ($f['message'] === '' || mb_strlen($f['message']) < 5)      $errors['message'] = 'Tell us a little about what you need.';
    if (!in_array($f['topic'], ['', 'Pricing question', 'Current client', 'Partnership', 'Something else'], true)) $f['topic'] = '';
}
if ($f['consent'] !== 'yes')                                       $errors['consent'] = 'Please tick the box so we can contact you.';

if ($errors) {
    respond(false, 'Please fix the highlighted fields.', $errors, 422);
}

// ------------------------------------------------------------------ email
if (strpos(TO_EMAIL, '[') !== false) {
    error_log('Roofrs send.php: TO_EMAIL is still a placeholder; message not sent.');
    respond(false, 'The form is not connected to an inbox yet. Please email us directly.', [], 503);
}

$consentText = 'I agree to be contacted by phone, text and email about my audit. Message & data rates may apply. Reply STOP to opt out.';
$phonePretty = strlen($digits) === 10 ? sprintf('(%s) %s-%s', substr($digits, 0, 3), substr($digits, 3, 3), substr($digits, 6)) : $f['phone'];

if ($type === 'audit') {
    $subject = sprintf('New Lead-Leak Audit request — %s (%s)', $f['company'], $f['city']);
    $lines = [
        'NEW LEAD-LEAK AUDIT REQUEST',
        str_repeat('=', 40),
        'Name:           ' . $f['name'],
        'Company:        ' . $f['company'],
        'Website:        ' . ($f['website'] ?: '—'),
        'City / state:   ' . $f['city'],
        'Phone:          ' . $phonePretty,
        'Email:          ' . $f['email'],
        'Runs Ads/LSA:   ' . $f['ads'],
        'Monthly leads:  ' . $f['leads'],
        'Plan interest:  ' . ($f['plan'] ?: '—'),
        '',
        'NEXT STEP: test-call their business (business hours + after hours) before the audit.',
    ];
} else {
    $subject = sprintf('Website contact — %s%s', $f['name'], $f['topic'] ? ' (' . $f['topic'] . ')' : '');
    $lines = [
        'NEW CONTACT MESSAGE',
        str_repeat('=', 40),
        'Name:     ' . $f['name'],
        'Company:  ' . ($f['company'] ?: '—'),
        'Phone:    ' . ($phonePretty ?: '—'),
        'Email:    ' . $f['email'],
        'Topic:    ' . ($f['topic'] ?: '—'),
        '',
        'Message:',
        $f['message'],
    ];
}
$lines[] = '';
$lines[] = str_repeat('-', 40);
$lines[] = 'CONSENT RECORD (keep for TCPA compliance)';
$lines[] = 'Consent given: yes';
$lines[] = 'Consent text:  ' . $consentText;
$lines[] = 'Submitted:     ' . gmdate('Y-m-d H:i:s') . ' UTC';
$lines[] = 'IP address:    ' . client_ip();
$lines[] = 'User agent:    ' . mb_substr(preg_replace('/[\x00-\x1F\x7F]+/', ' ', $_SERVER['HTTP_USER_AGENT'] ?? '') ?? '', 0, 250);
$lines[] = 'Page:          ' . ($f['page'] ?: '—');

$body = implode("\n", $lines) . "\n";
$encodedSubject = mb_encode_mimeheader($subject, 'UTF-8', 'B', "\r\n");
$headers = [
    'From: ' . SITE_NAME . ' Website <' . FROM_EMAIL . '>',
    'Reply-To: ' . $f['email'],          // validated by FILTER_VALIDATE_EMAIL — no CR/LF possible
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'X-Mailer: Roofrs-Site',
];

$sent = USE_ENVELOPE_F
    ? @mail(TO_EMAIL, $encodedSubject, $body, implode("\r\n", $headers), '-f' . FROM_EMAIL)
    : @mail(TO_EMAIL, $encodedSubject, $body, implode("\r\n", $headers));

if (!$sent) {
    error_log('Roofrs send.php: mail() returned false for ' . $type . ' form.');
    respond(false, 'We couldn\'t send that right now. Please email us directly and we\'ll handle it by hand.', [], 500);
}

$_SESSION['sends'][] = $now;
respond(true, 'Got it. Redirecting…', [], 200, THANK_YOU_URL . '?form=' . $type);
