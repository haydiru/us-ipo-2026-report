import sqlite3,openpyxl,collections,datetime,re,json,glob,os,hashlib,random
import sys
wb=openpyxl.load_workbook('output/us_ipo_report_2026.xlsx')
ws=wb['IPO_Report']
rows=[dict(zip([c.value for c in ws[1]],[c.value for c in r])) for r in ws.iter_rows(min_row=2)]
c=sqlite3.connect('runs/ledger.sqlite')
print("rows",len(rows))
# 1 universe
ciks=collections.Counter(); 
db=c.execute("select cik,accession_no,ticker,exchange,pricing_date from ipo_records").fetchall()
print("dup cik",[k for k,v in collections.Counter(r[0] for r in db).items() if v>1])
print("dup tkr+date",[k for k,v in collections.Counter((r[2],r[4]) for r in db).items() if v>1])
print("dup tkr",[k for k,v in collections.Counter(r[2] for r in db).items() if v>1])
print("dup acc",[k for k,v in collections.Counter(r['Accession No.'] for r in rows).items() if v>1])
print("exch",collections.Counter(r['Exchange'] for r in rows))
print("spac",collections.Counter(str(r['Is_SPAC']) for r in rows))
# 3 dates
bad=[]
for r in rows:
    d=r['Pricing Date']
    if d.weekday()>=5: bad.append((r['Ticker'],d.date(),'weekend'))
print("weekend",bad)
hol={datetime.date(2026,1,1),datetime.date(2026,1,19),datetime.date(2026,2,16),datetime.date(2026,4,3),datetime.date(2026,5,25),datetime.date(2026,6,19),datetime.date(2026,7,3),datetime.date(2026,9,7),datetime.date(2026,11,26)}
print("holiday",[(r['Ticker'],r['Pricing Date'].date()) for r in rows if r['Pricing Date'].date() in hol])
# 4 formulas
fb=[]
for i,r in enumerate(ws.iter_rows(min_row=2),start=2):
    g=r[6].value
    if g!=f'=E{i}*F{i}': fb.append((i,g))
print("formula bad",fb[:5],len(fb))
print("links",collections.Counter(str(r['SEC Final Prospectus'])[:30] for r in rows).most_common(3))
print("form",collections.Counter(r['Form Type'] for r in rows))
print("price types",collections.Counter(type(r['Offer Price']).__name__ for r in rows),collections.Counter(type(r['Base Shares Offered']).__name__ for r in rows))
for r in ws.iter_rows(min_row=2,max_row=3): print([ (x.value,x.hyperlink.target if x.hyperlink else None) for x in r[7:9]])
