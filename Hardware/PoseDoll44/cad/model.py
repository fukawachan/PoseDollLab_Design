"""Single source of mechanical dimensions and kinematics, in mm."""
from pathlib import Path
import json, math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
BASE=REPO/"Shared/Profiles/virtual_humanoid_44_v1.json"
FAMILIES={
 "S":{"radius_mm":12,"axial_mm":12,"shaft_mm":4,"design_capacity_nm":0.12,"module_mass_g":24,"grip_radius_mm":25},
 "M":{"radius_mm":18,"axial_mm":16,"shaft_mm":6,"design_capacity_nm":0.60,"module_mass_g":48,"grip_radius_mm":50},
 "L":{"radius_mm":26,"axial_mm":20,"shaft_mm":8,"design_capacity_nm":3.0,"module_mass_g":95,"grip_radius_mm":100}
}
# Capacities are sizing hypotheses, NOT measured ratings.
NODE_REGIONS={"pelvis":"N1","waist":"N1","chest":"N2","head":"N2",
 "clavicle_l":"N3","upperarm_l":"N3","elbow_l":"N3","forearm_l":"N3","hand_l":"N3",
 "clavicle_r":"N4","upperarm_r":"N4","elbow_r":"N4","forearm_r":"N4","hand_r":"N4",
 "thigh_l":"N5","calf_l":"N5","foot_l":"N5","ball_l":"N5",
 "thigh_r":"N6","calf_r":"N6","foot_r":"N6","ball_r":"N6"}
def family(axis):
    p=axis.split(".")[0]
    if p in ("pelvis","waist","chest"): return "L"
    if p.startswith(("head","hand","foot","ball")): return "S"
    return "M"
def profile():
    p=json.loads(BASE.read_text(encoding="utf8"))
    p["profile_id"]="physical_humanoid_44_revA_layout"
    p["status"]="H0_ENVELOPE_LAYOUT_NOT_CALIBRATED_NOT_MANUFACTURING_RELEASE"
    p["notes_zh"]=["由 cad/model.py 导出，真实制造限位仍待确定。","此文件是实体布局候选，不可作为已校准设备连接 UE。","单位转换在导出时执行，44 轴顺序与虚拟基线一致。"]
    for n in p["nodes"]:
        name=n["id"]; prefix=name.split(".")[0]; t=np.array(n["parent_to_axis"]["translation_m"])*1000
        if name=="pelvis.yaw_frame":t=[0,0,260]
        elif prefix in ("pelvis","waist","chest","head") and n.get("axis_id"):
            if name.endswith("yaw_frame"):t=[0,0,{"waist":35,"chest":40,"head":45}[prefix]]
            else:t=[0,0,28 if prefix=="head" else 35]
        elif name=="head_tip":t=[0,0,35]
        elif name.startswith("clavicle_"):
            s=1 if "_l" in name else -1
            t=[0,s*35,25] if "protract" in name else [0,s*24,0]
        elif name.startswith("upperarm_"):
            s=1 if "_l" in name else -1
            t=[0,s*60,0] if "flex_frame" in name else [0,0,-30]
        elif name.startswith("elbow_"):t=[0,0,-98]
        elif name.startswith("forearm_"):t=[0,0,-26]
        elif name.startswith("hand_") and not name.startswith("hand_tip"):
            t=[0,0,-90] if "flex_frame" in name else [0,0,-24]
        elif name.startswith("hand_tip"):t=[0,0,-40]
        elif name.startswith("thigh_"):
            s=1 if "_l" in name else -1
            t=[0,s*55,-30] if "flex_frame" in name else [0,0,-30]
        elif name.startswith("calf_"):t=[0,0,-100]
        elif name.startswith("foot_"):t=[0,0,-95] if "dorsiflex" in name else [0,0,-24]
        elif name.startswith("ball_"):t=[38,0,-4]
        elif name.startswith("sole_"):t=[20,0,-18]
        elif name.startswith("heel_"):t=[-15,0,-18]
        elif name.startswith("toe_tip"):t=[30,0,0]
        n["parent_to_axis"]["translation_m"]=[float(v)/1000 for v in t]
    return p
def rotation(axis,deg):
    a=np.array(axis,dtype=float);a/=np.linalg.norm(a); x,y,z=a
    K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    q=math.radians(deg)
    return np.eye(3)+math.sin(q)*K+(1-math.cos(q))*(K@K)
def fk(p,pose):
    transforms={}; axes={}
    for n in p["nodes"]:
        T=np.eye(4) if n["parent"] is None else transforms[n["parent"]].copy()
        pre=n["parent_to_axis"]; post=n["axis_to_child"]
        assert pre["rotation_xyzw"]==[0,0,0,1] and post["rotation_xyzw"]==[0,0,0,1]
        T[:3,3]+=T[:3,:3]@ (np.array(pre["translation_m"])*1000)
        if "axis_id" in n:
            axes[n["axis_id"]]={"origin":T[:3,3].copy(),"direction":T[:3,:3]@np.array(n["axis_local"]),"frame":T.copy(),"node":n["id"]}
            T[:3,:3]=T[:3,:3]@rotation(n["axis_local"],pose.get(n["axis_id"],0))
        T[:3,3]+=T[:3,:3]@(np.array(post["translation_m"])*1000)
        transforms[n["id"]]=T
    return transforms,axes
def keyposes():
    return {
      "neutral":{},
      "arms_forward":{f"upperarm_{s}.flex":90 for s in ("l","r")},
      "arms_overhead":{f"upperarm_{s}.flex":160 for s in ("l","r")},
      "arms_side":{f"upperarm_{s}.abduct":90 for s in ("l","r")},
      "hands_on_hips":{"upperarm_l.abduct":35,"upperarm_r.abduct":35,"elbow_l.flex":110,"elbow_r.flex":110,"upperarm_l.twist":-40,"upperarm_r.twist":-40},
      "arms_crossed":{"upperarm_l.flex":65,"upperarm_r.flex":65,"upperarm_l.abduct":-20,"upperarm_r.abduct":-20,"elbow_l.flex":115,"elbow_r.flex":115,"upperarm_l.twist":60,"upperarm_r.twist":60},
      "forehead":{"upperarm_l.flex":110,"elbow_l.flex":105,"upperarm_l.twist":-30},
      "sitting":{**{f"thigh_{s}.flex":90 for s in ("l","r")},**{f"calf_{s}.flex":90 for s in ("l","r")}},
      "crouch":{**{f"thigh_{s}.flex":115 for s in ("l","r")},**{f"calf_{s}.flex":135 for s in ("l","r")},"waist.pitch":25},
      "head_tilt":{"head.roll":30,"head.pitch":20},
      "hip_abduction":{"thigh_l.abduct":60,"thigh_r.abduct":60},
      "palms_turn":{"elbow_l.flex":90,"elbow_r.flex":90,"forearm_l.twist":85,"forearm_r.twist":-85}
    }
def node_positions(p,pose):
    T,A=fk(p,pose)
    anchors={"N1":"pelvis","N2":"chest","N3":"upperarm_l","N4":"upperarm_r","N5":"calf_l","N6":"calf_r"}
    return {k:(T[v][:3,3]+T[v][:3,:3]@np.array([-32,0,-65] if k in ("N3","N4") else [-42,0,0])) for k,v in anchors.items()}
