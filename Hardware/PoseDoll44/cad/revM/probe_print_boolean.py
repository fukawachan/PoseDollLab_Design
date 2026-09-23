from export_print_meshes import *
name='manny';id='elbow_l_flex_M_proximal_forearm';folder=ROOT/f'generated/revM/{name}';p=next(q for q in json.loads((folder/'manufacturing_manifest.json').read_text())['parts'] if q['id']==id);s=cq.importers.importStep(str(folder/p['STEP'])).val().clean();r=p['print']
for axis,angle in zip(((1,0,0),(0,1,0),(0,0,1)),r['euler_xyz_deg']):
 if angle:s=s.rotate((0,0,0),axis,angle)
s=s.translate(r['translation_mm']);orig=s.Volume();edges,counts=mesh_edges(folder/r['STL']);a,b=edges[0];d=b-a;L=np.linalg.norm(d);n=d/L
for rad in (.1,.2):
 cut=cq.Solid.makeCylinder(rad,float(L+.4),cq.Vector(*(a-.2*n)),cq.Vector(*n));print('cutV',cut.Volume(),flush=True)
 for tol in (None,1e-5,.001,.01):
  result=s.cut(cut,tol=tol);fixed=result.fix().clean();out=ROOT/f'generated/revM/mesh_probe/test_{rad}_{tol}.stl';mesh_export(fixed,out);e,c=mesh_edges(out);print(rad,tol,'rawvalid',result.isValid(),'fixed',fixed.isValid(),'solids',len(fixed.Solids()),'removed',orig-fixed.Volume(),'bad',c.tolist()[:10],flush=True)
