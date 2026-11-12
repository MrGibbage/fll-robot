#!/usr/bin/env python3
"""Read the team's parts inventory and resolve every entry to an LDraw part id.
Inventory = CSV with columns: tray,tray_name,part_name,part_number   (part_number may be blank if the
name contains "(1234 / 5678)"-style numbers). An .xlsx with sheets "Trays" and "Parts" also works.
Used by catalog.py and ldbom.py; run directly to see the mapping and any problems."""
import os,re,sys
sys.path.insert(0,os.path.dirname(__file__))
from ldflat import find
from config import INVENTORY
# same part / same job under another number (LDraw id we use in models : id in the trays)
EQUIV={'44874':'87082','59443':'6538a'}
def canonical(pid):
    """follow LDraw aliases ('=...') and renames ('~Moved to X') to the part file we actually use"""
    for _ in range(4):
        f=find(pid+'.dat')
        if not f: return pid
        lines=open(f,errors='replace').read().splitlines()
        d=lines[0][2:].strip() if lines else ''
        if d.startswith('~Moved to'): pid=d.split()[-1]; continue
        if d.startswith('='):
            refs=[l.split()[-1] for l in lines if l.startswith('1 ')]
            if len(refs)==1: pid=refs[0].replace('.dat',''); continue
        return pid
    return pid
def resolve(name,num):
    cands=[str(num)] if num else []
    for grp in re.findall(r'\(([^()]*)\)',name or ''):
        cands+=re.findall(r'\b(\d{4,6}[a-z]?)\b',grp)
    for c in cands:
        for v in (c, c+'a', c+'b', c+'c01', c+'p01'):
            if find(v+'.dat'): return canonical(v), cands
    return None, cands
def _rows():
    if INVENTORY.lower().endswith('.xlsx'):
        import openpyxl
        wb=openpyxl.load_workbook(INVENTORY,data_only=True)
        for tray,trayname,name,num in wb['Parts'].iter_rows(min_row=2,values_only=True):
            yield tray,trayname,name,num
    else:
        import csv
        with open(INVENTORY,newline='',encoding='utf-8') as fh:
            for r in csv.DictReader(fh):
                t=r.get('tray') or None
                yield (int(t) if t and t.isdigit() else t), r.get('tray_name'), r.get('part_name'), (r.get('part_number') or None)
def load():
    trays={}; items=[]
    for tray,trayname,name,num in _rows():
        if not name: continue
        if tray is not None: trays.setdefault(tray,trayname)
        pid,cands=resolve(name,num)
        items.append(dict(tray=tray,trayname=trayname,name=name,pid=pid,cands=cands,equiv=EQUIV.get(pid)))
    return trays,items
if __name__=='__main__':
    trays,items=load()
    seen={}
    for it in items:
        dup=' (DUPLICATE ROW)' if it['pid'] and it['pid'] in seen else ''
        seen.setdefault(it['pid'],it)
        print(f"tray {str(it['tray']):>3} {it['pid'] or '??':10s} {it['name']}{dup}" + ('' if it['pid'] else f"   <- candidates {it['cands']}"))
