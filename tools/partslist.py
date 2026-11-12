#!/usr/bin/env python3
"""Read the list of parts the team has available and resolve every entry to an LDraw part id.
Parts list = CSV with columns: part_number,category,part_name   (part_number may be blank if the
name contains "(1234 / 5678)"-style numbers). Default: PARTS_AVAILABLE.csv at the repo root;
a team with a different collection puts its own list in profile/parts.csv (or sets FLL_PARTS).
Used by catalog.py and ldbom.py; run directly to see the mapping and any problems."""
import os,re,sys,csv
sys.path.insert(0,os.path.dirname(__file__))
from ldflat import find
from config import PARTS
# same part / same job under another number (LDraw id we use in models : id in the parts list)
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
def load():
    """-> list of dict(pid, name, category, cands, equiv, resolved), in file order"""
    items=[]
    with open(PARTS,newline='',encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            name=(r.get('part_name') or '').strip()
            if not name: continue
            pid,cands=resolve(name,(r.get('part_number') or '').strip() or None)
            ok=pid is not None
            if not ok and cands: pid=cands[0]          # not in the libraries here (e.g. no Stud.io library): keep the number
            items.append(dict(pid=pid,name=name,category=(r.get('category') or 'Other').strip(),cands=cands,equiv=EQUIV.get(pid),resolved=ok))
    return items
if __name__=='__main__':
    print('parts list:',PARTS)
    seen=set()
    for it in load():
        dup=' (DUPLICATE ROW)' if it['pid'] and it['pid'] in seen else ''
        seen.add(it['pid'])
        print(f"{it['category'][:28]:28s} {(it['pid'] if it['resolved'] else '??'):10s} {it['name']}{dup}" + ('' if it['resolved'] else f"   <- not in library; candidates {it['cands']}"))
