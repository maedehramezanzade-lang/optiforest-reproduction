"""A small web shop plus a traffic simulator.
Real visitors are replaced by simulated 'personas': normal ones, legitimate look-alikes (search-engine crawler,
uptime monitor, power user) and four kinds of attacker. Writes access.log (server log) and labels.csv (ground truth)."""
import threading, time, random, csv, http.client
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import argparse, os, zlib
ap = argparse.ArgumentParser(description='Web shop + traffic simulator (writes access.log and labels.csv)')
ap.add_argument('--seed', type=int, default=42, help='master seed: decides visitor types and every visitor\'s own behaviour')
ap.add_argument('--sessions', type=int, default=6000)
ap.add_argument('--out-dir', default='.')
ap.add_argument('--port', type=int, default=8765)
ap.add_argument('--workers', type=int, default=64)
args = ap.parse_args()
SEED, N_SESSIONS, PORT, WORKERS = args.seed, args.sessions, args.port, args.workers
os.makedirs(args.out_dir, exist_ok=True)
LOCK = threading.Lock()
LOG = open(os.path.join(args.out_dir, 'access.log'), 'w')
# Server side: response *size* depends only on the URL (same page, same size) so it is reproducible;
# response *delay* is real timing noise and is deliberately NOT seeded (timings differ a little between runs and machines).
JITTER = random.Random()
def size(path, lo, hi):
    return random.Random(zlib.crc32(path.encode())).randint(lo, hi)

