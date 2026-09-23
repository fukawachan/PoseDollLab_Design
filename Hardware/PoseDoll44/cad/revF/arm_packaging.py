"""Manny/Quinn arm packaging assembly using actual revised link lengths.
Elbow and wrist-flex joints are populated. Shoulder, forearm twist and wrist
side-deviation remain integration interfaces; this is not a full 9-axis arm.
"""
from fork_joint import *
from functools import lru_cache

@lru_cache(None)
def neutral_joint(size):return module(size)

def beam(a,b,width=14,height=10,wall=2.4):
 a=np.array(a);b=np.array(b);v=b-a;L=np.linalg.norm(v)
 T=orient(v,a);s=cube((width,height,L),(0,0,L/2))
 if L>10:s=s.cut(cube((width-2*wall,height-2*wall,L-8),(0,0,L/2)))
 return move(s,T)

def add_input_adapter(parts,label,base,owner):
 # Outside face of the fixed fork: 6mm plate and two through M3 bolts.
 plate=cube((6,36,12),(-30,0,-18))
 for y in (-12,12):
  plate=plate.cut(rod((-40,y,-18),(-20,y,-18),1.8))
  washer=ring(3.5,1.6,0,.5);washer=move(washer,orient((1,0,0),(-33.5,y,-18)))
  screw=rod((-33.5,y,-18),(-17.5,y,-18),1.5).fuse(rod((-36.5,y,-18),(-33.5,y,-18),2.75))
  nut=hexprism(5.5,0,2.4).cut(cyl(1.3,-1,4));nut=move(nut,orient((1,0,0),(-21,y,-18)))
  for n,s in [('washer',washer),('screw',screw),('nut',nut)]:parts.append(shape_record(label+'_'+n+'_'+str(y),move(s,base),'fastener',owner,'arm'))
 return move(plate,base)

def add_output_adapter(parts,label,base,z,owner):
 plate=ring(18,4.2,z,5)
 for x in (-11,11):plate=hole(plate,x,0,2.2)
 for y in (-11,11):
  plate=hole(plate,0,y,1.8)
  top=z+5.5
  screw=cyl(1.5,top-14,14).fuse(cyl(2.75,top,3)).translate((0,y,0))
  nut=hexprism(5.5,z-6.4,2.4).cut(cyl(1.3,z-7,4)).translate((0,y,0))
  washer=ring(3.5,1.6,z+5,.5).translate((0,y,0))
  for n,s in [('screw',screw),('nut',nut),('washer',washer)]:parts.append(shape_record(label+'_'+n+'_'+str(y),move(s,base),'fastener',owner,'arm'))
 return move(plate,base)

def build_neutral_geometry(name,elbow=0,wrist=0):
 data=json.loads((ROOT/'verification/revE_proportion_baselines.json').read_text(encoding='utf8'))['characters'][name]['measurements_mm'];U=data['upperarm_l'];F=data['forearm_l']
 A=orient((0,-1,0));Re=matrix(rotation((0,-1,0),elbow));Rw=matrix(rotation((0,-1,0),wrist));W=matrix(p=(0,0,-F));parts=[]
 Ej,Ep=neutral_joint('M6');Wj,Wp=neutral_joint('S6')
 for label,items,pos,turn in [('elbow',Ej,np.eye(4),Re),('wrist',Wj,Re@W,Re@W@Rw)]:
  for p in items:
   T=pos@A if p['owner']=='fixed' else turn@A
   owner=('upperarm' if label=='elbow' else 'forearm') if p['owner']=='fixed' else ('forearm' if label=='elbow' else 'hand')
   parts.append(shape_record(label+'__'+p['name'],move(p['shape'],T),p['material'],owner,label,p['note']))
 # Upper-arm datum link for the future shoulder integration; actual centre-to-centre distance U.
 upper=add_input_adapter(parts,'upper_attach',A,'upperarm')
 elbow_input=(A@np.r_[Ep['input_mm'],1])[:3]
 start=np.array([-47,elbow_input[1],0.]);top=np.array([-47,elbow_input[1],U-6])
 upper=upper.fuse(beam(start,top));upper=upper.fuse(rod(start,elbow_input+[-6,0,0],4))
 upper=upper.fuse(beam(top,[0,0,U-6],12,10))
 datum=cube((28,22,6),(0,0,U-3))
 for x in (-9,9):datum=datum.cut(rod((x,0,U-8),(x,0,U+2),1.8))
 upper=upper.fuse(datum)
 # Drill again after joining ribs, preserving all bolt clearances.
 for yy in (-12,12):upper=upper.cut(move(rod((-42,yy,-18),(-20,yy,-18),1.8),A))
 parts.append(shape_record('upperarm_datum_link',upper,'printed','upperarm','arm','Shoulder reference interface remains provisional; exact upper-arm length preserved'))
 # Forearm side beam links the elbow output to wrist fixed input while returning to the true wrist centre.
 local_parts=[];plate=add_output_adapter(local_parts,'forearm_out',A,Ep['output_mm'][2],'forearm')
 wrist_input=add_input_adapter(local_parts,'wrist_in',W@A,'forearm')
 eout=(A@np.r_[Ep['output_mm'],1])[:3];win=(W@A@np.r_[Wp['input_mm'],1])[:3]
 end1=np.array([-38,eout[1]-2.5,-10]);end2=np.array([-38,eout[1]-2.5,-F]);end3=np.array([-38,win[1],-F])
 connector=plate.fuse(beam(eout+[-14,-2.5,-10],end1,10,10)).fuse(beam(end1,end2)).fuse(beam(end2,end3)).fuse(rod(end3,win+[-6,0,0],4)).fuse(wrist_input)
 connector=connector.cut(move(cyl(20,Ep['output_mm'][2]-10,10),A))
 for y in (-11,11):connector=connector.cut(move(cyl(1.8,Ep['output_mm'][2]-8,20).translate((0,y,0)),A))
 for x in (-11,11):connector=connector.cut(move(cyl(2.2,Ep['output_mm'][2]-2,10).translate((x,0,0)),A))
 for yy in (-12,12):connector=connector.cut(move(rod((-42,yy,-18),(-20,yy,-18),1.8),W@A))
 for p in local_parts:parts.append(dict(p,shape=move(p['shape'],Re)))
 parts.append(shape_record('forearm_return_link',move(connector,Re),'printed','forearm','arm','Variant-specific forearm length; detachable connections; central joint centres unchanged'))
 return parts,{'upper_arm_mm':U,'forearm_mm':F,'elbow_angle_deg':elbow,'wrist_flex_deg':wrist,'shoulder_reference_mm':[0,0,U],'elbow_centre_mm':[0,0,0],'wrist_centre_mm':(Re@np.array([0,0,-F,1]))[:3].tolist(),'populated_axes':['elbow_l.flex','hand_l.flex'],'remaining_arm_axes':'shoulder 3, forearm twist 1, wrist deviation 1, plus shoulder girdle 2; not yet integrated'}

