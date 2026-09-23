from final_model import *
from OCP.BRepTools import BRepTools
folder=ROOT/'generated/revM/mesh_probe';folder.mkdir(exist_ok=True)
d=json.loads((ROOT/'generated/revM/manny/manufacturing_manifest.json').read_text())
for id in ['elbow_l_flex_M_upperarm_carrier','elbow_l_flex_M_proximal_forearm','N1_case_rear','ball_l_M_toecap_left']:
 p=next(q for q in d['parts'] if q['id']==id);s=cq.importers.importStep(str(ROOT/'generated/revM/manny'/p['STEP'])).val().clean();record=p['print']
 for axis,angle in zip(((1,0,0),(0,1,0),(0,0,1)),record['euler_xyz_deg']):
  if angle:s=s.rotate((0,0,0),axis,angle)
 if record['diagonal']:s=s.moved(cq.Location(cq.Plane(origin=(0,0,0),normal=record['final_plane']['normal'],xDir=record['final_plane']['xdir'])))
 s=s.translate(record['translation_mm']);BRepTools.Clean_s(s.wrapped)
 cq.exporters.export(s,str(folder/(id+'.stl')),tolerance=.01,angularTolerance=.05)
 print(id,'roundtrip clean valid',s.isValid(),len(s.Solids()),flush=True)