class Shop(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def log_message(self, *a): pass
    def handle_request(self, method):
        t0 = time.time()
        client, path = self.headers.get('X-Client-Id', '-'), self.path
        body = self.rfile.read(int(self.headers.get('Content-Length', 0))).decode() if method == 'POST' else ''
        if path in ('/', '/products', '/cart'):
            time.sleep(JITTER.uniform(0.003, 0.015)); status, out = 200, b'x' * size(path, 800, 1500)
        elif path == '/robots.txt':
            time.sleep(0.002); status, out = 200, b'User-agent: *'
        elif path.startswith('/product/'):
            time.sleep(JITTER.uniform(0.005, 0.02))
            tail = path.split('/')[-1]
            status, out = (200, b'x' * size(path, 1500, 3000)) if tail.isdigit() and int(tail) < 500 else (404, b'not found')
        elif path.startswith('/search'):
            time.sleep(JITTER.uniform(0.02, 0.06)); status, out = 200, b'x' * size(path, 2000, 4000)
        elif path == '/login' and method == 'POST':
            time.sleep(JITTER.uniform(0.01, 0.03)); status, out = (200, b'welcome') if 'p=good' in body else (401, b'denied')
        elif path == '/checkout' and method == 'POST':
            time.sleep(JITTER.uniform(0.02, 0.05)); status, out = 200, b'order placed'
        else:
            time.sleep(JITTER.uniform(0.001, 0.005)); status, out = 404, b'not found'
        self.send_response(status); self.send_header('Content-Length', str(len(out))); self.end_headers(); self.wfile.write(out)
        ms = (time.time() - t0) * 1000
        ts = datetime.fromtimestamp(t0).strftime('%d/%b/%Y:%H:%M:%S.%f')[:-3]
        with LOCK:
            LOG.write(f'{client} - - [{ts}] "{method} {path} HTTP/1.1" {status} {len(out)} {ms:.1f}\n')
    def do_GET(self):  self.handle_request('GET')
    def do_POST(self): self.handle_request('POST')

SENSITIVE = ['/admin', '/.env', '/wp-login.php', '/phpmyadmin', '/config.json', '/backup.zip', '/.git/config', '/server-status']
def session(i, kind):
    rng = random.Random(f'{SEED}-{i}')            # every visitor has its own seeded generator
    def pause(lo, hi): time.sleep(rng.uniform(lo, hi))
    cid = f'10.{i // 62500}.{(i // 250) % 250}.{i % 250}'
    conn = http.client.HTTPConnection('127.0.0.1', PORT)
    def get(path): conn.request('GET', path, headers={'X-Client-Id': cid}); conn.getresponse().read()
    def post(path, body):
        conn.request('POST', path, body=body, headers={'X-Client-Id': cid, 'Content-Length': str(len(body))}); conn.getresponse().read()
    def login(ok): post('/login', 'u=%d&p=%s' % (i, 'good' if ok else 'bad'))
    def product(): get(f'/product/{rng.randint(1, 499)}')
    def browse(n, lo, hi):
        for _ in range(n):
            r = rng.random()
            if r < 0.45: get(f'/product/{rng.randint(1, 520) if rng.random() < 0.95 else 9999}')
            elif r < 0.65: get('/products')
            elif r < 0.85: get(f'/search?q=item{rng.randint(1, 50)}')
            else: get('/cart')
            pause(lo, hi)
    try:
        # ---- legitimate traffic (label 0), including look-alikes of attackers ----
        if kind == 'shopper':
            if rng.random() < 0.6: login(rng.random() < 0.93)
            if rng.random() < 0.08:                      # forgot the password
                for _ in range(rng.randint(2, 4)): login(False); pause(0.05, 0.2)
                login(True)
            browse(rng.randint(4, 14), 0.02, 0.15)
            if rng.random() < 0.3: post('/checkout', 'cart=1')
        elif kind == 'power_user':
            login(True); browse(rng.randint(25, 45), 0.005, 0.05)
            if rng.random() < 0.4: post('/checkout', 'cart=1')
        elif kind == 'crawler':                             # search-engine bot: many pages, fast, but polite
            get('/robots.txt')
            for _ in range(rng.randint(30, 70)): product(); pause(0.003, 0.03)
        elif kind == 'monitor':                             # uptime monitor: regular pings
            period = rng.uniform(0.03, 0.08)
            for _ in range(rng.randint(10, 25)): get('/'); time.sleep(period)
        # ---- attackers (label 1). About half of each kind is "mild": it blends in with normal visitors ----
        elif kind == 'scraper':
            mode = rng.random()
            if mode < 0.25:                                 # fast scraper
                for _ in range(rng.randint(40, 80)): product()
            elif mode < 0.5:                                # stealth scraper: slower, mixed pages
                for _ in range(rng.randint(20, 35)):
                    product() if rng.random() < 0.8 else get('/products'); pause(0.01, 0.06)
            else:                                           # mild: a dozen products at a human pace, mixed with browsing
                for _ in range(rng.randint(10, 18)):
                    product() if rng.random() < 0.7 else browse(1, 0, 0); pause(0.04, 0.15)
        elif kind == 'brute_force':
            mode = rng.random()
            if mode < 0.25:
                for _ in range(rng.randint(15, 40)): login(False)
            elif mode < 0.5:
                for _ in range(rng.randint(5, 9)): login(False); pause(0.02, 0.1)
            else:                                           # mild: 3-5 failed logins between normal browsing
                browse(rng.randint(1, 3), 0.02, 0.15)
                for _ in range(rng.randint(3, 5)): login(False); pause(0.05, 0.2)
                browse(rng.randint(0, 2), 0.02, 0.15)
        elif kind == 'slow_brute':
            for _ in range(rng.randint(6, 12)): login(False); pause(0.1, 0.3)
        elif kind == 'scanner':
            mode = rng.random()
            if mode < 0.25:
                for _ in range(rng.randint(10, 25)): get(rng.choice(SENSITIVE))
            elif mode < 0.5:                                # light scanner mixed with normal pages
                browse(rng.randint(2, 4), 0.02, 0.1)
                for _ in range(rng.randint(4, 8)): get(rng.choice(SENSITIVE)); pause(0.02, 0.1)
            else:                                           # mild: only two or three probes inside a normal visit
                browse(rng.randint(3, 6), 0.02, 0.15)
                for _ in range(rng.randint(2, 3)): get(rng.choice(SENSITIVE)); pause(0.05, 0.2)
                browse(rng.randint(1, 3), 0.02, 0.15)
        elif kind == 'broken_bot':                          # misbehaving client hammering broken links
            mode = rng.random()
            if mode < 0.5:
                for _ in range(rng.randint(15, 35)): get(f'/product/{rng.randint(500, 99999)}'); pause(0.0, 0.03)
            else:                                           # mild: a handful of broken links at a human pace
                for _ in range(rng.randint(7, 12)): get(f'/product/{rng.randint(500, 99999)}'); pause(0.04, 0.15)
    finally:
        conn.close()
    return cid, kind

KINDS   = ['shopper', 'power_user', 'crawler', 'monitor', 'scraper', 'brute_force', 'slow_brute', 'scanner', 'broken_bot']
WEIGHTS = [86.0,       3.0,          1.5,       1.0,       2.0,       2.0,           1.5,          1.5,       1.5]
ATTACK  = {'scraper', 'brute_force', 'slow_brute', 'scanner', 'broken_bot'}
kinds = random.Random(SEED).choices(KINDS, weights=WEIGHTS, k=N_SESSIONS)

ThreadingHTTPServer.request_queue_size = 256
server = ThreadingHTTPServer(('127.0.0.1', PORT), Shop)
threading.Thread(target=server.serve_forever, daemon=True).start()
t0 = time.time()
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    results = list(ex.map(lambda a: session(*a), enumerate(kinds)))
server.shutdown(); LOG.close()
with open(os.path.join(args.out_dir, 'labels.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['client', 'behaviour', 'is_attack']); w.writerows([(c, k, int(k in ATTACK)) for c, k in results])
print(f'Simulated {N_SESSIONS} visitor sessions -> {sum(1 for _ in open(os.path.join(args.out_dir, "access.log")))} requests logged in {time.time() - t0:.0f}s')
for k in KINDS: print(f'  {k:12s} {kinds.count(k):5d}   {"ATTACK" if k in ATTACK else ""}')