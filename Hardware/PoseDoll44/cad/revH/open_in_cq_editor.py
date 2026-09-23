# Open this file in CQ-editor and run it. Geometry is a packaging candidate.
from pathlib import Path
import sys
folder = Path(__file__).resolve().parent
sys.path.insert(0,str(folder))
from shoulder_mechanism import build,scene,cases,COL
CHARACTER = 'quinn'
POSE = 'neutral'
SHOW_RESERVED = False
profile,parts,metadata = build(CHARACTER)
items,transforms,axes = scene(parts,profile,cases()[POSE])
for item in items:
    if SHOW_RESERVED or item['role'] != 'reservation':
        show_object(item['shape'],name=item['name'],options={'color':COL[item['material']]})
