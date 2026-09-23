"""Quasi-static sizing scenarios, not measured capacity or structural certification."""
from design import *

def main():
 p=profile();items,_=geometry(p,{})
 T0,A0=fk(p,{});nodes={n["id"]:n for n in p["nodes"]};axes={a["id"]:a for a in p["axes"]}
 masses=[]
 densities={"print":1.24,"rotor":1.24,"metal":2.70,"pom":1.42,"pcb":1.90,"magnet":7.50}
 for item in items:
  c=np.array(item["shape"].Center().toTuple());owner=item["owner"]
  grams=2.2 if item["material"]=="pcb" else item["shape"].Volume()/1000*densities[item["material"]]
  masses.append(dict(name=item["name"],owner=owner,mass_g=grams,local_com_mm=(np.linalg.inv(T0[owner])@np.r_[c,1])[:3].tolist(),basis="assembled_PCB_2.2g_assumption" if item["material"]=="pcb" else "CAD_volume_times_assumed_density"))
 # Unmodeled retainers, friction stacks, screws and cable support are explicitly included.
 for g in groups(p):
  for aid in g["axes"]:
   n=axes[aid]["node"];allowance=30 if g["radius_mm"]>=20 else 15
   masses.append(dict(name=aid+"__unmodeled_hardware_allowance",owner=n,mass_g=allowance,local_com_mm=[0,0,0],basis="unmodeled_mass_allowance_not_BOM"))
 regional={"N1":"pelvis","N2":"chest","N3":"upperarm_l","N4":"upperarm_r","N5":"calf_l","N6":"calf_r"}
 for k,n in regional.items():masses.append(dict(name=k+"__node_harness",owner=n,mass_g=40,local_com_mm=[-30,0,0],basis="25g_node_plus_15g_harness_allowance"))
 descendants={}
 for aid,a in axes.items():
  want=a["node"];ds=set()
  for n in nodes:
   nn=n
   while nn is not None:
    if nn==want:ds.add(n);break
    nn=nodes[nn]["parent"]
  descendants[aid]=ds
 poses=dict(keyposes());poses["hip_abduction_arms_clear"]={"thigh_l.abduct":60,"thigh_r.abduct":60,"upperarm_l.abduct":35,"upperarm_r.abduct":35}
 # These independent endpoint stress cases need not be collision free. Keep them separate.
 for a in p["axes"]:
  lo,hi=[math.degrees(x) for x in a["limits_rad"]]
  poses[a["id"]+"__min"]={a["id"]:lo};poses[a["id"]+"__max"]={a["id"]:hi}
 rng=np.random.default_rng(44032026)
 for index in range(256):
  poses["combined_random_%03d"%index]={a["id"]:float(rng.uniform(*[math.degrees(v) for v in a["limits_rad"]])) for a in p["axes"]}
 def path_bound(aid,m):
  n=m["owner"];target=axes[aid]["node"];length=float(np.linalg.norm(m["local_com_mm"]))
  while n!=target:
   length+=float(np.linalg.norm(nodes[n]["parent_to_axis"]["translation_m"]))*1000
   n=nodes[n]["parent"]
  return length
 result={aid:dict(max_gravity_nm=0,pose=None,downstream_mass_g=sum(m["mass_g"] for m in masses if m["owner"] in descendants[aid])) for aid in axes}
 masses_kg=np.array([m["mass_g"]/1000 for m in masses]);masks={a:np.array([m["owner"] in descendants[a] for m in masses]) for a in axes}
 for name,pose in poses.items():
  Ts,As=fk(p,pose)
  positions=np.array([(Ts[m["owner"]]@np.r_[m["local_com_mm"],1])[:3]/1000 for m in masses])
  for aid,a in As.items():
   origin=a["origin"]/1000;mask=masks[aid]
   forces=np.zeros((int(mask.sum()),3));forces[:,2]=-masses_kg[mask]*9.80665
   torque=np.cross(positions[mask]-origin,forces).sum(axis=0)
   tau=abs(float(np.dot(torque,a["direction"])))
   if tau>result[aid]["max_gravity_nm"]:result[aid].update(max_gravity_nm=tau,pose=name)
 for aid,row in result.items():
  row["sizing_hold_target_nm"]=row["max_gravity_nm"]*1.5+0.02
  row["all_configuration_triangle_bound_nm"]=sum(m["mass_g"]/1000*9.80665*path_bound(aid,m)/1000 for m in masses if m["owner"] in descendants[aid])
  if aid=="pelvis.yaw":row["all_configuration_triangle_bound_nm"]=0.0
  row["bound_hold_target_nm"]=row["all_configuration_triangle_bound_nm"]*1.5+.02
  target=row["sizing_hold_target_nm"];family="S" if target<=.25 else ("M" if target<=1 else "L")
  ro,ri,grip={"S":(13,5.2,35),"M":(19,5.2,65),"L":(27,6.2,110)}[family]
  reff=(2/3)*(ro**3-ri**3)/(ro**2-ri**2)/1000
  row.update(candidate_clutch_family=family,friction_outer_radius_mm=ro,friction_inner_radius_mm=ri,assumed_two_faces=True,preload_at_mu_015_N=target/(2*.15*reff),preload_at_mu_030_N=target/(2*.30*reff),grip_force_N=target/(grip/1000),grip_arm_mm=grip)
 data=dict(status="SIZING_SCENARIOS_NOT_CAPACITY_OR_FEA",design_sha256=hashlib.sha256((HERE/"design.py").read_bytes()).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),sensor_step_sha256=hashlib.sha256(SENSOR_STEP.read_bytes()).hexdigest(),mass_total_g=sum(m["mass_g"] for m in masses),cad_mass_g=sum(m["mass_g"] for m in masses if not m["basis"].startswith("unmodeled") and not m["name"].endswith("__node_harness")),scenario_count=len(poses),axis_loads=result,mass_items=masses,assumptions=["Printed CAD modeled fully solid PLA; shafts modeled aluminum. These are estimates, not a measured BOM.","30g/15g per axis reserved for not-yet-modeled friction/retention hardware; 40g per node plus harness.","Torque is axis-projected gravity moment, not the sum of absolute mass-distance terms.","1.5x gravity plus 0.02Nm cable allowance; no impact, hand force, creep, joint wear or magnetic acceptance covered.","mu 0.15 and 0.30 are sensitivity values, not supplier-qualified material properties.","Includes 256 deterministic simultaneous random axis scenarios (seed44032026). These may self-collide; sampled targets are not certified worst cases.","Triangle bounds use full kinematic path lengths and COM distances; they are conservative configuration-independent gravity bounds, not reachable demonstrated poses.","Clutch family is based on sampled torque only. Bearing strength, diagonal loading, comfort and bound coverage remain unapproved."])
 save(ROOT/"verification/revC_load_sizing.json",data)
 print(json.dumps({"mass_total_g":data["mass_total_g"],"top_targets":sorted([(a,r["sizing_hold_target_nm"],r["preload_at_mu_015_N"]) for a,r in result.items()],key=lambda x:-x[1])[:8]}))
if __name__=="__main__":main()
