"""Content-addressed cache for an explicitly selected complete assembly builder.
Only our locally generated, input-matched BRep cache is read. No external pickle.
"""
from cad_cache import CadPickler
from pathlib import Path
import hashlib,pickle,sys,uuid

def dependencies(root,extra=()):
 cad=root/'cad';files=set()
 for m in list(sys.modules.values()):
  f=getattr(m,'__file__',None)
  if f and Path(f).suffix=='.py' and Path(f).resolve().is_relative_to(cad.resolve()):files.add(Path(f).resolve())
 files.update(root/x for x in extra)
 for pat in ('mechanical_manifest/physical_*_44_revG_humanform_trial.json','generated/revE/*/neutral_landmarks.json'):
  files.update(root.glob(pat))
 files.update(root/x for x in ['generated/revK/components/sensor_revC_mini.step','generated/revC/step/sensor_revB.step','verification/revG_surface_envelopes.json','verification/revE_proportion_baselines.json','electronics/regional_revM/regional_assembly_work.step','electronics/power_revM/power_assembly_work.step','electronics/power_revM/pad_map.json'])
 return sorted(files)

def get_assembly(name,builder,root,tag,extra=()):
 sources={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dependencies(root,extra)}
 key=hashlib.sha256(repr(sorted(sources.items())).encode()).hexdigest();folder=root/'generated/revM/cache';path=folder/(name+'_'+tag+'_'+key+'.pickle')
 if path.exists():
  print('Complete BRep cache hit',name,tag,key[:12],flush=True)
  with path.open('rb') as f:value=pickle.load(f)
  assert value['sources']==sources
  return value['assembly']
 A,meta=builder(name);temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.partial')
 with temp.open('wb') as f:CadPickler(f,protocol=5).dump(dict(sources=sources,assembly=(A,meta)))
 temp.replace(path);print('Complete BRep cache saved',name,tag,key[:12],flush=True)
 return A,meta
