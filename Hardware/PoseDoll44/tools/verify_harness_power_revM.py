"""Independent reach sampling and conservative power envelope; no physical pass."""
from build_harness_revM import *

def verify(name):
 d=json.loads((ROOT/f'harness/{name}_revM.json').read_text(encoding='utf-8'));p=json.loads((ROOT/f'mechanical_manifest/interfaces_revM_{name}.json').read_text(encoding='utf-8'))['profile'];rng=np.random.default_rng(410044)
 limits={q['id']:np.degrees(q['limits_rad']) for q in p['axes'] if not q['id'].startswith('pelvis.')}
 report=json.loads((ROOT/f'generated/revM/{name}/viewer.json').read_text(encoding='utf-8'))
 cases=[q['angles_deg'] for q in report['poses'].values()]+[{a:float(rng.uniform(lo,hi)) for a,(lo,hi) in limits.items()} for _ in range(1000)]
 worst={};count=0
 for pose in cases:
  T=fk(p,pose)
  for wire in d['cables']:
   world=[(T[q['owner']]@np.array([*q['local_mm'],1]))[:3] for q in wire['route']]
   for i,(a,b,s) in enumerate(zip(world,world[1:],wire['spans'])):
    distance=float(np.linalg.norm(a-b));bound=s['all_angles_chord_bound_mm']
    if distance>bound+.02:raise AssertionError((name,wire['id'],i,distance,bound))
    key=wire['id']+':'+str(i);worst[key]=max(worst.get(key,0),distance);count+=1
 # 160 MHz, no RF initialized: module 150 mA design allocation, not datasheet max.
 # Datasheet 81.1 mA typ all-clock 160 MHz, plus flash example ~10 mA.
 lengths={int(w['id'][1:]):w['cut_length_each_mm']/1000 for w in d['cables'] if w['kind']=='power'}
 def solve(module_A):
  sensor_counts=[3,6,9,9,7,7];loads=np.array([3.3*(module_A+.060+.015+.015*n) for n in sensor_counts]);R=np.array([2*lengths[n]*.16+.16+.35+.08 for n in range(1,7)])
  I=np.ones(6)*.35
  for _ in range(200):
   bus=4.75-.20*(float(I.sum())+.005);V=bus-I*R
   if np.min(V)<=3.3:raise AssertionError(('supply collapse',V.tolist()))
   new=loads/(.80*V)
   if max(abs(new-I))<1e-10:break
   I=new
  return dict(module_allocation_A=module_A,total_input_A=float(I.sum()+.005),minimum_node_input_V=float(V.min()),nodes=[dict(node=i+1,cable_m=lengths[i+1],branch_R_ohm=float(R[i]),load_3V3_W=float(loads[i]),input_A=float(I[i]),input_V=float(V[i]),ptc_hold_margin_at_60C=.54/float(I[i])) for i in range(6)])
 power=solve(.150);stress=solve(.200)
 assert power['total_input_A']<2.25 and power['minimum_node_input_V']>3.8
 row=dict(character=name,reach_cases=len(cases),reach_comparisons=count,reach_pass=True,source_harness_sha256=hashlib.sha256((ROOT/f'harness/{name}_revM.json').read_bytes()).hexdigest(),maximum_sampled_chords_mm=worst,nominal_design_envelope=power,higher_CPU_sensitivity=stress,physical_tested=False,notes=['150 mA MCU allowance and 80% converter efficiency are design assumptions requiring measurement.','4.75 V adapter minimum, 0.20 ohm common path and the listed worst branch resistance are budget inputs.','A 3 A fuse is not assumed to clear a fault supplied by a 3 A current-limited adapter; adapter short-circuit protection is required.','This test verifies the chord bound independently, not cable collision, fatigue, bend shape, temperature or signal integrity.'])
 save(ROOT/f'verification/revM_harness_power_{name}.json',row);print(name,'reach PASS',count,'power A',round(power['total_input_A'],3),'minimum V',round(power['minimum_node_input_V'],3),flush=True)
if __name__=='__main__':
 for n in ('manny','quinn'):verify(n)
