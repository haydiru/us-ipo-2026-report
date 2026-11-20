import json,sys,re,collections
sys.path.insert(0,'scripts')
import audit_extract as A
plan=json.load(open('runs/audit_plan.json'))
FOLLOW_ON={'MDLN':'Already Nasdaq-listed; selling-stockholder secondary at $41.00 (cover cites closing price)','ELOG':'Already Nasdaq-listed; best-efforts follow-on at $0.36','RUBI':'Already Nasdaq-listed (RUBI); registered direct/units follow-on','GLND':'Already Nasdaq-listed (GLND); follow-on with warrants','MGN':'IPO consummated 2025-09-29; 2026 filing is a follow-on','SHAZ':'Already trading OTC; Nasdaq up-list, not an IPO','OPTH':'Already trading on FSE/OTCQX; US listing, not a primary IPO'}
NONEQ={'GS':'Goldman Sachs structured notes pricing supplement','GAB':'Gabelli closed-end fund rights-offering supplement','PS':'Pershing Square Inc spin-off distribution (no offer price)','PSUS':'Closed-end fund (Pershing Square USA) - out of scope'}
def verdict(r):
    tk=r['tk']; db=r['db']
    if r.get('verdict')=='NO_DOC': 
        return ('EXCLUDE','UNVERIFIABLE_NO_CACHED_FILING','No cached 424B4 and values are the $20.00 / 10,000,000 placeholder pattern') if tk in('BRAI','WSHP') else None
    if tk in NONEQ: return ('EXCLUDE','NON_EQUITY_OR_FUND',NONEQ[tk])
    if tk in FOLLOW_ON: return ('EXCLUDE','FOLLOW_ON_ALREADY_LISTED',FOLLOW_ON[tk])
    if r['venue']=='NYSE American' or tk=='SNSC': return ('EXCLUDE','WRONG_VENUE_NYSE_AMERICAN','Cover: approved for listing on NYSE American (out of scope)')
    f=r['flags']
    if r['price'] is None and f['dl']: return ('EXCLUDE','DIRECT_LISTING_RESALE','Resale registration / direct listing - no primary offering price')
    return None
if __name__=='__main__':
    out=collections.defaultdict(list)
    for r in plan:
        v=verdict(r)
        if v: out[v[1]].append(r['tk'])
    for k,v in out.items(): print(k,len(v),v)
    # rows still lacking price/base
    keep=[r for r in plan if not verdict(r)]
    print('keep',len(keep))
    for r in keep:
        if r.get('verdict')=='NO_DOC' or r['price'] is None or r['base'] is None: print('UNRESOLVED',r['tk'],r['db']['price'],r['db']['base'],r.get('price'),r.get('base'),r.get('flags'))
