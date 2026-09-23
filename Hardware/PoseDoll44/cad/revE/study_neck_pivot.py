import sys,json
from pathlib import Path
sys.path.insert(0,str(Path('Hardware/PoseDoll44/cad/revE').resolve()))
from check_proportions import *
result={}
for name in ('manny','quinn'):
 c=reference_character(name);p=make_profile(c)
 rows=json.loads((ROOT/'verification/revE_kinematic_comparison.json').read_text())['characters'][name]['poses']
 rows=[r for r in rows if not r['pose'].startswith('holdout_')]
 residuals=[];jac=[]
 for row in rows:
  pose=row['angles_deg'];T,_=fk(p,pose)
  actual=physical_points(c,p,pose)['head'];g=expected_bones(c,p,pose)['head']
  residuals.append(actual-(SWAP@g[:3,3]*10*SCALE+c['shift_mm']))
  jac.append((T['chest'][:3,:3]-T['head'][:3,:3])[:,[0,2]])
 residuals=np.array(residuals);jac=np.array(jac)
 best=(float(np.max(np.linalg.norm(residuals,axis=1))),[0.,0.]);centre=[0,0]
 for radius,step in [(8.,.5),(1.,.05),(.1,.005)]:
  for dx in np.arange(centre[0]-radius,centre[0]+radius+step/2,step):
   for dz in np.arange(centre[1]-radius,centre[1]+radius+step/2,step):
    value=float(np.max(np.linalg.norm(residuals+np.einsum('nij,j->ni',jac,[dx,dz]),axis=1)))
    if value<best[0]:best=(value,[float(dx),float(dz)])
  centre=best[1]
 result[name]={'baseline_max':float(np.max(np.linalg.norm(residuals,axis=1))),'candidate_max':best[0],'delta_x_z_mm':best[1],'method':'minimax grid search on 232 design poses; needs independent holdout','head_pivot_initial_mm':((c['points']['neck_01']+c['points']['neck_02']+c['points']['head'])/3).tolist()}
 print(json.dumps({name:result[name]}),flush=True)
save(ROOT/'verification/revE_neck_pivot_study.json',result)
