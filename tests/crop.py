import json
from playwright.sync_api import sync_playwright
JS = """async () => {
  if (typeof window.yombalCropSquarePhoto !== 'function') return {fn:false};
  const c = document.createElement('canvas'); c.width = 515; c.height = 700;
  const x = c.getContext('2d'); x.fillStyle = '#c33'; x.fillRect(0,0,515,700); x.fillStyle='#fff'; x.fillRect(100,150,300,300);
  const blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.9));
  const file = new File([blob], 'test-515.jpg', {type:'image/jpeg'});
  const p = window.yombalCropSquarePhoto(file, {size:1200});
  await new Promise(r => setTimeout(r, 800));
  const panel = document.querySelector('.yombal-cropper');
  const info = {fn:true, opened: !!panel, hasZoom: !!(panel && panel.querySelector('input[type=range]')), btns: panel ? [...panel.querySelectorAll('button')].map(b=>b.innerText.trim()) : []};
  if (panel) panel.querySelector('[data-act="apply"]').click();
  const out = await Promise.race([p, new Promise(r => setTimeout(() => r('timeout'), 8000))]);
  if (out && out.size) {
    const im = new Image(); const u = URL.createObjectURL(out);
    await new Promise(r => { im.onload = r; im.src = u; });
    info.out = {type: out.type, w: im.naturalWidth, h: im.naturalHeight, bytes: out.size};
  } else info.out = String(out);
  return info;
}"""
res = []
with sync_playwright() as p:
    for dev in ['iPhone 15', 'iPhone SE', 'Pixel 7']:
        b = (p.webkit if 'iPhone' in dev else p.chromium).launch()
        pg = b.new_context(**p.devices[dev], locale='fr-FR').new_page()
        pg.goto('https://yombal.sn/', wait_until='load'); pg.wait_for_timeout(3500)
        r = pg.evaluate(JS); r['device'] = dev; res.append(r); print('CROP', dev, json.dumps(r, ensure_ascii=False))
        b.close()
