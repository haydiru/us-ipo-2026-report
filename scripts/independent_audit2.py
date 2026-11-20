import sqlite3,re,html,os,collections,json
c=sqlite3.connect('runs/ledger.sqlite')
ev={}
for cik,url,sha in c.execute("select cik,source_url,doc_sha256 from evidence"): ev.setdefault(cik,(url,sha))
def text(sha):
    p=f'cache/raw/{sha}'
    if not os.path.exists(p): return None
    t=open(p,'rb').read().decode('utf8','ignore')
    t=re.sub(r'<[^>]+>',' ',t); t=html.unescape(t).replace('\xa0',' ')
    return re.sub(r'\s+',' ',t)
num=lambda s:int(s.replace(',',''))
res=[]
for cik,acc,name,tk,ex,pd,price,base,oa,gross,spac,st in c.execute("select cik,accession_no,company_name,ticker,exchange,pricing_date,offer_price,base_shares,overallotment_shares,gross_offering_amount,is_spac,status from ipo_records"):
    if cik not in ev: res.append((cik,tk,'NO_EVIDENCE'));continue
    t=text(ev[cik][1])
    if t is None: res.append((cik,tk,'NO_RAW'));continue
    head=t[:12000]
    issue=[]
    # base shares must appear on the cover
    b=f'{base:,}'
    if b not in head: issue.append(f'base {b} not on cover')
    if oa and base==oa: issue.append('base==OA')
    if oa and f'{base-oa:,}' in head and b not in head: issue.append('base looks = total incl OA')
    p=price.rstrip('0').rstrip('.') if '.' in price else price
    if not re.search(r'\$\s?'+re.escape(price.rstrip('0') if '.' in price else price)+r'|\$\s?'+re.escape(p),head): issue.append(f'price {price} not on cover')
    if abs(float(price)*base-float(gross))>0.005: issue.append('arith')
    res.append((cik,tk,acc,name,price,base,oa,issue))
bad=[r for r in res if len(r)>3 and r[-1]] + [r for r in res if len(r)==3]
print(len(res),"checked;",len(bad),"with cover issues")
for r in bad: print(r)
