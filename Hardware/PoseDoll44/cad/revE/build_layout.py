"""Two exact-scale joint-centre CAD layouts and actual mesh reference previews.
The STEP entities are construction geometry, not manufactured joint parts.
"""
from character_reference import *
from check_proportions import expected_bones,physical_points
import cadquery as cq
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPolyData,vtkCellArray
from vtkmodules.vtkFiltersCore import vtkPolyDataNormals,vtkQuadricDecimation
from vtkmodules.vtkRenderingCore import vtkActor,vtkPolyDataMapper,vtkRenderer,vtkRenderWindow,vtkWindowToImageFilter,vtkTextActor
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkIOPLY import vtkPLYWriter
import vtkmodules.vtkRenderingOpenGL2,vtkmodules.vtkRenderingFreeType

def rod(a,b,r):
 a=np.array(a);b=np.array(b);d=b-a;length=np.linalg.norm(d)
 return cq.Solid.makeCylinder(r,float(length),cq.Vector(*a),cq.Vector(*(d/length)))

def cad_items(c,p,pose=None):
 pose=pose or {};T,A=fk(p,pose);items=[]
 for node in p['nodes']:
  parent=node['parent']
  if parent is None or parent=='device_base':continue
  a=T[parent][:3,3];b=T[node['id']][:3,3]
  if np.linalg.norm(b-a)>1e-4:items.append(('REFERENCE_LINK__'+node['id'],rod(a,b,1.4),(.24,.32,.38)))
 for i,(aid,a) in enumerate(A.items()):
  centre=a['origin'];direction=a['direction']
  # Each line is the exact rotation axis through the target pivot, not a load shaft.
  color=(.93,.35,.19) if i%3==0 else ((.25,.65,.48) if i%3==1 else (.25,.46,.83))
  items.append(('REFERENCE_AXIS__'+aid,rod(centre-direction*6,centre+direction*6,.6),color))
 for name,position in physical_points(c,p,pose).items():
  if name.startswith('tip_'):continue
  items.append(('LANDMARK__'+name,cq.Solid.makeSphere(2.4,cq.Vector(*position)),(.08,.27,.37)))
 return items

def polydata(vertices,faces):
 pts=vtkPoints()
 for v in vertices:pts.InsertNextPoint(*v)
 cells=vtkCellArray()
 for f in faces:
  cells.InsertNextCell(3)
  for i in f:cells.InsertCellPoint(int(i))
 mesh=vtkPolyData();mesh.SetPoints(pts);mesh.SetPolys(cells);return mesh

def actor(mesh,color,opacity=1):
 normal=vtkPolyDataNormals();normal.SetInputData(mesh);normal.ComputePointNormalsOn();normal.SplittingOff()
 mapper=vtkPolyDataMapper();mapper.SetInputConnection(normal.GetOutputPort());obj=vtkActor();obj.SetMapper(mapper)
 obj.GetProperty().SetColor(*color);obj.GetProperty().SetOpacity(opacity);obj.GetProperty().SetAmbient(.25);obj.GetProperty().SetDiffuse(.75)
 return obj

def skin_pose(c,p,pose):
 G=expected_bones(c,p,pose);geo=c['geometry'];positions=np.array(geo['positions_cm']);out=np.zeros_like(positions);weightsum=np.zeros(len(positions));bybone=[[] for _ in c['names']]
 for vi,weights in enumerate(geo['skin_weights']):
  for bi,w in weights:bybone[bi].append((vi,w))
 for bi,items in enumerate(bybone):
  if not items:continue
  ids=np.array([v[0] for v in items]);w=np.array([v[1] for v in items]);delta=G[c['names'][bi]]@np.linalg.inv(c['reference'][bi])
  out[ids]+=(positions[ids]@delta[:3,:3].T+delta[:3,3])*w[:,None];weightsum[ids]+=w
 return (out/weightsum[:,None])@SWAP.T*10*SCALE+c['shift_mm']

def text(renderer,value,x,y,size,color=(.12,.18,.23)):
 t=vtkTextActor();t.SetInput(value);t.SetDisplayPosition(x,y);t.GetTextProperty().SetFontSize(size);t.GetTextProperty().SetColor(*color);renderer.AddActor2D(t)

