/**
 * Re-opens the file for someone who already paid, using the email they paid with.
 *
 * The first version of this asked for an "access code". Nobody was ever sent
 * one: payment unlocks automatically through api/unlock.js, and the code box
 * was left over from an earlier design where codes were emailed by hand. A box
 * asking for something that does not exist is worse than no box.
 *
 * So this asks Stripe instead. Stripe knows who has an active subscription, so
 * the buyer types the address on their receipt and gets their file back. No
 * code to lose, nothing for us to store.
 *
 * WHAT THIS IS NOT. Knowing a buyer's email is enough to open the file here.
 * That is deliberately weak for a $99 data subscription being tested with a
 * handful of counsellors, where the cost of locking a paying customer out is
 * far higher than the cost of someone guessing an address. If this becomes a
 * real revenue line, replace it with a link emailed to the address rather than
 * an unlock granted to whoever types it.
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

function mint(ref, expiresAt) {
  const secret = signingSecret();
  if (!secret) return null;
  const payload = ref + '|' + expiresAt;
  const sig = crypto.createHmac('sha256', secret).update(payload).digest();
  return b64url(payload) + '.' + b64url(sig);
}

async function stripe(path, key) {
  const r = await fetch('https://api.stripe.com/v1/' + path, {
    headers: { Authorization: 'Bearer ' + key },
  });
  return { ok: r.ok, body: await r.json() };
}

module.exports = async (req, res) => {
  const url = new URL(req.url, 'http://x');
  const email = String(url.searchParams.get('email') || '').trim().toLowerCase();

  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store, private');

  if (!email || email.indexOf('@') === -1) {
    res.statusCode = 400;
    return res.end(JSON.stringify({ error: 'that does not look like an email address' }));
  }

  const key = process.env.STRIPE_SECRET_KEY;
  if (!key || !signingSecret()) {
    res.statusCode = 503;
    return res.end(JSON.stringify({
      message: 'Our end is not switched on yet. Mail rahul@pavetheway.ai and it gets opened today.',
    }));
  }

  try {
    const found = await stripe('customers?limit=20&email=' + encodeURIComponent(email), key);
    if (!found.ok) {
      // Surface Stripe's own reason. Without it a restricted key missing
      // customers:read is indistinguishable from Stripe being down, and the
      // first version of this reported both as "try again in a minute".
      const why = (found.body && found.body.error && found.body.error.message) || 'unknown';
      res.statusCode = 502;
      return res.end(JSON.stringify({
        message: 'We could not check that with Stripe. Mail rahul@pavetheway.ai and it gets opened by hand.',
        stripe: why,
      }));
    }

    const customers = (found.body && found.body.data) || [];
    for (const c of customers) {
      const subs = await stripe(
        'subscriptions?limit=10&status=active&customer=' + encodeURIComponent(c.id), key);
      const active = subs.ok && subs.body && (subs.body.data || []).length > 0;
      if (active) {
        const expiresAt = Date.now() + YEAR_MS;
        res.statusCode = 200;
        return res.end(JSON.stringify({ token: mint(c.id, expiresAt) }));
      }
    }

    // No active subscription. Say which case it is, because "not found" and
    // "cancelled" need different things from the reader.
    res.statusCode = 404;
    return res.end(JSON.stringify({
      message: customers.length
        ? 'That address has no active subscription. If you think it should, mail rahul@pavetheway.ai.'
        : 'We have no payment against that address. Check it is the one on your receipt.',
    }));
  } catch (e) {
    res.statusCode = 502;
    return res.end(JSON.stringify({ message: 'Something broke at our end, not yours. Mail rahul@pavetheway.ai.' }));
  }
};
