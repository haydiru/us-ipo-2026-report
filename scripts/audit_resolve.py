import sys,re,os,json,collections
sys.path.insert(0,'scripts')
import audit_extract as A
NUM=A.NUM; N=A.N
def cover(t):
    i=max(t.find('Filed Pursuant'),0); h=t[i:i+16000]; o={'h':h}
    # price candidates
    P=[]
    for m in re.finditer(r'(?:[Oo]ffering [Pp]rice|has a price|price to the public|[Pp]ublic offering price|[Oo]ffering price per (?:unit|share|ADS))[^$]{0,90}?(?:US)?\$\s?([\d,]+(?:\.\d+)?)',h): P.append(N(m.group(1)))
    m=re.search(r'(?:[Pp]ublic [Oo]ffering [Pp]rice|Price to [Pp]ublic|[Oo]ffering [Pp]rice)\s*(?:\(\d\))?\s*(?:US)?\$\s?([\d,]+(?:\.\d+)?)\s+(?:US)?\$\s?([\d,]+(?:\.\d+)?)',h)
    if m: o['tp']=N(m.group(1)); o['tt']=N(m.group(2)); P.insert(0,o['tp'])
    o['price']=collections.Counter(P).most_common(1)[0][0] if P else None
    m=re.search(r'\$\s?([\d,]{9,})\s+[^$]{2,90}?'+NUM+r'\s+(?:Units|units|Class|ordinary|Shares|shares|American|ADS|Common)',h[:2500])
    if m: o['ht']=N(m.group(1)); o['hs']=N(m.group(2))
    S=[]
    for m in re.finditer(NUM+r'\s*(?:Units|units|Shares|S hares|shares|ADSs|American Depositary|Class [AB] ordinary|ordinary shares|common shares)',h[:3500]): S.append(N(m.group(1)))
    o['S']=S[:4]
    m=re.search(r'option to purchase (?:up to )?(?:an )?(?:additional )?'+NUM,h); o['oa']=N(m.group(1)) if m else None
    l=h.lower()
    o['ipo']=bool(re.search(r'initial public offering|no public market|no established public',l[:9000]))
    o['resale']=bool(re.search(r'resale of|offered by the selling|selling (?:stock|share)holders?|direct listing|market making|market-making',l[:5000]))
    o['notes']=bool(re.search(r'per note|medium-term|structured|rights offering|subscription rights',l[:5000]))
    return o
def resolve(d):
    t=A.clean(open(A.doc(d['url'],d['cik'])[0],'rb').read().decode('utf8','ignore')) if A.doc(d['url'],d['cik']) else None
    if t is None: return None
    return cover(t)
if __name__=='__main__':
    out=[]
    for d in A.load():
        o=resolve(d)
        if o is None: out.append((d['tk'],'NODOC'));continue
        pr=o['price']; sh=[x for x in [o.get('tt') and o.get('tt')/o['tp'] if o.get('tp') else None,o.get('hs')]+o['S'] if x]
        ok=pr is not None and abs(pr-d['price'])<1e-6 and any(abs(x-d['base'])<1 for x in sh)
        if ok: continue
        print(d['tk'],d['spac'],'DB',d['price'],d['base'],d['oa'],'| COV',pr,o.get('hs'),o['S'][:3],'oa',o['oa'],'ipo' if o['ipo'] else '-', 'RESALE' if o['resale'] else '','NOTES' if o['notes'] else '')
