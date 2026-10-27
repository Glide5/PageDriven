#!/usr/bin/env python3
"""Builds the PageDriven multi-page site from site.json + the home page source."""
import json, re, os, base64, html as H

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("PD_OUT") or os.path.join(BASE, ".out", "site")  # preview build; _source/export.py copies it to the repo root
SRC = open(os.path.join(BASE, "src.html")).read()
D = json.load(open(os.path.join(BASE, "site.json")))
ASSETS = json.load(open(os.path.join(BASE, "assets.json")))

def e(s): return H.escape(s, quote=True)

# ---------- images ----------
os.makedirs(OUT + "/assets/img", exist_ok=True)
def write_data_uri(key, name):
    b = base64.b64decode(ASSETS[key].split(",", 1)[1])
    open(f"{OUT}/assets/img/{name}", "wb").write(b)
for i in range(10): write_data_uri(f"I{i}", f"i{i}.webp")
write_data_uri("RIZ", "riz-waist.webp"); write_data_uri("AVATAR", "avatar.webp")
from PIL import Image
Image.open(os.path.join(BASE, "images", "riz.png")).save(f"{OUT}/assets/img/riz-full.webp", quality=90)
import shutil
for i in (8, 9, *range(10, 16)): shutil.copy(os.path.join(BASE, "images", f"i{i}.webp"), f"{OUT}/assets/img/i{i}.webp")  # 8 and 9 re-rendered upright
shutil.copy(os.path.join(BASE, "images", "team.webp"), f"{OUT}/assets/img/team.webp")
shutil.copy(os.path.join(BASE, "images", "riz-meeting.webp"), f"{OUT}/assets/img/riz-meeting.webp")
shutil.copy(os.path.join(BASE, "images", "andrew.webp"), f"{OUT}/assets/img/andrew.webp")
shutil.copy(os.path.join(BASE, "images", "chat-riz.webp"), f"{OUT}/assets/img/chat-riz.webp")
for n in ("logo.webp", "logo-foot.webp", "larry-video.webp") + tuple(f"{c}-logo.webp" for c in ("levitate", "frisco", "lourcey", "one10", "rset")) + tuple(f"{c}-{t}.webp" for c in ("caseleap", "frisco", "levitate", "outdoor", "lourcey") for t in ("before", "after")) + ("one10-site.webp", "rset-site.webp", "stainguys-site.webp"): shutil.copy(os.path.join(BASE, "images", n), f"{OUT}/assets/img/{n}")
IMG = {f"I{i}": f"assets/img/i{i}.webp" for i in range(16)}
IMG.update(RIZ="assets/img/riz-waist.webp", AVATAR="assets/img/avatar.webp")
def img_paths(s):
    for k, v in IMG.items(): s = s.replace(f"__{k}__", v)
    return s

# ---------- icons ----------
IC = {
 "eye":'<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
 "trophy":'<path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M17 5h3v2a3 3 0 0 1-3 3M7 5H4v2a3 3 0 0 0 3 3"/>',
 "pointer":'<path d="M5 3l14 7-6 2-2 6z"/>',
 "form":'<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9h10M7 13h6M7 17h4"/>',
 "phone":'<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
 "shield":'<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M12 8v4M12 15.5h.01"/>',
 "shieldcheck":'<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
 "dollar":'<circle cx="12" cy="12" r="9"/><path d="M15 9.5c-.5-1-1.6-1.5-3-1.5-1.7 0-3 .8-3 2s1.3 1.7 3 2 3 .8 3 2-1.3 2-3 2c-1.4 0-2.5-.5-3-1.5M12 6.5v11"/>',
 "timer":'<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2M9 2h6"/>',
 "calx":'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4M10 14l4 4M14 14l-4 4"/>',
 "help":'<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6V14M12 17.5h.01"/>',
 "video":'<rect x="2" y="6" width="14" height="12" rx="2"/><path d="M16 10l6-3v10l-6-3z"/>',
 "play":'<circle cx="12" cy="12" r="9"/><path d="M10 8.5v7l5.5-3.5z"/>',
 "layers":'<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
 "search":'<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
 "cross":'<path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6z"/>',
 "pin":'<path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
 "grid":'<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
 "monitor":'<rect x="2" y="4" width="20" height="13" rx="2"/><path d="M8 21h8M12 17v4"/>',
 "globe":'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/>',
 "trend":'<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
 "info":'<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/>',
 "mail":'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
 "ig":'<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6"/>',
 "fb":'<path d="M14 21v-7h3l.5-3.5H14V8.6c0-1 .3-1.6 1.7-1.6H18V3.9c-.4-0-1.6-.2-3-.2-3 0-4.6 1.8-4.6 4.9v2H7.5V14h2.9v7"/>',
 "chev":'<path d="M6 9l6 6 6-6"/>',
 "menu":'<path d="M4 7h16M4 12h16M4 17h16"/>',
 "x":'<path d="M6 6l12 12M18 6L6 18"/>',
 "users":'<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.7-3.6 3.3-5.5 6.5-5.5s5.8 1.9 6.5 5.5M16 4.8a3.5 3.5 0 0 1 0 6.4M18 14.8c1.9.8 3.1 2.6 3.5 5.2"/>',
 "calendar":'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
 "chat":'<path d="M4 5h16v11H9l-5 4z"/>',
 "target":'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>',
 "pen":'<path d="M4 20l4-1 11-11-3-3L5 16z"/><path d="M14 6l3 3"/>',
}
def icon(n, cls="ico-svg"): return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{IC[n]}</svg>'

def mute(text, hl):
    """Grey out the highlight phrase (Stripe-style emphasis)."""
    if not hl or hl == text or hl not in text: return e(text)
    a, b = text.split(hl, 1)
    return f'{e(a)}<span class="mute">{e(hl)}</span>{e(b)}'

ARROW = '<span class="arr">→</span>'
ON = ' class="on"'
SVC_META = {  # slug: (css class, icon, short nav description)
 "landing-pages": ("s1", "I4", "Campaign pages built around one clear action"),
 "conversion-websites": ("s2", "I5", "Sites structured around how buyers decide"),
 "cro-audits": ("s3", "I6", "Find and fix what's costing you conversions"),
 "ongoing-optimization": ("s4", "I7", "A conversion partner after launch"),
}
SERVICES = D["SERVICES"]
SVC = {s["slug"]: s for s in SERVICES}

# ---------- work data (card art) ----------
WART = {
 "caseleap": dict(name="CaseLeap", tag="B2B video · Ongoing CRO", font="600 42px/1 var(--f-sans);letter-spacing:-.045em",
   sub="Ongoing CRO and UX optimization that took average homepage visits from 3 to 18 seconds.",
   art=dict(angle=0, zoom=1.0, bg="#2A2F52", dark="#151933", light="#DCD7FF", pts=[[-.2,.6],[.35,-.2],[.55,1.25],[1.2,.35]], width=.27, twist=1.9, phase=.6)),
 "frisco-spinal-rehab": dict(name="Frisco Spinal Rehab", tag="Healthcare · Google Ads", font="600 32px/1 var(--f-sans);letter-spacing:-.03em",
   sub="Rebuilt a spinal decompression funnel around patient concerns, stronger proof, one consistent offer and a clearer form journey.",
   art=dict(angle=-28, zoom=1.35, bg="#0B2545", dark="#06162B", light="#C9DDF7", pts=[[-.15,.95],[.35,.05],[.55,1.15],[1.15,.15]], width=.24, twist=1.6, phase=.4)),
 "levitate-media": dict(name="LEVITATE", tag="Video production · UX audit", font="600 38px/1 var(--f-sans);letter-spacing:.18em",
   sub="Analyzed visitor behavior across six service pages to find which content earned attention and where UX refinements could lift lead capture.",
   art=dict(angle=18, zoom=1.1, bg="#5452F6", dark="#2F28B8", light="#ECEAFF", pts=[[-.2,.35],[.4,1.25],[.6,-.25],[1.2,.75]], width=.26, twist=2.2, phase=1.1)),
 "outdoor-living-remodeling": dict(name="Outdoor Living", tag="Home remodeling · Website", font="500 40px/1 var(--f-sans);letter-spacing:-.04em",
   sub="A phased Elementor redesign that turned an aging, SEO-driven website into a polished, conversion-focused experience.",
   art=dict(angle=58, zoom=1.2, bg="#3A9FD6", dark="#1D6FA3", light="#E6F4FC", pts=[[.1,1.2],[.05,.2],[.95,.95],[.9,-.2]], width=.22, twist=1.3, phase=2.0)),
 "lourcey-photography": dict(name="Lourcey", tag="Photography · Webflow", font="300 52px/1 var(--f-sans);letter-spacing:-.05em",
   sub="An image-led Webflow redesign that balances visual storytelling with mobile usability, performance and search visibility.",
   art=dict(angle=-10, zoom=1.5, bg="#0E1220", dark="#05070D", light="#E9ECF5", pts=[[-.2,.78],[.36,.02],[.62,1.06],[1.2,.26]], width=.28, twist=1.8, phase=.2)),
 "one10-driving-school": dict(name="one10", tag="Education · Custom WordPress", font="700 56px/1 var(--f-sans);letter-spacing:-.06em",
   sub="A custom WordPress theme combining a distinctive brand with Moneris payments and a tailored course-enrollment checkout.",
   art=dict(angle=34, zoom=1.05, bg="#D9699E", dark="#A9467A", light="#FFE6F1", pts=[[-.15,.75],[.45,-.3],[.5,1.3],[1.15,.3]], width=.25, twist=2.4, phase=.8)),
 "rset-wellness": dict(name="RSET", tag="Ecommerce · Shopify", font="700 50px/1 var(--f-sans);letter-spacing:.12em",
   sub="Redesigned the page and copy around subscription and discount offers so the saving shows at the point of choice.",
   art=dict(angle=162, zoom=1.25, bg="#D38A2E", dark="#9C5F14", light="#FFEFD2", pts=[[1.2,.9],[.6,-.2],[.3,1.25],[-.2,.25]], width=.24, twist=1.5, phase=1.6)),
 "stain-guys": dict(name="Local Services", tag="Local services · Landing page", font="500 34px/1 var(--f-sans);letter-spacing:-.03em",
   sub="Turned a colour-browsing page into a free quote request funnel for high-intent organic visitors.",
   art=dict(angle=-48, zoom=1.4, bg="#E0735B", dark="#B04C36", light="#FFE6DE", pts=[[-.1,1.15],[.2,.4],[.75,.6],[1.1,-.15]], width=.3, twist=2.0, phase=2.6)),
}
WORK = D["WORK"]
WBY = {w["slug"]: w for w in WORK}
def art_attr(slug): return e(json.dumps(WART[slug]["art"], separators=(",", ":")))
def wordmark(slug, extra=""):
    a = WART[slug]; return f'<span class="wordmark" style="font:{a["font"]}{extra}">{e(a["name"])}</span>'

# ---------- testimonials ----------
TESTI = [
 dict(q="Working with Rizvi has been a dream come true for our marketing department. Before working with him we were utilizing different contractors for site design, development, and CRO. Rizvi is a one-stop shop and consistently executes at a high level. Planning to use him ongoing for a long time to come.",n="Andrew",r="Founder, CaseLeap & Levitate Media",c="#12345E",i="CL"),
 dict(q="If you're looking for somebody who gets sh*t done, doesn't need hand-holding, and speaks and writes well, Riz is your man! He's been working alongside us for over 6 months, and it's been a pleasure. Knows his craft, is well-versed, and communicates clearly.",n="Danny Thomas",r="RevConstruct, Marketing Agency, CA",c="#E0735B",i="RC"),
 dict(q="Rizvi has been a pleasure to work with. He is very sharp and understands his craft well. The landing page he built for us has been a major upgrade and he went above and beyond integrating MS Clarity for tracking and optimization.",n="Dr. David Kaff",r="Frisco Spinal Rehab, TX",c="#3A9FD6",i="FS"),
 dict(video=True,q="Larry talks through the Webflow rebuild of his photography site and what it was like working together.",n="Larry Lourcey",r="Lourcey Photography, TX",c="rgba(255,255,255,.16)",i="LP"),
 dict(q="Rizvi delivered exceptional landing page design and refinement with a sharp web design eye and conversion-focused approach. Clear communication, fast turnaround, clean responsive files. Highly recommend for landing page and CRO work.",n="Wes Kennedy",r="FBL Coaching Inc, Canada",c="#0F9F84",i="FB"),
 dict(q="He was receptive to feedback, detail-oriented in execution, and showed a genuine commitment to quality rather than rushing work just to finish. That mattered a lot to us, especially in the healthcare space where clarity and precision are critical.",n="Izaiah Jacobson",r="WJMeda, NY",c="#5452F6",i="WJ"),
 dict(q="Rizvi did an excellent job building my new landing page. He was responsive, professional, and easy to work with. He quickly understood what I was trying to accomplish, incorporated feedback without hesitation, and delivered a polished landing page.",n="Dr. Jason Wayne",r="Certified Chiropractor, TX",c="#D38A2E",i="JW"),
 dict(q="Rizvi did a fantastic job with our client's landing pages. Communication was clear, the timeline was met, and he was quick to make changes or requests we had. We will be using him for more projects in the future!",n="Danny Thomas",r="RevConstruct, Marketing Agency, CA",c="#E0735B",i="RC"),
 dict(q="He did a good job improving a landing page.",n="Tim Peacock",r="Marketing Agency Owner, AZ",c="#D9699E",i="TP"),
]
TILE = {"Andrew":("#12345E","CL"),"Danny Thomas":("#E0735B","RC"),"Dr. David Kaff":("#3A9FD6","FS"),"Wes Kennedy":("#0F9F84","FB"),
        "Izaiah Jacobson":("#5452F6","WJ"),"Dr. Jason Wayne":("#D38A2E","JW"),"Tim Peacock":("#D9699E","TP")}
def who(n, r, c, i): return f'<div class="who"><span class="logo-tile" style="background:{c}">{e(i)}</span><div><b>{e(n)}</b><small>{e(r)}</small></div></div>'
def tcard(t, light=False):
    if t.get("video"):
        return ('<figure class="tcard video">'
          '<div class="vplayer"><button class="vposter" type="button" data-yt="E-EcIqCFIIs" aria-label="Play the video testimonial from Larry Lourcey">'
          '<img class="vthumb" src="assets/img/larry-video.webp" alt="" width="1280" height="721"><span class="vtag">Video testimonial</span><span class="vname">Larry Lourcey · Lourcey Photography</span>'
          '<span class="vplay" aria-hidden="true"><svg width="20" height="20" viewBox="0 0 20 20"><path d="M6 3.8v12.4L16.4 10z" fill="#5452F6"/></svg></span></button></div>'
          f'<p>{e(t["q"])}</p>{who(t["n"],t["r"],t["c"],t["i"])}'
          '<a class="vlink" href="https://www.youtube.com/watch?v=E-EcIqCFIIs" target="_blank" rel="noopener">Watch on YouTube <span aria-hidden="true">↗</span></a></figure>')
    return f'<figure class="tcard{" light" if light else ""}"><span class="stars" aria-label="5 stars">★★★★★</span><p>“{e(t["q"])}”</p>{who(t["n"],t["r"],t["c"],t["i"])}</figure>'
