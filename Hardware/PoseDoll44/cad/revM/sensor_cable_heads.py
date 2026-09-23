"""Real wire-to-board connector integration. No free moving cable is implied.
39 SH6 mini heads plus two inherited GH6 abduction heads.
"""
from torso_shells import *
import torso_shells as body
from full_body_audit import channels41,poses,readout
REVERSED={'clavicle_l.protract','upperarm_l.flex','upperarm_r.flex'}

def place_channels(A,name):
 changes=[];records=[];A.sensor_channel_overrides={}
 for c in channels41(A,name):
  q=next((q for q in A.parts if q['name'].startswith(c['part_prefix']) and q['name'].endswith('J1_dimension_envelope')),None)
  if q is None:continue
  origin=np.array(c['origin_neutral_mm']);normal=np.array(c['normal_neutral']);loc=cq.Location(cq.Plane(origin=tuple(origin),normal=tuple(normal),xDir=tuple(c['xdir_neutral'])))
  rot=c.get('board_rotation_deg',0)+(180 if c['axis_id'] in REVERSED else 0);datum=c['package_face_mm']+1.995
  if c['axis_id'] in REVERSED:
   for comp in A.parts:
    if comp['name'].startswith(c['part_prefix']) and '_pcb_' in comp['name']:
     w=h.move(comp['local_shape'],A.T0[comp['owner']]).rotate(tuple(origin),tuple(origin+normal),180)
     comp['local_shape']=w.translate(tuple(-A.T0[comp['owner']][:3,3]))
   A.sensor_channel_overrides[c['axis_id']]=dict(board_rotation_deg=rot)
  plug=cube((9.4,9.6,3.3),(0,2.1,datum+1.65)).rotate((0,0,0),(0,0,1),rot).moved(loc)
  replace_world(A,q,plug,'JST SM06B-SRSS-TB side-entry SH6, conservative 9.4 x9.6 x3.3 mm mated plug allocation; cable bend remains a separate harness requirement','pcb_component')
  pcbpre=q['name'].removesuffix('J1_dimension_envelope');cap=next(q for q in A.parts if q['name']==pcbpre+'C2')
  env=cube((2.3,1.45,1.45),(2.3,3.75,datum-.995-.725)).rotate((0,0,0),(0,0,1),rot).moved(loc)
  replace_world(A,cap,env,'CL21A106KAYNNNE maximum body height 1.45 mm; dimension envelope includes package tolerance','pcb_component')
  obsolete=[r for r in A.parts if r['name']==pcbpre+'FPC_short_tail']
  for r in obsolete:A.parts.remove(r)
  changes += [q['name'],cap['name']]
  records.append(dict(axis_id=c['axis_id'],connector_part=q['name'],board_rotation_deg=rot,PCB='electronics/sensor_revM_side/PoseDoll_AS5048A_revM_side.kicad_pcb',socket='SM06B-SRSS-TB(LF)(SN)',mated_envelope_mm=[9.4,9.6,3.3]))
 return changes,records

