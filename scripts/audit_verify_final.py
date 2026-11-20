import sys, os, re, json, datetime, collections, random
sys.path.insert(0, 'scripts')
import openpyxl
from decimal import Decimal
import audit_extract as A, audit_resolve as R, audit_plan as P
wb = openpyxl.load_workbook('output/us_ipo_report_2026.xlsx')
ws = wb['IPO_Report']
hdr = [c.value for c in ws[1]]
rows = []
for i, r in enumerate(ws.iter_rows(min_row=2), start=2):
    d = {h: c.value for h, c in zip(hdr, r)}
    d['_i'] = i; d['_f'] = r[6].value; d['_link'] = r[7].hyperlink.target if r[7].hyperlink else None
    rows.append(d)
print('rows', len(rows), 'SPAC', sum(1 for r in rows if r['Is_SPAC'] == 'TRUE'))
print('C1 dup ticker', [k for k, v in collections.Counter(r['Ticker'] for r in rows).items() if v > 1], 'dup acc', [k for k, v in collections.Counter(r['Accession No.'] for r in rows).items() if v > 1], 'dup tkr+date', [k for k, v in collections.Counter((r['Ticker'], r['Pricing Date']) for r in rows).items() if v > 1])
print('C1 exchanges', collections.Counter(r['Exchange'] for r in rows))
print('C3 weekend', [r['Ticker'] for r in rows if r['Pricing Date'].weekday() >= 5])
hol = {datetime.date(2026, 1, 1), datetime.date(2026, 1, 19), datetime.date(2026, 2, 16), datetime.date(2026, 4, 3), datetime.date(2026, 5, 25), datetime.date(2026, 6, 19), datetime.date(2026, 7, 3), datetime.date(2026, 9, 7)}
print('C3 holiday', [r['Ticker'] for r in rows if r['Pricing Date'].date() in hol])
print('C3 date>today', [r['Ticker'] for r in rows if r['Pricing Date'].date() > datetime.date(2026, 11, 20)])
bad = [r['_i'] for r in rows if r['_f'] != '=E%d*F%d' % (r['_i'], r['_i'])]
print('C4 formula bad', bad)
print('C4 link bad', [r['Ticker'] for r in rows if not (r['_link'] and '/Archives/edgar/data/' in r['_link'] and r['Accession No.'].replace('-', '') in r['_link'])])
print('C4 form', collections.Counter(r['Form Type'] for r in rows))
# cover verification against exact chosen filing
SHA = {u: s for u, s in A.c.execute("select distinct source_url,doc_sha256 from evidence")}
fails = []; ok = 0
for r in rows:
    s = SHA.get(r['_link'])
    path = 'cache/raw/' + s if s else None
    if not path or not os.path.exists(path):
        fails.append((r['Ticker'], 'no cached doc')); continue
    t = A.clean(open(path, 'rb').read().decode('utf8', 'ignore'))
    o = R.cover(t)
    sh = [x for x in [o.get('tt') / o['tp'] if o.get('tp') and o.get('tt') else None, o.get('hs')] + o['S'] if x]
    pr = o['price']
    cond_p = pr is not None and abs(pr - float(r['Offer Price'])) < 1e-6
    cond_s = any(abs(x - r['Base Shares Offered']) < 1 for x in sh)
    if cond_p and cond_s: ok += 1
    else: fails.append((r['Ticker'], r['Offer Price'], r['Base Shares Offered'], pr, o['S'][:3], o.get('hs')))
print('C2 cover price+base match', ok, 'of', len(rows), '; unmatched', len(fails))
for f in fails: print('   ', f)
tot = sum(Decimal(str(r['Offer Price'])) * Decimal(r['Base Shares Offered']) for r in rows)
print('total', tot)
top = sorted(rows, key=lambda r: -float(Decimal(str(r['Offer Price'])) * Decimal(r['Base Shares Offered'])))[:5]
for r in top: print('TOP', r['_i'], r['Ticker'], r['Offer Price'], r['Base Shares Offered'], r['Accession No.'], r['Status'])