def find_testi(name):
    for t in D["TESTIMONIALS"]:
        if t["name"] == name or t["role"] == name: return t
    return None
def tcard_src(t, light=True):
    c, i = TILE.get(t["name"], ("#5452F6", t["name"][:2].upper()))
    return tcard(dict(q=t["quote"], n=t["name"], r=t["role"], c=c, i=i), light)

def testimonial_wall(title='Marketing teams and agencies <span class="mute">who stopped guessing</span>', eyebrow="Client words"):
    return f'''<section class="band night" aria-label="Client testimonials">
  <div class="bgfx aurora" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap">
    <div class="sec-head center"><span class="eyebrow">{eyebrow}</span><h2 class="h2">{title}</h2></div>
    <div class="t-grid">{"".join(tcard(t) for t in TESTI)}</div>
  </div>
</section>'''

# ---------- shared chrome ----------
def header(active):
    def cur(k): return ' aria-current="page"' if active == k else ""
    mega = "".join(
        f'<a href="{s["slug"]}.html"{cur("svc:"+s["slug"])}><img src="{IMG[SVC_META[s["slug"]][1]]}" alt="" width="48" height="48"><b>{e(s["name"])}</b><small>{e(SVC_META[s["slug"]][2])}</small></a>'
        for s in SERVICES)
    mlinks = "".join(
        f'<a href="{s["slug"]}.html"{cur("svc:"+s["slug"])}><img src="{IMG[SVC_META[s["slug"]][1]]}" alt="" width="36" height="36">{e(s["name"])}</a>'
        for s in SERVICES)
    svc_cur = " current" if active.startswith("svc:") else ""
    return f'''<header class="nav" id="nav">
  <div class="wrap nav-in">
    <a href="index.html" class="logo" aria-label="PageDriven home"><img src="assets/img/logo.webp" alt="PageDriven" width="146" height="32"></a>
    <nav class="nav-links" aria-label="Main">
      <div class="nav-item{svc_cur}">
        <button type="button" id="svcBtn" aria-expanded="false" aria-controls="svcMenu">Services {icon("chev")}</button>
        <div class="mega" id="svcMenu"><div class="mega-in">
          <div class="mega-grid">{mega}</div>
          <div class="mega-foot"><span>Not sure where to start?</span><a href="#" data-open-review>Get a free page review →</a></div>
        </div></div>
      </div>
      <a href="work.html"{cur("work")}>Work</a>
      <a href="agency-partners.html"{cur("agency")}>Agency Partners</a>
      <a href="about.html"{cur("about")}>About</a>
    </nav>
    <div class="nav-cta">
      <button class="btn btn-primary" data-open-review><span><span class="nl">Get My </span>Free Review</span> {ARROW}</button>
      <button class="burger" id="mnavBtn" type="button" aria-expanded="false" aria-controls="mnav" aria-label="Open menu"><svg class="b-menu ico-svg" viewBox="0 0 24 24">{IC["menu"]}</svg><svg class="b-x ico-svg" viewBox="0 0 24 24">{IC["x"]}</svg></button>
    </div>
  </div>
</header>
<nav id="mnav" aria-label="Mobile" hidden><div class="mnav-in">
  <span class="lbl">Services</span>{mlinks}<hr>
  <a href="index.html"{cur("home")}>Home</a><a href="work.html"{cur("work")}>Work</a><a href="agency-partners.html"{cur("agency")}>Agency Partners</a><a href="about.html"{cur("about")}>About</a><a href="book.html"{cur("book")}>Book a call</a>
  <button class="btn btn-primary" data-open-review>Get My Free Page Review {ARROW}</button>
</div></nav>'''

UR = '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M5 11 11 5M6 5h5v5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>'
def footer():
    svc = "".join(f'<li><a href="{s["slug"]}.html">{e(s["name"])}</a></li>' for s in SERVICES)
    soc = "".join(f'<li><a href="{D["SITE"][k]}" target="_blank" rel="noopener">{n}<span class="f-ur">{UR}</span></a></li>' for k, n in (("facebook", "Facebook"), ("instagram", "Instagram")))
    return f'''<footer class="footer">
  <div class="wrap f-in">
    <div class="f-top">
      <div class="f-lead">
        <p class="f-title">You’ve reached the bottom <span>of the funnel.</span></p>
        <a class="f-pill" href="book.html">Book a call<span class="f-pill-ic">{UR}</span></a>
        <div><span class="f-lab">Email us</span><a class="f-mail" href="mailto:{D["SITE"]["email"]}">{D["SITE"]["email"]}</a></div>
      </div>
      <nav class="f-cols" aria-label="Footer">
        <div><span class="f-lab">Services</span><ul>{svc}<li><a href="agency-partners.html">Agency partnerships</a></li></ul></div>
        <div><span class="f-lab">Company</span><ul><li><a href="work.html">Work</a></li><li><a href="about.html">About</a></li><li><a href="book.html">Book a call</a></li><li><button type="button" data-open-review>Free page review</button></li><li><button type="button" data-open-contact>Contact</button></li></ul></div>
        <div><span class="f-lab">Availability</span><p class="f-hours">Daily, during<br>US business hours</p><span class="f-lab" style="margin-top:28px">Follow</span><ul>{soc}</ul></div>
        <p class="f-tag">Planned by a strategist.<br>Built to be measured.</p>
        <p class="f-loc">Remote, across<br>the US &amp; Canada</p>
      </nav>
    </div>
    <div class="f-base"><span>© 2026 PageDriven. All rights reserved.</span><span class="f-legal"><a href="privacy.html">Privacy Policy</a><a href="terms.html">Terms of Service</a></span></div>
  </div>
  <div class="wrap"><div class="f-markbox"><img class="f-logo" src="assets/img/logo-foot.webp" alt="" width="1176" height="259"></div></div>
</footer>'''

MICRO = ('<p class="micro2"><span><svg class="mi" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l7.5 3v5.5c0 4.6-3.2 8.2-7.5 9.5-4.3-1.3-7.5-4.9-7.5-9.5V6z"/><path d="M8.8 12.2l2.3 2.3 4.3-4.6"/></svg>No Obligation</span>'
         '<i class="mdiv" aria-hidden="true"></i><span><svg class="mi" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>Response within 1 day</span></p>')
def cta_stack(btn_html, extra=""):
    return f'<div class="cta-stack{extra}">{btn_html}{MICRO}</div>'

ov_start = SRC.index('<div class="mbar" id="mbar">'); ov_end = SRC.index('</dialog>') + len('</dialog>')
CONTACT = f'''<dialog id="contact" aria-labelledby="c-title">
  <div class="m-in">
    <div class="m-top"><div style="display:grid;gap:6px"><span class="eyebrow">Contact</span><h3 id="c-title">Send Riz a message</h3></div><button class="m-x" type="button" id="cClose" aria-label="Close">✕</button></div>
    <form id="cForm" novalidate style="display:grid;gap:16px"><input class="hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="field"><label for="c-name">Your name</label><input id="c-name" autocomplete="name" placeholder="Jordan Lee"></div>
      <div class="field"><label for="c-email">Work email</label><input id="c-email" type="email" autocomplete="email" placeholder="jordan@company.com"></div>
      <div class="field"><label for="c-msg">How can we help?</label><textarea id="c-msg" placeholder="Tell us about the page, the traffic and what you'd like to improve."></textarea></div>
      <p class="err" id="cErr" role="alert"></p>
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap"><span class="m-note">Replies during US business hours</span><button class="btn btn-primary" type="submit" style="height:44px">Send message {ARROW}</button></div>
    </form>
    <div id="cOk" class="m-ok" hidden><span class="tick"><svg width="26" height="26" viewBox="0 0 26 26"><path d="M7 13.5l4 4 8-9" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></span><h3 id="cOkT">Message received</h3><p>Riz will reply by email.</p></div>
  </div>
</dialog>'''
_ov = img_paths(SRC[ov_start:ov_end])
_old_acts = """    <div id="mActs" style="display:flex;gap:10px;justify-content:space-between;align-items:center;flex-wrap:wrap">
      <span class="m-note">Free · Personalized · No obligation</span>
      <div style="display:flex;gap:8px"><button type="button" class="btn btn-ghost" id="mBack" hidden style="height:44px">Back</button><button type="submit" class="btn btn-primary" id="mNext" style="height:44px">Continue <span class="arr">→</span></button></div>
    </div>"""
assert _old_acts in _ov
_ov = _ov.replace(_old_acts, '<div id="mActs" class="m-acts"><button type="button" class="btn btn-ghost" id="mBack" hidden>Back</button>' + cta_stack('<button type="submit" class="btn btn-primary" id="mNext">Continue <span class="arr">→</span></button>', " full") + '</div>')
OVERLAYS = _ov + CONTACT

SCRIPTS = '''<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://unpkg.com/lenis@1.1.13/dist/lenis.min.js"></script>
<script src="assets/site.js"></script>'''

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@300..700&display=swap">'

def final_cta(title_html='Get a free review of the page <span class="mute">costing you leads.</span>',
              body="Riz personally reviews your page and sends back where it's losing momentum, plus the three highest-impact fixes in priority order.",
              btn="Get My Free Page Review", service=None):
    ds = f' data-service="{e(service)}"' if service else ""
    return f'''<section class="cta-band" aria-labelledby="h-cta">
  <div class="wrap">
    <div class="cta">
      <div class="cta-bg" aria-hidden="true"><i></i><i></i></div>
      <div class="cta-copy">
        <h2 id="h-cta">{title_html}</h2>
        <p style="max-width:48ch">{e(body)}</p>
        {cta_stack(f'<button class="btn btn-primary" data-open-review{ds}>{e(btn)} {ARROW}</button>')}
      </div>
      <div class="cta-person">
        <svg class="cta-arrow" viewBox="0 0 128 100" aria-hidden="true">
          <path id="arrowPath" d="M110 29C100 27 89 27 80 28C60 30 41 37 28 50C16 62 12 78 18 92"/>
          <path id="arrowHead" d="M7.5 83.5c4 3 7 5.6 10.5 8.5 1.2-4.2 1.4-8.6.9-13.2"/>
        </svg>
        <div class="cta-name"><b>Rizvi (Riz)</b><small>PageDriven founder &amp;<br>conversion strategist</small></div>
        <img id="riz" src="{IMG["RIZ"]}" alt="Riz, founder and conversion strategist at PageDriven" width="337" height="470">
      </div>
    </div>
  </div>
</section>'''

# case-study card copy: service pill, industry, outcome headline (muted tail) — claims stay within what each case study documents
WCARD = {
 "caseleap": ("CRO", "B2B video production", "How we took CaseLeap's homepage visits", "from 3 to 18 seconds"),
 "frisco-spinal-rehab": ("Landing page", "Healthcare", "How we rebuilt Frisco Spinal Rehab's", "Google Ads funnel around patients"),
 "levitate-media": ("UX audit", "Video production", "How we found what earns attention", "on Levitate Media's service pages"),
 "outdoor-living-remodeling": ("Website", "Home remodeling", "How we redesigned a remodeler's site", "to match the spaces it builds"),
 "lourcey-photography": ("Website", "Photography", "How we built Lourcey an image-led site", "that stays fast on mobile"),
 "one10-driving-school": ("Website", "Education", "How we built One10 a custom", "enrollment and payment flow"),
 "rset-wellness": ("Landing page", "Wellness ecommerce", "How we put RSET's subscription saving", "at the point of choice"),
 "stain-guys": ("Landing page", "Local home services", "How we turned a colour page", "into a quote request funnel"),
}
# client logos centred over a card's wave art (white artwork on transparent background)
def _logo(n, h): return f'<img class="wart-logo" src="assets/img/{n}-logo.webp" alt="" width="640" height="{h}">'
def _word(t): return f'<span class="wart-word" aria-hidden="true">{e(t)}</span>'
WCARD_LOGO = {"levitate-media": _logo("levitate", 156), "frisco-spinal-rehab": _logo("frisco", 189), "lourcey-photography": _logo("lourcey", 154),
              "one10-driving-school": _logo("one10", 189), "rset-wellness": _logo("rset", 112),
              # no logo artwork: bold white wordmark at the same visual height
              "caseleap": _word("CaseLeap"), "outdoor-living-remodeling": _word("Outdoor Living"), "stain-guys": _word("Local Services")}
def wcard(slug, attrs=""):
    a, (pill, ind, h, hm) = WART[slug], WCARD[slug]
    size = max(17, round(int(re.search(r"(\d+)px", a["font"]).group(1)) * .48))
    return (f'<a class="wcard"{attrs} href="work-{slug}.html" draggable="false" style="--c:{a["art"]["bg"]};--cd:{a["art"]["dark"]};--wf:{size}">'
            f'<div class="wtop">{wordmark(slug, ";font-size:calc(var(--wf) * var(--wk, 1) * 1px)")}<span class="wpill">{e(pill)}</span></div>'
            f'<div class="wart"><canvas data-art="{art_attr(slug)}" aria-hidden="true"></canvas>{WCARD_LOGO.get(slug, "")}</div>'
            f'<span class="wind">{e(ind)}</span><h3>{e(h)} <span class="mute">{e(hm)}</span></h3>'
            f'<p class="wsub">{e(a["sub"])}</p><span class="wmore">Learn more <span>→</span></span></a>')
def work_carousel(slugs, title='Find out how we\'ve helped businesses <span class="mute">just like yours</span>', eyebrow="Client work", sid="work", tone=""):
    n = len(slugs)
    return f'''<section class="band hs{tone}" id="{sid}" aria-label="Client work">
  <div class="wrap work-head">
    <div class="sec-head"><span class="eyebrow">{eyebrow}</span><h2 class="h2">{title}</h2></div>
    <a class="tlink" href="work.html">See all case studies <span>→</span></a>
  </div>
  <div class="hs-outer"><div class="hs-track">{"".join(wcard(s) for s in slugs)}</div></div>
  <div class="wrap"><div class="hs-ctrl">
    <div class="hs-progress" aria-hidden="true"><i></i></div><span class="hs-count">01 / {n:02d}</span>
    <div class="hs-btns">
      <button class="hs-btn hs-prev" type="button" aria-label="Previous case study"><svg width="18" height="18" viewBox="0 0 18 18"><path d="M11 4L6 9l5 5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      <button class="hs-btn hs-next" type="button" aria-label="Next case study"><svg width="18" height="18" viewBox="0 0 18 18"><path d="M7 4l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
    </div>
  </div></div>
</section>'''

