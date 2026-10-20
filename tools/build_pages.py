"""Genera las páginas internas de cabonurse.com y sitemap.xml en data/site/.

index.html se edita a mano; este script reutiliza su header, footer, barra móvil
y widget de chat para que todas las páginas compartan el mismo marco.
Uso:  python3 tools/build_pages.py
"""
import re
from html import escape
from pathlib import Path
from urllib.parse import quote

SITE = Path(__file__).resolve().parent.parent / "data" / "site"
DOMAIN = "https://cabonurse.com"
OG_IMAGE = DOMAIN + "/images/hero-nurse-iv-kit-los-cabos.jpg"
WA = "https://wa.me/526242261023"
TEL = "tel:+526242261023"
PHONE_TXT = "+52 624 226 1023"

home = (SITE / "index.html").read_text(encoding="utf-8")


def between(start, end):
    i = home.index(start)
    return home[i:home.index(end, i) + len(end)]


def fix_links(h):
    h = h.replace('href="#top"', 'href="/"')
    return re.sub(r'href="#(?!main)', 'href="/#', h)


HEADER = fix_links(between('<header class="nav">', "</header>"))
FOOTER = fix_links(between('<footer id="contact">', "</footer>"))
TAIL = between("<!-- MOBILE STICKY CONTACT -->", "</button>")
GTAG = between("<!-- Google tag:", "gtag('config', 'AW-XXXXXXXXXX');\n</script>")


def wa_link(text):
    return f"{WA}?text={quote(text, safe='')}"


def cta(wa_text, label="Message us on WhatsApp"):
    return (f'<a class="btn btn-gold" href="{wa_link(wa_text)}" target="_blank" rel="noopener">{label}</a>\n'
            f'          <a class="btn btn-outline-cream" href="{TEL}">Call {PHONE_TXT}</a>')


