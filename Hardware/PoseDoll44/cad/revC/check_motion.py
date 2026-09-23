"""Rigid-body collision samples; NOT a continuous motion/clearance certificate."""
from design import *
from copy import copy
p=profile();items,_=geometry(p,{})
T0,_=fk(p,{})
report={"complete":False,"design_sha256":hashlib.sha256((HERE/"design.py").read_bytes()).hexdigest(),"sensor_step_sha256":hashlib.sha256(SENSOR_STEP.read_bytes()).hexdigest(),"scope":"44-axis rigid body samples with presently modeled components", "physical_tested":False,"poses":[]}
poses=keyposes()
poses["hip_abduction_arms_clear"]={"thigh_l.abduct":60,"thigh_r.abduct":60,"upperarm_l.abduct":35,"upperarm_r.abduct":35}
for name,pose in poses.items():
    Ts,_=fk(p,pose)
    sample=[]
    for item in items:
        i=copy(item);i["shape"]=moved(item["shape"],Ts[item["owner"]]@np.linalg.inv(T0[item["owner"]]));sample.append(i)
    hits=collisions(sample)
    row=dict(name=name,angles_deg=pose,collisions=hits,collision_count=len(hits));report["poses"].append(row)
    print(json.dumps({"pose":name,"hits":len(hits)}),flush=True)
    save(ROOT/"verification/revC_motion_samples.json",report)
    if name in ("arms_forward","sitting","arms_crossed"):
        render([(x["name"],x["shape"],COL[x["material"]]) for x in sample],OUT/"images"/(name+".png"),"Rev C motion sample | "+name+" | not released")

report["complete"]=True
report["sample_count"]=len(report["poses"])
report["limitations"]=["Discrete poses only, not path planning or continuous collision detection.","Same-rigid-owner pairs excluded; this cannot certify fastening or assembly access.","Cable plugs, protective covers, final friction mechanisms and fixed stand are not in this body model.","hip_abduction with arms down is an intentional retained self-contact stress case; raise arms before moving legs outward."]
save(ROOT/"verification/revC_motion_samples.json",report)
