"""Independent audit planner: re-derives every IPO_Report row from the cached SEC cover page."""
import sys,re,os,json,datetime,collections,sqlite3
sys.path.insert(0,'scripts')
import audit_extract as A, audit_resolve as R
c=A.c
def acc_of(url):
    m=re.search(r'/data/\d+/(\d{18})/',url); s=m.group(1); return f'{s[:10]}-{s[10:12]}-{s[12:]}'
EVURL={}
for cik,url,sha in c.execute("select distinct cik,source_url,doc_sha256 from evidence"): EVURL.setdefault(cik,{})[url]=sha
FD={a:f for a,f in c.execute("select accession_no,filing_date from candidates")}
M="January|February|March|April|May|June|July|August|September|October|November|December"; mon={m:i for i,m in enumerate(M.split('|'),1)}
def text(path): return A.clean(open(path,'rb').read().decode('utf8','ignore'))
def prosp_date(t):
    m=re.search(r'(?:date of this prospectus is|[Pp]rospectus dated|PROSPECTUS DATED|[Dd]ated:?)\s*,?\s*('+M+r')\s+(\d{1,2})\s?,\s*(2026)',t[:40000])
    return datetime.date(2026,mon[m.group(1)],int(m.group(2))).isoformat() if m else None
def venue(t):
    h=t[:60000]
    m=re.search(r'(?:approved|authorized|accepted|cleared|listed|list|listing)[^.]{0,160}?(NYSE American|NYSE Texas|New York Stock Exchange American|Nasdaq|NASDAQ|New York Stock Exchange|NYSE)',h)
    if not m: return None
    v=m.group(1)
    if 'American' in v: return 'NYSE American'
    if v.lower().startswith('nasdaq'): return 'NASDAQ'
    return 'NYSE'
def analyse(url,sha,cik):
    path='cache/raw/'+sha
    if not os.path.exists(path): return None
    t=text(path); o=R.cover(t); o['venue']=venue(t); o['pdate']=prosp_date(t)
    h=t[:9000].lower()
    o['listed']=bool(re.search(r'closing (?:sales )?price[^.]{0,80}(?:as reported|on the)|our (?:class [ab] )?(?:common|ordinary) (?:shares|stock) (?:are|is) (?:currently )?(?:listed|quoted|traded) on|trade on the otc|quoted (?:for trading )?on',h)) and not re.search(r'no public market',h)
    o['mm']='market making' in h or 'market-making' in h
    o['dl']=bool(re.search(r'direct listing|resale of|offered by the selling|sold by registered|selling securityholders|registered (?:share|stock)holders',h))
    o['fund']=bool(re.search(r'closed-end|management investment company|subscription rights',h))
    o['spinoff']='distribution' in h and 'psus' in h
    t2=t[:3000]
    return o
def shares_price(d,o):
    pr,sh,how=None,None,None
    import audit_decide as D
    pr,sh,how=D.decide(d,o)
    if pr and sh and sh>=1000: return pr,sh,how
    if pr and o['S'] and not o['dl']:
        # accept cover headline share count when price is cover-stated and IPO signal present
        if o['ipo'] and o['S'][0]>=1000: return pr,int(o['S'][0]),'cover headline shares'
    return pr,None,None
plan=[]
for d in A.load():
    cik=d['cik']; docs=EVURL.get(cik,{})
    cands=[]
    for url,sha in docs.items():
        o=analyse(url,sha,cik)
        if o is None: continue
        cands.append((FD.get(acc_of(url),'9999'),url,sha,o))
    cands.sort(key=lambda x:x[0])
    # choose IPO doc: earliest with IPO signal and not already-listed; else record's own doc
    chosen=None
    for fdt,url,sha,o in cands:
        if o['ipo'] and not o['listed'] and not o['dl'] and not o['mm'] and not o['fund']: chosen=(fdt,url,sha,o); break
    own=[x for x in cands if x[1]==d['url']]
    if chosen is None: chosen=own[0] if own else (cands[0] if cands else None)
    rec=dict(tk=d['tk'],cik=cik,name=d['name'],db=dict(price=d['price'],base=d['base'],oa=d['oa'],acc=d['acc'],url=d['url'],pd=d['pd'],ex=d['ex'],spac=d['spac']),ncand=len(cands))
    if not chosen: rec['verdict']='NO_DOC'; plan.append(rec); continue
    fdt,url,sha,o=chosen
    rec.update(acc=acc_of(url),url=url,filing=fdt,pdate=o['pdate'],venue=o['venue'],flags=dict(dl=o['dl'],listed=o['listed'],mm=o['mm'],fund=o['fund'],ipo=o['ipo'],notes=o['notes']))
    d2=dict(d); 
    pr,sh,how=shares_price(d2,o); rec.update(price=pr,base=sh,how=how,oa=o['oa'])
    plan.append(rec)
json.dump(plan,open('runs/audit_plan.json','w'),indent=1,default=str)
print(len(plan))
