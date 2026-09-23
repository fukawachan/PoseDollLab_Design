"""Canonical Rev M assembly entry. Self-generated cache is tied to all CAD inputs."""
from shell_mounts import *
import shell_mounts as body
from cad_cache import CadPickler
from assembly_cache import dependencies
import pickle,hashlib,uuid

# Capture geometry dependencies at import, excluding tools which only consume A.
EXCLUDE={'final_model.py','assembly_cache.py','load_budget.py'}
SOURCES=[p for p in dependencies(ROOT) if p.name not in EXCLUDE and not p.name.startswith(('export_','release_','check_','probe_','inspect_','audit_')) and p.resolve()!=Path(getattr(sys.modules['__main__'],'__file__','')).resolve()]
SOURCES.append(Path(__file__).resolve())

def source_hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(SOURCES))}
def build(name):
 sources=source_hashes();key=hashlib.sha256(repr(sorted(sources.items())).encode()).hexdigest();folder=ROOT/'generated/revM/cache';path=folder/f'{name}_complete_{key}.pickle'
 if path.exists():
  with path.open('rb') as f:r=pickle.load(f)
  assert r['source_sha256']==sources;print('Complete model cache',name,key[:12],flush=True);return r['assembly']
 A,meta=body.build(name)
 A.profile=json.loads(json.dumps(A.profile));A.profile['profile_id']=f'physical_{name}_41_revM';A.profile['status']='DIGITAL_PROTOTYPE_CANDIDATE_NOT_MANUFACTURING_RELEASE';A.profile['notes_zh']=['对应角色参考骨架的 1:2 完整机械模型；44 个协议槽位保留。','骨盆三轴为固定参考；整体位置和全部整体旋转由 UE Placement 调整。','41 个相对测量轴；稳定躯段包壳，活动区域裸露；尚未实物鉴定。']
 meta=dict(meta,revision='M',source_sha256=sources,manufacturing_released=False,physical_tested=False)
 temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.partial')
 with temp.open('wb') as f:CadPickler(f,protocol=5).dump(dict(source_sha256=sources,assembly=(A,meta)))
 temp.replace(path);print('Complete model saved',name,key[:12],flush=True);return A,meta
if __name__=='__main__':
 for name in ('manny','quinn'):
  A,meta=build(name);h.save(ROOT/f'mechanical_manifest/wire_anchors_revM_{name}.json',meta['wire_anchors']);print(name,len(A.parts),flush=True)
