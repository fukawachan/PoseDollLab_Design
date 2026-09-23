from pathlib import Path
import sys
_revl_dir=Path(__file__).resolve().parent
sys.path.insert(0,str(_revl_dir))
from flex_encoder import *
character='quinn'
p,parts,meta=build(character)
items,_,_=h.scene(parts,p,{})
for q in items:
    if q['role']!='reservation':
        show_object(q['shape'],name=q['name'],options={'color':COL[q['material']]})
