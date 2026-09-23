from pathlib import Path
import sys
_revk_dir=Path(__file__).resolve().parent
sys.path.insert(0,str(_revk_dir))
from compact_twist import *
character='quinn'
p,parts,meta=build(character)
items,_,_=h.scene(parts,p,{})
for q in items:
 if q['role']!='reservation':
  show_object(q['shape'],name=q['name'],options={'color':COL[q['material']]})