def render_pair(characters,dest,pose_name='neutral',view='front',overlay=True):
 renderer=vtkRenderer();renderer.SetBackground(.954,.963,.975);offsets=(-170,170);colors=((.18,.51,.66),(.58,.32,.58))
 for ci,(c,p) in enumerate(characters):
  samples=json.loads((OUT/c['name']/'pose_samples.json').read_text(encoding='utf8'))['poses'];pose=samples[pose_name]
  verts=c['vertices_mm'] if not pose else skin_pose(c,p,pose)
  shift=np.array([0,offsets[ci],0]);mesh=polydata(verts+shift,c['geometry']['triangles']);renderer.AddActor(actor(mesh,colors[ci],.22 if overlay else 1))
  if overlay:
   for n,s,color in cad_items(c,p,pose):
    vertices,faces=s.tessellate(.3);ps=np.array([v.toTuple() for v in vertices])+shift
    renderer.AddActor(actor(polydata(ps,faces),color))
 text(renderer,'POSEDOLL 44 / REV E',44,864,28)
 text(renderer,'Manny + Quinn | same 1:3 scale | '+pose_name.replace('_',' '),44,832,21)
 text(renderer,'Reference surfaces + ideal joint centres. Mechanical packaging is pending.',44,25,17)
 text(renderer,'MANNY / blue',315,65,18,(.18,.40,.52))
 text(renderer,'QUINN / plum',740,65,18,(.48,.28,.48))
 cam=renderer.GetActiveCamera();focus=np.array([0,0,300.]);cam.SetFocalPoint(*focus)
 direction=np.array([1600,0,0.]) if view=='front' else np.array([1500,-1800,500.])
 cam.SetPosition(*(focus+direction));cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(425);renderer.ResetCameraClippingRange()
 win=vtkRenderWindow();win.SetOffScreenRendering(1);win.SetMultiSamples(4);win.SetSize(1200,920);win.AddRenderer(renderer);win.Render()
 snap=vtkWindowToImageFilter();snap.SetInput(win);snap.ReadFrontBufferOff();snap.Update();writer=vtkPNGWriter();writer.SetFileName(str(dest));writer.SetInputConnection(snap.GetOutputPort());writer.Write();win.Finalize()

def main():
 pairs=[];report={'status':'JOINT_CENTRE_CAD_AND_REFERENCE_SURFACES_NOT_MANUFACTURED_PARTS','characters':{}}
 for name in ('manny','quinn'):
  c=reference_character(name);p=make_profile(c);pairs.append((c,p));folder=OUT/name
  items=cad_items(c,p);assembly=cq.Assembly(name=name.title()+'_44_proportion_layout')
  for label,shape,color in items:
   if not shape.isValid():raise ValueError(label)
   assembly.add(shape,name=label.replace('.','_'),color=cq.Color(*color))
  step=folder/(name.title()+'_44_proportion_layout.step');assembly.save(str(step))
  mesh=polydata(c['vertices_mm'],c['geometry']['triangles']);ply=vtkPLYWriter();ply.SetInputData(mesh);ply.SetFileName(str(folder/(name+'_surface_reference.ply')));ply.SetFileTypeToBinary();ply.Write()
  # Compact standalone browser viewer data, not the measurement source.
  decimate=vtkQuadricDecimation();decimate.SetInputData(mesh);decimate.SetTargetReduction(.94);decimate.Update();small=decimate.GetOutput()
  pts=[list(small.GetPoint(i)) for i in range(small.GetNumberOfPoints())];tri=[]
  for i in range(small.GetNumberOfCells()):
   cell=small.GetCell(i);tri.extend([cell.GetPointId(j) for j in range(3)])
  _,A=fk(p,{})
  view={'name':name,'vertices':[round(v,3) for point in pts for v in point],'triangles':tri,'joints':{a:v['origin'].tolist() for a,v in A.items()},'height_mm':c['height_mm']}
  save(folder/'viewer_data.json',view)
  report['characters'][name]={'step':str(step.relative_to(ROOT)),'entity_count':len(items),'axis_count':len(A),'all_reference_shapes_valid':True,'surface_vertices':len(c['vertices_mm']),'surface_triangles':len(c['geometry']['triangles']),'manufacturing_release':False}
  print(json.dumps({'name':name,'step_entities':len(items),'viewer_triangles':small.GetNumberOfCells()}),flush=True)
 images=OUT/'images';images.mkdir(exist_ok=True)
 render_pair(pairs,images/'Manny_Quinn_proportion_front.png')
 render_pair(pairs,images/'Manny_Quinn_surface_front.png',overlay=False)
 render_pair(pairs,images/'Manny_Quinn_threequarter.png',view='threequarter',overlay=False)
 render_pair(pairs,images/'Manny_Quinn_hands_together.png',pose_name='hands_together_tip_contact',view='threequarter')
 render_pair(pairs,images/'Manny_Quinn_forehead.png',pose_name='hand_to_forehead_tip_contact',view='threequarter')
 save(ROOT/'verification/revE_layout_geometry.json',report)
if __name__=='__main__':main()
