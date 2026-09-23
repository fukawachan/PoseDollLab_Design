"""CQ-editor entry: ideal joint centres and reference links; not manufactured parts."""
from pathlib import Path
import sys,importlib
here=Path(__file__).resolve().parent
for folder in (here.parent,here):
 if str(folder) in sys.path:sys.path.remove(str(folder))
 sys.path.insert(0,str(folder))
import character_reference,build_layout
importlib.reload(character_reference)
importlib.reload(build_layout)
CHARACTER='BOTH' # BOTH, MANNY, QUINN
POSE='neutral' # neutral, hands_together_tip_contact, hand_to_forehead_tip_contact, sitting...
for name in ('manny','quinn'):
 if CHARACTER.upper() not in ('BOTH',name.upper()):continue
 c=character_reference.reference_character(name);p=character_reference.make_profile(c)
 poses=character_reference.json.loads((character_reference.OUT/name/'pose_samples.json').read_text(encoding='utf8'))['poses']
 offset=(0,(-170 if name=='manny' else 170) if CHARACTER.upper()=='BOTH' else 0,0)
 for label,shape,color in build_layout.cad_items(c,p,poses[POSE]):
  show_object(shape.translate(offset),name=name+'__'+label.replace('.','_'),options={'color':color})
