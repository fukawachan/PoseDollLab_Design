"""Clean imported final STEP tessellation and export dimension-preserving print meshes."""
from final_model import *
from OCP.BRepTools import BRepTools
from OCP.ShapeFix import ShapeFix_Shape

def mesh_edges(path):
 raw=path.read_bytes();dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]);t=np.frombuffer(raw,offset=84,dtype=dt)['v'].astype(float);u,ix=np.unique(t.reshape(-1,3),axis=0,return_inverse=True);f=ix.reshape(-1,3);f=f[(f[:,0]!=f[:,1])&(f[:,0]!=f[:,2])&(f[:,1]!=f[:,2])];edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);edges.sort(axis=1);edges,count=np.unique(edges,axis=0,return_counts=True);return u[edges[count!=2]],count[count!=2]

def mesh_export(shape,path):
 BRepTools.Clean_s(shape.wrapped);cq.exporters.export(shape,str(path),tolerance=.01,angularTolerance=.05)

def main():
 out=json.loads((ROOT/'verification/revM_print_mesh_export.json').read_text()) if '--quinn-only' in sys.argv else {}
 for name in (('quinn',) if '--quinn-only' in sys.argv else ('manny','quinn')):
  folder=ROOT/f'generated/revM/{name}';d=json.loads((folder/'manufacturing_manifest.json').read_text());rows=[]
  for p in d['parts']:
   if 'print' not in p:continue
   step=folder/p['STEP'];s=cq.importers.importStep(str(step)).val().clean();assert s.isValid() and len(s.Solids())==1
   assert abs(s.Volume()-p['volume_mm3'])/p['volume_mm3']<1e-5
   record=p['print']
   for axis,angle in zip(((1,0,0),(0,1,0),(0,0,1)),record['euler_xyz_deg']):
    if angle:s=s.rotate((0,0,0),axis,angle)
   if record['diagonal']:s=s.moved(cq.Location(cq.Plane(origin=(0,0,0),normal=record['final_plane']['normal'],xDir=record['final_plane']['xdir'])))
   s=s.translate(record['translation_mm']);nominal=s;outpath=folder/record['STL'];temp=outpath.with_name(outpath.stem+'.new.stl');reliefs=[];mesh_export(s,temp)
   for attempt in range(3):
    edges,counts=mesh_edges(temp)
    if not len(edges):break
    assert all(c==4 for c in counts),(p['id'],'unexpected open edge counts',counts.tolist())
    for edge in edges:
     a,b=np.array(edge[0]),np.array(edge[1]);delta=b-a;length=float(np.linalg.norm(delta));assert length>1e-4
     # A zero-thickness pinch is not a printable web. Bridge only this singular
     # edge with a 0.10 mm process bead, then check the added material separately.
     n=delta/length
     if n[int(np.argmax(np.abs(n)))]<0:a,b=b,a;n=-n
     cut=cq.Solid.makeCylinder(.10,length+.20,cq.Vector(*(a-.10*n)),cq.Vector(*n));s=s.fuse(cut);reliefs.append(dict(edge_in_print_coordinates_mm=edge.tolist(),radius_mm=.10,extra_length_each_end_mm=.10,operation='add_micro_bead'))
    s=s.clean();fix=ShapeFix_Shape(s.wrapped);fix.SetPrecision(1e-5);fix.SetMaxTolerance(1e-4);fix.Perform();s=cq.Shape.cast(fix.Shape());assert s.isValid() and len(s.Solids())==1,(p['id'],s.isValid(),[(v.Volume(),v.Center().toTuple()) for v in s.Solids()]);mesh_export(s,temp)
   edges,counts=mesh_edges(temp);assert not len(edges),(p['id'],'remaining mesh edges',counts.tolist())
   delta=s.Volume()-nominal.Volume();assert -.0001<=delta and delta/nominal.Volume()<.001,(p['id'],delta)
   added_bound=sum(math.pi*r['radius_mm']**2*(float(np.linalg.norm(np.array(r['edge_in_print_coordinates_mm'][1])-r['edge_in_print_coordinates_mm'][0]))+2*r['extra_length_each_end_mm']) for r in reliefs);assert delta<=added_bound+.001,(p['id'],delta,added_bound)
   process_step=None
   if reliefs:
    process_step='print_candidates/'+p['id']+'_print_process.step';s.exportStep(str(folder/process_step),precision_mode=1);back=cq.importers.importStep(str(folder/process_step)).val();assert back.isValid() and len(back.Solids())==1 and abs(back.Volume()-s.Volume())<.0002,p['id'];print(name,p['id'],len(reliefs),'pinch beads; added',round(delta,5),'mm3',flush=True)
   temp.replace(outpath)
   rows.append(dict(id=p['id'],source_STEP_sha256=hashlib.sha256(step.read_bytes()).hexdigest(),STL_sha256=hashlib.sha256(outpath.read_bytes()).hexdigest(),linear_deflection_mm=.01,angular_tolerance_rad=.05,nominal_STEP_volume_mm3=nominal.Volume(),print_process_volume_mm3=s.Volume(),reliefs=reliefs,added_volume_mm3=delta,maximum_added_bead_volume_mm3=added_bound,print_process_STEP=process_step,print_process_STEP_sha256=hashlib.sha256((folder/process_step).read_bytes()).hexdigest() if process_step else None,STEP_readback_validated=bool(process_step),STEP_precision_mode=1 if process_step else None))
  out[name]=dict(source_cad_sha256=d['source_sha256'],prints=rows,nominal_assembly_changed=False,print_process_beads=sum(len(r['reliefs']) for r in rows),scope='Nominal master assembly preserved. Non-printable zero-thickness edges receive R0.10 mm print-process beads. Updated printable STEP files accompany STL. Separate interference and mass checks are mandatory for these variants.');h.save(ROOT/'verification/revM_print_mesh_export.json',out);print(name,len(rows),'print meshes re-exported from final STEP',flush=True)
if __name__=='__main__':main()
