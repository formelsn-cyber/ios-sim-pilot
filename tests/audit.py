import json, sys, time
from playwright.sync_api import sync_playwright
BASE = 'https://yombal.sn'
PAGES = ['/', '/modeles/', '/tissus/', '/parcours/', '/vendeurs-de-tissus/', '/mon-compte/', '/panier/', '/rejoindre/', '/tailleurs/', '/?s=bazin', '/contact/', '/a-propos/', '/confidentialite/', '/conditions-generales/']
DEVICES = ['iPhone 15', 'iPhone SE', 'Pixel 7']
out = []
with sync_playwright() as p:
    for dev in DEVICES:
        browser = (p.webkit if 'iPhone' in dev else p.chromium).launch()
        ctx = browser.new_context(**p.devices[dev], locale='fr-FR')
        for path in PAGES:
            page = ctx.new_page()
            errs, bad = [], []
            page.on('console', lambda m, e=errs: e.append(m.text[:160]) if m.type == 'error' else None)
            page.on('pageerror', lambda x, e=errs: e.append('PAGEERROR ' + str(x)[:160]))
            page.on('response', lambda r, b=bad: b.append('%s %s' % (r.status, r.url[:110])) if r.status >= 400 else None)
            r = {'device': dev, 'path': path}
            try:
                resp = page.goto(BASE + path, wait_until='load', timeout=45000)
                page.wait_for_timeout(2500)
                r['status'] = resp.status if resp else None
                r['title'] = page.title()[:80]
                r.update(page.evaluate("""() => ({
                  overflowX: document.documentElement.scrollWidth - window.innerWidth,
                  h1: (document.querySelector('h1')||{}).innerText || null,
                  imgsNoAlt: [...document.images].filter(i=>!i.alt).length,
                  smallTargets: [...document.querySelectorAll('a,button')].filter(e=>{const b=e.getBoundingClientRect();return b.width>0&&b.height>0&&(b.width<32||b.height<32)}).length,
                  manifest: !!document.querySelector('link[rel=manifest]'),
                  viewport: !!document.querySelector('meta[name=viewport]')})"""))
                safe = (dev + path).replace(' ', '').replace('/', '_').replace('?', '_').replace('=', '_')
                page.screenshot(path='shots/%s.png' % safe, full_page=False)
            except Exception as ex:
                r['error'] = str(ex)[:200]
            r['consoleErrors'] = errs[:5]
            r['http4xx5xx'] = bad[:5]
            out.append(r); page.close()
        browser.close()
json.dump(out, open('shots/audit.json', 'w'), ensure_ascii=False, indent=1)
print('done', len(out))
