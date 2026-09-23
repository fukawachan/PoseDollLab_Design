from export_print_meshes import *
name='quinn';id='elbow_r_flex_M_proximal_forearm';folder=ROOT/f'generated/revM/{name}';p=next(q for q in json.loads((folder/'manufacturing_manifest.json').read_text())['parts'] if q['id']==id);s=cq.importers.importStep(str(folder/p['STEP'])).val().clean();r=p['print']
for axis,angle in zip(((1,0,0),(0,1,0),(0,0,1)),r['euler_xyz_deg']):
 if angle:s=s.rotate((0,0,0),axis,angle)
s=s.translate(r['translation_mm']);edges,c=mesh_edges(folder/r['STL']);a,b=edges[0];d=b-a;L=np.linalg.norm(d);n=d/L;print('source',s.ShapeType(),len(s.Solids()),'edge',edges.tolist(),flush=True)
for radius in (.05,.1,.15,.2,.3):
 for tol in (None,1e-6,1e-5,.0001,.001):
  tool=cq.Solid.makeCylinder(radius,float(L+.2),cq.Vector(*(a-.1*n)),cq.Vector(*n));q=s.Solids()[0].fuse(tool,tol=tol).clean();fix=ShapeFix_Shape(q.wrapped);fix.SetPrecision(1e-5);fix.SetMaxTolerance(1e-4);fix.Perform();q=cq.Shape.cast(fix.Shape())
  if q.isValid() and len(q.Solids())==1:
   delta=q.Volume()-s.Volume();tmp=ROOT/f'generated/revM/mesh_probe/quinn_var_{radius}_{tol}.stl';mesh_export(q,tmp);e,ct=mesh_edges(tmp);print('candidate',radius,tol,delta,'bad',ct.tolist()[:6],flush=True)
