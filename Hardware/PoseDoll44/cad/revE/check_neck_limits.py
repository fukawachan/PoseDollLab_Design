import sys,json
from pathlib import Path
sys.path.insert(0,str(Path('Hardware/PoseDoll44/cad/revE').resolve()))
from check_proportions import *
for name in ('manny','quinn'):
 c=reference_character(name);p=make_profile(c)
 rows=json.loads((ROOT/'verification/revE_kinematic_comparison.json').read_text())['characters'][name]['poses']
 headrows=[r for r in rows if r['pose'].startswith('head.')]
 print(name, [(r['pose'],round(r['errors_mm']['head'],3)) for r in headrows])
 worst=max(rows,key=lambda r:r['errors_mm']['head'])
 for ids in [('head.',),('head.','waist.'),('head.','chest.')]:
  pose={a:q for a,q in worst['angles_deg'].items() if a.startswith(ids)}
  print(ids,endpoint_error(c,p,pose)['head'])
try:
 import scipy
 print('scipy',scipy.__version__)
except ImportError:print('scipy unavailable')