def relieve(A,records):
 modified=[];details=[]
 # Low-profile screw preserves the independent output retention function.
 for side in ('l','r'):
  j=A.joints['upperarm_'+side+'.flex'];loc=j['loc'];q,w=world_part(A,side+'_flex_clutch_inner_M3x8');w=w.moved(loc.inverse);bb=w.BoundingBox();seat=bb.zmin+3
  new=cyl(seat,bb.zmax,1.5).fuse(cyl(seat-1.65,seat,2.85)).cut(hexagon(2,seat-1.75,seat-.65))
  replace_world(A,q,new.moved(loc),'M3x8 ISO7380-1 low-profile button screw, 1.65 mm nominal head height; independent output-hub retention, no spring adjustment','fastener');modified.append(q['name'])
  r=next(r for r in records if r['axis_id']=='forearm_'+side+'.twist');plug,ps=world_part(A,r['connector_part']);bb=ps.BoundingBox();centre=((bb.xmin+bb.xmax)/2,(bb.ymin+bb.ymax)/2,(bb.zmin+bb.zmax)/2)
  tool=cq.Workplane('XY').box(bb.xlen+1.2,bb.ylen+1.2,bb.zlen+1.2).edges('|Z').fillet(.8).val().translate(centre)
  q,w=world_part(A,'elbow_'+side+'_flex_M_proximal_forearm');before=w.Volume();new=w.cut(tool)
  replace_world(A,q,new,q['note']+'; rounded underside pocket gives 0.6 mm nominal SH plug clearance; upper load bridge retained',q['material']);modified.append(q['name']);details.append(dict(part=q['name'],removed_mm3=before-new.Volume()))
  q,w=world_part(A,side+'_arm_forearm_shell_front_distal');bb=w.BoundingBox();new=w.intersect(cube((400,400,1000),((bb.xmin+bb.xmax)/2,(bb.ymin+bb.ymax)/2,bb.zmin+505)))
  replace_world(A,q,new,q['note']+'; distal front edge retracted 5 mm to clear mated wrist connector',q['material']);modified.append(q['name'])
 # Only relieve exposed support material; reserve at least 1.5 mm metal outside
 # the four reamed yaw bush bores. A remaining collision is a failed design.
 q,fw=world_part(A,'chest_M_body_frame');protected=[]
 for side in ('l','r'):
  for tail in ('yaw_bush_top','yaw_bush_lower'):
   b=world_part(A,side+'_'+tail)[1].BoundingBox();protected.append(cyl(b.zmin-.1,b.zmax+.1,4.5).translate(((b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2,0)))
 before=fw.Volume();limits={x['id']:np.degrees(x['limits_rad']) for x in A.profile['axes']}
 for side in ('l','r'):
  r=next(r for r in records if r['axis_id']=='upperarm_'+side+'.flex');cqpart,cw=world_part(A,r['connector_part']);b=cw.BoundingBox()
  # World inflation is conservative for the rotation sweep, with no clearance
  # masking in collision classification.
  cutter=cube((b.xlen+1.2,b.ylen+1.2,b.zlen+1.2),((b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2,(b.zmin+b.zmax)/2));local=cutter.translate(tuple(-A.T0[cqpart['owner']][:3,3]))
  for p in np.linspace(*limits['clavicle_'+side+'.protract'],7):
   for e in np.linspace(*limits['clavicle_'+side+'.elevate'],5):
    T,_=h.fk(A.profile,{'clavicle_'+side+'.protract':float(p),'clavicle_'+side+'.elevate':float(e)});tool=h.move(local,T[cqpart['owner']])
    for reserve in protected:tool=tool.cut(reserve)
    fw=fw.cut(tool)
 replace_world(A,q,fw,q['note']+'; local SH plug swing relief outside protected yaw-bearing walls',q['material']);modified.append(q['name']);details.append(dict(part=q['name'],removed_mm3=before-fw.Volume(),minimum_bearing_wall_reserved_mm=1.5))
 return modified,details

def build(name):
 A,meta=body.build(name);changed,records=place_channels(A,name);modified,details=relieve(A,records)
 return A,dict(meta,sensor_heads=records,sensor_channel_overrides=A.sensor_channel_overrides,sensor_cable_clearance_changes=details,affected_sensor_cable_parts=changed+modified)

def main():
 out={}
 for name in ('quinn','manny'):
  A,meta=build(name);cache=CollisionCache(A);cases,_=poses(A);checks=[];chs=channels41(A,name);read=readout(A,chs,cases)
  print('Sensor cable setup',name,json.dumps(meta['sensor_cable_clearance_changes']),flush=True)
  for label,pose in cases.items():
   raw=cache.contacts(pose,set(meta['affected_sensor_cable_parts']),label!='neutral');review=classify_all(raw,A.parts);bad=[x for x in review if x['classification']=='structural'];checks.append(dict(pose=label,angles_deg=pose,review=review))
   if bad:print(json.dumps(dict(character=name,pose=label,structural=bad)),flush=True)
  out[name]=dict(heads=meta['sensor_heads'],reliefs=meta['sensor_cable_clearance_changes'],checks=checks,readout=read);h.save(ROOT/'verification/revM_sensor_cable_heads_work.json',out);print(name,'finished',len(checks),'failed',sum(any(x['classification']=='structural' for x in r['review']) for r in checks),flush=True)
if __name__=='__main__':main()
