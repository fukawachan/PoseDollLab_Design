"""Validate delivered binary STL bounds, closed edge incidence and volume."""
from pathlib import Path
import json,hashlib,struct,collections,numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
 out={}
 for name in ('manny','quinn'):
  folder=ROOT/f'generated/revM/{name}';mf=folder/'manufacturing_manifest.json';d=json.loads(mf.read_text());rows=[]
  for part in d['parts']:
   if 'print' not in part:continue
   path=folder/part['print']['STL'];raw=path.read_bytes();count=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*count
   triangles=np.frombuffer(raw,offset=84,dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')]))['vertices'].astype(np.float64);assert np.isfinite(triangles).all() and count>0
   vertices=triangles.reshape(-1,3);bounds=vertices.max(0)-vertices.min(0);error=float(np.max(np.abs(bounds-np.array(part['print']['bounds_mm']))));assert error<.101,(name,part['id'],error)
   # Use the exported float32 coordinates exactly; ignore zero-area repeated-index facets.
   _,index=np.unique(vertices,axis=0,return_inverse=True);faces=index.reshape(-1,3);faces=faces[(faces[:,0]!=faces[:,1])&(faces[:,0]!=faces[:,2])&(faces[:,1]!=faces[:,2])];edges=np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]);edges.sort(axis=1);edges=edges[edges[:,0]!=edges[:,1]];_,n=np.unique(edges,axis=0,return_counts=True);bad=int(np.count_nonzero(n!=2))
   assert max(bounds[0]+6,bounds[1]+6,bounds[2])<=180,(name,part['id'],'actual STL exceeds printer envelope')
   volume=abs(float(np.sum(np.einsum('ij,ij->i',triangles[:,0],np.cross(triangles[:,1],triangles[:,2])))/6));relative=abs(volume-part['volume_mm3'])/part['volume_mm3']
   rows.append(dict(id=part['id'],triangles=count,actual_bounds_mm=bounds.tolist(),minimum_coordinates_mm=vertices.min(0).tolist(),a1_mini_actual_bounds_with_3mm_brim=True,bounds_error_mm=error,bounds_error_limit_mm=.101,non_two_incidence_edges=bad,mesh_volume_mm3=volume,CAD_volume_mm3=part['volume_mm3'],relative_volume_error=relative,sha256=hashlib.sha256(raw).hexdigest()))
  bad=[r for r in rows if r['non_two_incidence_edges'] or r['relative_volume_error']>.05]
  out[name]=dict(source_cad_sha256=d['source_sha256'],source_manifest_sha256=hashlib.sha256(mf.read_bytes()).hexdigest(),count=len(rows),passed=not bad,checks=rows,scope='Closed-edge incidence at exact STL float32 coordinates, degenerate repeated-index facets omitted; bounds (including documented R0.10 mm print-process beads, 0.101 mm extent tolerance) and volume; no slicer path, support or strength validation.');print(name,len(rows),'STL checks','PASS' if not bad else 'FAIL',bad[:6],flush=True)
 (ROOT/'verification/revM_print_exports.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
 if not all(d['passed'] for d in out.values()):raise SystemExit(1)
if __name__=='__main__':main()
