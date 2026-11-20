import sqlite3,re,html,os,glob,json
c=sqlite3.connect('runs/ledger.sqlite')
def clean(raw):
    t=re.sub(r'<[^>]+>',' ',raw); t=html.unescape(t).replace('\xa0',' ')
    t=re.sub(r'\s*\.{3,}\s*',' ',t)
    return re.sub(r'\s+',' ',t)
idx={}
for p in glob.glob('cache/raw/*'):
    raw=open(p,'rb').read().decode('utf8','ignore')
    m=re.search(r'<FILENAME>([^\s<]+)',raw[:600])
    idx.setdefault(m.group(1).lower() if m else None,[]).append(p)
EV={}
for cik,sha in c.execute("select cik,doc_sha256 from evidence"): EV.setdefault(cik,sha)
def doc(url,cik=None):
    if cik in EV and os.path.exists('cache/raw/'+EV[cik]): return ['cache/raw/'+EV[cik]]
    ps=idx.get(url.rsplit('/',1)[1].lower())
    return ps if ps and len(ps)==1 else None
N=lambda s:float(s.replace(',','').replace(' ',''))
NUM=r'(\d{1,3}(?:\s?,\s?\d{3})+|\d+)'
def extract(t):
    h=t[:18000]; o={}
    m=re.search(r'(?:[Ii]nitial )?(?:[Pp]ublic )?[Oo]ffering [Pp]rice(?: per [A-Za-z ]{2,20}?)?\s*(?:\(\d\))?\s*\$\s?([\d,]+(?:\.\d+)?)\s+\$\s?([\d,]+(?:\.\d+)?)',h) or re.search(r'(?:[Pp]ublic offering price|Price to [Pp]ublic)\s*(?:\(\d\))?\s*\$\s?([\d,]+(?:\.\d+)?)\s+\$\s?([\d,]+(?:\.\d+)?)',h)
    if m: o['price']=N(m.group(1)); o['total']=N(m.group(2)); o['tbl_shares']=o['total']/o['price'] if o['price'] else None
    if 'price' not in o:
        m=re.search(r'(?:offering price (?:per (?:share|unit|ADS)[^$]{0,60}?)?(?:of|is|was)|per unit (?:has an )?offering price of|unit has an offering price of|price per share (?:of|is)|at an? (?:initial public )?offering price (?:per share )?of)\s*(?:approximately )?\$\s?([\d,]+(?:\.\d+)?)',h)
        if m: o['price']=N(m.group(1))
    m=re.search(r'\$\s?([\d,]{9,})\s+(?:[A-Z][^.]{2,70}?)\s+'+NUM+r'\s+(?:Units|units|Class [AB]|ordinary|Shares|shares|American|ADS)',h[:2500])
    if m: o['head_total']=N(m.group(1)); o['head_shares']=N(m.group(2))
    m=re.search(r'(?:^|\s)'+NUM+r'\s*(?:Units|Shares|S ?hares|Class [AB] (?:ordinary|common)|ordinary shares|American Depositary|common shares|shares of)',h[:3000])
    if m: o['lead_shares']=N(m.group(1))
    m=re.search(r'option to purchase (?:up to )?(?:an )?(?:additional )?'+NUM,h)
    if m: o['oa']=N(m.group(1))
    low=h.lower()
    o['flags']=[k for k,p in {'RESALE':r'resale of','DIRECT_LISTING':r'direct listing','SUPPLEMENT':r'supplement no','RIGHTS':r'subscription rights|rights offering','NOTES':r'per note|structured|medium-term notes','SELL_ONLY':r'selling (?:stock|share)holders? named in this prospectus are offering','LISTED_ALREADY':r'closing (?:sales )?price[^.]{0,80}as reported','FUND':r'closed-end|investment company act'}.items() if re.search(p,low)]
    return o
def load():
    rows=[]
    for cik,acc,name,tk,ex,pd,price,base,oa,gross,url,spac in c.execute("select cik,accession_no,company_name,ticker,exchange,pricing_date,offer_price,base_shares,overallotment_shares,gross_offering_amount,prospectus_url,is_spac from ipo_records"):
        ps=doc(url,cik); d=dict(cik=cik,acc=acc,name=name,tk=tk,ex=ex,pd=pd,price=float(price),base=base,oa=oa,gross=float(gross),url=url,spac=spac)
        if not ps: d['cov']=None
        else:
            d['cov']=extract(clean(open(ps[0],'rb').read().decode('utf8','ignore')))
        rows.append(d)
    return rows
def classify(d):
    e=d['cov']
    if e is None: return 'NO_RAW'
    cands=[x for x in (e.get('tbl_shares'),e.get('head_shares'),e.get('lead_shares')) if x]
    pr=e.get('price')
    if pr is None: return 'UNPARSED_PRICE'
    if abs(pr-d['price'])>1e-6: return 'PRICE_MISMATCH'
    if any(abs(x-d['base'])<1 for x in cands): return 'OK'
    if not cands: return 'UNPARSED_SHARES'
    return 'SHARES_MISMATCH'
if __name__=='__main__':
    import collections
    rows=load(); cl=collections.Counter(classify(d) for d in rows); print(cl)
    for d in rows:
        k=classify(d)
        if k!='OK': 
            e=d['cov'] or {}
            print(k,d['tk'],d['price'],d['base'],d['oa'],'|',e.get('price'),e.get('tbl_shares'),e.get('head_shares'),e.get('lead_shares'),e.get('oa'),e.get('flags'))
