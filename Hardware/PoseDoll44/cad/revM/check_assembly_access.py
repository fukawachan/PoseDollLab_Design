"""Straight tool/bolt/nut access for new arm-cover mounts, in the arm subassembly."""
from final_model import *
def main():
 out={}
 for name in ('manny','quinn'):
  A,m=build(name);rows=[]
  for mount in m['arm_cover_mounts']:
   owner=mount['owner'];z=mount['local_z_mm'];y=mount['local_y_mm'];O=A.T0[owner][:3,3];loc=cq.Location(cq.Plane(origin=(0,y,z),normal=(1,0,0),xDir=(0,1,0)))
   shapes={'driver_shank':h.axis_cyl(0,12.1,80,1.3,(0,y,z)), 'bolt_head_insertion':h.axis_cyl(0,10,80,1.95,(0,y,z)), 'nut_insertion':hexagon(4.05,-80,-9.6).moved(loc)}
   for step,tool in shapes.items():
    hits=[]
    for q in A.parts:
     if q['owner']!=owner or q['name'] in (mount['screw'],mount['nut']):continue
     v=q['local_shape'].intersect(tool).Volume()
     if v>.02:hits.append(dict(part=q['name'],volume_mm3=v))
    rows.append(dict(mount=mount['screw'],step=step,hits=hits,scope='same rigid arm segment, assemble covers before connecting full body'))
  out[name]=dict(source_sha256=m['source_sha256'],checks=rows,passed=all(not r['hits'] for r in rows));h.save(ROOT/'verification/revM_cover_assembly_access.json',out);print(name,len(rows),'cover access',out[name]['passed'],[q for q in rows if q['hits']],flush=True)
if __name__=='__main__':main()