def faq_section(items, title='Questions before <span class="mute">the first call</span>', tone=""):
    det = "".join(f'<details{" open" if i == 0 else ""}><summary>{e(q)}<i aria-hidden="true"></i></summary><p class="ans">{e(a)}</p></details>' for i, (q, a) in enumerate(items))
    return f'''<section class="band{tone}" id="faq" aria-labelledby="h-faq">
  <div class="wrap split">
    <div class="split-head">
      <span class="eyebrow">FAQ</span>
      <h2 id="h-faq" class="h2" style="font-size:clamp(30px,3.4vw,42px)">{title}</h2>
      <p>Still unsure? Ask in the chat, or email Riz directly.</p>
      <div class="mailbox"><code id="mail">hello@pagedriven.com</code><button class="copy" type="button" data-copy="hello@pagedriven.com" data-copy-el="mail">Copy</button></div>
    </div>
    <div class="faq">{det}</div>
  </div>
</section>'''

def inline_review(eyebrow="Or start here", title='Send the page and <span class="mute">we\'ll come prepared</span>', body="Riz reviews the page before you talk, so the conversation starts with specifics: where it loses momentum and the three fixes worth doing first.", tone=" mist", sid="review-form"):
    opts = "".join(f"<option>{o}</option>" for o in ["Calls", "Bookings", "Quote requests", "Sales", "Not sure yet"])
    return f'''<section class="band{tone}" id="{sid}" aria-labelledby="h-{sid}">
  <div class="bgfx gridbg" aria-hidden="true"></div>
  <div class="wrap split-lr">
    <div class="sticky">
      <span class="eyebrow">{eyebrow}</span>
      <h2 id="h-{sid}" class="h2" style="font-size:clamp(30px,3.4vw,44px)">{title}</h2>
      <p class="lede" style="font-size:17px">{e(body)}</p>
      <ul class="checklist"><li>A personal review from Riz, not an automated score</li><li>Where the page is most likely losing momentum</li><li>The three highest-impact fixes, in priority order</li></ul>
    </div>
    <form class="irform inline-review reveal" novalidate><input class="hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="ir-fields">
        <div class="field full"><label for="{sid}-url">Page URL</label><input id="{sid}-url" name="url" type="url" inputmode="url" placeholder="https://yourbusiness.com/landing-page" autocomplete="url"></div>
        <div class="field"><label for="{sid}-name">Your name</label><input id="{sid}-name" name="name" autocomplete="name" placeholder="Jordan Lee"></div>
        <div class="field"><label for="{sid}-email">Work email</label><input id="{sid}-email" name="email" type="email" autocomplete="email" placeholder="jordan@company.com"></div>
        <div class="field full"><label for="{sid}-goal">What should this page get you more of?</label><select id="{sid}-goal" name="goal">{opts}</select></div>
        <p class="err full" role="alert"></p>
        <div class="full ir-act">{cta_stack(f'<button class="btn btn-primary" type="submit">Send my page for review {ARROW}</button>')}</div>
      </div>
      <div class="ir-ok" hidden><span class="tick"><svg width="26" height="26" viewBox="0 0 26 26"><path d="M7 13.5l4 4 8-9" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></span><h3>Request received</h3><p>Riz will look at where the page loses momentum and send back the three highest-impact fixes.</p></div>
    </form>
  </div>
</section>'''

_b0 = SRC.index('<div class="badges g-in" aria-label="Track record">'); _b1 = SRC.index('</div>\n  </div>\n  <div class="platforms">', _b0)
BADGES = SRC[_b0:_b1].rstrip()  # the homepage trust badges, reused in every inner-page hero

def phero(copy_html, visual_html="", center=False, wave=True, badges=True, cls=""):
    canvas = '<canvas data-wave="soft" aria-hidden="true"></canvas>' if wave else ""
    if center:
        inner = f'<div class="phero-copy">{copy_html}</div>{visual_html}'
    else:
        inner = f'<div class="phero-in"><div class="phero-copy">{copy_html}</div><div class="pvis g-in">{visual_html}</div></div>'
    if badges: inner += f'<div class="hero-badges">{BADGES}</div>'
    return f'<section class="phero{" center" if center else ""}{cls}">{canvas}<div class="wrap">{inner}</div></section>'

def crumbs(*parts):
    return ""  # breadcrumbs removed from all page heroes
    out = ['<nav class="crumbs g-in" aria-label="Breadcrumb"><a href="index.html">Home</a>']
    for label, href in parts:
        out.append('<span aria-hidden="true">/</span>')
        out.append(f'<a href="{href}">{e(label)}</a>' if href else f'<span aria-current="page">{e(label)}</span>')
    out.append("</nav>")
    return "".join(out)

def meta_dl(rows, wide_last=False):
    items = []
    for i, (k, v) in enumerate(rows):
        wide = ' class="wide"' if (wide_last and i == len(rows) - 1) else ""
        items.append(f"<div{wide}><dt>{e(k)}</dt><dd>{e(v)}</dd></div>")
    return f'<dl class="meta-dl">{"".join(items)}</dl>'

def cards(items, cols="grid3", tone_cycle=("c-violet", "c-cyan", "c-pink", "c-amber", "c-mint", "c-lilac")):
    out = []
    for i, (ic, t, b) in enumerate(items):
        out.append(f'<div class="card {tone_cycle[i % len(tone_cycle)]}"><span class="tile">{icon(ic)}</span><h3>{e(t)}</h3><p>{e(b)}</p></div>')
    return f'<div class="{cols} stagger mt-l">{"".join(out)}</div>'

def steps(items, titled=True):
    lis = []
    for i, it in enumerate(items, 1):
        if titled: lis.append(f'<li><span class="n">{i}</span><div><h3>{e(it[0])}</h3><p>{e(it[1])}</p></div></li>')
        else: lis.append(f'<li><span class="n">{i}</span><p class="only">{e(it)}</p></li>')
    return f'<ol class="steps-v"><span class="steps-line" aria-hidden="true"><i></i></span>{"".join(lis)}</ol>'

def ba(before, after, bl="Before", al="After"):
    b = "".join(f"<li>{e(x)}</li>" for x in before); a = "".join(f"<li>{e(x)}</li>" for x in after)
    return f'<div class="ba stagger"><div class="b"><span class="tag">{e(bl)}</span><ul>{b}</ul></div><div class="a"><span class="tag">{e(al)}</span><ul>{a}</ul></div></div>'

def cmp_label(t):
    """'Before · Original page': the detail after the dot hides on narrow screens."""
    head, _, rest = t.partition(" · ")
    return e(head) + (f'<span class="cl-d"> · {e(rest)}</span>' if rest else "")

SKEL_PANES = '''<div class="cmp-pane cmp-before"><div class="mock"><div class="navl"><i></i><i></i><i></i><i></i><i></i><i></i></div><span class="hd" style="width:70%"></span><span class="ln"></span><span class="ln" style="width:85%"></span><span class="ln" style="width:60%"></span><div class="btns"><i></i><i></i><i></i></div><span class="imgb"></span><span class="ln"></span><span class="ln" style="width:72%"></span></div></div>
  <div class="cmp-pane cmp-after"><div class="mock after"><div class="navl"><i style="background:var(--violet)"></i><i style="flex:0 0 40px"></i><i style="flex:0 0 40px"></i><i style="flex:0 0 80px;background:var(--ink);height:14px;border-radius:999px"></i></div><span class="hd"></span><span class="hd v"></span><span class="ln"></span><span class="ln" style="width:70%"></span><div class="btns"><i></i><i></i></div><div class="trust"><b>★★★★★</b> Proof beside the decision</div><div class="logos"><i></i><i></i><i></i><i></i><i></i></div><div class="quote"><span class="ln" style="background:#D9DCEA"></span><span class="ln" style="width:60%;background:#D9DCEA"></span></div></div></div>'''

def compare_mock(left="Before", right="After", foot="Homepage · Iteration 1", shots=None):
    panes = ""
    if shots:  # real before/after screenshots instead of the skeleton mock
        panes = (f'<div class="cmp-pane cmp-before shot"><img src="{shots[0][0]}" alt="{e(shots[0][1])}" width="705" height="869"></div>'
                 f'<div class="cmp-pane cmp-after shot"><img src="{shots[1][0]}" alt="{e(shots[1][1])}" width="705" height="869"></div>')
    return f'''<div class="pvis-card"><div class="compare" data-sweep style="--split:50%;min-height:440px">
  <span class="cmp-label l">{cmp_label(left)}</span><span class="cmp-label r">{cmp_label(right)}</span>
  {panes or SKEL_PANES}
  <div class="cmp-handle" aria-hidden="true"></div>
  <input class="cmp-range" type="range" min="0" max="100" value="50" aria-label="Drag to compare before and after">
  <div class="cmp-foot"><span>{e(foot)}</span><span>Drag to compare</span></div>
</div></div>'''

def process_section():
    s = SRC.index('<!-- 6. PROCESS -->'); t = SRC.index('<!-- 7. WORK -->')
    return SRC[s:t].replace('<canvas class="bgfx" id="fxOrbit"', '<canvas class="bgfx" data-fx="orbit"')

def svc_viz(slug):
    n = SVC_META[slug][0][1]
    s = SRC.index(f'<article class="svc-card s{n}" id="svc-{n}">'); s = SRC.index('<div class="viz"', s)
    t = SRC.index('<div class="svc-body">', s)
    return SRC[s:t].strip()


# ---------- Landing Page Sprints: focus problem, solution rows, comparison, engagement cards ----------
CHECK = '<svg class="cm" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
DASH = '<svg class="cm" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 12h12"/></svg>'
CROSS = '<svg class="cm" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 7l10 10M17 7L7 17"/></svg>'
MARK = {"y": (CHECK, "Included"), "p": (DASH, "Sometimes"), "n": (CROSS, "Not usually")}

# per-service content for the shared service-page sections (problem, solution, comparison, engagement).
# Rows reuse each service's own outcomes/includes/steps; titles, tags and micro-lines summarise them.
SVC_X = {
 "landing-pages": dict(
   sol_h='A page built to finish <span class="mute">what the ad started.</span>',
   sol_lede="Four outcomes every Landing Page Sprint is built to deliver, whichever platform the page lives on.",
   sol=[("Message match", 0, "Ad promise → page headline", "target"),
        ("One clear action", "One clear action per page, whether that's a call, booking, quote, or purchase, instead of competing links.", "1 primary CTA per page", "pointer"),
        ("Tracking from day one", 2, "GA4 · Clarity · form events", "trend"),
        ("Edits without a developer", 3, "Built on the platform you already use", "pen")],
   cmp_h='Everything a sprint includes, <span class="mute">and how it compares.</span>',
   cmp_lede="Six things every Landing Page Sprint covers, set against the other ways teams usually get a campaign page made.",
   cmp=[("Founder-led discovery", "Offer, audience and traffic source, mapped by Riz", "pnn"),
        ("Structure before design", "Message hierarchy and page flow planned first", "ppn"),
        ("Copy written for the campaign", "Not repurposed from your website", "pnp"),
        ("Built on your platform", "Responsive, no migration needed", "yyn"),
        ("Tracking wired and tested", "Forms, events and thank-you flow", "ppn"),
        ("Final quality review", "Every page checked before handover", "ypn")],
   eng_h='From brief to launch, <span class="mute">in four focused steps.</span>',
   eng_lede="Most landing pages ship in 5–7 business days. Here's what happens at each step, and what you'll see from us along the way.",
   micro=["You share the offer, audience, ad or keyword, and platform.", "You see the page flow before any design starts.",
          "You review copy and layout together, in one pass.", "You get a tracked page, tested on real devices."],
   icons=["I10", "I11", "I12", "I13"]),
 "conversion-websites": dict(
   sol_h='A site built to move buyers, <span class="mute">not just impress them.</span>',
   sol_lede="Four outcomes every Conversion-Focused Website is built to deliver, whichever platform it's built on.",
   sol=[("One job per page", 0, "1 primary action per page", "target"),
        ("Answers in the right order", 1, "Buyer questions → page sections", "layers"),
        ("Clear paths to enquiry", 2, "Paid and organic visitors", "pointer"),
        ("Built to be maintained", 3, "Editable without breaking structure", "pen")],
   cmp_h='Everything a website build includes, <span class="mute">and how it compares.</span>',
   cmp_lede="Six things every Conversion-Focused Website covers, set against the other ways teams usually get a site built.",
   cmp=[("Conversion intent per page", "Site structure mapped page by page", "pnn"),
        ("Messaging framework", "Across home, service and location pages", "ppn"),
        ("Copy and design for every template", "Written and designed together", "ppn"),
        ("Built on your platform", "Responsive, accessible markup", "yyn"),
        ("Lead capture and tracking connected", "Analytics and events tested", "ppn"),
        ("Handover documentation", "So your team can maintain it", "ppn")],
   eng_h='From site map to launch, <span class="mute">in four focused steps.</span>',
   eng_lede="Here's what happens at each step of a website build, and what you'll see from us along the way.",
   micro=["You see each page's job and primary action before design starts.", "You review the messaging and copy before layouts are built.",
          "You review every template on desktop and mobile.", "You get tracking, documentation and a site your team can update."],
   icons=["I11", "I12", "I5", "I13"]),
 "cro-audits": dict(
   sol_h='Find the leak <span class="mute">before you pay to fix it.</span>',
   sol_lede="Four outcomes every CRO Audit is built to deliver, before a rebuild is even on the table.",
   sol=[("Fixes in priority order", 0, "Ranked by impact and effort", "trend"),
        ("Quick wins shipped", 1, "Implemented where scope allows", "pen"),
        ("A straight answer on rebuilds", 2, "Rebuild only when justified", "shieldcheck"),
        ("A plan you own", 3, "Act on it with us or without us", "layers")],
   cmp_h='Everything an audit includes, <span class="mute">and how it compares.</span>',
   cmp_lede="Five things every CRO Audit covers, set against the other ways teams usually get a page reviewed.",
   cmp=[("Reviewed against its traffic", "Ad or search intent, not just the page", "pnn"),
        ("Message, structure, design and offer", "All four assessed together", "ppp"),
        ("Fixes ranked by impact", "A prioritized plan, not a checklist", "pnp"),
        ("Quick wins implemented", "Where scope allows", "ppn"),
        ("An honest rebuild call", "Only recommended when justified", "pnn")],
   eng_h='From context to fixes, <span class="mute">in four focused steps.</span>',
   eng_lede="Here's what happens at each step of an audit, and what you'll get from us along the way.",
   micro=["You share analytics access, traffic sources and the conversion goal.", "Each section is checked against the traffic it receives.",
          "You get a prioritized plan: what to fix, why, and in what order.", "Quick wins go live; bigger changes come with a clear recommendation."],
   icons=["I10", "I6", "I2", "I13"]),
 "ongoing-optimization": dict(
   sol_h='Pages that keep improving <span class="mute">after launch day.</span>',
   sol_lede="Four outcomes every Ongoing Conversion Support engagement is built to deliver, month after month.",
   sol=[("Always improving", 0, "Reviewed on a regular cadence", "trend"),
        ("A backlog that stays current", 1, "Highest-impact work first", "layers"),
        ("New pages as offers change", 2, "Campaign and location pages", "monitor"),
        ("Direct access to Riz", 3, "Strategy calls and prioritization", "chat")],
   cmp_h='Everything ongoing support includes, <span class="mute">and how it compares.</span>',
   cmp_lede="Five things every Ongoing Conversion Support engagement covers, set against the other ways teams usually keep pages improving.",
   cmp=[("Regular performance reviews", "Signals checked on a set cadence", "ppn"),
        ("A backlog kept current", "Prioritized, not ad hoc", "pnn"),
        ("Changes shipped on a cadence", "Copy, design and build", "ypn"),
        ("New campaign and location pages", "As the offer evolves", "yyp"),
        ("Direct founder access", "Strategy calls with Riz", "pnn")],
   eng_h='One improvement cycle, <span class="mute">in four focused steps.</span>',
   eng_lede="Here's how each cycle runs, and what you'll see from us every time it does.",
   micro=["You see what 'working' looks like before anything changes.", "You see the ranked backlog and why each item is on it.",
          "Changes go live on a predictable cadence, reviewed first.", "You get a short report on what changed and what it did."],
   icons=["I10", "I2", "I5", "I7"]),
}

