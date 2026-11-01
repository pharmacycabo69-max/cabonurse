// POST /api/checkout  (form field: option)
// Creates a Stripe Checkout Session for the 50% deposit of an IV option and
// redirects the customer to Stripe. Prices live server-side in _prices.json;
// the client only sends the option key. Requires env STRIPE_SECRET_KEY.
const OPTIONS = require("./_prices.json");

const SITE = process.env.SITE_URL || "https://cabonurse.com";
const WA_FALLBACK = "https://wa.me/526242261023?text=" +
  encodeURIComponent("Hi, I'd like to book IV therapy in Cabo today");

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).send("Method not allowed");
  }

  const key = req.body && req.body.option;
  const option = Object.prototype.hasOwnProperty.call(OPTIONS, key) ? OPTIONS[key] : null;
  if (!option) return res.status(400).send("Unknown IV option");

  const secret = process.env.STRIPE_SECRET_KEY;
  if (!secret) {
    console.error("STRIPE_SECRET_KEY is not set");
    return res.redirect(303, WA_FALLBACK);
  }

  const deposit = Math.round(option.price * 100 / 2); // cents, 50%
  const p = new URLSearchParams({
    mode: "payment",
    "line_items[0][quantity]": "1",
    "line_items[0][price_data][currency]": "usd",
    "line_items[0][price_data][unit_amount]": String(deposit),
    "line_items[0][price_data][product_data][name]": `IV Therapy deposit — ${option.name}`,
    "line_items[0][price_data][product_data][description]":
      `50% deposit of $${option.price} USD. The remaining balance is paid after the session.`,
    "payment_intent_data[description]": `IV deposit — ${option.name} (total $${option.price} USD)`,
    "payment_intent_data[metadata][option]": key,
    "payment_intent_data[metadata][total_usd]": String(option.price),
    "metadata[option]": key,
    "custom_fields[0][key]": "location",
    "custom_fields[0][label][type]": "custom",
    "custom_fields[0][label][custom]": "Hotel / villa and room or address",
    "custom_fields[0][type]": "text",
    success_url: `${SITE}/iv-therapy/thanks/`,
    cancel_url: `${SITE}/iv-therapy/#iv-options`,
  });
  p.set("phone_number_collection[enabled]", "true");

  try {
    const r = await fetch("https://api.stripe.com/v1/checkout/sessions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${secret}`,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: p,
    });
    const data = await r.json();
    if (!r.ok || !data.url) {
      console.error("Stripe error", r.status, data && data.error);
      return res.redirect(303, WA_FALLBACK);
    }
    return res.redirect(303, data.url);
  } catch (err) {
    console.error("Checkout failed", err);
    return res.redirect(303, WA_FALLBACK);
  }
};
