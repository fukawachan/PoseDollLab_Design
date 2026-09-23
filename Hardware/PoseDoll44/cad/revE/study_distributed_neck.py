from check_proportions import *

def matrices(c,p,rows):
 residual=[];jac=[]
 nodes={a['id']:a['node'] for a in p['axes']}
 for pose in rows:
  T,_=fk(p,pose);g=expected_bones(c,p,pose)['head']
  residual.append(physical_points(c,p,pose)['head']-(SWAP@g[:3,3]*10*SCALE+c['shift_mm']))
  r0=T['chest'][:3,:3];r1=T[nodes['head.yaw']][:3,:3];r2=T[nodes['head.pitch']][:3,:3];r3=T['head'][:3,:3]
  jac.append(np.column_stack([(r0-r1)[:,0],(r0-r1)[:,1],(r1-r2)[:,0],(r1-r2)[:,2],(r2-r3)[:,1],(r2-r3)[:,2]]))
 return np.array(residual),np.array(jac)

def fit(e,J):
 q=np.zeros(J.shape[-1]);tau=.04
 def obj(q):
  r=e+np.einsum('nij,j->ni',J,q);norm=np.linalg.norm(r,axis=1);mx=norm.max();w=np.exp((norm-mx)/tau);w/=w.sum()
  return mx+tau*np.log(np.exp((norm-mx)/tau).sum()),np.einsum('nij,ni,n->j',J,r/np.maximum(norm[:,None],1e-12),w)
 for _ in range(1500):
  value,g=obj(q);step=1.
  for _ in range(25):
   candidate=np.clip(q-step*g,-6,6)
   if obj(candidate)[0]<value:break
   step*=.5
  if np.linalg.norm(q-candidate)<1e-8:break
  q=candidate
 return np.round(q,2)

def main():
 report={}
 for name in ('manny','quinn'):
  c=reference_character(name);p=make_profile(c)
  design=json.loads((ROOT/'verification/revE_kinematic_comparison.json').read_text())['characters'][name]['poses']
  design=[r for r in design if not r['pose'].startswith('holdout_')]
  e,J=matrices(c,p,[r['angles_deg'] for r in design]);q=fit(e,J)
  rng=np.random.default_rng(923741);poses=[{a['id']:float(rng.uniform(*np.degrees(a['limits_rad']))) for a in p['axes']} for _ in range(512)]
  import itertools
  head=[a for a in p['axes'] if a['id'].startswith('head.')]
  for angles in itertools.product(*[np.linspace(*np.degrees(a['limits_rad']),7) for a in head]):poses.append(dict(zip([a['id'] for a in head],map(float,angles))))
  eh,Jh=matrices(c,p,poses)
  row={'candidate_offsets_mm':dict(zip(['yaw_x','yaw_y','pitch_x','pitch_z','roll_y','roll_z'],q.tolist())),'design_old_max_mm':float(np.max(np.linalg.norm(e,axis=1))),'design_candidate_max_mm':float(np.max(np.linalg.norm(e+np.einsum('nij,j->ni',J,q),axis=1))),'holdout_count':len(poses),'holdout_old_max_mm':float(np.max(np.linalg.norm(eh,axis=1))),'holdout_candidate_max_mm':float(np.max(np.linalg.norm(eh+np.einsum('nij,j->ni',Jh,q),axis=1))),'threshold_mm':c['height_mm']*.01,'applied':False}
  report[name]=row;print(json.dumps({name:row}),flush=True)
 save(ROOT/'verification/revE_distributed_neck_pivot_study.json',report)
if __name__=='__main__':main()
