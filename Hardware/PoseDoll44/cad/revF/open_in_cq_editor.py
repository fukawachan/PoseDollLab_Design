"""CQ-editor entry for the Rev F mechanical assemblies. Development, not print release."""
from pathlib import Path
import sys,importlib
folder=Path(__file__).resolve().parent
if str(folder) in sys.path:sys.path.remove(str(folder))
sys.path.insert(0,str(folder))
# Re-evaluating in the same CQ-editor must not reuse cached old geometry.
for module_name in ('arm_packaging','fork_joint','pivot','common'):
 sys.modules.pop(module_name,None)
from arm_packaging import geometry,neutral_joint,COL
VIEW='BOTH' # BOTH / MANNY / QUINN / JOINT
ELBOW_DEG=0 # 0 .. 145
WRIST_DEG=0 # -65 .. 65
if VIEW=='JOINT':
 for p in neutral_joint('M6')[0]:show_object(p['shape'],name=p['name'],options={'color':COL[p['material']]})
else:
 for name in ('manny','quinn'):
  if VIEW.upper() not in ('BOTH',name.upper()):continue
  offset=(0,(-100 if name=='manny' else 100) if VIEW.upper()=='BOTH' else 0,0)
  for p in geometry(name,ELBOW_DEG,WRIST_DEG)[0]:show_object(p['shape'].translate(offset),name=name+'_'+p['name'],options={'color':COL[p['material']]})
