from export_print_meshes import *
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
name='manny';id='elbow_l_flex_M_proximal_forearm';folder=ROOT/f'generated/revM/{name}';p=next(q for q in json.loads((folder/'manufacturing_manifest.json').read_text())['parts'] if q['id']==id);s=cq.importers.importStep(str(folder/p['STEP'])).val().clean();r=p['print']
for axis,angle in zip(((1,0,0),(0,1,0),(0,0,1)),r['euler_xyz_deg']):
 if angle:s=s.rotate((0,0,0),axis,angle)
s=s.translate(r['translation_mm']);edges,c=mesh_edges(folder/r['STL']);a,b=edges[0];d=b-a;L=np.linalg.norm(d);n=d/L;tool=cq.Solid.makeCylinder(.1,float(L+.2),cq.Vector(*(a-.1*n)),cq.Vector(*n));result=s.fuse(tool).clean();an=BRepCheck_Analyzer(result.wrapped)
for category,sub in [('face',result.Faces()),('edge',result.Edges()),('shell',result.Shells()),('solid',result.Solids())]:
 for i,q in enumerate(sub):
  stats=[str(v) for v in an.Result(q.wrapped).Status()]
  if stats!=['BRepCheck_Status.BRepCheck_NoError']:print(category,i,stats,flush=True)
for tol in (1e-5,.0001,.001,.01,.05):
 fix=ShapeFix_Shape(result.wrapped);fix.SetPrecision(tol);fix.SetMaxTolerance(tol*10);fix.Perform();q=cq.Shape.cast(fix.Shape());print('fix',tol,q.isValid(),len(q.Solids()),q.Volume()-s.Volume(),flush=True)
