from export_print_meshes import *
name='manny';id='elbow_l_flex_M_proximal_forearm';folder=ROOT/f'generated/revM/{name}';p=next(q for q in json.loads((folder/'manufacturing_manifest.json').read_text())['parts'] if q['id']==id);s=cq.importers.importStep(str(folder/p['STEP'])).val().clean();r=p['print']
for axis,angle in zip(((1,0,0),(0,1,0),(0,0,1)),r['euler_xyz_deg']):
 if angle:s=s.rotate((0,0,0),axis,angle)
s=s.translate(r['translation_mm']);orig=s.Volume();edges,counts=mesh_edges(folder/r['STL']);a,b=edges[0];d=b-a;L=np.linalg.norm(d);n=d/L
for width in (.1,.2,.4,1.):
 for ext in (.1,1.,10.):
  cut=cq.Workplane(cq.Plane(origin=tuple(a-ext*n),normal=tuple(n))).rect(width,width).extrude(float(L+ext*2)).val();result=s.cut(cut).clean();out=ROOT/f'generated/revM/mesh_probe/box_{width}_{ext}.stl';mesh_export(result,out);e,c=mesh_edges(out);print(width,ext,'valid',result.isValid(),'solids',len(result.Solids()),'removed',orig-result.Volume(),'bad',c.tolist()[:5],flush=True)
