"""Content-addressed local BRep build cache for iterative integration checks.
Cache is private generated work data, never a released design input.
"""
from assembly_core import *
import pickle,io,hashlib,uuid

def restore_shape(b):return cq.Shape.importBrep(io.BytesIO(b))
def restore_loc(t,r):return cq.Location(t,r)
class CadPickler(pickle.Pickler):
 def reducer_override(self,o):
  if isinstance(o,cq.Shape):
   s=io.BytesIO();o.exportBrep(s);return restore_shape,(s.getvalue(),)
  if isinstance(o,cq.Location):
   t,r=o.toTuple();return restore_loc,(t,r)
  return NotImplemented

def get_body(name,builder):
 src=[p for p in (ROOT/'cad').rglob('*.py') if p.parent.name!='revM' or p.name in {'compact_axis.py','assembly_core.py','arm_integration.py','wrist_integration.py','hand_shells.py','mechanism_modules.py','leg_integration.py','trunk_integration.py','neck_module.py','body_integration.py','twist_completion.py'}]
 src += [ROOT/f'mechanical_manifest/physical_{name}_44_revG_humanform_trial.json',ROOT/'generated/revK/components/sensor_revC_mini.step',ROOT/'generated/revC/step/sensor_revB.step',ROOT/'verification/revG_surface_envelopes.json',ROOT/'verification/revE_proportion_baselines.json',ROOT/f'generated/revE/{name}/neutral_landmarks.json']
 digest=hashlib.sha256()
 for p in sorted(src):
  if not p.exists():raise FileNotFoundError('Missing CAD cache dependency: '+str(p))
  digest.update(str(p.relative_to(ROOT)).encode());digest.update(p.read_bytes())
 key=digest.hexdigest();folder=ROOT/'generated/revM/cache';folder.mkdir(parents=True,exist_ok=True);path=folder/(name+'_body_'+key+'.pickle')
 if path.exists():
  print('BRep body cache hit',name,key[:12],flush=True)
  with path.open('rb') as f:return pickle.load(f)
 value=builder(name)
 temporary=path.with_name(path.name+'.'+uuid.uuid4().hex+'.partial')
 with temporary.open('wb') as f:CadPickler(f,protocol=5).dump(value)
 temporary.replace(path)
 print('BRep body cache saved',name,key[:12],flush=True);return value
