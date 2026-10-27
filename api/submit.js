// Vercel serverless function: receives PageDriven form submissions and emails them via Resend.
// Env vars (Vercel → Project → Settings → Environment Variables):
//   RESEND_API_KEY   required  Resend API key
//   FORM_TO_EMAIL    optional  inbox for submissions (default riz@gopagedriven.com)
//   FORM_FROM_EMAIL  optional  verified sender, e.g. "PageDriven <forms@gopagedriven.com>"
//                              (default "PageDriven Forms <onboarding@resend.dev>", Resend's test sender)

const TO = process.env.FORM_TO_EMAIL || "riz@gopagedriven.com";
const FROM = process.env.FORM_FROM_EMAIL || "PageDriven Forms <onboarding@resend.dev>";
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const clip = (v, n = 2000) => String(v == null ? "" : v).trim().slice(0, n);
const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ ok: false, error: "Method not allowed" });
  }

  let body = req.body;
  if (typeof body === "string") {
    try { body = JSON.parse(body); } catch { return res.status(400).json({ ok: false, error: "Invalid JSON" }); }
  }
  body = body || {};

  // spam trap: real visitors never fill the hidden "website" field
  if (clip(body.website)) return res.status(200).json({ ok: true });

  const kind = body.kind === "contact" ? "contact" : "review";
  const name = clip(body.name, 120);
  const email = clip(body.email, 200);
  if (!name || !EMAIL_RE.test(email)) return res.status(400).json({ ok: false, error: "Name and a valid email are required" });

  const fields = kind === "contact"
    ? [["Name", name], ["Email", email], ["Message", clip(body.message, 5000)]]
    : [["Name", name], ["Email", email], ["Page URL", clip(body.url, 500)], ["Goal", clip(body.goal, 80)], ["Service", clip(body.service, 120)]];
  fields.push(["Submitted from", clip(body.page, 200) || "/"]);
  if (kind === "contact" && fields[2][1].length < 5) return res.status(400).json({ ok: false, error: "Message is too short" });

  const subject = kind === "contact" ? `New message from ${name}` : `Page review request from ${name}`;
  const text = fields.map(([k, v]) => `${k}: ${v}`).join("\n");
  const html = `<h2 style="font-family:Arial,sans-serif;color:#0B2545">${esc(subject)}</h2>
<table style="font-family:Arial,sans-serif;font-size:14px;border-collapse:collapse">${fields
    .map(([k, v]) => `<tr><td style="padding:6px 16px 6px 0;color:#7D88A3;vertical-align:top">${esc(k)}</td><td style="padding:6px 0;color:#0D1B33;white-space:pre-wrap">${esc(v)}</td></tr>`)
    .join("")}</table>`;

  if (!process.env.RESEND_API_KEY) {
    console.error("RESEND_API_KEY is not set");
    return res.status(500).json({ ok: false, error: "Email service not configured" });
  }

  try {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from: FROM, to: [TO], reply_to: email, subject, text, html }),
    });
    if (!r.ok) {
      console.error("Resend error", r.status, await r.text());
      return res.status(502).json({ ok: false, error: "Email could not be sent" });
    }
    return res.status(200).json({ ok: true });
  } catch (e) {
    console.error("Resend request failed", e);
    return res.status(502).json({ ok: false, error: "Email could not be sent" });
  }
};
