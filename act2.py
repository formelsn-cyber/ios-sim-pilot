import os, time, json, subprocess
from appium import webdriver
from appium.options.ios import XCUITestOptions
U = os.environ['UDID']
o = XCUITestOptions()
o.platform_name = 'iOS'
o.udid = U
o.browser_name = 'Safari'
o.set_capability('appium:autoAcceptAlerts', False)
o.set_capability('appium:wdaLaunchTimeout', 240000)
o.set_capability('appium:newCommandTimeout', 600)
d = webdriver.Remote('http://127.0.0.1:4723', options=o)
os.makedirs('shots', exist_ok=True)
def snap(n):
    d.save_screenshot('shots/%s.png' % n)
def dump(n):
    try:
        d.switch_to.context('NATIVE_APP')
        open('shots/%s.xml' % n, 'w').write(d.page_source)
    except Exception as e:
        print('dump fail', e)
d.get('https://yombal.sn/')
time.sleep(25)
snap('a01-home')
ctx = d.contexts; print('CONTEXTS', ctx)
# standalone / manifest checks in the page
d.switch_to.context([c for c in ctx if c.startswith('WEBVIEW')][0])
print('JS', json.dumps(d.execute_script("return {sa: navigator.standalone, dm: matchMedia('(display-mode: standalone)').matches, manifest: !!document.querySelector('link[rel=manifest]'), capable: (document.querySelector('meta[name=apple-mobile-web-app-capable]')||{}).content, ua: navigator.userAgent}")))
dump('a02-native-before')
d.switch_to.context('NATIVE_APP')
try:
    el = d.find_element('xpath', "//*[contains(@label,'Installer') or contains(@name,'Installer')]")
    el.click(); time.sleep(5); snap('a03-after-install-click'); dump('a04-native-after')
except Exception as e:
    print('no install button', str(e)[:200])
d.quit()