def lp_problem(s, cta):
    return f'''<section class="pfocus" id="problem" aria-labelledby="h-pf">
  <div class="wrap pf-in">
    <h2 class="eyebrow" id="h-pf">The problem</h2>
    <p class="pf-text" data-words><strong>{e(s["problemTitle"])}</strong> {e(s["problemBody"])}</p>
    <div class="pf-foot"><span>Sound familiar?</span><button class="tlink" data-open-review data-service="{e(cta["service"])}">Get a free review of your page <span>→</span></button></div>
  </div>
</section>'''

def lp_solution(s):
    x = SVC_X[s["slug"]]
    rows = [(t, s["outcomes"][b] if isinstance(b, int) else b, m, ic) for t, b, m, ic in x["sol"]]
    rh = "".join(f'<div class="sol-row{" on" if i==0 else ""}" tabindex="0"><h3>{e(t)}</h3><div class="sol-r"><p>{e(b if b.endswith(".") else b + ".")}</p><span class="sol-tag">{icon(ic)}{e(m)}</span></div></div>' for i, (t, b, m, ic) in enumerate(rows))
    return f'''<section class="sol" aria-labelledby="h-sol">
  <div class="sol-grain" aria-hidden="true"></div>
  <div class="wrap sol-head">
    <span class="eyebrow">The solution</span>
    <h2 id="h-sol" class="h2">{x["sol_h"]}</h2>
    <p class="sol-lede">{e(x["sol_lede"])}</p>
  </div>
  <div class="sol-rows">{rh}</div>
</section>'''

def lp_compare(s):
    x = SVC_X[s["slug"]]
    body = ""
    for t, sub, vals in x["cmp"]:
        cells = f'<td class="pd">{CHECK}<span class="sr">Included</span></td>'
        for v in vals:
            ic, lbl = MARK[v]; cells += f'<td class="v-{v}">{ic}<span class="sr">{lbl}</span></td>'
        body += f'<tr><th scope="row"><b>{e(t)}</b><small>{e(sub)}</small></th>{cells}</tr>'
    note = ""
    if s.get("note"):
        note = f'<div class="note reveal mt-l"><span class="tile">{icon("info")}</span><div><h3>{e(s["note"]["title"])}</h3><p>{e(s["note"]["body"])}</p></div></div>'
    return f'''<section class="band" id="included" aria-labelledby="h-cmp">
  <div class="wrap">
    <div class="sec-head"><span class="eyebrow">What's included</span><h2 id="h-cmp" class="h2">{x["cmp_h"]}</h2><p class="lede">{e(x["cmp_lede"])}</p></div>
    <div class="cmpt-wrap reveal" data-lenis-prevent>
      <table class="cmpt">
        <thead><tr><th scope="col"><span class="sr">What's included</span></th><th scope="col" class="pd"><img src="{IMG["I14"]}" alt="" width="72" height="72"><span>PageDriven</span></th><th scope="col">Design agency</th><th scope="col">Freelancer</th><th scope="col">AI alone</th></tr></thead>
        <tbody class="stagger">{body}</tbody>
      </table>
    </div>
    <div class="cmpt-legend"><span>{CHECK} Included</span><span>{DASH} Sometimes</span><span>{CROSS} Not usually</span><em>Typical of each option. Individual providers vary.</em></div>
    {note}
  </div>
</section>'''

def lp_engagement(s):
    x = SVC_X[s["slug"]]
    cards = ""
    for i, st in enumerate(s["steps"]):
        cards += f'''<article class="ecard{" on" if i==0 else ""}" tabindex="0" aria-label="Step {i+1}: {e(st["title"])}">
  <span class="en">{i+1:02d}</span><h3>{e(st["title"]).replace(" &amp; ", " &amp;<br>")}</h3>
  <img class="eimg" src="{IMG[x["icons"][i]]}" alt="" width="220" height="220">
  <div class="ecopy"><p>{e(st["body"])}</p><span class="emicro">{e(x["micro"][i])}</span></div>
</article>'''
    return f'''<section class="band night" id="how-it-works" aria-labelledby="h-eng">
  <div class="bgfx aurora" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap">
    <div class="sec-head"><span class="eyebrow">How the engagement works</span><h2 id="h-eng" class="h2">{x["eng_h"]}</h2><p class="lede">{e(x["eng_lede"])}</p></div>
    <div class="ecards stagger mt-l">{cards}</div>
  </div>
</section>'''


# ---------- Platforms: cursor chips that float in two at a time ----------
PLATFORMS = {
 "Unbounce": ("#6E63F6", '<circle cx="12" cy="12" r="10" fill="#141414"/><circle cx="12" cy="12" r="5" fill="none" stroke="#fff" stroke-width="2.3"/><path d="M16 5.2 8 18.8" stroke="#141414" stroke-width="4.6"/><path d="M15.6 6 8.4 18" stroke="#fff" stroke-width="2.3" stroke-linecap="round"/>'),
 "Webflow": ("#3A8FE0", '<path d="M23 6.4s-2.8 8.8-3 9.4c-.1-.7-2-12.2-2-12.2-3.5 0-5.4 2.5-6.4 5.2 0 0-2.5 6.5-2.7 7.1 0-.6-.6-6.7-.6-6.7C7.7 6.2 5.1 4.6 2.9 4.6l2.6 15.5c3.3 0 5.1-2.3 6.1-4.7l2-5.4c0 .3 1.5 10.1 1.5 10.1 3.3 0 5.1-2.1 6.1-4.5z" fill="#4353FF"/>'),
 "HighLevel": ("#2FB04A", '<path d="M3.5 21V9.5H1.8L5.3 4l3.5 5.5H7.1V21z" fill="#F5B60A"/><path d="M10.3 21v-7.8H8.6L12 7.8l3.4 5.4h-1.7V21z" fill="#2E8BF0"/><path d="M17 21V9.5h-1.7L18.8 4l3.4 5.5h-1.7V21z" fill="#37B34A"/>'),
 "ClickFunnels": ("#E8436F", '<rect x="2" y="3" width="20" height="18" rx="3.5" fill="#0B1F4D"/><path d="M8.4 7.8H6.6v8.4h1.8M15.6 7.8h1.8v8.4h-1.8" stroke="#fff" stroke-width="1.7" fill="none"/><path d="M9.6 8.6h4.8l-1.6 3.1h-1.6zM11.2 12.6h1.6l-.4 3.2h-.8z" fill="#E8436F"/>'),
 "WordPress": ("#2A8BC9", '<circle cx="12" cy="12" r="10.2" fill="#21759B"/><circle cx="12" cy="12" r="8.4" fill="none" stroke="#fff" stroke-width="1.1"/><text x="12" y="16.4" text-anchor="middle" font-family="Georgia,Times,serif" font-weight="700" font-size="12.5" fill="#fff">W</text>'),
 "Shopify": ("#5BAF3C", '<path d="M5.2 7.6 6.7 21l11.6 1.4 1.5-14.8z" fill="#95BF47"/><path d="M9.2 7.6V6a2.9 2.9 0 0 1 5.8 0v1.6" fill="none" stroke="#5E8E3E" stroke-width="1.6"/><text x="12.6" y="18.4" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-weight="800" font-size="9.5" fill="#fff">S</text>'),
 "HubSpot": ("#FF7A59", '<circle cx="15.4" cy="14.2" r="3.9" fill="none" stroke="#FF7A59" stroke-width="2.6"/><path d="M15.4 10.3V6.4" stroke="#FF7A59" stroke-width="2.2"/><circle cx="15.4" cy="5" r="1.9" fill="#FF7A59"/><path d="M12.3 11.9 6.6 7.6M12.5 16.8l-3.2 3" stroke="#FF7A59" stroke-width="2.2" stroke-linecap="round"/><circle cx="5.6" cy="6.8" r="1.9" fill="#FF7A59"/><circle cx="8.6" cy="20.4" r="1.5" fill="#FF7A59"/>'),
}
CURSOR = '<svg class="pc-cur" viewBox="0 0 32 32" aria-hidden="true"><path d="M5 3.5 27 12.6l-9.4 3.1-3.3 9.8z" fill="var(--c)" stroke="#fff" stroke-width="1.8" stroke-linejoin="round"/></svg>'
def platforms_section(names, slug):
    chips = ""
    for n in names:
        if n not in PLATFORMS: continue
        c, svg = PLATFORMS[n]
        chips += (f'<div class="pchip" style="--c:{c}">'
                  f'<span class="pc-ico"><svg viewBox="0 0 24 24">{svg}</svg></span><b>{e(n)}</b>{CURSOR}</div>')
    listing = ", ".join(names)
    return f'''<section class="plat" aria-labelledby="h-plat-{slug}">
  <div class="plat-rings" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="plat-stage" aria-hidden="true">{chips}</div>
  <div class="wrap plat-center">
    <span class="eyebrow">Platforms</span>
    <h2 id="h-plat-{slug}" class="plat-h">Built on the platform<br><span class="mute">you already use</span></h2>
    <p class="lede">No migration on your roadmap. We work where your pages already live.</p>
    <p class="sr">Platforms we build on: {e(listing)}.</p>
  </div>
</section>'''

# ---------- page writer ----------
CSS = SRC[SRC.index("<style>") + 7:SRC.index("</style>")] + open(os.path.join(BASE, "inner.css")).read()
os.makedirs(OUT + "/assets", exist_ok=True)
open(OUT + "/assets/site.css", "w").write(CSS)
open(OUT + "/assets/site.js", "w").write(open(os.path.join(BASE, "site.js")).read())
PAGES = []
def page(fname, title, desc, active, main_html, final=True, cta=None, main_cls=""):
    body = header(active) + f'\n<main id="top"{f' class="{main_cls}"' if main_cls else ""}>\n' + main_html + (final_cta(**(cta or {})) if final else "") + '\n</main>\n' + footer() + "\n" + OVERLAYS + "\n" + SCRIPTS
    head = f'<title>{e(title)}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<meta name="description" content="{e(desc)}">\n{FONTS}\n<link rel="stylesheet" href="assets/site.css">\n'
    if fname == "index.html":
        out = head + body
    else:
        out = f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n{head}</head>\n<body>\n{body}\n</body>\n</html>\n'
    open(f"{OUT}/{fname}", "w").write(out); PAGES.append(fname)

# =====================================================================
# HOME
# =====================================================================
home = SRC[SRC.index('<main id="top">') + len('<main id="top">'):SRC.index('<!-- 10. CTA with founder -->')]
home = img_paths(home)
_old_cta = """    <div class="hero-ctas g-in">
      <button class="btn btn-primary" data-open-review>Get My Free Page Review <span class="arr">→</span></button>
      <a class="btn btn-ghost" href="#case">See Client Results</a>
    </div>
    <p class="micro g-in"><span>Free</span><span>Personalized</span><span>No obligation</span></p>"""
assert _old_cta in home
home = home.replace(_old_cta, f"""    <div class="hero-ctas g-in">
      {cta_stack('<button class="btn btn-primary" data-open-review>Get My Free Page Review <span class="arr">→</span></button>')}
    </div>""")
home = home.replace('<canvas id="wave" aria-hidden="true"></canvas>', '<canvas id="wave" data-wave="full" aria-hidden="true"></canvas>')
home = home.replace('<canvas class="bgfx" id="fxDots"', '<canvas class="bgfx" data-fx="dots"').replace('<canvas class="bgfx" id="fxOrbit"', '<canvas class="bgfx" data-fx="orbit"')
home = home.replace('<div class="compare" id="compare" style="--split:50%">', '<div class="compare" data-sweep style="--split:50%">').replace(' id="cmpRange"', "")
home = home.replace('href="https://pagedriven.com/work/caseleap" target="_blank" rel="noopener"', 'href="work-caseleap.html"')
home = home.replace('<a class="path reveal" href="#svc-1">', '<a class="path reveal" href="landing-pages.html">')
home = home.replace('<a class="path reveal" href="https://pagedriven.com/agency-partners" target="_blank" rel="noopener">', '<a class="path reveal" href="agency-partners.html">')
for slug, label in [("landing-pages","Get a landing page quote"),("conversion-websites","Get a website quote"),("cro-audits","Request an audit"),("ongoing-optimization","Discuss CRO support")]:
    old = re.search(r'<button class="tlink" data-open-review data-service="[^"]+">' + re.escape(label) + r' <span>→</span></button>', home).group(0)
    home = home.replace(old, f'<a class="tlink" href="{slug}.html">Explore {e(SVC[slug]["name"])} <span>→</span></a>')
w0 = home.index('<!-- 7. WORK -->'); w1 = home.index('<!-- 8. TESTIMONIALS -->')
home = home[:w0] + work_carousel([s for s in WART if s != "caseleap"]) + "\n" + home[w1:]
home = home.replace('<div class="t-grid" id="tGrid"></div>', '<div class="t-grid">' + "".join(tcard(t) for t in TESTI) + "</div>")
HOME_FAQ = [
 ("How long does a landing page take?","Most landing pages are completed in 5–7 business days, depending on scope and feedback rounds. Rush timelines are available."),
 ("How is the free page review different from a paid CRO audit?","The free page review is a short, personal look at one page: where it's most likely losing momentum and the three highest-impact fixes. A CRO audit is a comprehensive paid engagement with a full page and funnel review against traffic data, prioritized findings, and quick-win implementation where scope allows."),
 ("What do you need from us to get started?","Your offer details, any relevant assets, brand guidelines if you have them, and examples you like. We guide you through the rest."),
 ("Which platforms do you build on?","Webflow, WordPress, Shopify, Unbounce, ClickFunnels, HighLevel, HubSpot, Wix, and more. We build where your page already lives, so you do not need to migrate."),
 ("Do you run A/B tests?","Where it makes sense. Reliable experiments need sufficient traffic and trustworthy tracking. We'll tell you honestly whether your traffic supports testing, and prioritize direct, evidence-based improvements when it doesn't."),
 ("Do you work with agencies?","Yes. We provide white-label landing pages, location pages, website production, UX improvements, and technical support for SEO, PPC, and digital agencies."),
 ("Who actually does the work?","Riz leads discovery, conversion strategy, and final quality review on every engagement, supported by a specialist copy, design, and development team."),
 ("Where are you based, and how do you handle time zones?","Working with businesses and agencies across the US and Canada. Remote collaboration with daily availability for meetings during US business hours."),
]
f0 = home.index('<!-- 9. FAQ -->')
home = home[:f0] + faq_section(HOME_FAQ) + "\n"
page("index.html", "PageDriven", "PageDriven plans, writes, designs, and builds conversion-focused landing pages and websites for service businesses and the agencies behind them.", "home", home)