def faq_html(items):
    return "\n".join(f"      <details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)


def page(path, title, desc, h1, intro, body, wa_text, kicker):
    url = f"{DOMAIN}{path}"
    t, d = escape(title), escape(desc)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{t}</title>
<meta name="description" content="{d}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0F2341">

<meta property="og:type" content="website">
<meta property="og:site_name" content="Cabo Nurse">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{OG_IMAGE}">

<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/images/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/images/favicon-16x16.png">
<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">

{GTAG}

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&amp;family=Schibsted+Grotesk:wght@400;500;600;700&amp;family=IBM+Plex+Mono:wght@400;500&amp;display=swap">
<link rel="stylesheet" href="/css/style.css">
<script>
(function(){{
  try{{
    var saved = localStorage.getItem('cabonurse_theme');
    var theme = saved || ((window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
  }}catch(e){{}}
}})();
</script>
</head>
<body>

<a class="skip-link" href="#main">Skip to content</a>

{HEADER}

<main id="main">

  <section class="page-hero">
    <div class="container">
      <span class="label">{kicker}</span>
      <h1>{h1}</h1>
      <p class="hero-lead">{intro}</p>
      <div class="hero-cta">
          {cta(wa_text)}
      </div>
    </div>
  </section>

{body}

  <section class="cta-band plate">
    <div class="container cta-inner">
      <h2>Care is one message away.</h2>
      <div class="cta-actions">
        <a class="btn btn-outline-navy" href="{wa_link(wa_text)}" target="_blank" rel="noopener" style="background:var(--navy); color:var(--cream); border-color:var(--navy);">Message on WhatsApp</a>
        <a class="btn btn-outline-navy" href="{TEL}">Call {PHONE_TXT}</a>
      </div>
    </div>
  </section>

</main>

{FOOTER}

{TAIL}

<script src="/js/main.js"></script>
</body>
</html>
"""


def section(cls, label, h2, inner):
    return f"""  <section class="{cls}">
    <div class="container">
      <div class="sec-head">
        <span class="label">{label}</span>
        <h2>{h2}</h2>
      </div>
{inner}
    </div>
  </section>
"""


def steps(items):
    out = '      <div class="steps">\n'
    for n, (h, p) in enumerate(items, 1):
        out += (f'        <div class="step"><span class="step-num">0{n}</span><h3>{h}</h3><p>{p}</p></div>\n')
    return out + "      </div>"


def faq_section(items, cls="sec-beige"):
    return section(cls, "FAQ", "Common questions", f'      <div class="faq">\n{faq_html(items)}\n      </div>')


def includes(items):
    return "      <ul class=\"incl\">\n" + "\n".join(f"        <li>{i}</li>" for i in items) + "\n      </ul>"


SAFETY = """  <section class="sec-beige-dim">
    <div class="container">
      <div class="safety">
        <h2>Safety first</h2>
        <p>Every session starts with a brief health screening by a licensed nurse. IV therapy is not a substitute for emergency care. For emergencies, call 911.</p>
      </div>
    </div>
  </section>
"""

PAGES = {}

# ---------------------------------------------------------------- IV therapy
IV_OPTIONS = [
    ("Hydration", "Fluids and electrolytes", ["Fluids and electrolytes to rehydrate", "A simple, light option after sun, flights or long days", "About 45 minutes"]),
    ("Hydration + Vitamins", "Our most popular choice", ["Hydration base with B-complex and vitamin C", "Replenish and refresh in one visit", "About 60 minutes"]),
    ("Recovery", "After sun, travel or a late night", ["Fluids and electrolytes to rehydrate", "Vitamin blend to help you feel refreshed", "Delivered to your hotel room or villa"]),
    ("Immunity", "Vitamin-focused", ["Vitamin C and zinc blend to replenish", "Popular before or during a trip", "About 60 minutes"]),
    ("Athletic recovery", "After golf, fishing, surf or training", ["Electrolytes and fluids to rehydrate", "Magnesium and B vitamins to replenish", "About 60&ndash;75 minutes"]),
]
iv_cards = ""
for name, sub, bullets in IV_OPTIONS:
    li = "".join(f"<li>{b}</li>" for b in bullets)
    iv_cards += (f'        <div class="opt-card"><h3>{name}</h3><p class="opt-sub">{sub}</p><ul>{li}</ul>'
                 f'<div class="opt-price">From $___ USD</div></div>\n')
iv_body = section("sec-beige", "IV options", "Choose what fits your day",
                  f'      <div class="opt-grid">\n{iv_cards}      </div>\n'
                  '      <p class="coverage-note">The nurse confirms the exact formula after a short health screening. Pricing is confirmed in USD before we dispatch.</p>')
iv_body += section("sec-navy", "How it works", "Three simple steps", steps([
    ("Message us on WhatsApp", "Tell us where you&rsquo;re staying and which option you&rsquo;d like."),
    ("A nurse confirms availability and pricing", "You get a clear price in USD before anyone is dispatched."),
    ("We arrive at your door in 20&ndash;60 minutes", "A licensed nurse brings sealed, sterile supplies to your hotel, villa or home."),
]))
iv_body += SAFETY
iv_body += section("sec-beige", "Coverage", "Arrival times across Los Cabos", """      <div class="coverage-list">
        <div class="coverage-item"><span>Cabo San Lucas</span><span class="tag-note">20&ndash;40 min</span></div>
        <div class="coverage-item"><span>Tourist Corridor</span><span class="tag-note">30&ndash;50 min</span></div>
        <div class="coverage-item"><span>San Jos&eacute; del Cabo</span><span class="tag-note">40&ndash;60 min</span></div>
      </div>""")
iv_body += faq_section([
    ("How long does a session take?", "Most sessions take 45&ndash;75 minutes depending on the option you choose, plus a short health screening before we start. A nurse usually arrives within 20&ndash;60 minutes of confirming."),
    ("Is it safe?", "Every session is administered by a COFEPRIS-licensed nurse using sealed, sterile, single-use supplies, and starts with a brief health screening. If something isn&rsquo;t right for you, the nurse will tell you and won&rsquo;t proceed. IV therapy is not a substitute for emergency care &mdash; for emergencies, call 911."),
    ("Can you come to a yacht?", "Yes. We visit boats docked at marinas in Cabo San Lucas and San Jos&eacute; del Cabo. Send us the marina and slip number on WhatsApp when you message."),
    ("How do I pay?", "Pricing is confirmed in USD on WhatsApp before a nurse is dispatched, and we&rsquo;ll tell you the accepted payment methods at that time. We don&rsquo;t bill insurance."),
], "sec-beige-dim")
PAGES["/iv-therapy/"] = dict(
    title="Mobile IV Therapy in Los Cabos | Cabo Nurse",
    desc="Mobile IV therapy in Los Cabos: hydration, vitamins and electrolytes administered by COFEPRIS-licensed nurses at your hotel, villa or home in 20–60 minutes.",
    h1="Mobile IV Therapy in Los Cabos",
    intro="Hydration, vitamins and electrolytes administered by COFEPRIS-licensed nurses at your hotel, villa or home. Usually within 20&ndash;60 minutes, anywhere from Cabo San Lucas to San Jos&eacute; del Cabo.",
    body=iv_body, wa="Hi, I'd like to book IV therapy in Los Cabos", kicker="Mobile IV therapy")

# ---------------------------------------------------------------- short pages
def short(path, title, desc, h1, intro, kicker, incl, faqs, wa, steps_tail):
    body = section("sec-beige", "What&rsquo;s included", "What a visit includes", includes(incl))
    body += section("sec-navy", "How it works", "Three simple steps", steps([
        ("Message or call us", "Tell us where you are and what you need."),
        steps_tail,
        ("We arrive in 20&ndash;60 minutes", "A licensed clinician comes to your hotel, villa or home."),
    ]))
    body += SAFETY
    body += faq_section(faqs)
    PAGES[path] = dict(title=title, desc=desc, h1=h1, intro=intro, body=body, wa=wa, kicker=kicker)


short("/doctor-house-calls/", "Doctor House Calls in Los Cabos | Cabo Nurse",
      "Licensed physician house calls in Los Cabos. Bilingual doctors evaluate and treat you at your hotel, villa or home, usually within 20–60 minutes.",
      "Doctor House Calls in Los Cabos",
      "A licensed bilingual physician evaluates and treats you at your hotel, villa or home &mdash; no waiting room, no transport. Usually within 20&ndash;60 minutes.",
      "Doctor house calls",
      ["In-person evaluation by a licensed physician", "Treatment and prescriptions when medically appropriate", "Care in English or Spanish", "A visit summary you can keep for your records"],
      [("How fast can a doctor arrive?", "Usually within 20&ndash;60 minutes depending on your location in Los Cabos."),
       ("Do I need an appointment?", "No. Message us on WhatsApp and we confirm availability and pricing right away."),
       ("What about emergencies?", "House calls are not a substitute for emergency care. For emergencies, call 911.")],
      "Hi, I'd like to request a doctor house call in Los Cabos",
      ("A doctor confirms availability and pricing", "You get a clear price in USD before we dispatch."))

short("/private-nursing/", "Private Nursing in Los Cabos | Cabo Nurse",
      "Private nursing in Los Cabos: licensed bilingual nurses for single visits or 8, 12 and 24-hour shifts at your hotel, villa or home.",
      "Private Nursing in Los Cabos",
      "Licensed bilingual nurses at your hotel, villa or home &mdash; for a single visit or private-duty shifts of 8, 12 or 24 hours.",
      "Private nursing",
      ["Medication administration and reminders", "Vitals monitoring and care notes", "Injections and IV line care as prescribed", "Single visits or 8, 12 and 24-hour shifts"],
      [("Can I book a nurse for a full day?", "Yes. Private-duty shifts of 8, 12 or 24 hours are available &mdash; message us for a quote."),
       ("Are your nurses licensed?", "Yes. Our team is COFEPRIS-licensed and bilingual."),
       ("How is it priced?", "Pricing is confirmed in USD on WhatsApp before we dispatch.")],
      "Hi, I'd like to arrange private nursing in Los Cabos",
      ("A nurse confirms availability and pricing", "We agree on schedule and price before anyone is dispatched."))

short("/wound-care/", "Wound Care at Home in Los Cabos | Cabo Nurse",
      "Wound care in Los Cabos: sterile dressing changes and post-op support from licensed nurses at your hotel, villa or home.",
      "Wound Care at Home in Los Cabos",
      "Sterile dressing changes and post-procedure support from licensed nurses, delivered to your hotel, villa or home.",
      "Wound care",
      ["Sterile dressing changes with sealed supplies", "Care for surgical sites, incisions and travel injuries", "Monitoring and clear instructions for follow-up", "Repeat visits on a schedule that suits you"],
      [("How long is a visit?", "A typical wound care visit takes about 30 minutes."),
       ("Can you follow my surgeon&rsquo;s instructions?", "Yes. Share your discharge instructions on WhatsApp and the nurse will follow them."),
       ("When should I seek emergency care?", "If you have heavy bleeding, fever or sudden worsening, call 911.")],
      "Hi, I'd like to book wound care in Los Cabos",
      ("A nurse confirms availability and pricing", "You get a clear price in USD before we dispatch."))

short("/senior-care/", "Senior Concierge Care in Los Cabos | Cabo Nurse",
      "Senior concierge care in Los Cabos: licensed nurses for recurring home visits, vitals, mobility support and medication reminders.",
      "Senior Concierge Care in Los Cabos",
      "Recurring, personal care for residents and long-stay visitors &mdash; licensed nurses who come to the home, on a schedule that works for the family.",
      "Senior concierge care",
      ["Vitals checks and care notes", "Mobility assistance and companionship", "Medication reminders and management support", "A recurring schedule built around your household"],
      [("Can visits be recurring?", "Yes. We build a recurring plan around your household rather than a one-off visit."),
       ("Are the nurses bilingual?", "Yes, our team works in English and Spanish."),
       ("How do we start?", "Message us on WhatsApp with a few details and we&rsquo;ll propose a schedule and price.")],
      "Hi, I'd like to ask about senior care in Los Cabos",
      ("A nurse confirms availability and pricing", "We agree on a schedule and price before the first visit."))

# ---------------------------------------------------------------- legal
PH = lambda t: f'<span class="ph">[PENDIENTE: {t}]</span>'
legal_body = f"""  <section class="sec-beige">
    <div class="container legal-body">
      <h2>Datos de la empresa / Company information</h2>
      <dl>
        <div><dt>Razón social</dt><dd>{PH("razón social")}</dd></div>
        <div><dt>Dirección física</dt><dd>{PH("dirección física")}</dd></div>
        <div><dt>Licencia o aviso de funcionamiento COFEPRIS</dt><dd>{PH("número y fecha")}</dd></div>
        <div><dt>Responsable sanitario</dt><dd>{PH("nombre completo")} &middot; Cédula profesional: {PH("número")}</dd></div>
        <div><dt>Contacto</dt><dd>{PHONE_TXT} &middot; <a href="mailto:care@cabonurse.com">care@cabonurse.com</a></dd></div>
      </dl>
      <h2 id="privacidad">Aviso de privacidad / Privacy notice</h2>
      <p>{PH("pegar aviso de privacidad integral conforme a la LFPDPPP")}</p>
      <h2>Emergencias</h2>
      <p>Nuestros servicios no sustituyen la atención de urgencias. Para emergencias llame al 911. / Our services are not a substitute for emergency care. For emergencies, call 911.</p>
    </div>
  </section>
"""
PAGES["/legal/"] = dict(
    title="Legal Information | Cabo Nurse",
    desc="Company, COFEPRIS licence, sanitary officer and privacy information for Cabo Nurse.",
    h1="Legal information", intro="Información legal y de cumplimiento de Cabo Nurse.",
    body=legal_body, wa="Hi, I have a question about Cabo Nurse", kicker="Legal")

# ---------------------------------------------------------------- write
def main():
    for path, p in PAGES.items():
        out = SITE / path.strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(path, p["title"], p["desc"], p["h1"], p["intro"], p["body"], p["wa"], p["kicker"]), encoding="utf-8")
        print("wrote", out.relative_to(SITE.parent.parent))
    urls = ["/"] + list(PAGES)
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += [f"  <url><loc>{DOMAIN}{u}</loc></url>" for u in urls]
    xml.append("</urlset>")
    (SITE / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")


if __name__ == "__main__":
    main()