@lru_cache(None)
def neutral_arm(name):return build_neutral_geometry(name)

def geometry(name,elbow=0,wrist=0):
 parts,meta=neutral_arm(name);F=meta['forearm_mm'];Re=matrix(rotation((0,-1,0),elbow));W=matrix(p=(0,0,-F));Rw=matrix(rotation((0,-1,0),wrist))
 transforms={'upperarm':np.eye(4),'forearm':Re,'hand':Re@W@Rw@np.linalg.inv(W)}
 posed=[dict(p,shape=move(p['shape'],transforms[p['owner']])) for p in parts]
 return posed,dict(meta,elbow_angle_deg=elbow,wrist_flex_deg=wrist,wrist_centre_mm=(Re@np.array([0,0,-F,1]))[:3].tolist())

def exceptions(parts):
 names={p['name'] for p in parts};pairs=set()
 for tag,size in [('elbow','M6'),('wrist','S6')]:
  for pair in exception_pairs(neutral_joint(size)[0]):pairs.add(frozenset(tag+'__'+x for x in pair))
 for tag,values in [('upper_attach',(-12,12)),('forearm_out',(-11,11)),('wrist_in',(-12,12))]:
  for v in values:pairs.add(frozenset((tag+'_screw_'+str(v),tag+'_nut_'+str(v))))
 return {p for p in pairs if p<=names}

def main():
 report={'status':'ARM_PACKAGING_ASSEMBLY_TWO_AXES_POPULATED_NOT_FULL_ARM_RELEASE','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'characters':{}}
 profile=json.loads((ROOT/'mechanical_manifest/physical_manny_44_revE_proportion.json').read_text(encoding='utf8'))
 limits={a['id']:np.degrees(a['limits_rad']).tolist() for a in profile['axes']}
 elimit=limits['elbow_l.flex'];wlimit=limits['hand_l.flex']
 es=sorted({elimit[0],elimit[1],*[v for v in (0,45,90,135) if elimit[0]<=v<=elimit[1]]})
 ws=sorted({wlimit[0],0.,wlimit[1]});poses=list(itertools.product(es,ws))
 report['sampled_elbow_angles_deg']=es;report['sampled_wrist_angles_deg']=ws
 for name in ('manny','quinn'):
  parts,meta=geometry(name);folder=OUT/'variants'/name;folder.mkdir(exist_ok=True)
  assy=cq.Assembly(name=name.title()+'_arm_packaging');records=[]
  for p in parts:
   shape=p['shape'];b=shape.BoundingBox();assy.add(shape,name=p['name'],color=cq.Color(*COL[p['material']]))
   records.append({k:v for k,v in p.items() if k!='shape'}|{'mass_g':mass(p),'solid_count':len(shape.Solids()),'bbox_mm':[b.xlen,b.ylen,b.zlen],'valid':shape.isValid()})
   if p['name'].endswith('_link'):cq.exporters.export(shape,str(folder/(p['name']+'.step')))
  assy.save(str(folder/(name.title()+'_arm_packaging.step')))
  allow=exceptions(parts);allhits=pair_hits(parts);bad=[h for h in allhits if frozenset((h['a'],h['b'])) not in allow]
  results=[]
  for e,w in poses:
   posed,m=geometry(name,e,w);hits=pair_hits(posed,skip_same_owner=True)
   results.append({'elbow_deg':e,'wrist_deg':w,'hits':hits,'forearm_length_mm':float(np.linalg.norm(m['wrist_centre_mm']))})
  report['characters'][name]={'parts':records,'meta':meta,'mass_g':sum(mass(p) for p in parts),'unplanned_assembly_hits':bad,'thread_envelope_hits':[h for h in allhits if h not in bad],'pose_checks':results}
  print(json.dumps({'name':name,'parts':len(parts),'mass_g':report['characters'][name]['mass_g'],'assembly_hits':bad,'pose_hit_counts':[len(x['hits']) for x in results]}),flush=True)
  render([(p['name'],p['shape'],COL[p['material']]) for p in parts],OUT/'images'/(name+'_arm_packaging.png'),name.title()+' | revised upper-arm/forearm dimensions | 2 axes populated, other interfaces pending',camera=(900,-1500,500))
 save(ROOT/'verification/revF_arm_packaging.json',report)
if __name__=='__main__':main()
