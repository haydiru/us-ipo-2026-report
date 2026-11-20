import sys,re,json,collections
sys.path.insert(0,'scripts')
import audit_extract as A, audit_resolve as R
def decide(d,o):
    pr=o['price']; ht=o.get('ht'); hs=o.get('hs'); tp=o.get('tp'); tt=o.get('tt')
    sh=None; how=None
    if tp and tt and abs(tt/tp-round(tt/tp))<0.01: sh=round(tt/tp); how='cover table total/price'
    elif hs and pr and ht and abs(hs*pr-ht)/ht<0.002: sh=int(hs); how='cover headline units x price'
    elif pr and o['S'] and ht and abs(o['S'][0]*pr-ht)/ht<0.002: sh=int(o['S'][0]); how='cover share count'
    elif pr and o['S'] and not o['resale'] and o['ipo'] and not o['notes'] and len(o['S'])>=1 and d['spac']: sh=int(o['S'][0]); how='cover headline units'
    return pr,sh,how
if __name__=='__main__':
    res=[];
    for d in A.load():
        docp=A.doc(d['url'],d['cik'])
        if not docp: res.append((d,None,None,None,None)); continue
        o=R.cover(A.clean(open(docp[0],'rb').read().decode('utf8','ignore')))
        pr,sh,how=decide(d,o)
        res.append((d,o,pr,sh,how))
    c=collections.Counter()
    for d,o,pr,sh,how in res:
        if o is None: c['nodoc']+=1; continue
        match = pr is not None and abs(pr-d['price'])<1e-6 and sh==d['base']
        if match: c['ok']+=1
        elif pr and sh: c['fixable']+=1
        else: c['manual']+=1; print('MANUAL',d['tk'],d['spac'],d['price'],d['base'],'cov',pr,o['S'][:3],o.get('ht'),'ipo' if o['ipo'] else '-','RESALE' if o['resale'] else '','NOTES' if o['notes'] else '')
    print(c)
    for d,o,pr,sh,how in res:
        if o and pr and sh and not(abs(pr-d['price'])<1e-6 and sh==d['base']): print('FIX',d['tk'],d['price'],d['base'],'->',pr,sh,how,'OA',o['oa'], 'RESALE' if o['resale'] else '')
