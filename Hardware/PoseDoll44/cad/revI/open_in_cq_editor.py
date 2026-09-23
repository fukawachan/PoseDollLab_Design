# Open and run in CQ-editor. Design candidate, not a manufacturing release.
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from shoulder_integration import build,h,COL
CHARACTER='quinn'
POSE='neutral'
SHOW_RESERVED=False
p,parts,metadata=build(CHARACTER)
items,_,_=h.scene(parts,p,h.cases()[POSE])
for item in items:
 if SHOW_RESERVED or item['role']!='reservation':
  show_object(item['shape'],name=item['name'],options={'color':COL[item['material']]})
