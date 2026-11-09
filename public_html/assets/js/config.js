/* ==========================================================================
   ROOFRS — site config
   Runtime settings read by main.js. Static text placeholders that live in the
   HTML itself ([DOMAIN], [US PHONE] …) are listed here too so there is one
   place to look. See README.md → "Replace placeholders" for the find/replace
   commands.

   PLACEHOLDER           WHERE IT LIVES               EXAMPLE
   Roofrs / ROOFRS       every HTML page, send.php    Ridgeline
   [DOMAIN]              HTML, sitemap.xml, robots    roofrs.com
   [US PHONE]            HTML (display text)          (210) 555-0142
   [US_PHONE_E164]       HTML (tel: links)            +12105550142
   hello@[DOMAIN]        HTML, privacy/terms          hello@roofrs.com
   [TO_EMAIL]            send.php                     you@yourinbox.com
   [CALENDLY_URL]        this file                    https://calendly.com/you/audit
   [GA4_ID]              this file                    G-XXXXXXXXXX
   [ADS_CONVERSION_ID]   this file                    AW-123456789
   [ADS_CONVERSION_LABEL] this file                   AbCdEfGhIjk
   ========================================================================== */
window.SITE_CONFIG = {
  brandName: "Roofrs",
  domain: "[DOMAIN]",
  phoneDisplay: "[US PHONE]",
  phoneE164: "[US_PHONE_E164]",
  email: "hello@[DOMAIN]",
  hours: "8am–6pm Central, Monday–Friday",

  /* Booking — paste your Calendly event link. Leave as-is to show the placeholder box. */
  calendlyUrl: "[CALENDLY_URL]",

  /* Analytics — set enabled: true after adding real IDs. Nothing loads until then. */
  analytics: {
    enabled: false,
    ga4Id: "[GA4_ID]",
    adsConversionId: "[ADS_CONVERSION_ID]",       /* e.g. AW-123456789 */
    adsConversionLabel: "[ADS_CONVERSION_LABEL]"  /* fired on successful form submit */
  }
};
