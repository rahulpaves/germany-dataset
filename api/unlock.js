/**
 * Turns a completed Stripe payment into an access token.
 *
 * There is no database here on purpose. Stripe already knows who paid, so it
 * is the record: this asks Stripe whether a checkout session was actually
 * paid, and only then issues a token. Nothing to keep in sync, nothing to
 * back up, and no list of customers to leak.
 *
 * The token is a signed string, not a stored secret. api/data.js verifies the
 * signature by itself, so the reader's file opens without another call to
 * Stripe on every fetch.
 *
 * Flow:
 *   Stripe payment link succeeds
 *     -> /thanks-file.html?session_id={CHECKOUT_SESSION_ID}
 *     -> this endpoint verifies with Stripe
 *     -> token saved in the buyer's browser
 *     -> /api/data?c=italy&k=<token> serves the file
 *
 * Needs STRIPE_SECRET_KEY. TOKEN_SECRET is optional: without it the Stripe key
 * signs the tokens, which is fine, but setting a separate one means rotating
 * the Stripe key does not lock every existing buyer out.
 */

const crypto = require('crypto');

const YEAR_MS = 365 * 24 * 60 * 60 * 1000;

function signingSecret() {
  return process.env.TOKEN_SECRET || process.env.STRIPE_SECRET_KEY || '';
}

function b64url(buf) {
  return Buffer.from(buf).toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function mint(sessionId, expiresAt) {
  const secret = signingSecret();
  if (!secret) return null;
  const payload = sessionId + '|' + expiresAt;
  const sig = crypto.createHmac('sha256', secret).update(payload).digest();
  return b64url(payload) + '.' + b64url(sig);
}

module.exports = async (req, res) => {
  const url = new URL(req.url, 'http://x');
  const sessionId = String(url.searchParams.get('session_id') || '').trim();

  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store, private');

  if (!sessionId.startsWith('cs_')) {
    res.statusCode = 400;
    return res.end(JSON.stringify({ error: 'no checkout session' }));
  }

  const key = process.env.STRIPE_SECRET_KEY;
  if (!key || !signingSecret()) {
    // Say plainly that the server is not set up rather than implying the
    // buyer did something wrong. They paid; this is ours to fix.
    res.statusCode = 503;
    return res.end(JSON.stringify({
      error: 'not configured',
      message: 'Payment went through. Access is not switched on yet at our end, so mail rahul@pavetheway.ai and it will be sorted today.',
    }));
  }

  try {
    const r = await fetch(
      'https://api.stripe.com/v1/checkout/sessions/' + encodeURIComponent(sessionId),
      { headers: { Authorization: 'Bearer ' + key } }
    );
    const session = await r.json();

    if (!r.ok) {
      res.statusCode = 400;
      return res.end(JSON.stringify({ error: 'stripe rejected the session' }));
    }

    /* Two states unlock.
       'paid' is the ordinary case.
       'no_payment_required' is what Stripe returns when a 100% discount covers
       the whole amount. That only happens against a coupon we created, so it
       cannot be triggered by someone who has not been given one, and it is how
       a comped counsellor or a full-price test gets in. Rejecting it was the
       first version's bug: a 100% coupon looked identical to a failed payment.
       'unpaid' still means no money and no coupon, so it stays shut. */
    const okStates = ['paid', 'no_payment_required'];
    if (okStates.indexOf(session.payment_status) === -1) {
      res.statusCode = 402;
      return res.end(JSON.stringify({
        error: 'not paid',
        message: 'Stripe has not recorded a payment on this session yet. If you have just paid, give it a minute and reload.',
      }));
    }

    const expiresAt = Date.now() + YEAR_MS;
    const token = mint(sessionId, expiresAt);

    res.statusCode = 200;
    return res.end(JSON.stringify({
      token: token,
      expires: new Date(expiresAt).toISOString().slice(0, 10),
      // Shown back to the buyer so they can see we have the right address,
      // and so a wrong one gets corrected while they are still on the page.
      email: (session.customer_details && session.customer_details.email) || null,
    }));
  } catch (e) {
    res.statusCode = 502;
    return res.end(JSON.stringify({
      error: 'could not reach stripe',
      message: 'Your payment is fine. Mail rahul@pavetheway.ai and we will open it by hand.',
    }));
  }
};