# =====================================================================
# SERVICE PAGES
# =====================================================================
for s in SERVICES:
    slug = s["slug"]; cls, ic, _ = SVC_META[slug]; cta = D["SERVICE_CTAS"][slug]
    copy = (crumbs(("Services", None), (s["name"], None)) +
      f'<span class="eyebrow g-in">{e(s["name"])}</span>'
      f'<h1 class="g-in">{mute(s["headline"], s["headlineHighlight"])}</h1>'
      f'<p class="lede g-in">{e(s["subheadline"])}</p>'
      f'<div class="btn-row g-in">{cta_stack(f"""<button class="btn btn-primary" data-open-review data-service="{e(cta['service'])}">{e(cta['primary'])} {ARROW}</button>""")}<a class="btn btn-ghost" href="{cta["secondaryHref"]}">{e(cta["secondary"])}</a></div>')
    vis = f'<img class="float-ico tilt3d" src="{IMG[ic]}" alt="" width="120" height="120"><div class="pvis-card {cls}">{svc_viz(slug)}</div>'
    m = phero(copy, vis, badges=False)
    m += lp_problem(s, cta) + lp_solution(s) + lp_compare(s) + lp_engagement(s)
    proof = [find_testi(n) for n in s["proofNames"]]
    proof = [p for p in proof if p]
    light = True  # all service pages use the light feedback band
    m += f'''<section class="band{" mist" if light else " night"}" aria-labelledby="h-proof-{slug}">
  {"" if light else '<div class="bgfx aurora" aria-hidden="true"><i></i><i></i><i></i></div>'}
  <div class="wrap">
    <div class="sec-head center"><span class="eyebrow">Client feedback</span><h2 id="h-proof-{slug}" class="h2">What clients say <span class="mute">about the work.</span></h2></div>
    <div class="t-grid eq">{"".join(tcard_src(p, light=light) for p in proof)}</div>
  </div>
</section>'''
    if slug == "cro-audits":
        m += f'''<section class="band night" id="audit-examples" aria-labelledby="h-audit">
  <canvas class="bgfx" data-fx="dots" aria-hidden="true"></canvas>
  <div class="wrap split-lr">
    <div class="sticky">
      <span class="eyebrow">Real audit example</span>
      <h2 id="h-audit" class="h2" style="font-size:clamp(30px,3.4vw,44px)">See what an actionable <span class="mute">CRO audit looks like.</span></h2>
      <p class="lede" style="font-size:17px">Not a generic checklist. Each recommendation connects a specific change to the evidence behind it, then ranks it by priority so the team knows what to fix, test or investigate first.</p>
      <div class="grid3 stagger" style="grid-template-columns:1fr;gap:10px">
        <div class="card c-cyan" style="grid-template-columns:auto 1fr;align-items:center;padding:18px"><span class="tile" style="margin:0">{icon("pointer")}</span><div><h3 style="font-size:16px">Behavior-informed</h3><p style="font-size:14px">Attention patterns, clicks and recordings</p></div></div>
        <div class="card c-pink" style="grid-template-columns:auto 1fr;align-items:center;padding:18px"><span class="tile" style="margin:0">{icon("phone")}</span><div><h3 style="font-size:16px">Device-specific</h3><p style="font-size:14px">Separate desktop and mobile findings</p></div></div>
        <div class="card c-amber" style="grid-template-columns:auto 1fr;align-items:center;padding:18px"><span class="tile" style="margin:0">{icon("trend")}</span><div><h3 style="font-size:16px">Prioritized for action</h3><p style="font-size:14px">Clear urgency, evidence and effort</p></div></div>
      </div>
      <div><button class="btn btn-primary" data-open-review data-service="{e(cta["service"])}">{e(cta["primary"])} {ARROW}</button></div>
    </div>
    <div class="report reveal" aria-label="Sample pages from a three-page CRO and UX review">
      <div class="rpage"><span class="k-lbl">Page 1</span><span class="rh">Summary and high-priority desktop findings</span><span class="rshot"></span><div class="rr"><span>Hero misses search intent</span><span class="pillx p-hi">High</span></div><div class="rr"><span>Reviews below the fold</span><span class="pillx p-hi">High</span></div><div class="rr"><span>Two competing CTAs</span><span class="pillx p-md">Med</span></div><span class="rl"></span><span class="rl" style="width:70%"></span></div>
      <div class="rpage"><span class="k-lbl">Page 2</span><span class="rh">Medium and low-priority desktop findings</span><div class="rr"><span>Offer stated twice, differently</span><span class="pillx p-md">Med</span></div><div class="rr"><span>Form asks for 7 fields</span><span class="pillx p-md">Med</span></div><div class="rr"><span>Footer links leak attention</span><span class="pillx p-lo">Low</span></div><span class="rshot"></span><span class="rl"></span><span class="rl" style="width:80%"></span></div>
      <div class="rpage"><span class="k-lbl">Page 3</span><span class="rh">Mobile findings and measurement note</span><span class="rshot"></span><div class="rr"><span>Sticky CTA hides content</span><span class="pillx p-hi">High</span></div><div class="rr"><span>Tap targets too small</span><span class="pillx p-lo">Quick win</span></div><span class="rl"></span><span class="rl" style="width:60%"></span></div>
    </div>
  </div>
</section>'''
    related = [w["slug"] for w in WORK if w["service"] == slug] + [w["slug"] for w in WORK if w["service"] != slug]
    m += work_carousel(related, title=f'Pages we\'ve shipped <span class="mute">for teams like yours</span>', eyebrow="Related work")
    if s.get("platforms"):
        m += platforms_section(s["platforms"], slug)
    others = "".join(
        f'<a class="svc-link reveal" href="{o["slug"]}.html"><img src="{IMG[SVC_META[o["slug"]][1]]}" alt="" width="64" height="64"><h3>{e(o["name"])}</h3><p>{e(o["short"])}</p><span class="tlink">Learn more <span>→</span></span></a>'
        for o in SERVICES if o["slug"] != slug)
    m += f'''<section class="band{"" if s.get("platforms") else " mist"}" aria-labelledby="h-other-{slug}">
  <div class="wrap"><div class="sec-head"><span class="eyebrow">Other services</span><h2 id="h-other-{slug}" class="h2" style="font-size:clamp(28px,3vw,40px)">More ways to fix <span class="mute">the page that costs you leads.</span></h2></div>
  <div class="svc-links mt-l">{others}</div></div>
</section>'''
    m += faq_section([(f["q"], f["a"]) for f in s["faqs"]], title=f'Questions about <span class="mute">{e(s["name"].lower())}</span>', tone=" mist" if s.get("platforms") else "")
    page(f"{slug}.html", f'{s["name"]} · PageDriven', s["short"], "svc:" + slug, m,
         cta=dict(title_html=f'Ready to move on <span class="mute">{e(s["name"].lower())}?</span>', body="Share your page and goal. We'll reply with a clear recommendation and scope.", btn=cta["primary"], service=cta["service"]))

# =====================================================================
# ABOUT
# =====================================================================
copy = (crumbs(("About", None)) + '<span class="eyebrow g-in">About PageDriven</span>'
  '<h1 class="g-in">A founder-led agency <span class="mute">built around conversion.</span></h1>'
  '<p class="lede g-in">PageDriven helps service businesses and marketing agencies convert more of the paid and organic traffic they already pay for, through landing pages, websites, CRO improvements, and ongoing optimization.</p>')
m = phero(copy, center=True, cls=" tight-b")
# founder story: scroll-lit copy (data-words="flow", no pin) beside the portrait; credentials sit below the portrait, never over it
UPW = re.search(r'<svg class="upw".*?</svg>', SRC, re.S).group(0)
PMP = ('<svg class="pmp" viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="17.5" fill="none" stroke="currentColor" stroke-width="2"/>'
       '<circle cx="20" cy="20" r="13.5" fill="none" stroke="currentColor" stroke-width="1" opacity=".35"/>'
       '<text x="20" y="24" text-anchor="middle" font-size="10.5" font-weight="700" letter-spacing=".4" fill="currentColor">PMP</text></svg>')
m += f'''<section class="band mist story-band" aria-labelledby="h-story">
  <div class="bgfx gridbg" aria-hidden="true"></div>
  <div class="wrap story-in">
    <div class="story-copy">
      <span class="eyebrow">The founder story</span>
      <h2 id="h-story" class="h2">From product leadership <span class="mute">to PageDriven.</span></h2>
      <div class="story-text" data-words="flow">
        <p>Before founding PageDriven, Riz spent years in <strong>product leadership</strong>, working on how people move through digital products, <mark>where they hesitate, and what gets them to act.</mark> The pattern was always the same: teams invested heavily in getting visitors to the door, then <mark>under-invested in what those visitors found when they arrived.</mark></p>
        <p><strong>PageDriven exists to close that gap.</strong> Instead of treating a website as a design artifact, we treat it as <mark>the working part of a traffic investment</mark>: planned around the visitor&#x27;s intent, written around the offer, and built to be measured.</p>
        <p>That product background shapes every engagement. <mark>Start with the user and the goal,</mark> then let structure, copy, and design follow.</p>
      </div>
    </div>
    <figure class="story-fig">
      <div class="sp-wrap">
        <div class="story-portrait"><img src="assets/img/riz-full.webp" alt="Riz, founder and conversion strategist at PageDriven" width="337" height="629"></div>
        <svg class="sf-arrow" viewBox="0 0 128 100" aria-hidden="true"><path d="M110 29C100 27 89 27 80 28C60 30 41 37 28 50C16 62 12 78 18 92"/><path d="M7.5 83.5c4 3 7 5.6 10.5 8.5 1.2-4.2 1.4-8.6.9-13.2"/></svg>
        <div class="sf-name" aria-hidden="true"><b>Rizvi (Riz)</b><small>PageDriven founder &amp;<br>conversion strategist</small></div>
      </div>
      <ul class="creds" aria-label="Credentials">
        <li><span class="cr-ic up">{UPW}</span><b>Top Rated</b><small>on Upwork</small></li>
        <li><span class="cr-ic pm">{PMP}</span><b>PMP®</b><small>Certified</small></li>
        <li><span class="cr-ic cl">{icon("users")}</span><b>100+ clients</b><small>served</small></li>
      </ul>
      <figcaption><b>Rizvi (Riz)</b><span>PageDriven founder &amp; conversion strategist</span></figcaption>
    </figure>
  </div>
</section>'''

# how the work gets done: grid-lined rows; the centre image stays put and cross-fades as the second row takes focus
def lead_bold(x):
    k, _, rest = x.partition(": ")
    return f"<b>{e(k)}:</b> {e(rest)}" if rest else e(x)
WGD = [("s1", "Handled personally by Riz",
        ["Discovery: understanding your offer, audience, traffic sources, and goals before anything is designed",
         "Conversion strategy: the message hierarchy, page structure, and proof plan behind every engagement",
         "Final quality review: every page is personally reviewed before it reaches you"],
        '<img class="wgd-riz" src="assets/img/riz-meeting.webp" alt="Riz talking a client through their page" width="1254" height="1254">'),
       ("s2", "Supported by the specialist team",
        ["Conversion copywriting for campaigns and websites", "Design that serves the message rather than decorating it", "Development across the platforms clients already use"],
        '<img class="wgd-team" src="assets/img/team.webp" alt="The PageDriven specialist team reviewing a page together" width="1200" height="900">')]
rows = "".join(f'''<div class="wgd-row {c}{" on" if i == 0 else ""}"><div class="wrap wgd-cols">
      <div class="wgd-l"><h3>{e(t)}</h3></div>
      <div class="wgd-m"><div class="wgd-pic {c}">{img}</div></div>
      <ul class="wgd-r">{"".join(f"<li><span>{lead_bold(x)}</span></li>" for x in items)}</ul>
    </div></div>''' for i, (c, t, items, img) in enumerate(WGD))
pics = "".join(f'<div class="wgd-pic {c}{" on" if i == 0 else ""}">{img}</div>' for i, (c, _, _, img) in enumerate(WGD))
m += f'''<section class="band wgd" aria-labelledby="h-team">
  <div class="sol-grain" aria-hidden="true"></div>
  <div class="wgd-lines" aria-hidden="true"><div class="wrap"><i></i><i></i><i></i></div></div>
  <div class="wrap"><div class="sec-head center"><span class="eyebrow">How the work gets done</span><h2 id="h-team" class="h2">Founder-led strategy. <span class="mute">Specialist delivery.</span></h2><p class="lede">Every engagement is led personally and shipped by a focused specialist team.</p></div></div>
  <div class="wgd-body">
    {rows}
    <div class="wgd-stick"><div class="wrap wgd-cols"><div class="wgd-media"><div class="wgd-frame">{pics}</div></div></div></div>
  </div>
</section>'''

m += process_section()
# conversion philosophy: expanding cards with the landing-page "How the engagement works" mechanics, in a light tone (sits between two navy bands)
pr = [("I0","Traffic first,|page second","We start from the traffic already pointed at the page: what it was promised and what it expects to find."),
      ("I11","Structure|before styling","A page converts because of order, clarity, and proof. Visual polish comes after those are settled."),
      ("I4","One goal|per page","Every page we ship has a single action it is trying to earn. Everything else supports it."),
      ("I13","No inflated|claims","We describe the work and the outcome. We do not attach numbers we cannot verify.")]
pcards = "".join(f'''<article class="ecard s{i}{" on" if i == 1 else ""}" tabindex="0" aria-label="Principle {i}: {e(t.replace("|", " "))}">
  <span class="en">{i:02d}</span><h3>{"<br>".join(e(x) for x in t.split("|"))}</h3>
  <img class="eimg" src="{IMG[ic]}" alt="" width="220" height="220">
  <div class="ecopy"><p>{e(b)}</p></div>
</article>''' for i, (ic, t, b) in enumerate(pr, 1))
m += f'''<section class="band mist" aria-labelledby="h-prin">
  <div class="bgfx gridbg" aria-hidden="true"></div>
  <div class="wrap">
    <div class="sec-head"><span class="eyebrow">The conversion philosophy</span><h2 id="h-prin" class="h2">Principles that shape <span class="mute">every build.</span></h2></div>
    <div class="ecards light stagger mt-l">{pcards}</div>
  </div>
</section>'''
m += testimonial_wall()
page("about.html", "About PageDriven", "PageDriven is a founder-led conversion agency. Riz leads discovery, conversion strategy, and final quality review, supported by a specialist design and development team.", "about", m)

