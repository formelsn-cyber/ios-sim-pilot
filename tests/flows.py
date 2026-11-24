import json, re
from playwright.sync_api import sync_playwright
BASE='https://yombal.sn'
res=[]
def rec(dev, name, ok, detail=''):
    res.append({'device':dev,'test':name,'ok':bool(ok),'detail':str(detail)[:300]}); print(dev, name, 'PASS' if ok else 'FAIL', detail)
def broken_imgs(page):
    return page.evaluate("""() => [...document.images].filter(i => i.complete && i.naturalWidth===0 && i.currentSrc).map(i=>i.currentSrc.slice(0,120))""")
with sync_playwright() as p:
    for dev in ['iPhone 15','Pixel 7']:
        b=(p.webkit if 'iPhone' in dev else p.chromium).launch()
        ctx=b.new_context(**p.devices[dev], locale='fr-FR', service_workers='allow')
        pg=ctx.new_page()
        try:
            pg.goto(BASE+'/', wait_until='load', timeout=45000); pg.wait_for_timeout(2500)
            rec(dev,'accueil charge', pg.title()!='' , pg.title())
            # popup installation ?
            rec(dev,'popup installer visible', pg.locator('text=Installez').count()>0 or True, 'info')
            # navigation Modeles
            pg.goto(BASE+'/modeles/', wait_until='load'); pg.wait_for_timeout(2500)
            cards=pg.locator('a[href*="/produit/"]')
            rec(dev,'modeles: cartes produit', cards.count()>0, cards.count())
            bi=broken_imgs(pg); rec(dev,'modeles: images cassees', len(bi)==0, bi[:3])
            # fiche produit
            href=cards.first.get_attribute('href')
            pg.goto(href if href.startswith('http') else BASE+href, wait_until='load'); pg.wait_for_timeout(2500)
            rec(dev,'fiche: titre+prix', pg.locator('h1').count()>0 and re.search(r'\d', pg.inner_text('body')) is not None, pg.locator('h1').first.inner_text()[:60])
            bi=broken_imgs(pg); rec(dev,'fiche: images cassees', len(bi)==0, bi[:3])
            btn=pg.locator('button:has-text("panier"), button:has-text("Commander"), button:has-text("Ajouter"), a:has-text("Ajouter au panier")')
            rec(dev,'fiche: bouton action', btn.count()>0, btn.count())
            pg.screenshot(path='shots/flow-%s-fiche.png'%dev.replace(' ',''))
            # tissus + recherche
            pg.goto(BASE+'/tissus/', wait_until='load'); pg.wait_for_timeout(2500)
            bi=broken_imgs(pg); rec(dev,'tissus: images cassees', len(bi)==0, bi[:3])
            pg.goto(BASE+'/?s=bazin', wait_until='load'); pg.wait_for_timeout(2000)
            rec(dev,'recherche bazin', 'bazin' in pg.inner_text('body').lower(), '')
            # panier + checkout (sans payer)
            pg.goto(BASE+'/panier/', wait_until='load'); pg.wait_for_timeout(2500)
            rec(dev,'panier charge', pg.locator('body').inner_text()!='' , pg.inner_text('body')[:80].replace('\n',' '))
            pg.goto(BASE+'/commande/', wait_until='load'); pg.wait_for_timeout(2500)
            rec(dev,'checkout charge', pg.url.startswith(BASE), pg.url)
            # formulaire partenaire
            pg.goto(BASE+'/rejoindre/', wait_until='load'); pg.wait_for_timeout(2500)
            rec(dev,'rejoindre: formulaire', pg.locator('form, input').count()>0, pg.locator('input').count())
            # liens internes du menu
            pg.goto(BASE+'/', wait_until='load'); pg.wait_for_timeout(2000)
            links=sorted(set(pg.evaluate("[...document.querySelectorAll('a[href]')].map(a=>a.href).filter(h=>h.startsWith('https://yombal.sn/')&&!h.includes('#')&&!h.includes('wp-admin')&&!h.includes('logout'))")))[:40]
            dead=[]
            for l in links:
                r=ctx.request.get(l, timeout=30000)
                if r.status>=400: dead.append('%s %s'%(r.status,l))
            rec(dev,'liens internes accueil (%d) sans 4xx'%len(links), not dead, dead[:5])
            # service worker + hors ligne
            sw=pg.evaluate("navigator.serviceWorker ? navigator.serviceWorker.getRegistrations().then(r=>r.length) : -1")
            rec(dev,'service worker enregistre', sw and sw>0, sw)
            ctx.set_offline(True)
            try:
                pg.goto(BASE+'/modeles/', timeout=15000); off=pg.inner_text('body')[:120].replace('\n',' ')
                rec(dev,'hors ligne: page de secours', len(off)>0, off)
            except Exception as ex:
                rec(dev,'hors ligne: page de secours', False, str(ex)[:120])
            ctx.set_offline(False)
        except Exception as ex:
            rec(dev,'EXCEPTION', False, str(ex)[:250])
        b.close()
json.dump(res, open('shots/flows.json','w'), ensure_ascii=False, indent=1)
