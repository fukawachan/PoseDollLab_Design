from export_print_meshes import *
from OCP.ShapeFix import ShapeFix_ShapeTolerance
from OCP.TopAbs import TopAbs_VERTEX,TopAbs_EDGE
folder=ROOT/'generated/revM/manny';id='elbow_l_flex_M_proximal_forearm';p=next(q for q in json.loads((folder/'manufacturing_manifest.json').read_text())['parts'] if q['id']==id);s=cq.importers.importStep(str(folder/p['STEP'])).val().clean();r=p['print']
for axis,angle in zip(((1,0,0),(0,1,0),(0,0,1)),r['euler_xyz_deg']):
 if angle:s=s.rotate((0,0,0),axis,angle)
s=s.translate(r['translation_mm']);data=json.loads((ROOT/'verification/revM_print_mesh_export.json').read_text());row=next(q for q in data['manny']['prints'] if q['id']==id)
for edge in row['reliefs']:
 a,b=np.array(edge['edge_in_print_coordinates_mm']);d=b-a;L=np.linalg.norm(d);n=d/L
 if n[int(np.argmax(abs(n)))]<0:a,b=b,a;n=-n
 tool=cq.Solid.makeCylinder(.1,float(L+.2),cq.Vector(*(a-.1*n)),cq.Vector(*n));s=s.fuse(tool).clean()
fix=ShapeFix_Shape(s.wrapped);fix.SetPrecision(1e-5);fix.SetMaxTolerance(1e-4);fix.Perform();s=cq.Shape.cast(fix.Shape());print('native',s.isValid(),flush=True)
for adjust in (False,True):
 if adjust:
  t=ShapeFix_ShapeTolerance();t.SetTolerance(s.wrapped,1e-4,TopAbs_VERTEX);t.SetTolerance(s.wrapped,1e-4,TopAbs_EDGE)
 for pc in (True,False):
  for precision in (-1,0,1):
   file=ROOT/f'generated/revM/mesh_probe/step_{adjust}_{pc}_{precision}.step';s.exportStep(str(file),write_pcurves=pc,precision_mode=precision);q=cq.importers.importStep(str(file)).val();print(adjust,pc,precision,q.isValid(),len(q.Solids()),q.Volume()-row['print_process_volume_mm3'],flush=True)
