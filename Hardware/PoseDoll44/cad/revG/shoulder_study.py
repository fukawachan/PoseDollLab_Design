"""Shoulder-girdle motion reference for intentionally exposed moving regions.
UE skinning is a visual reference, not material simulation of a physical cover.
"""
from pathlib import Path
import sys,json,math
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OUT=ROOT/'generated/revG'
sys.path.insert(0,str(HERE.parent/'revE'))
from character_reference import reference_character,make_profile,fk
from build_layout import skin_pose,polydata,actor,text
from vtkmodules.vtkFiltersCore import vtkQuadricDecimation
from vtkmodules.vtkRenderingCore import vtkRenderer,vtkRenderWindow,vtkWindowToImageFilter
from vtkmodules.vtkIOImage import vtkPNGWriter
SCALE_FACTOR=1.5
POSES={'neutral':('自然',0,0),'forward':('双肩前伸',30,0),'backward':('双肩后收',-20,0),'shrug':('耸肩',0,30),'down':('肩部下压',0,-15),'forward_up':('前伸并耸肩',30,30),'asymmetric':('左肩前伸、右肩后收',30,0)}
def save(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
def skin_mesh(c,p,pose):
 verts=skin_pose(c,p,pose)*SCALE_FACTOR;faces=np.array(c['geometry']['triangles'])
 keep=verts[faces].min(axis=1)[:,2]>c['points']['pelvis'][2]*SCALE_FACTOR-15
 mesh=polydata(verts,faces[keep]);dec=vtkQuadricDecimation();dec.SetInputData(mesh);dec.SetTargetReduction(.88);dec.Update();small=dec.GetOutput()
 return {'vertices':[[round(v,3) for v in small.GetPoint(i)] for i in range(small.GetNumberOfPoints())],'triangles':[[small.GetCell(i).GetPointId(j) for j in range(3)] for i in range(small.GetNumberOfCells())]}

def main():
 report={'status':'KINEMATIC_SHOULDER_AND_COVER_BOUNDARY_STUDY','hardware_shoulder_validated':False,'soft_material_simulated':False,'new_trial_scale':.5,'cover_policy':'EXPOSED_DEFORMING_REGIONS','soft_cover_required':False,'characters':{}}
 viewer={'poses':{k:v[0] for k,v in POSES.items()},'characters':{}}
 for name in ('manny','quinn'):
  c=reference_character(name);p=make_profile(c);T0,A0=fk(p,{});rows=[];views={}
  for key,(label,pro,ele) in POSES.items():
   q={f'clavicle_{side}.{axis}':value for side in ('l','r') for axis,value in [('protract',pro),('elevate',ele)]}
   if key=='asymmetric':q['clavicle_r.protract']=-20
   T,A=fk(p,q);points={};shoulders={};spans=[]
   for side in ('l','r'):
    sid='upperarm_'+side+'.flex';base=A0[sid]['origin']*SCALE_FACTOR;current=A[sid]['origin']*SCALE_FACTOR
    shoulders[side]={'neutral_mm':base.tolist(),'posed_mm':current.tolist(),'delta_mm':(current-base).tolist(),'travel_mm':float(np.linalg.norm(current-base))}
    points['clavicle_'+side]=(A['clavicle_'+side+'.protract']['origin']*SCALE_FACTOR).tolist();points['shoulder_'+side]=current.tolist();points['elbow_'+side]=(A['elbow_'+side+'.flex']['origin']*SCALE_FACTOR).tolist()
    root=A0['clavicle_'+side+'.protract']['origin']*SCALE_FACTOR;sign=1 if side=='l' else -1
    R=T['clavicle_'+side][:3,:3]@T0['clavicle_'+side][:3,:3].T
    for region,x in [('front',18),('back',-18)]:
     fixed=root+.48*(base-root)+[x,0,-10]
     mobile0=base+[x,-sign*16,0];mobile=root+R@(mobile0-root)
     spans.append({'side':side,'region':region,'fixed_anchor_mm':fixed.tolist(),'moving_anchor_mm':mobile.tolist(),'neutral_straight_span_mm':float(np.linalg.norm(mobile0-fixed)),'posed_straight_span_mm':float(np.linalg.norm(mobile-fixed))})
   rows.append({'pose':key,'label':label,'angles_deg':q,'shoulders':shoulders,'illustrative_cover_spans':spans})
   views[key]=skin_mesh(c,p,q)|{'points':points,'spans':spans,'angles':q,'label':label}
  report['characters'][name]={'axis_ranges_deg':{'protract':[-20,30],'elevate':[-15,30]},'poses':rows,'maximum_sampled_shoulder_travel_mm':max(s['travel_mm'] for r in rows for s in r['shoulders'].values()),'cover_boundary_note':'Illustrative anchor pairs, not attachment points on a completed shell. Straight spans are geometric gap distances, not strain, soft material force or required skin length.'}
  viewer['characters'][name]=views
  print(json.dumps({'name':name,'motions':[(r['pose'],r['shoulders']['l']['delta_mm'],r['shoulders']['l']['travel_mm']) for r in rows]},ensure_ascii=False),flush=True)
 save(ROOT/'verification/revG_shoulder_motion.json',report)
 save(OUT/'viewer/shoulder_data.json',viewer)
 template=(HERE/'shoulder_review.template.html').read_text(encoding='utf8')
 (OUT/'Human_Form_and_Shoulder_Review.html').write_text(template.replace('__DATA__',json.dumps(viewer,separators=(',',':'))),encoding='utf8')
 # Two poses of Quinn with real reference skin deformation, clearly labelled.
 rr=vtkRenderer();rr.SetBackground(.955,.967,.973)
 for pose,offset in [('neutral',-145),('forward_up',145)]:
  d=viewer['characters']['quinn'][pose];verts=np.array(d['vertices'])+[0,offset,0];rr.AddActor(actor(polydata(verts,d['triangles']),(.65,.73,.77)))
 text(rr,'QUINN | SHOULDER-GIRDLE MOTION',30,865,26)
 text(rr,'Neutral (left) / forward + raised (right) | 1:2 size study',30,830,19)
 text(rr,'UE mesh deformation reference. Physical shoulder mechanism and soft cover are not validated.',30,22,15)
 cam=rr.GetActiveCamera();focus=np.array([0,0,700]);cam.SetFocalPoint(*focus);cam.SetPosition(*(focus+[1800,-550,120]));cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(315);rr.ResetCameraClippingRange()
 win=vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1200,920);win.AddRenderer(rr);win.Render();grab=vtkWindowToImageFilter();grab.SetInput(win);grab.Update();writer=vtkPNGWriter();writer.SetFileName(str(OUT/'images/Quinn_shoulder_motion_reference.png'));writer.SetInputConnection(grab.GetOutputPort());writer.Write();win.Finalize()
if __name__=='__main__':main()
