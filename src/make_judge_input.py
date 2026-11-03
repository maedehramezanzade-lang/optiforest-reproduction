import re, csv, random, json, collections
LOG='/tmp/judge/sim_out/access.log'; LAB='/tmp/judge/sim_out/labels.csv'
pat=re.compile(r'^(\S+) - - \[(\d+)/(\w+)/(\d+):(\d+):(\d+):(\d+)\.(\d+)\] "(\w+) (\S+) HTTP/1.1" (\d+) (\d+) ([\d.]+)')
sess=collections.defaultdict(list)
for line in open(LOG):
    m=pat.match(line)
    if not m: continue
    ip=m.group(1); h,mi,s,ms=int(m.group(5)),int(m.group(6)),int(m.group(7)),int(m.group(8))
    t=h*3600+mi*60+s+ms/1000.0
    sess[ip].append((t,m.group(9),m.group(10),int(m.group(11)),int(m.group(12)),float(m.group(13))))
lab={r['client']:(int(r['is_attack']),r['behaviour']) for r in csv.DictReader(open(LAB))}
EXCLUDE={'10.0.0.0','10.0.0.1'}   # two rows were shown by accident earlier
rng=random.Random(2026)
att=sorted(c for c,(a,b) in lab.items() if a==1 and c not in EXCLUDE and c in sess)
nor=sorted(c for c,(a,b) in lab.items() if a==0 and c not in EXCLUDE and c in sess)
pick=rng.sample(att,30)+rng.sample(nor,30)
rng.shuffle(pick)
key={}; out=[]
for i,c in enumerate(pick,1):
    jid=f'S{i:02d}'
    key[jid]={'client':c,'is_attack':lab[c][0],'behaviour':lab[c][1]}
    rows=sorted(sess[c]); t0=rows[0][0]
    out.append(f'=== Session {jid}: {len(rows)} requests, duration {rows[-1][0]-t0:.1f} s ===')
    for r in rows[:40]:
        out.append(f'+{r[0]-t0:7.2f}s  {r[1]:4s} {r[2]:28s} -> {r[3]}  {r[4]} bytes  {r[5]:.0f} ms')
    if len(rows)>40: out.append(f'... ({len(rows)-40} more requests not shown)')
    out.append('')
open('/tmp/judge/work/judge_input.txt','w').write('\n'.join(out))
json.dump(key,open('/tmp/judge/work/KEY_do_not_open.json','w'))
print('sessions',len(pick),'lines',len(out))
