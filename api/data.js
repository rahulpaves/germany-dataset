/**
 * The gate.
 *
 * Germany is free and served as a static file, exactly as before. The other
 * seven countries leave the server only through here, and only with an access
 * code that matches one we issued.
 *
 * Why a function rather than a check in the page: the country JSON used to sit
 * in data/ and was fetched from the browser, so anyone could open
 * /data/italy.json and take it. A gate in the page would not have withheld
 * anything, and a test of whether counsellors will pay is worthless if the
 * thing is still free to anyone who opens the network tab.
 *
 * Codes live in the ACCESS_CODES environment variable, comma separated. One
 * code per buyer, issued on the Stripe success page. Adding a buyer is an
 * environment variable edit, which is the right amount of machinery for a test
 * whose whole purpose is to find out whether anybody buys at all.
 */

const PAID = require('../lib/paid-data.js');

const FREE_COUNTRIES = ['germany'];

function issuedCodes() {
  return String(process.env.ACCESS_CODES || '')
    .split(',')
    .map(s => s.trim().toUpperCase())
    .filter(Boolean);
}

function valid(code) {
  if (!code) return false;
  const codes = issuedCodes();
  if (!codes.length) return false;
  return codes.indexOf(String(code).trim().toUpperCase()) !== -1;
}

module.exports = (req, res) => {
  const url = new URL(req.url, 'http://x');
  const country = String(url.searchParams.get('c') || '').toLowerCase().trim();
  const code = url.searchParams.get('k');
  const part = String(url.searchParams.get('part') || 'programmes').toLowerCase();

  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  // Never cache a gated response at the edge: one buyer's payload must not be
  // served to the next visitor without a code.
  res.setHeader('Cache-Control', 'no-store, private');

  if (!country) {
    res.statusCode = 400;
    return res.end(JSON.stringify({ error: 'name a country' }));
  }

  // Germany is free. The page fetches it statically, but answer here too so a
  // single code path works for every country.
  if (FREE_COUNTRIES.indexOf(country) !== -1) {
    res.statusCode = 302;
    res.setHeader('Location', '/data/' + country + (part === 'visa' ? '-visa' : '') + '.json');
    return res.end();
  }

  if (!PAID[country]) {
    res.statusCode = 404;
    return res.end(JSON.stringify({ error: 'no such country' }));
  }

  if (!valid(code)) {
    res.statusCode = 402; // Payment Required, which is what this actually is
    return res.end(JSON.stringify({
      error: 'locked',
      country: country,
      message: 'Germany is free. The other seven countries need an access code.',
    }));
  }

  const payload = part === 'visa'
    ? (PAID[country].visa || [])
    : PAID[country].programmes;

  res.statusCode = 200;
  return res.end(JSON.stringify(payload));
};
