#!/usr/bin/env python3
"""Build pattiep.com from content.json.

Run:  python3 build.py
Writes index.html and privacy.html next to this file. Every word comes from
content.json, so the pages are plain HTML that any browser, search engine or
AI crawler can read without running JavaScript. Refuses to build if any
"NEEDED" marker or empty required field is left in the content.
"""
import html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(HERE, "content.json"), encoding="utf-8"))
e = html.escape


def guard(obj, path="content"):
    """Fail the build on placeholders or blank required text."""
    problems = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not k.startswith("_"):
                problems += guard(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            problems += guard(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        if re.search(r"[A-Z]+ NEEDED\]|NEEDED\]|\[FILL|\bTODO\b", obj) or re.search(r"lorem ipsum", obj, re.I):
            problems.append(f"{path} still has a placeholder: {obj[:60]}")
        if not obj.strip():
            problems.append(f"{path} is empty")
    return problems


bad = guard(C)
if len(C['site']['description']) > 160:
    bad.append(f"site.description is {len(C['site']['description'])} characters; keep it at 160 or less so Google shows all of it")
if bad:
    print("NOT BUILT. Fix these in content.json first:\n  " + "\n  ".join(bad))
    sys.exit(1)

A, S = C["agent"], C["site"]

CSS = """
:root{--ink:#1A1A1A;--paper:#FFFFFF;--soft:#F5F5F3;--red:#D1242A;--red-dark:#A81C21;--navy:#1F2A44;
--gray:#3d3d3d;--line:#DADAD6;--serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
--sans:-apple-system,BlinkMacSystemFont,"Helvetica Neue",Helvetica,Arial,sans-serif}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:18px;line-height:1.65}
img{max-width:100%;height:auto;display:block}
a{color:var(--navy)}
a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible{outline:3px solid var(--navy);outline-offset:3px}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
.narrow{max-width:680px}
section{padding:72px 0}
.label{font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:var(--navy);font-weight:700}
h1,h2,h3{font-family:var(--serif);font-weight:400;line-height:1.12;text-wrap:balance}
h1{font-size:clamp(38px,6.4vw,64px);margin:12px 0 16px}
h2{font-size:clamp(30px,4.6vw,44px);margin:10px 0 20px}
p{max-width:65ch}
.btn{display:inline-block;text-decoration:none;font-weight:700;font-size:18px;padding:15px 28px;border-radius:4px;border:2px solid var(--navy);color:var(--navy);background:transparent;cursor:pointer;text-align:center}
.btn.primary{background:var(--red);border-color:var(--red);color:#fff}
.btn.primary:hover{background:var(--red-dark);border-color:var(--red-dark)}
.btns{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px}

/* header */
.top{border-bottom:1px solid var(--line);background:var(--paper)}
.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-top:12px;padding-bottom:12px}
.top img{height:44px;width:auto}
.top a.call{font-weight:700;text-decoration:none;color:var(--ink);white-space:nowrap}
.top a.call span{color:var(--red)}

/* hero */
.hero{padding:56px 0 64px}
.hero .wrap{display:grid;grid-template-columns:1fr;gap:36px;align-items:center}
@media(min-width:880px){.hero .wrap{grid-template-columns:1.15fr .85fr}}
.hero .sub{font-size:21px;color:var(--gray)}
.hero ul{list-style:none;margin:22px 0 0}
.hero li{padding:7px 0 7px 28px;position:relative}
.hero li:before{content:"";position:absolute;left:3px;top:17px;width:10px;height:10px;background:var(--red);transform:rotate(45deg)}
.hero .reassure{font-family:var(--serif);font-style:italic;font-size:22px;margin-top:22px;color:var(--navy)}
.hero figure{width:100%;max-width:400px;justify-self:center}
.hero figure img{border-radius:50%;width:100%;height:auto;aspect-ratio:1/1;object-fit:cover;object-position:center 20%;border:6px solid var(--paper);box-shadow:0 0 0 2px var(--navy)}
.hero figcaption{text-align:center}
.hero figcaption{font-size:15px;color:var(--gray);margin-top:8px}

/* plan */
.plan{background:var(--navy);color:#fff}
.plan .label{color:#fff}
.plan p.intro{color:#EEF0F5;font-size:20px}
.steps{list-style:none;counter-reset:s;display:grid;grid-template-columns:1fr;gap:16px;margin-top:32px}
@media(min-width:760px){.steps{grid-template-columns:repeat(5,1fr)}}
.steps li{counter-increment:s;border-top:3px solid var(--red);padding-top:14px}
.steps li b{display:block;font-family:var(--serif);font-weight:400;font-size:24px;margin-bottom:6px}
.steps li b:before{content:counter(s) ". "}
.steps li span{color:#E3E6EE;font-size:17px}

/* reviews */
.reviews .grid{display:grid;grid-template-columns:1fr;gap:18px;margin-top:28px}
@media(min-width:760px){.reviews .grid{grid-template-columns:1fr 1fr}}
.review{border:1px solid var(--line);border-left:4px solid var(--red);padding:22px 22px 18px;border-radius:4px;background:var(--paper)}
.review blockquote{font-family:var(--serif);font-size:20px;line-height:1.45}
.review .who{margin-top:12px;font-weight:700}
.review .ctx{font-size:15px;color:var(--gray)}
.source{font-size:15px;color:var(--gray);margin-top:16px}

/* listing */
.listing{background:var(--soft)}
.card{display:grid;grid-template-columns:1fr;background:var(--paper);border:1px solid var(--line);border-radius:6px;overflow:hidden}
@media(min-width:760px){.card{grid-template-columns:1.1fr 1fr}}
.card img{width:100%;height:100%;min-height:240px;object-fit:cover}
.card .body{padding:28px}
.card .price{font-family:var(--serif);font-size:30px;margin:6px 0}
.card .facts{color:var(--gray)}

/* about */
.about .wrap{display:grid;grid-template-columns:1fr;gap:36px;align-items:start}
.about .wrap{max-width:760px}
.about p{margin-bottom:1em}

/* contact */
.contact{background:var(--soft)}
.contact .wrap{display:grid;grid-template-columns:1fr;gap:40px}
@media(min-width:880px){.contact .wrap{grid-template-columns:1fr 1fr}}
.contact .big{font-family:var(--serif);font-size:clamp(30px,5vw,40px);margin-top:18px}
.contact .big a{color:var(--ink);text-decoration:none}
.contact .mail{margin-top:6px}
form{background:var(--paper);border:1px solid var(--line);border-top:4px solid var(--red);border-radius:6px;padding:26px}
.field{margin-bottom:14px}
.field label{display:block;font-size:14px;font-weight:700;margin-bottom:5px}
.field input,.field textarea{width:100%;font:inherit;font-size:17px;padding:12px 13px;border:1px solid #9a9a95;border-radius:4px;background:#fff;color:var(--ink)}
.field textarea{min-height:110px;resize:vertical}
.consent{display:flex;gap:10px;align-items:flex-start;font-size:15px;color:var(--gray);margin:6px 0 16px}
.consent input{margin-top:4px;width:18px;height:18px;flex:none}
.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.status{margin-top:12px;font-weight:700}
.status.err{color:#B3261E}
.small{font-size:14px;color:var(--gray);margin-top:10px}

footer{background:var(--ink);color:#E6E6E6;font-size:14px;padding:36px 0 90px;line-height:1.8}
footer a{color:#fff}
footer .logos{display:flex;gap:22px;align-items:center;margin-bottom:16px;flex-wrap:wrap}
footer .logos img{height:40px;width:auto;background:#fff;padding:6px 10px;border-radius:4px}

.bar{position:fixed;left:0;right:0;bottom:0;display:flex;z-index:50;box-shadow:0 -6px 18px rgba(0,0,0,.18)}
.bar a{flex:1;text-align:center;padding:15px 8px calc(15px + env(safe-area-inset-bottom,0px));color:#fff;text-decoration:none;font-weight:700;background:var(--red)}
.bar a+a{background:var(--navy)}
@media(min-width:880px){.bar{display:none}}
"""


def head(title, desc, path, extra=""):
    url = S["url"] + path
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{e(url)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{e(S['url'] + S['share_image'])}">
<meta name="twitter:card" content="summary_large_image">
<style>{CSS}</style>
{extra}
</head>
<body>
<header class="top"><div class="wrap">
  <a href="{e(S['url'])}"><img src="images/pattie-logo.png" alt="Pattie, Committed to Your Success" width="126" height="44"></a>
  <a class="call" href="tel:{e(A['phone_tel'])}">Call or text <span>{e(A['phone_display'])}</span></a>
</div></header>
"""


def footer():
    L = C["legal"]
    return f"""<footer><div class="wrap">
  <div class="logos"><img src="images/pattie-logo.png" alt="Pattie, Committed to Your Success"><img src="images/exp-logo.png" alt="eXp Realty"></div>
  <div>{e(A['name'])}, {e(A['license'])} · {e(A['brokerage'])}, {e(A['brokerage_license'])}</div>
  <div>{e(A['phone_display'])} · <a href="mailto:{e(A['email'])}">{e(A['email'])}</a> · {e(A['area'])}</div>
  <div>{e(L['fair_housing'])} {e(L['disclaimer'])} <a href="privacy.html">Privacy policy</a></div>
</div></footer>
<nav class="bar" aria-label="Quick contact"><a href="tel:{e(A['phone_tel'])}">Call Pattie</a><a href="sms:{e(A['phone_tel'])}">Text Pattie</a></nav>
</body></html>
"""


def index():
    H, P, R, Li, Ab, Co = C["hero"], C["plan"], C["reviews"], C["listing"], C["about"], C["contact"]
    bullets = "".join(f"<li>{e(b)}</li>" for b in H["bullets"])
    steps = "".join(f"<li><b>{e(s['name'])}</b><span>{e(s['text'])}</span></li>" for s in P["steps"])
    reviews = "".join(
        f'<figure class="review"><blockquote>&ldquo;{e(r["quote"])}&rdquo;</blockquote>'
        f'<figcaption><div class="who">{e(r["name"])}</div><div class="ctx">{e(r["context"])}</div></figcaption></figure>'
        for r in R["items"])
    about = "".join(f"<p>{e(p)}</p>" for p in Ab["paragraphs"])
    ld = {
        "@context": "https://schema.org",
        "@type": "RealEstateAgent",
        "name": A["name"],
        "alternateName": A["business"],
        "url": S["url"],
        "image": S["url"] + Ab["image"],
        "telephone": A["phone_tel"],
        "email": A["email"],
        "description": S["description"],
        "areaServed": {"@type": "City", "name": "Petaluma, CA"},
        "address": {"@type": "PostalAddress", "addressLocality": "Petaluma", "addressRegion": "CA", "addressCountry": "US"},
        "parentOrganization": {"@type": "RealEstateOrganization", "name": A["brokerage"]},
        "slogan": A["tagline"],
        "knowsAbout": ["Downsizing", "Pre-listing inspections", "Preparing a home for sale", "Single-level homes"],
    }
    extra = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>"
    return head(S["title"], S["description"], "", extra) + f"""
<main>
<section class="hero"><div class="wrap">
  <div>
    <span class="label">{e(H['eyebrow'])}</span>
    <h1>{e(H['headline'])}</h1>
    <p class="sub">{e(H['subhead'])}</p>
    <ul>{bullets}</ul>
    <p class="reassure">&ldquo;{e(H['reassure'])}&rdquo;</p>
    <div class="btns">
      <a class="btn primary" href="tel:{e(A['phone_tel'])}">Call or text {e(A['phone_display'])}</a>
      <a class="btn" href="#plan">See how I work</a>
    </div>
  </div>
  <figure><img src="{e(Ab['image'])}" alt="{e(Ab['image_alt'])}" width="1300" height="946"><figcaption>{e(A['name'])} · {e(A['tagline'])}</figcaption></figure>
</div></section>

<section class="plan" id="plan"><div class="wrap">
  <span class="label">{e(P['eyebrow'])}</span>
  <h2>{e(P['headline'])}</h2>
  <p class="intro">{e(P['intro'])}</p>
  <ol class="steps">{steps}</ol>
</div></section>

<section class="reviews" id="reviews"><div class="wrap">
  <span class="label">{e(R['eyebrow'])}</span>
  <h2>{e(R['headline'])}</h2>
  <div class="grid">{reviews}</div>
  <p class="source">{e(R['source_note'])}</p>
</div></section>

<section class="listing" id="listing"><div class="wrap">
  <span class="label">{e(Li['eyebrow'])}</span>
  <h2>My current listing</h2>
  <div class="card">
    <img src="{e(Li['image'])}" alt="{e(Li['image_alt'])}" loading="lazy" width="1200" height="800">
    <div class="body">
      <h3 style="font-size:28px">{e(Li['address'])}</h3>
      <div class="facts">{e(Li['city'])}</div>
      <div class="price">{e(Li['price'])}</div>
      <div class="facts">{e(Li['facts'])}</div>
      <p style="margin-top:12px">{e(Li['text'])}</p>
      <div class="btns"><a class="btn" href="{e(Li['url'])}">See all the photos</a></div>
    </div>
  </div>
</div></section>

<section class="about" id="about"><div class="wrap">
  <div>
    <span class="label">{e(Ab['eyebrow'])}</span>
    <h2>{e(Ab['headline'])}</h2>
    {about}
  </div>
</div></section>

<section class="contact" id="contact"><div class="wrap">
  <div>
    <span class="label">{e(Co['eyebrow'])}</span>
    <h2>{e(Co['headline'])}</h2>
    <p>{e(Co['text'])}</p>
    <div class="big"><a href="tel:{e(A['phone_tel'])}">{e(A['phone_display'])}</a></div>
    <div class="mail"><a href="mailto:{e(A['email'])}">{e(A['email'])}</a></div>
    <div class="btns">
      <a class="btn primary" href="tel:{e(A['phone_tel'])}">Call Pattie</a>
      <a class="btn" href="sms:{e(A['phone_tel'])}">Text Pattie</a>
    </div>
  </div>
  <form id="contact-form" novalidate>
    <p style="margin-bottom:14px;font-weight:700">{e(Co['form_intro'])}</p>
    <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" type="text" autocomplete="name" required></div>
    <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
    <div class="field"><label for="f-phone">Phone (optional)</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
    <div class="field"><label for="f-msg">How can I help?</label><textarea id="f-msg" name="message"></textarea></div>
    <label class="consent"><input id="f-sms" name="sms_consent" type="checkbox" value="yes"><span>{e(Co['sms_consent'])}</span></label>
    <div class="hp" aria-hidden="true"><label for="f-bot">Leave this empty</label><input id="f-bot" name="botcheck" type="checkbox" tabindex="-1"></div>
    <button class="btn" type="submit" style="width:100%;background:var(--navy);color:#fff">Send to Pattie</button>
    <p id="f-status" class="status" role="status" aria-live="polite"></p>
    <p class="small">Goes straight to Pattie. See the <a href="privacy.html">privacy policy</a>.</p>
  </form>
</div></section>
</main>
<script>
(function(){{
  var f=document.getElementById('contact-form'),st=document.getElementById('f-status');
  var KEY={json.dumps(Co['web3forms_key'])},OK={json.dumps(Co['success'])},ERR={json.dumps(Co['error'])};
  f.addEventListener('submit',function(ev){{
    ev.preventDefault();
    if(f.dataset.busy==='1')return;
    function v(id){{return document.getElementById(id);}}
    var name=v('f-name').value.trim(),email=v('f-email').value.trim(),phone=v('f-phone').value.trim();
    st.className='status';
    if(!name||!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email)){{st.className='status err';st.textContent='Please add your name and a valid email.';return;}}
    if(v('f-bot').checked){{return;}}
    var consent=v('f-sms').checked;
    var body={{access_key:KEY,subject:'Website message from '+name,from_name:'pattiep.com',name:name,email:email,
      phone:consent?phone:(phone?'(given, but no permission to call or text)':''),
      sms_consent:consent?'yes':'no',message:v('f-msg').value.trim(),page:location.href,botcheck:false}};
    f.dataset.busy='1';var btn=f.querySelector('button');btn.disabled=true;btn.textContent='Sending...';
    fetch('https://api.web3forms.com/submit',{{method:'POST',headers:{{'Content-Type':'application/json','Accept':'application/json'}},body:JSON.stringify(body)}})
      .then(function(r){{return r.json();}})
      .then(function(d){{if(!d||d.success!==true)throw new Error('not sent');f.innerHTML='<p class="status" style="font-size:20px">'+OK+'</p>';}})
      .catch(function(){{f.dataset.busy='0';btn.disabled=false;btn.textContent='Send to Pattie';st.className='status err';st.textContent=ERR;}});
  }});
}})();
</script>
""" + footer()


def privacy():
    body = f"""
<main><section><div class="wrap narrow">
  <span class="label">Privacy policy</span>
  <h1>Privacy policy</h1>
  <p><em>Last updated: October 8, 2026</em></p>
  <p>This website, pattiep.com, is run by {e(A['name'])}, a real estate agent with {e(A['brokerage'])} ({e(A['license'])}). This page explains what information is collected here and how it is used.</p>
  <h2 style="font-size:28px;margin-top:32px">What we collect</h2>
  <p>When you send a message through the form on this site, we collect the details you type in: your name, email address, phone number if you give it, and your message. We also note whether you gave permission to be called or texted.</p>
  <p>We do not use advertising trackers on this site. The site's host may keep standard technical logs, such as your browser type and the time of your visit.</p>
  <h2 style="font-size:28px;margin-top:32px">How we use it</h2>
  <p>We use your information only to answer you and to help with your real estate questions. Your message is delivered to {e(A['name'])} by email through a form service (Web3Forms) and may be saved in her client contact system. We only call or text you if you gave permission, and you can reply STOP to any text to opt out.</p>
  <h2 style="font-size:28px;margin-top:32px">What we don't do</h2>
  <p>We do not sell your information. We do not share it with anyone else, except service providers that help deliver and store your messages, or when the law requires it.</p>
  <h2 style="font-size:28px;margin-top:32px">Your choices</h2>
  <p>You can ask to see, correct, or delete the information you sent us. California residents have rights under the California Consumer Privacy Act. To make a request, email <a href="mailto:{e(A['email'])}">{e(A['email'])}</a> or call {e(A['phone_display'])}.</p>
  <h2 style="font-size:28px;margin-top:32px">Questions</h2>
  <p>Contact {e(A['name'])} at <a href="mailto:{e(A['email'])}">{e(A['email'])}</a> or {e(A['phone_display'])}.</p>
  <p style="margin-top:28px"><a href="index.html">Back to the home page</a></p>
</div></section></main>
"""
    return head("Privacy policy · " + A["name"], "How pattiep.com collects and uses the information you send.", "privacy.html") + body + footer()


open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(index())
open(os.path.join(HERE, "privacy.html"), "w", encoding="utf-8").write(privacy())
print("Built index.html and privacy.html")
