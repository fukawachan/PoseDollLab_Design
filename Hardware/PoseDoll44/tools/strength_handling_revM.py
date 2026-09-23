"""Demand-only strength/handling worksheet. No claimed FEA or rated capacity."""
from pathlib import Path
import json,math,hashlib
R=Path(__file__).resolve().parents[1]
def main():
 path=R/'verification/revM_load_work.json';loads=json.loads(path.read_text());out={'source_load_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'physical_tested':False,'rated_capacity':False,'characters':{}}
 for name,b in loads.items():
  rows=[]
  for a in b['axes']:
   t=a['nominal_clutch_Nm'];rows.append(dict(axis=a['axis'],nominal_torque_Nm=t,gravity_bound_Nm=a['worst_case_torque_Nm'],measured_holding_target_Nm=1.5*a['worst_case_torque_Nm'],tangential_force_at_100mm_N=None if t is None else t/.1,tangential_force_at_50mm_N=None if t is None else t/.05))
  out['characters'][name]=dict(estimated_total_mass_kg=b['model_mass_kg']+b['allowance_mass_kg'],handling=rows)
 F=1656.;proof=1.5*F;as3=5.03;le=6.;thread_area=.5*math.pi*2.675*le
 T=5.187110904977376;flat_width=2*math.sqrt(4**2-3.5**2);flat_depth=4.95
 upperT=.15*F*(2/3*(11**3-5**3)/(11**2-5**2))/1000
 out['high_load_demands']=dict(axial_nominal_N=F,axial_proof_target_N=proof,M3_tensile_area_mm2=as3,M3_nominal_tensile_MPa=F/as3,M3_proof_tensile_MPa=proof/as3,thread_effective_engagement_assumption_mm=le,thread_shear_area_simplified_mm2=thread_area,thread_proof_mean_shear_MPa=proof/thread_area,D8_flat_bearing_area_mm2=flat_width*flat_depth,D8_nominal_mean_flat_pressure_MPa=T*1000/(3.5*flat_width*flat_depth),upper_face_nominal_torque_Nm=upperT,D6_hollow_upper_branch_nominal_torsion_MPa=upperT*1000*3/(math.pi*(6**4-2.5**4)/32),warning='Mean-section demands only. D-flat, transverse/axial holes, notch, contact distribution, preload scatter, bolt-head strength, bending and fatigue are not covered.')
 out['PLA_beam_reference']=dict(outer_mm=[12,10],inner_mm=[8,6],minimum_I_mm4=856.,section_modulus_mm3=171.2,example_moment_Nm=2.,nominal_bending_MPa=2000/171.2,example_local_factor_assumed=2.,factored_bending_MPa=2*2000/171.2,status='Illustrative nominal section from the design, not a global strength proof. Actual print anisotropy, stress concentration, walls, supports and full frame load path require sample proof tests.')
 out['not_covered']=['No FEA was run.','No material strength minimum is assumed from typical supplier values.','No universal screw-tightening torque or safe lifting/load rating is issued.','Use fitted geometry and supplier material certificates for production stress/thread review.','Minimum hand force depends on the actual grasp point and coupled joints; 50/100 mm figures are ideal isolated-joint examples.']
 (R/'verification/revM_strength_handling_screen.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(out['high_load_demands']));print('Handling and demand worksheet written; no strength pass claimed')
if __name__=='__main__':main()
