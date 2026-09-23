from export_print_meshes import *
name='quinn';id='elbow_r_flex_M_proximal_forearm';folder=ROOT/f'generated/revM/{name}';p=next(q for q in json.loads((folder/'manufacturing_manifest.json').read_text())['parts'] if q['id']==id);s=cq.importers.importStep(str(folder/p['STEP'])).val().clean();r=p['print']
for axis,angle in zip(((1,0,0),(0,1,0),(0,0,1)),r['euler_xyz_deg']):
 if angle:s=s.rotate((0,0,0),axis,angle)
s=s.translate(r['translation_mm']);edges,c=mesh_edges(folder/r['STL']);a,b=edges[0];d=b-a;L=np.linalg.norm(d);n=d/L
for reverse in (False,True):
 start,end=(b,a) if reverse else (a,b);vec=(end-start)/L
 for turn in (0,30,60,90,135):
  for offset in ((0,0,0),(.001,.001,.001)):
   tool=cq.Solid.makeCylinder(.1,float(L+.2),cq.Vector(*(start-.1*vec)),cq.Vector(*vec)).rotate(tuple(a),tuple(b),turn).translate(offset);q=s.fuse(tool).clean();fix=ShapeFix_Shape(q.wrapped);fix.SetPrecision(1e-5);fix.SetMaxTolerance(1e-4);fix.Perform();q=cq.Shape.cast(fix.Shape())
   if q.isValid() and len(q.Solids())==1:
    tmp=ROOT/f'generated/revM/mesh_probe/quinn_ok_{reverse}_{turn}_{offset[0]}.stl';mesh_export(q,tmp);e,ct=mesh_edges(tmp);print('candidate',reverse,turn,offset,q.Volume()-s.Volume(),'bad',ct.tolist()[:6],flush=True)