# =====================================================================
# AGENCY PARTNERS
# =====================================================================
AC = D["AGENCY_CTA"]
copy = (crumbs(("Agency Partners", None)) + '<span class="eyebrow g-in">For SEO, PPC, and digital agencies</span>'
  '<h1 class="g-in">Your conversion design and build team, <span class="mute">without another full-time hire.</span></h1>'
  '<p class="lede g-in">PageDriven gives your agency white-label landing pages, location pages, website production, and ongoing conversion improvements, led by a conversion strategist and delivered under your brand.</p>'
  f'<div class="btn-row g-in"><button class="btn btn-primary" data-open-review data-service="{e(AC["service"])}">{e(AC["primary"])} {ARROW}</button><a class="btn btn-ghost" href="#how-partnerships-work">{e(AC["secondary"])}</a></div>')
m = phero(copy, center=True, badges=False, cls=" roomy-b")
# what we take off your plate: product-style cards, a skeleton UI per service instead of an icon
def sk_row(label, pill, cls, lead=""):
    return f'<div class="sk-row">{lead}<span class="sk-tx">{label}</span><span class="pillx {cls}">{pill}</span></div>'
SK_CHECK = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 8.4l2.6 2.5L12 5.4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
SK = [
 # campaign landing pages: the ad promise carried into the page
 f'''<span class="sk-k">Paid search ad</span>
 <div class="sk-box sk-ad"><span class="sk-adtag">Ad</span><b>Free roof inspection, Dallas</b></div>
 <div class="sk-match"><i>{SK_CHECK}</i>Message match</div>
 <div class="sk-box"><span class="sk-k">Landing page</span><b class="sk-h">Free roof inspection, Dallas</b><span class="sk-bar" style="width:78%"></span><span class="sk-btn">Book inspection</span></div>''',
 # location and service pages: one template, many pages
 f'''<div class="sk-row"><span class="sk-k">Location template</span><span class="pillx p-lo">24 pages</span></div>
 <div class="sk-list">{"".join(sk_row(f"/roofing/{c}", st, cl, '<i class="sk-thumb"></i>') for c, st, cl in (("dallas","Live","p-lo"),("plano","Live","p-lo"),("frisco","Live","p-lo"),("mckinney","Draft","p-nx")))}</div>''',
 # website production: a full page wireframe
 '''<div class="sk-win"><div class="sk-wbar"><i></i><i></i><i></i><span>client-site.com</span></div>
 <div class="sk-wnav"><b></b><span></span><span></span><span></span><em></em></div>
 <div class="sk-whero"><span class="sk-bar dk" style="width:64%"></span><span class="sk-bar" style="width:46%"></span><span class="sk-btn sm"></span></div>
 <div class="sk-wcols"><i></i><i></i><i></i></div></div>''',
 # ux audits: prioritized fixes
 f'''<div class="sk-row"><span class="sk-k">Prioritized fixes</span><span class="sk-k">3 found</span></div>
 <div class="sk-list">{sk_row("Hero doesn&#x27;t match the ad","High","p-hi",'<i class="sk-cb"></i>')}{sk_row("Reviews sit below the fold","High","p-hi",'<i class="sk-cb"></i>')}{sk_row("Form asks for 9 fields","Quick win","p-lo",'<i class="sk-cb on">'+SK_CHECK+'</i>')}</div>''',
 # platform implementation: build where the client already lives
 f'''<span class="sk-k">Client platform</span>
 <div class="sk-plats">{"".join(f'<span class="{"on" if n == "Webflow" else ""}"><svg viewBox="0 0 24 24" aria-hidden="true">{PLATFORMS[n][1]}</svg>{n}</span>' for n in ("Webflow","WordPress","Shopify","HighLevel","Unbounce","HubSpot"))}</div>
 <div class="sk-checks"><span><i>{SK_CHECK}</i>GA4 events</span><span><i>{SK_CHECK}</i>Form → CRM</span></div>''',
 # ongoing improvements: this month's retainer queue
 f'''<div class="sk-row"><span class="sk-k">This month</span><span class="sk-k">Retainer</span></div>
 <div class="sk-list">{sk_row("New hero variant","Live","p-lo",'<i class="sk-dot" style="background:var(--mint)"></i>')}{sk_row("FAQ section","In review","p-md",'<i class="sk-dot" style="background:var(--amber)"></i>')}{sk_row("Spring campaign page","Queued","p-nx",'<i class="sk-dot"></i>')}</div>
 <div class="sk-prog"><span class="sk-k">1 of 3 shipped</span><span class="sk-bar"><i style="width:34%"></i></span></div>''',
]
sup = [("layers","Landing pages","Campaign landing pages","Pages matched to your clients' paid search and paid social campaigns: message, copy, design, and build around one clear action.","landing-pages.html","Explore landing pages","#5452F6","rgba(84,82,246,.34)"),
       ("pin","Location pages","Location and service pages","Scalable location and service-area templates that stay consistent and conversion-aware across dozens of pages.","conversion-websites.html","Explore location pages","#3A9FD6","rgba(90,205,220,.42)"),
       ("grid","Websites","Website production","Full site builds executed from your designs or ours, structured around how the client's buyers actually decide.","conversion-websites.html","Explore website builds","#7472F8","rgba(150,140,255,.4)"),
       ("monitor","Audits","UX audits and quick wins","Reviews of existing client pages with prioritized fixes, implemented where scope allows, no rebuild required.","cro-audits.html","Explore CRO audits","#D9699E","rgba(240,150,190,.42)"),
       ("globe","Platforms","Platform implementation","Builds, tracking, forms, and integrations on the platform the client already runs: Webflow, WordPress, Shopify, HighLevel, Unbounce, HubSpot, and more.","book.html","Discuss a client's stack","#D38A2E","rgba(245,190,110,.45)"),
       ("trend","Ongoing CRO","Ongoing client-site improvements","Continuous conversion work on client pages: new variants, new sections, and new campaign pages as retainers evolve.","ongoing-optimization.html","Explore ongoing CRO","#0F9F84","rgba(110,215,180,.42)")]
CHEV = '<svg width="14" height="14" viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3.5 10.5 8 6 12.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
pcs = "".join(f'''<a class="pcard" href="{href}" style="--tc:{tc};--glow:{gl}">
      <div class="pc-stage" aria-hidden="true"><div class="pc-sheet">{SK[i]}</div></div>
      <div class="pc-body"><span class="pc-chip">{icon(ic)}{e(chip)}</span><h3>{e(t)}</h3><p>{e(b)}</p><span class="pc-more">{e(more)}{CHEV}</span></div>
    </a>''' for i, (ic, chip, t, b, href, more, tc, gl) in enumerate(sup))
m += f'''<section class="band mist pcs" aria-labelledby="h-sup">
  <div class="wrap"><div class="sec-head"><span class="eyebrow">What we take off your plate</span><h2 id="h-sup" class="h2">The production work <span class="mute">that slows delivery down.</span></h2><p class="lede">Six ways agencies use PageDriven, per project or as ongoing monthly capacity.</p></div>
  <div class="pc-grid stagger">{pcs}</div></div>
</section>'''

D_FIT = ["SEO and PPC agencies whose campaigns outpace their clients' pages","Digital agencies that need reliable production capacity without hiring","Agencies that want conversion thinking attached to the build, not just execution"]
# who the partnership is for: scroll-lit statement (same mechanics as "The problem"), audience points as glass chips in a row
FIT_CK = '<span class="pf-ck"><svg width="14" height="14" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 8.4l2.6 2.5L12 5.4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>'
fit = "".join(f"<li>{FIT_CK}<span>{e(x)}</span></li>" for x in D_FIT)
m += f'''<section class="pfocus pf-glass" aria-labelledby="h-fit">
  <div class="pf-orbs" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap pf-in">
    <h2 class="eyebrow" id="h-fit">Who the partnership is for</h2>
    <p class="pf-text" data-words><strong>Agencies whose campaigns outpace their clients&#x27; pages.</strong> You can sell the traffic and the strategy. The bottleneck is getting conversion-quality pages produced for every client who needs them. That&#x27;s the gap this partnership fills.</p>
    <ul class="pf-chips">{fit}</ul>
  </div>
</section>'''
# how the partnership works: the landing-page engagement cards (navy band, aurora, expand on hover/focus)
part = [("I13","White-label|delivery","We deliver under your brand, in your tools and your format. Your client relationship stays entirely yours. We never appear unless you want us to."),
        ("I6","Founder-led|strategy and QA","Riz leads the conversion strategy on every engagement and personally reviews everything before it goes back to you. Nothing ships unreviewed."),
        ("I5","Predictable|monthly capacity","Ongoing partnerships run on a scoped monthly cadence sized to your pipeline, so you can plan client work without guessing at availability."),
        ("I10","Communication|and workflow","You brief us the way you brief an internal team. We work inside your project tools, keep status visible, and flag questions early instead of silently guessing.")]
pecards = "".join(f'''<article class="ecard{" on" if i == 1 else ""}" tabindex="0" aria-label="{i}: {e(t.replace("|", " "))}">
  <span class="en">{i:02d}</span><h3>{"<br>".join(e(x) for x in t.split("|"))}</h3>
  <img class="eimg" src="{IMG[ic]}" alt="" width="220" height="220">
  <div class="ecopy"><p>{e(b)}</p></div>
</article>''' for i, (ic, t, b) in enumerate(part, 1))
m += f'''<section class="band night" id="how-partnerships-work" aria-labelledby="h-how">
  <div class="bgfx aurora" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="wrap">
    <div class="sec-head"><span class="eyebrow">How the partnership works</span><h2 id="h-how" class="h2">Built to feel like <span class="mute">your internal team.</span></h2></div>
    <div class="ecards tight stagger mt-l">{pecards}</div>
  </div>
</section>'''
danny = next(t for t in D["TESTIMONIALS"] if t["name"] == "Danny Thomas")
andrew = next(t for t in D["TESTIMONIALS"] if t["role"] == "Levitate Media, Founder")
m += f'''<section class="band mist" aria-labelledby="h-ap">
  <div class="wrap"><div class="sec-head center"><span class="eyebrow">From agency partners</span><h2 id="h-ap" class="h2">What it's like <span class="mute">to work with us.</span></h2></div>
  <div class="grid2 mt-l stagger">{tcard_src(danny)}{tcard_src(andrew)}</div></div>
</section>'''
m += work_carousel(list(WART.keys()), eyebrow="Recent work", title='Pages delivered <span class="mute">for agency clients and direct clients</span>')
agfaq = [("Is the work fully white-label?","Yes. Deliverables, communication, and documentation carry your brand. We work as your production team and never contact your clients directly unless you ask us to join a call."),
 ("How does monthly capacity work?","We scope a monthly cadence around your pipeline: the mix of landing pages, location pages, and improvement work you actually have. Capacity is planned in advance so client work can be scheduled with confidence."),
 ("Who leads the work?","Riz leads conversion strategy and final quality review on every engagement, supported by a specialist copy, design, and development team. You get one accountable point of contact."),
 ("Can you work from our briefs and designs?","Yes. We can execute from your briefs and designs, or handle strategy, copy, and design end to end. Most partnerships mix both depending on the client and the month."),
 ("Which platforms do you build on?","Webflow, WordPress, Shopify, HighLevel, Unbounce, ClickFunnels, HubSpot, Wix, and more. We build where the client's site already lives, so there's no migration to sell them."),
 ("Where are you based, and how do time zones work?", D["SITE"]["coverage"] + " " + D["SITE"]["availability"])]
m += faq_section(agfaq, title='Partnership <span class="mute">questions</span>', tone=" mist")
page("agency-partners.html", "Agency Partners · PageDriven", "White-label landing pages, location pages, website production, UX improvements, and ongoing client-site support for SEO, PPC, and digital agencies.", "agency", m,
     cta=dict(title_html='Start a partnership <span class="mute">conversation.</span>', body="Tell us about your client load and the work you'd hand over. No commitment, just a short call to see whether the fit is there.", btn=AC["primary"], service=AC["service"]), main_cls="pg-tight")

# =====================================================================
# WORK INDEX
# =====================================================================
copy = (crumbs(("Work", None)) + '<span class="eyebrow g-in">Client work</span>'
  '<h1 class="g-in">Real pages, <span class="mute">built for real offers.</span></h1>'
  '<p class="lede g-in">Projects across industries and platforms. Open any card for the goal, the problem and what we changed.</p>')
filters = "".join(f'<button type="button" data-filter="{f["key"]}" aria-pressed="{"true" if f["key"]=="all" else "false"}">{e(f["label"])}</button>' for f in D["WORK_FILTERS"])
m = phero(copy, center=True)
wcards = "".join(wcard(w["slug"], f' data-service="{w["service"]}"') for w in WORK)
empty = '<p class="wempty" hidden>No case studies in this category yet. <button type="button" class="tlink" data-filter-reset>See all work <span>→</span></button></p>'
# filter tabs sit directly above the grid they filter
m += f'<section class="band wk-list" aria-label="Case studies"><div class="wrap"><div class="filters" data-for="wlist" role="group" aria-label="Filter case studies">{filters}</div><div class="wgrid stagger" id="wlist">{wcards}</div>{empty}</div></section>'
m += testimonial_wall()
m += inline_review(eyebrow="Your page next", title='Want this kind of thinking <span class="mute">on your page?</span>', tone=" mist")
page("work.html", "Client Work · PageDriven", "Case studies from landing pages and websites built across healthcare, ecommerce, media, education and local service businesses.", "work", m)

# =====================================================================
# CASE STUDIES
# =====================================================================
def svc_card_band(slug):
    s = SVC[slug]
    return f'''<section class="band mist" aria-label="Related service" style="padding-block:clamp(48px,5.5vw,76px)">
  <div class="wrap"><div class="card svc-band reveal">
    <img src="{IMG[SVC_META[slug][1]]}" alt="" width="88" height="88">
    <div style="display:grid;gap:6px"><span class="k-lbl">Service used</span><h2 style="font-size:clamp(22px,2.4vw,30px)">{e(s["name"])}</h2><p>{e(s["short"])}</p></div>
    <div class="btn-row"><a class="btn btn-primary" href="{slug}.html">See the service {ARROW}</a><a class="btn btn-ghost" href="work.html">All client work</a></div>
  </div></div>
</section>'''

def case_hero(w, eyebrow, h1, lede, extra_btn=True, visual=None):
    live = f'<a class="btn btn-ghost" href="{e(w["url"])}" target="_blank" rel="noopener nofollow">View live page ↗</a>' if w.get("url") else ""
    copy = (crumbs(("Work", "work.html"), (w["client"] if not w["client"].startswith("Confidential") else WART[w["slug"]]["name"], None)) +
      f'<span class="eyebrow g-in">{e(eyebrow)}</span><h1 class="g-in">{h1}</h1><p class="lede g-in">{e(lede)}</p>'
      f'<div class="btn-row g-in"><button class="btn btn-primary" data-open-review>Get My Free Page Review {ARROW}</button>{live}</div>')
    if visual is None:
        visual = f'<div class="wthumb" style="aspect-ratio:4/3.4;border-radius:24px;box-shadow:0 40px 80px -40px rgba(11,37,69,.5)"><canvas data-art="{art_attr(w["slug"])}" aria-hidden="true"></canvas>{wordmark(w["slug"])}</div>'
    return phero(copy, visual, badges=False)

