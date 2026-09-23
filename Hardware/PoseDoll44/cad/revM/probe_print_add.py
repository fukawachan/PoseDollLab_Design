from export_print_meshes import *
name='manny';id='elbow_l_flex_M_proximal_forearm';folder=ROOT/f'generated/revM/{name}';p=next(q for q in json.loads((folder/'manufacturing_manifest.json').read_text())['parts'] if q['id']==id);s=cq.importers.importStep(str(folder/p['STEP'])).val().clean();r=p['print']
for axis,angle in zip(((1,0,0),(0,1,0),(0,0,1)),r['euler_xyz_deg']):
 if angle:s=s.rotate((0,0,0),axis,angle)
s=s.translate(r['translation_mm']);orig=s.Volume();edges,c=mesh_edges(folder/r['STL']);a,b=edges[0];d=b-a;L=np.linalg.norm(d);n=d/L
for rad in (.1,.2,.4):
 tool=cq.Solid.makeCylinder(rad,float(L+.2),cq.Vector(*(a-.1*n)),cq.Vector(*n));result=s.fuse(tool).clean();out=ROOT/f'generated/revM/mesh_probe/add_{rad}.stl';mesh_export(result,out);e,c=mesh_edges(out);print(rad,'valid',result.isValid(),'solids',len(result.Solids()),'delta',result.Volume()-orig,'tool',tool.Volume(),'bad',c.tolist()[:8],flush=True)
