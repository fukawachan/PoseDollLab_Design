from export_print_meshes import *
A,meta=build('manny');id='elbow_l_flex_M_proximal_forearm';p=next(q for q in json.loads((ROOT/'generated/revM/manny/manufacturing_manifest.json').read_text())['parts'] if q['id']==id);s=next(q['local_shape'] for q in A.parts if q['name']==id).clean();r=p['print']
for axis,angle in zip(((1,0,0),(0,1,0),(0,0,1)),r['euler_xyz_deg']):
 if angle:s=s.rotate((0,0,0),axis,angle)
s=s.translate(r['translation_mm']);tmp=ROOT/'generated/revM/mesh_probe/native.stl';mesh_export(s,tmp);edges,c=mesh_edges(tmp);print('native bad',c.tolist(),edges.tolist(),flush=True)
for i,edge in enumerate(edges[:1]):
 a,b=edge;d=b-a;L=np.linalg.norm(d);n=d/L
 for tol in (None,1e-5,.001):
  cutter=cq.Solid.makeCylinder(.1,float(L+.2),cq.Vector(*(a-.1*n)),cq.Vector(*n));cut=s.cut(cutter,tol=tol).clean();print('nativecut',tol,cut.isValid(),len(cut.Solids()),s.Volume()-cut.Volume(),'shells',len(cut.Shells()),flush=True)