def quote_band(t_quote, name, role, c, i, note=None, fx="dots"):
    n = f'<p class="note-sm">{e(note)}</p>' if note else ""
    return f'''<section class="band night" aria-label="Client testimonial">
  <canvas class="bgfx" data-fx="{fx}" aria-hidden="true"></canvas>
  <div class="wrap"><figure class="quote-xl reveal" style="margin:0 auto"><div class="qm" aria-hidden="true">“</div><blockquote>{e(t_quote)}</blockquote>{who(name, role, c, i)}{n}</figure></div>
</section>'''

LOCK = '<svg width="10" height="10" viewBox="0 0 16 16" aria-hidden="true"><rect x="3" y="7" width="10" height="7" rx="1.5" fill="currentColor"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'
def shot_frame(src, alt, label, w, h, tall=False):
    """Single live-site screenshot in a browser frame (no before/after available). Tall pages pan slowly."""
    ar = "4/4.3" if tall else f"{w}/{h}"
    return (f'<figure class="shotcard{" tall" if tall else ""}">'
            f'<div class="sc-bar" aria-hidden="true"><i></i><i></i><i></i><span class="sc-url">{LOCK}{e(label)}</span></div>'
            f'<div class="sc-view" style="aspect-ratio:{ar}"><img src="{src}" alt="{e(alt)}" width="{w}" height="{h}"></div></figure>')

CASE_SHOTS = {
 "one10-driving-school": shot_frame("assets/img/one10-site.webp", "One10 Driving School homepage: Learn to Drive with Confidence, from first lesson to test day", "one10drivingschool.com", 862, 1489, tall=True),
 "rset-wellness": shot_frame("assets/img/rset-site.webp", "RSET Flow product page: Boost Focus + Energy for up to 70% off", "getrset.com", 1400, 796),
 "stain-guys": shot_frame("assets/img/stainguys-site.webp", "Fence staining landing page: See Every Color. Pick Your Perfect Stain.", "Live landing page", 1400, 959),
 "outdoor-living-remodeling": compare_mock("Before · Original website", "After · Redesign", "Homepage · Phased Elementor redesign", shots=(("assets/img/outdoor-before.webp", "Remodeling client homepage before: Custom Hardscaping Design and Installation in Naperville"), ("assets/img/outdoor-after.webp", "Remodeling client homepage after: Custom Outdoor Living and Landscape Transformations"))),
 "lourcey-photography": compare_mock("Before · Original Webflow page", "After · Redesign", "Lourcey Photography · Webflow redesign", shots=(("assets/img/lourcey-before.webp", "Lourcey Photography before: Senior Portrait Photography in Dallas and Plano"), ("assets/img/lourcey-after.webp", "Lourcey Photography after: Portraiture Elevated Into Fine Art"))),
}
# ---- generic case studies ----
for w in WORK:
    if w["slug"] in ("caseleap", "frisco-spinal-rehab", "levitate-media"): continue
    title = mute(w["title"], w["titleHighlight"]) if w["titleHighlight"] != w["title"] else e(w["title"])
    m = case_hero(w, w["category"] + " case study", title, w["clientContext"], visual=CASE_SHOTS.get(w["slug"]))
    m += f'<section class="band" style="padding-block:0 24px"><div class="wrap">{meta_dl([("Client", w["client"]), ("Traffic source", w["trafficSource"]), ("Conversion goal", w["goal"]), ("Platform", w["platform"])])}</div></section>'
    secs = [("problem", "The original problem", f'<p class="prose">{e(w["originalProblem"])}</p>'),
            ("before-after", "Before and after", ba(w["beforeState"], w["afterState"])),
            ("strategy", "Strategy", f'<p class="prose" style="font-size:19px;color:var(--ink)">{e(w["strategy"])}</p>'),
            ("changes", "Changes implemented", '<ul class="checklist cards stagger">' + "".join(f"<li>{e(c)}</li>" for c in w["changes"]) + "</ul>"),
            ("measurement", "Measurement and outcome", f'<div class="note"><span class="tile">{icon("info")}</span><div><p>{e(w["measurement"])}</p></div></div>')]
    toc = "".join(f'<a href="#{sid}"{ON if k==0 else ""}>{e(t)}</a>' for k, (sid, t, _) in enumerate(secs))
    body = "".join(f'<section id="{sid}"><span class="eyebrow">{k+1:02d}</span><h2>{e(t)}</h2>{c}</section>' for k, (sid, t, c) in enumerate(secs))
    m += f'<section class="band" style="padding-top:64px"><div class="wrap doc"><nav class="toc" aria-label="On this page">{toc}</nav><div class="doc-body">{body}</div></div></section>'
    t = find_testi(w["testimonialName"]) if w.get("testimonialName") else None
    if t:
        c, i = TILE.get(t["name"], ("#5452F6", "PD"))
        m += quote_band(t["quote"], t["name"], t["role"], c, i)
    m += svc_card_band(w["service"])
    page(f'work-{w["slug"]}.html', f'{WART[w["slug"]]["name"]} Case Study · PageDriven', w["problem"], "work", m)

# ---- CaseLeap ----
w = WBY["caseleap"]
m = case_hero(w, "B2B Video Services · Ongoing CRO", 'From a 3-second glance to an <span class="mute">18-second visit.</span>',
  "CaseLeap, a B2B testimonial video production company serving US marketing teams, was already attracting visitors, but the homepage was losing them within seconds. We used GA4 and Microsoft Clarity to identify where attention was being lost, then refined the message, surfaced proof earlier, clarified the CTA hierarchy, and reduced conversion friction.",
  visual=compare_mock("Before · Original homepage", "After · CRO iteration", "CaseLeap homepage · Iteration 1", shots=(("assets/img/caseleap-before.webp", "CaseLeap homepage before: Testimonial Video Production for B2B Teams"), ("assets/img/caseleap-after.webp", "CaseLeap homepage after: Turn Customer Stories Into Real Business Results"))))
m += f'''<section class="band" style="padding-block:0 32px"><div class="wrap" style="display:grid;gap:16px">
  {meta_dl([("Client","CaseLeap"),("Traffic","US organic and referral"),("Platform","Webflow"),("Primary conversion","Custom quote requests and strategy calls"),("Scope","Ongoing CRO & UX optimization across the homepage, campaign pages, service pages and pricing journey")], wide_last=True)}
  <div class="metrics stagger">
    <div class="metric"><span class="big" data-count="6" data-suffix="×">6×</span><b>Longer average time on the homepage</b><small>3 seconds → 18 seconds</small></div>
    <div class="metric"><span class="big" data-count="45" data-prefix="+" data-suffix="%">+45%</span><b>More events per homepage visit</b><small>3.34 → 4.84</small></div>
    <div class="metric"><span class="big" data-count="45" data-prefix="−" data-suffix="%">−45%</span><b>Fewer quick backs</b><small>21.4% → 11.8%</small></div>
  </div>
</div></section>'''
m += f'''<section class="band" aria-labelledby="h-ch">
  <div class="wrap">
    <div class="split-lr"><div class="sticky"><span class="eyebrow">The challenge</span><h2 id="h-ch" class="h2" style="font-size:clamp(30px,3.4vw,44px)">Good traffic was slipping away <span class="mute">before the message could land.</span></h2></div>
    <p class="prose reveal">CaseLeap was already attracting the right visitors: US marketing teams looking for testimonial video production. But the homepage was losing them within seconds. The message, proof and next step weren't landing fast enough to hold attention.</p></div>
    <div class="sec-head mt-l"><span class="eyebrow">What the data showed</span></div>
    {cards([("eye","Visitors left within seconds","Homepage visitors averaged 3 seconds before leaving. The message, proof and next step weren't landing fast enough."),("trophy","Proof sat too low","Trust signals and testimonials were far below the fold, long after visitors had formed their first impression."),("pointer","Competing calls to action","The primary CTA competed with equally weighted alternatives, splitting attention at the decision point."),("form","Form friction","Forms added avoidable effort at the moment visitors were ready to act."),("phone","Mobile conversion friction","The mobile experience added extra friction at the decision point.")])}
  </div>
</section>'''
m += f'''<section class="band mist" aria-labelledby="h-st">
  <div class="bgfx gridbg" aria-hidden="true"></div>
  <div class="wrap split-lr">
    <div class="sticky"><span class="eyebrow">The strategy</span><h2 id="h-st" class="h2" style="font-size:clamp(30px,3.4vw,44px)">Let behavior data <span class="mute">decide what changes first.</span></h2><p class="lede" style="font-size:17px">Rather than redesigning on instinct, every decision was grounded in what GA4 and Microsoft Clarity showed about real visitor behavior on the page.</p></div>
    {steps(["Use GA4 and Microsoft Clarity to find where the homepage loses attention.","Refine the message so the value is clear within the first few seconds.","Surface proof earlier, closer to the headline and decision points.","Clarify the CTA hierarchy so the primary action stands out.","Reduce conversion friction in forms and the mobile experience."], titled=False)}
  </div>
</section>'''
m += f'''<section class="band" aria-labelledby="h-ba">
  <div class="wrap" style="display:grid;gap:32px">
    <div class="sec-head"><span class="eyebrow">Before and after</span><h2 id="h-ba" class="h2" style="font-size:clamp(30px,3.4vw,44px)">What changed <span class="mute">on the homepage.</span></h2></div>
    {ba(w["beforeState"], w["changes"])}
    <div class="chips">{"".join(f"<span>{x}</span>" for x in ["CRO &amp; UX Analysis","GA4 + MS Clarity Insights","Conversion Copy","Homepage UX Redesign","Webflow Implementation"])}</div>
  </div>
</section>'''
m += f'''<section class="band night" aria-labelledby="h-out">
  <canvas class="bgfx" data-fx="dots" aria-hidden="true"></canvas>
  <div class="wrap" style="display:grid;gap:40px">
    <div class="sec-head center"><span class="eyebrow">Outcome</span><h2 id="h-out" class="h2">Engagement moved decisively <span class="mute">in the right direction.</span></h2>
      <p class="lede">In the measured period after Iteration 1, average time on the homepage rose from 3 seconds to 18 seconds, events per homepage visit rose from 3.34 to 4.84, and quick backs fell from 21.4% to 11.8%. The homepage now holds attention long enough for the proof, the message and the next step to do their job.</p></div>
    <div class="metrics stagger">
      <div class="metric"><span class="big">6×</span><b>Time on homepage</b><small>3s → 18s</small></div>
      <div class="metric"><span class="big">+45%</span><b>Events per visit</b><small>3.34 → 4.84</small></div>
      <div class="metric"><span class="big">−45%</span><b>Quick backs</b><small>21.4% → 11.8%</small></div>
    </div>
    <figure class="quote-xl reveal" style="margin:0 auto"><div class="qm" aria-hidden="true">“</div><blockquote>{e(TESTI[0]["q"])}</blockquote>{who("Andrew","CaseLeap (company of Levitate Media), Founder","#12345E","CL")}
    <p class="note-sm">Results compare US traffic before and after Iteration 1, measured in GA4 and Microsoft Clarity. No controlled experiment was run; figures describe observed behavior during the measured period.</p></figure>
  </div>
</section>'''
m += svc_card_band("ongoing-optimization")
page("work-caseleap.html", "CaseLeap CRO Case Study · PageDriven", "See how GA4 and Microsoft Clarity insights reshaped the CaseLeap homepage, and how engagement changed in the measured period after Iteration 1.", "work", m,
     cta=dict(title_html='Is your page losing visitors <span class="mute">in the first few seconds?</span>', body="Send us your page. We'll show you where attention drops, and what to change first."))

# ---- Frisco ----
w = WBY["frisco-spinal-rehab"]
m = case_hero(w, "Healthcare · Google Ads Landing Page", 'Turning a treatment-first funnel into a <span class="mute">patient-first conversion journey.</span>',
  "Frisco Spinal Rehab was sending high-intent Google Ads traffic to a spinal decompression funnel. We audited the landing and scheduling experience, then rebuilt it around patient concerns, credible proof, a consistent offer and a clearer path to submitting the form.",
  visual=compare_mock("Before · Original funnel", "After · Patient-first page", "Spinal decompression funnel · GoHighLevel", shots=(("assets/img/frisco-before.webp", "Frisco Spinal Rehab page before: Avoid Surgery and Improve Your Life with the DRX9000"), ("assets/img/frisco-after.webp", "Frisco Spinal Rehab page after: Still in Pain After PT, Injections, or Medication?"))))
