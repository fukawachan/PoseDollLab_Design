"""PD41 harness lengths from owner-local anchors and bounded kinematic reach.
A service loop is a manufacturing allowance, not a simulated elastic cable.
"""
from pathlib import Path
import sys,json,math,hashlib,csv
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
sys.path.insert(0,str(REPO/'Tools/PoseDollSimulator/src'))
from posedoll_sim.core import rigid,rotate


def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def fk(p,angles):
 T={}
 for n in p['nodes']:
  pre=rigid(n['parent_to_axis']);post=rigid(n['axis_to_child']);pre[:3,3]*=1000;post[:3,3]*=1000
  T[n['id']]=(T[n['parent']] if n['parent'] else np.eye(4))@pre@(rotate(n['axis_local'],math.radians(angles.get(n['axis_id'],0))) if n['kind']=='revolute' else np.eye(4))@post
 return T

def run(name):
 d=json.loads((ROOT/f'mechanical_manifest/interfaces_revM_{name}.json').read_text(encoding='utf-8'));p=d['profile'];T0={k:np.array(v) for k,v in d['nodes_neutral'].items()}
 net=json.loads((ROOT/'mechanical_manifest/network_revM.json').read_text(encoding='utf-8'))
 heads=d['heads']
 head={q['axis_id']:q for q in heads};chs={q['axis_id']:q for q in d['channels']};pods={q['node']:q for q in d['pods']}
 anchors=json.loads((ROOT/f'mechanical_manifest/wire_anchors_revM_{name}.json').read_text(encoding='utf-8'))
 parents={n['id']:n['parent'] for n in p['nodes']};nodes={n['id']:n for n in p['nodes']}
 def path(o):
  out=[]
  while o is not None:out.append(o);o=parents[o]
  return out
 def point(owner,world,label,**kw):return dict(owner=owner,local_mm=(np.array(world)-T0[owner][:3,3]).tolist(),label=label,**kw)
 def bound(a,b):
  if a['owner']==b['owner']:return float(np.linalg.norm(np.array(a['local_mm'])-b['local_mm'])),False
  pa,pb=path(a['owner']),path(b['owner']);lca=next(o for o in pa if o in pb)
  # Collapse fixed transforms, then bound each segment between actual rotation
  # centres. For an ancestor endpoint, subtract the first pivot location before
  # taking a norm (do not route unnecessarily via the anatomical origin).
  def branch(q):
   chain=list(reversed(path(q['owner'])[:path(q['owner']).index(lca)]));M=np.eye(4);first=None;radius=0.0
   for owner in chain:
    n=nodes[owner];pre=rigid(n['parent_to_axis']);post=rigid(n['axis_to_child']);pre[:3,3]*=1000;post[:3,3]*=1000;M=M@pre
    if n['kind']=='revolute':
     if first is None:first=M[:3,3].copy()
     else:radius+=float(np.linalg.norm(M[:3,3]))
     M=post
    else:M=M@post
   tail=(M@np.array([*q['local_mm'],1]))[:3]
   if first is None:return tail,0.0
   return first,radius+float(np.linalg.norm(tail))
  ca,ra=branch(a);cb,rb=branch(b)
  return float(np.linalg.norm(ca-cb))+ra+rb,True
 def measure(route,radius):
  spans=[]
  for a,b in zip(route,route[1:]):
   length,moving=bound(a,b)
   # Pi*R is reserved for an open U loop at each moving interface. Fixed spans
   # also carry end dressing allowance; no tightly wound spiral around a shaft.
   alloc=length+(math.pi*radius+10 if moving else 4)
   spans.append(dict(from_label=a['label'],to_label=b['label'],moving=moving,all_angles_chord_bound_mm=round(length,2),allocated_mm=round(alloc,2),minimum_bend_radius_mm=radius))
  cut=int(math.ceil((sum(s['allocated_mm'] for s in spans)+30)/10)*10)
  return spans,cut
 def pod_exit(node,label):
  pod=pods[node];O=np.array(pod['origin_mm']);return point(pod['owner'],O+[-8,0,-58],label,attachment='case bottom exit; silicone edge liner')
 rows=[]
 for n in net['nodes']:
  pod=pods[n['id']];O=np.array(pod['origin_mm']);owner=pod['owner']
  for port in n['ports']:
   aid=port['axis_id'];c=chs[aid];hh=head[aid];num=port['port'];col=(num-1)%3;row=(num-1)//3;u=(-12,0,12)[col];v=(5,-6,-17)[row]
   # SH drawing has a 6.25 mm complete mated side-entry length. Local wire exit
   # at Y=+3.65 from footprint origin; flat six-wire internal S bends R6.5.
   route=[point(owner,O+[-3.25,u,v-3.65],f'N{n["id"]}.J{10+num}',attachment='connector housing pin numbering'),point(owner,O+[-(3.25+13*(1-math.cos(math.radians((70,60,50)[row])))),u,v-3.65-13*math.sin(math.radians((70,60,50)[row]))],f'N{n["id"]}.internal_S_{num}',attachment='fixed loose wire dressing; R6.5 minimum'),pod_exit(n['id'],f'N{n["id"]}.exit')]
   route[-1]['local_mm'][1]+=(-7,0,7)[col]
   chain=path(c['fixed_owner']);selected=[a for a in anchors if a['owner'] in chain and a['owner'] not in path(owner)]
   selected.sort(key=lambda a:-chain.index(a['owner']))
   for a in selected:route.append(point(a['owner'],a['origin_neutral_mm'],a['id'],attachment=a['mount_part']))
   z=np.array(c['normal_neutral']);x=np.array(c['xdir_neutral']);y=np.cross(z,x);R=np.column_stack((x,y,z));rot=math.radians(hh.get('board_rotation_deg',0));rz=np.array([[math.cos(rot),-math.sin(rot),0],[math.sin(rot),math.cos(rot),0],[0,0,1]])
   large=aid.startswith('upperarm_') and aid.endswith('.abduct');datum=c['package_face_mm']+(2.595 if large else 1.995)
   # Starts outside the already collision-checked conservative mated allocation.
   local=np.array([0,.3 if large else 6.9,datum+1.65]);end=np.array(c['origin_neutral_mm'])+R@rz@local
   posts=[q for q in d['parts'] if q['name'].startswith(c['part_prefix']) and q['owner']==c['fixed_owner'] and any(s in q['name'] for s in ('post_','standoff_','spacer_','seat_saddle_'))]
   assert posts,aid
   post=min(posts,key=lambda q:np.linalg.norm((np.array(q['bounds_mm'][:3])+q['bounds_mm'][3:])/2-end))
   # Final 35 mm is a loose lead anchored to a protected fixed mounting saddle,
   # not tightened around an exposed PCB or a rotating magnet keeper.
   route.append(point(c['fixed_owner'],end,aid+'.J1',attachment=post['name'],strain_relief='silicone sleeve + loose 2.5 mm tie on fixed post/saddle; retain 35 mm free lead at connector'))
   spans,cut=measure(route,12);cut+=40
   rows.append(dict(id=f'S{port["protocol_index"]:02}',kind='sensor',axis_id=aid,node=n['id'],port=num,from_connector=f'N{n["id"]}.J{10+num}',to_connector=aid+'.J1',pin_map=[1,2,3,4,5,6],pins=['GND','3V3','SCK','MOSI','MISO','CS_N'],wire='Alpha 2841/7 AWG30 7/38 PTFE OD0.61',housing_both_ends='SHR-06V-S',contact='SSH-003T-P0.2-H',wires=6,cut_length_each_mm=cut,route=route,spans=spans,physical_routing_validated=False))
 # CAN is one line, no star. Gateway N1 is an interior node.
 order=[6,1,5,3,2,4]
 for i,(a,b) in enumerate(zip(order,order[1:]),1):
  route=[pod_exit(a,f'N{a}.J3'),pod_exit(b,f'N{b}.J2')];spans,cut=measure(route,12);cut+=150
  rows.append(dict(id=f'C{i}',kind='can',from_connector=f'N{a}.J3',to_connector=f'N{b}.J2',pin_map=[1,2,3],pins=['GND','CAN_L','CAN_H'],wire='Alpha 5851 AWG30 PTFE OD0.81; twist H/L together, 20 mm pitch',housing_both_ends='GHR-03V-S',contact='SSHL-002T-P0.2',wires=3,cut_length_each_mm=cut,route=route,spans=spans,physical_routing_validated=False))
 PO=np.array(pods[1]['origin_mm'])
 for node in range(1,7):
  route=[point('pelvis',PO+[-19.8,0,51],f'POWER.J{node+1}',attachment='power case upper relief; 100 mm internal dressing'),pod_exit(node,f'N{node}.J1')];spans,cut=measure(route,15);cut+=150
  rows.append(dict(id=f'P{node}',kind='power',from_connector=f'POWER.J{node+1}',to_connector=f'N{node}.J1',pin_map=[1,2],pins=['5V','GND'],wire='Alpha 3049 AWG26 7/34 PVC OD1.30',housing_both_ends='PHR-2',contact='SPH-002T-P0.5S',wires=2,cut_length_each_mm=cut,route=route,spans=spans,physical_routing_validated=False))
 # Conservative material mass from published conductor area + insulation OD;
 # connectors/crimps include a separately visible assembly allowance per cable.
 models={'sensor':(.06,.61,2.2,.40),'can':(.06,.81,2.2,.40),'power':(.14,1.30,1.45,.55)}
 for q in rows:
  copper,od,rho,terminal_g=models[q['kind']];gpm=copper*8.96+(math.pi*od**2/4-copper)*rho
  q['estimated_mass_g']=round(gpm*q['wires']*q['cut_length_each_mm']/1000+terminal_g*2,3)
 mass_lumps=[]
 for q in rows:
  # Allocate each moving span to its more distal owner; this intentionally puts
  # its full weight downstream for the gravity screen. 15% wire-mass reserve
  # covers cut allowance, unmodelled labels and sensor strain-relief ties.
  total=sum(x['allocated_mm'] for x in q['spans'])
  for a,b,span in zip(q['route'],q['route'][1:],q['spans']):
   pick=a if len(path(a['owner']))>len(path(b['owner'])) else b
   mass_lumps.append(dict(name=q['id']+'_'+span['to_label'],owner=pick['owner'],kg=q['estimated_mass_g']/1000*1.15*span['allocated_mm']/total,local_com_mm=pick['local_mm'],material='harness_estimate'))
 sources=[f'mechanical_manifest/interfaces_revM_{name}.json',f'mechanical_manifest/wire_anchors_revM_{name}.json','mechanical_manifest/network_revM.json']
 result=dict(schema='posedoll.harness/1',character=name,source_cad_sha256=d['source_sha256'],source_sha256={r:hashlib.sha256((ROOT/r).read_bytes()).hexdigest() for r in sources},physical_validated=False,CAN_linear_order=order,termination_nodes=[6,4],sensor_count=41,cables=rows,mass_lumps=mass_lumps,gravity_mass_with_15_percent_reserve_g=sum(q['kg'] for q in mass_lumps)*1000,total_estimated_mass_g=sum(q['estimated_mass_g'] for q in rows),limits=['Reach bound guarantees only available chord length, not an unobstructed elastic route.','Service loops must be dressed outside each joint, with no wrap around a rotating shaft.','Loose lead and minimum bend radius need physical inspection across the motion range.','SPI cable capacitance / ringing and repeated flex life are not qualified by length calculation.'])
 save(ROOT/f'harness/{name}_revM.json',result)
 with (ROOT/f'harness/{name}_cut_list_revM.csv').open('w',newline='',encoding='utf-8-sig') as f:
  fields=['id','kind','from_connector','to_connector','cut_length_each_mm','wires','wire','housing_both_ends','contact'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
 print(name,len(rows),'cables; mass',round(result['total_estimated_mass_g'],1),'g; longest sensor',max(q['cut_length_each_mm'] for q in rows if q['kind']=='sensor'))
 return result
if __name__=='__main__':
 for n in ('manny','quinn'):run(n)
