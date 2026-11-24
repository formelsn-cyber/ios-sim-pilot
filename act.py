import json, subprocess, sys, time, os
U = os.environ['UDID']
def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout
def tree(name):
    out = sh('idb', 'ui', 'describe-all', '--udid', U, '--json', '--nested')
    open('shots/' + name + '.json', 'w').write(out)
    items = []
    def walk(n):
        if isinstance(n, list):
            for x in n: walk(x)
        elif isinstance(n, dict):
            items.append(n)
            for c in n.get('children', []) or []: walk(c)
    try: walk(json.loads(out))
    except Exception as e: print('tree parse fail', e)
    return items
def shot(name):
    sh('xcrun', 'simctl', 'io', U, 'screenshot', 'shots/' + name + '.png')
def tap_label(items, needle):
    for n in items:
        lab = (n.get('AXLabel') or '') + ' ' + (n.get('title') or '')
        if needle.lower() in lab.lower() and n.get('frame'):
            f = n['frame']; x = f['x'] + f['width'] / 2; y = f['y'] + f['height'] / 2
            print('TAP', needle, x, y)
            sh('idb', 'ui', 'tap', '--udid', U, str(int(x)), str(int(y)))
            return True
    print('NOT FOUND', needle)
    return False
if __name__ == '__main__':
    steps = sys.argv[1:]
    n = 0
    for s in steps:
        items = tree('t%02d-before' % n)
        print('LABELS', [ (i.get('AXLabel') or '')[:40] for i in items if i.get('AXLabel')][:60])
        tap_label(items, s)
        time.sleep(6)
        shot('s%02d-after-%s' % (n, ''.join(c for c in s if c.isalnum())[:20]))
        n += 1