m += f'<section class="band" style="padding-block:0 32px"><div class="wrap">{meta_dl([("Client","Frisco Spinal Rehab"),("Traffic","Google Ads"),("Platform","GoHighLevel"),("Primary conversion","Form submission"),("Scope","CRO audit, conversion copy, UX/UI redesign, landing-page build and MS Clarity setup")], wide_last=True)}</div></section>'
m += f'''<section class="band" aria-labelledby="h-ch">
  <div class="wrap">
    <div class="split-lr"><div class="sticky"><span class="eyebrow">The challenge</span><h2 id="h-ch" class="h2" style="font-size:clamp(30px,3.4vw,44px)">High-intent patients needed reassurance <span class="mute">before being asked to act.</span></h2></div>
    <div class="prose reveal"><p>The ads targeted people searching for spinal decompression, herniated discs, sciatica, pinched nerves, stenosis, persistent back or arm pain and failed back surgery.</p><p>Many visitors had already tried physical therapy, injections or medication. The funnel needed to acknowledge that frustration, establish credibility and make the next step feel clear and reassuring.</p></div></div>
    <div class="sec-head mt-l"><span class="eyebrow">Audit findings</span><h2 class="h2" style="font-size:clamp(26px,2.8vw,36px)">Where the funnel <span class="mute">was losing momentum.</span></h2></div>
    {cards([("cross","Treatment before the patient","The headline led with the DRX9000 machine before connecting with what the patient was experiencing."),("shield","Missing trust signals","The clinic's 5-star reputation and 400+ patient reviews were not visible on the paid-traffic page."),("dollar","Conflicting offer language","“$49 Session” and “Secure My Free Session” appeared in the same journey."),("timer","Misplaced urgency","The scarcity message appeared while visitors were still looking for information."),("calx","Abrupt scheduling handoff","Visitors moved from the landing page to a bare calendar without sufficient context or reassurance."),("help","Uncertain confirmation language","“This is not a confirmed appointment” introduced doubt at the moment of commitment.")])}
  </div>
</section>'''
flow = "".join(f"<li><span>{e(x)}</span></li>" for x in ["Google search intent","Patient-first message","Relevant proof","Consistent offer","What-to-expect reassurance","Form submission","Clear confirmation"])
m += f'''<section class="band mist" aria-labelledby="h-st">
  <div class="bgfx gridbg" aria-hidden="true"></div>
  <div class="wrap" style="display:grid;gap:48px">
    <div class="split-lr">
      <div class="sticky"><span class="eyebrow">The strategy</span><h2 id="h-st" class="h2" style="font-size:clamp(30px,3.4vw,44px)">Align the ad, the patient's concern <span class="mute">and one clear next step.</span></h2></div>
      {steps(["Lead with the patient's pain, concerns and previous attempts, not the machine.","Match the page message with high-intent Google searches.","Bring review proof closer to the headline, form and scheduling decision.","Use one consistent offer and CTA throughout the funnel.","Explain what happens during the consultation and what happens after submission.","Keep the form or calendar within the persuasive context of the landing page.","Install MS Clarity to support ongoing behavior-based optimization."], titled=False)}
    </div>
    <div class="card reveal" style="padding:28px;gap:16px"><span class="k-lbl">The conversion flow</span><ol class="flow">{flow}</ol></div>
  </div>
</section>'''
m += f'''<section class="band" aria-labelledby="h-ba">
  <div class="wrap" style="display:grid;gap:32px">
    <div class="sec-head"><span class="eyebrow">Before and after</span><h2 id="h-ba" class="h2" style="font-size:clamp(30px,3.4vw,44px)">From machine-first messaging <span class="mute">to a more reassuring patient journey.</span></h2></div>
    {ba(w["beforeState"], w["changes"])}
  </div>
</section>'''
m += f'''<section class="band night" aria-labelledby="h-out">
  <canvas class="bgfx" data-fx="dots" aria-hidden="true"></canvas>
  <div class="wrap" style="display:grid;gap:40px">
    <div class="sec-head center"><span class="eyebrow">Outcome</span><h2 id="h-out" class="h2">A major page upgrade, <span class="mute">and a funnel ready to learn.</span></h2>
      <p class="lede">The completed page created a clearer, more professional experience for people making a serious healthcare decision. It aligned the campaign message with patient intent, strengthened trust around the form journey and established the tracking foundation needed for continued optimization.</p></div>
    <figure class="quote-xl reveal" style="margin:0 auto"><div class="qm" aria-hidden="true">“</div><blockquote>The landing page he built for us has been a major upgrade, and he went above and beyond integrating MS Clarity for tracking and optimization. Nothing but positive things to say.</blockquote>{who("Dr. David Kaff","Frisco Spinal Rehab, TX","#3A9FD6","FS")}
    <p class="note-sm">This case study documents the strategy, redesign and client-verified delivery. No numerical conversion lift is presented because a controlled pre/post dataset was not available.</p></figure>
    <div class="chips" style="justify-content:center">{"".join(f"<span>{x}</span>" for x in ["CRO Audit","Conversion Copy","UX/UI Redesign","GoHighLevel Build","MS Clarity Setup"])}</div>
  </div>
</section>'''
m += svc_card_band("landing-pages")
page("work-frisco-spinal-rehab.html", "Frisco Spinal Rehab Case Study · PageDriven", "How PageDriven rebuilt a Google Ads landing-page funnel for Frisco Spinal Rehab around patient intent, trust, offer clarity and form submissions.", "work", m,
     cta=dict(title_html='Let\'s find where your funnel is <span class="mute">losing momentum.</span>', body="Send us your landing page and ad message. We'll identify the highest-impact opportunities across positioning, proof, offer clarity and conversion flow.", btn="Get My Free Audit Report"))

# ---- Levitate ----
w = WBY["levitate-media"]
m = case_hero(w, "Video Production · Multi-Page CRO", 'Using visitor behavior <span class="mute">to strengthen six service pages.</span>',
  "Levitate Media already had a mature service-page system with strong work samples, proof and process content. Visitor behavior across six pages was analyzed to identify which elements consistently earned attention, which valuable sections were being overlooked, and where targeted UX and CRO refinements could make the experience easier to evaluate and act on.",
  visual=compare_mock("Before · Original page", "After · CRO prototype", "Service page · Recommended framework", shots=(("assets/img/levitate-before.webp", "Levitate explainer video service page before"), ("assets/img/levitate-after.webp", "Levitate explainer video service page after: Explainer Videos That Make Your Value Obvious"))))
m += f'<section class="band" style="padding-block:0 32px"><div class="wrap">{meta_dl([("Client","Levitate Media"),("Engagement","Behavioral UX & CRO Review"),("Coverage","Six service pages"),("Evidence","Visitor recordings and attention patterns"),("Deliverables","Prioritized recommendations, recommended page framework and interface concepts")], wide_last=True)}</div></section>'
m += f'''<section class="band" aria-labelledby="h-ch">
  <div class="wrap">
    <div class="split-lr"><div class="sticky"><span class="eyebrow">The challenge</span><h2 id="h-ch" class="h2" style="font-size:clamp(30px,3.4vw,44px)">The pages were strong. <span class="mute">The opportunity was to make the strongest content work harder.</span></h2></div>
    <p class="prose reveal">Visitor behavior showed a clear preference for visual proof, particularly video examples, case studies and the production process. The opportunity was not to rebuild the page system, but to give these high-value elements greater prominence, reduce avoidable friction and improve how visitors moved toward a quote request.</p></div>
    <div class="sec-head mt-l"><span class="eyebrow">Key findings</span></div>
    {cards([("video","Video examples led attention","Work samples consistently attracted the strongest engagement, showing that buyers wanted to evaluate production quality early."),("play","Video case studies strengthened proof","On the 2D and 3D pages, video case studies aligned naturally with how visitors preferred to assess the work."),("layers","The process remained valuable","The production-process timeline continued to earn attention even when it appeared further down the page."),("search","Useful content was sometimes buried","FAQs and other decision-support content received meaningful engagement when visitors reached it, suggesting an opportunity to improve discoverability."),("pointer","CTA treatment could be tightened","CTA wording and width varied across some pages, creating an opportunity for more consistent presentation."),("shieldcheck","Trust deserved stronger presentation","Existing client volume, ratings and recognizable logos could be surfaced in a more concise and visually prominent trust strip.")])}
  </div>
</section>'''
m += f'''<section class="band mist" aria-labelledby="h-seq">
  <div class="bgfx gridbg" aria-hidden="true"></div>
  <div class="wrap split-lr">
    <div class="sticky"><span class="eyebrow">Recommended page sequence</span><h2 id="h-seq" class="h2" style="font-size:clamp(30px,3.4vw,44px)">Turning behavioral patterns <span class="mute">into a clearer page journey.</span></h2><p class="lede" style="font-size:17px">The audit translated recurring attention patterns into a recommended page sequence. This was an optimization framework based on observed behavior, not a correction of inconsistent page structures.</p><p class="note-sm">Individual recommendations still varied by page according to visitor behavior and content performance.</p></div>
    {steps(["Hero with clear value proposition, trust and relevant metrics","Filterable video examples","Scannable reasons-to-choose section","Production-process timeline","Video case studies","Featured testimonial","Lead form","FAQs","Final CTA"], titled=False)}
  </div>
</section>'''
recs = "".join(f"<li>{e(x)}</li>" for x in ["Feature the strongest video examples first instead of displaying too many simultaneously.","Add industry filters to make relevant work easier to find.","Make video examples manageable through the CMS.","Redesign dense text sections into more scannable cards supported by relevant visuals.","Give the pink/red brand palette a more intentional role in calls to action and emphasis.","Use a curated set of recognizable logos rather than an oversized logo collection.","Consider section-aware navigation to improve access to FAQs, case studies and other valuable lower-page content.","Preserve high-performing elements such as the process timeline and featured testimonial."])
m += f'''<section class="band" aria-labelledby="h-rec">
  <div class="wrap"><div class="sec-head"><span class="eyebrow">Recommendations</span><h2 id="h-rec" class="h2" style="font-size:clamp(30px,3.4vw,44px)">Evidence-led refinements <span class="mute">for emphasis, scannability and trust.</span></h2></div>
  <ul class="checklist cards stagger mt-l" style="grid-template-columns:1fr 1fr;display:grid">{recs}</ul></div>
</section>'''
m += f'''<section class="band night" aria-labelledby="h-out">
  <canvas class="bgfx" data-fx="dots" aria-hidden="true"></canvas>
  <div class="wrap" style="display:grid;gap:40px">
    <div class="sec-head center"><span class="eyebrow">Outcome</span><h2 id="h-out" class="h2">From behavioral evidence <span class="mute">to a prioritized optimization roadmap.</span></h2>
      <p class="lede">Levitate received a cross-page CRO plan grounded in the sections visitors were already engaging with. The recommendations preserved the existing strengths of the service pages while improving emphasis, scannability, trust presentation, CTA treatment and access to valuable lower-page content.</p></div>
    <figure class="quote-xl reveal" style="margin:0 auto"><div class="qm" aria-hidden="true">“</div><blockquote>{e(TESTI[0]["q"])}</blockquote>{who("Andrew","Levitate Media, Founder","#5452F6","LM")}
    <p class="note-sm">This case study documents the audit evidence and recommended strategy. No conversion-lift percentage is shown because verified post-implementation performance data was not supplied.</p></figure>
  </div>
</section>'''
m += svc_card_band("cro-audits")
page("work-levitate-media.html", "Levitate Media Case Study · PageDriven", "How visitor behavior across six Levitate Media service pages was analyzed and turned into an evidence-led optimization roadmap.", "work", m,
     cta=dict(title_html='Let\'s find where your pages are <span class="mute">losing momentum.</span>', body="Send us your page. We'll identify the highest-impact opportunities across message, structure, proof and conversion flow."))

# =====================================================================
# BOOK
# =====================================================================
copy = (crumbs(("Book a call", None)) + '<span class="eyebrow g-in">Book a call</span>'
  '<h1 class="g-in">Let\'s talk about the page between <span class="mute">your ad and your customer.</span></h1>'
  '<p class="lede g-in">The fastest start is to send the page first. Riz reviews it before the call, so the conversation begins with specifics instead of introductions.</p>'
  f'<p class="fine g-in">{e(D["SITE"]["coverage"])}</p>'
  f'<div class="btn-row g-in"><a class="btn btn-primary" href="#review-form">Send my page first {ARROW}</a><button class="btn btn-ghost" type="button" data-open-contact>{icon("mail")} Message us to arrange a time</button></div>')
vis = f'''<div class="pvis-card" style="padding:28px;display:grid;gap:16px">
  <div style="display:flex;align-items:center;gap:12px"><img src="{IMG["AVATAR"]}" alt="" width="48" height="48" style="border-radius:50%"><div><b style="color:var(--ink);font-weight:600">Riz · PageDriven</b><div style="font-size:13px;color:var(--ink-3)">Replies during US business hours</div></div></div>
  {steps([("Send the page","Share the URL and what it should get you more of."),("Riz reviews it","Where it loses momentum and the three fixes worth doing first."),("The call starts with specifics","No introductions-only call. You talk through the findings.")])}
</div>'''
m = phero(copy, vis)
m += inline_review()
m += testimonial_wall()
page("book.html", "Book a Call · PageDriven", "Talk through your traffic, your offer, and what your page needs to do. Send your page for a free review or message us to arrange a call.", "book", m, final=False)

# =====================================================================
# LEGAL
# =====================================================================
def legal(fname, title, intro, secs, kind):
    copy = crumbs((title, None)) + f'<span class="eyebrow g-in">Legal</span><h1 class="g-in">{e(title)}</h1><p class="lede g-in">{e(intro)}</p><p class="fine g-in">Last updated October 2026</p>'
    m = f'<section class="phero"><canvas data-wave="soft" aria-hidden="true"></canvas><div class="wrap"><div class="phero-copy" style="max-width:760px">{copy}</div></div></section>'
    secs = secs + [("Contact", None)]
    toc = "".join(f'<a href="#s{i}"{ON if i==0 else ""}>{e(h)}</a>' for i, (h, _) in enumerate(secs))
    body = ""
    for i, (h, p) in enumerate(secs):
        if p is None:
            p_html = f'<p>Questions about this {kind}? Email us.</p><div class="mailbox"><code id="mail">hello@pagedriven.com</code><button class="copy" type="button" data-copy="hello@pagedriven.com" data-copy-el="mail">Copy</button></div>'
        else: p_html = f"<p>{e(p)}</p>"
        body += f'<section id="s{i}"><h2>{e(h)}</h2>{p_html}</section>'
    m += f'<section class="band" style="padding-top:32px"><div class="wrap doc"><nav class="toc" aria-label="On this page">{toc}</nav><div class="doc-body">{body}</div></div></section>'
    page(fname, f"{title} · PageDriven", intro, "", m, final=False)
legal("privacy.html", "Privacy Policy", "This policy explains what PageDriven collects through this website and what we do with it.", [
 ("Information we collect","When you submit a form on this site we collect the details you provide: your name, email address, the page URL you want reviewed, any ad copy or link you share, and a description of what you are trying to improve. We do not ask for payment details through this website."),
 ("How we use it","We use your details to prepare and send the review or response you asked for, and to follow up about that enquiry. We do not sell your information or share it with third parties for marketing."),
 ("Analytics","We use Microsoft Clarity to understand how visitors use this site. It records aggregated usage and interaction data such as pages viewed, clicks, and scrolling. This helps us improve the site and is not used to identify you personally."),
 ("Storage and processing","Form submissions are stored in our secured database and emailed to us so we can respond. Access is limited to PageDriven personnel who need it to handle your enquiry."),
 ("Retention","We keep enquiry records for as long as needed to respond and maintain our business records. You can ask us to delete your details at any time."),
 ("Your choices","You can request a copy of the information we hold about you, ask us to correct it, or ask us to delete it. Email us and we will action the request.")], "policy")
legal("terms.html", "Terms of Service", "These terms apply to your use of the PageDriven website.", [
 ("Using this site","This website describes PageDriven's services. Content is provided for information only and may change without notice."),
 ("Enquiries and free reviews","Submitting a form does not create a contract. A free page review is provided as a good-faith professional opinion. It is not a guarantee of results, and acting on it is your decision."),
 ("Engagements","Paid work is governed by the written scope, timeline, and terms agreed for that specific engagement. Where those terms conflict with this page, the engagement terms apply."),
 ("Intellectual property","The PageDriven name, logo, site content, and case study material belong to PageDriven. Deliverables created for a client transfer according to the engagement agreement."),
 ("Third-party platforms","We often build inside platforms you already license, such as Webflow, WordPress, Shopify, Unbounce, ClickFunnels, HighLevel, HubSpot, and Wix. Your use of those platforms remains subject to their own terms."),
 ("Limitation of liability","To the extent permitted by law, PageDriven is not liable for indirect or consequential losses arising from use of this website or reliance on its content.")], "terms")

print(len(PAGES), "pages:", ", ".join(PAGES))
