"""Full44 compact mechanical design candidate. No physical acceptance is implied."""
from pathlib import Path
import sys,json,math,hashlib,itertools
import numpy as np
import cadquery as cq
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from model import fk,rotation,NODE_REGIONS,keyposes
from build import render
ROOT=HERE.parents[1]; REPO=ROOT.parents[1]; OUT=ROOT/"generated/revC"
for d in ("step","stl_review","images"): (OUT/d).mkdir(exist_ok=True)
BASE=json.loads((REPO/"Shared/Profiles/virtual_humanoid_44_v1.json").read_text(encoding="utf8"))
# Shared shaft diameter; ring size changes with load and articulation.
RADII={"pelvis":26,"waist":23,"chest":20,"head":16,"clavicle":14,"shoulder":18,"hip":20,"wrist":14,"ankle":16,"elbow":17,"knee":19,"toe":12}
SENSOR_STEP=OUT/"step/sensor_revB.step"
SENSOR_IF=ROOT/"electronics/sensor_revB/mechanical_interface.json"
PCB_NATIVE=None
COL={"print":(.22,.53,.66),"rotor":(.82,.56,.23),"metal":(.64,.67,.70),"pom":(.85,.87,.82),"pcb":(.10,.36,.23),"magnet":(.75,.18,.20)}
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def cube(dims,at):return cq.Workplane("XY").box(*dims).translate(at).val()
def rod(a,b,r):
    a,b=np.array(a,float),np.array(b,float);d=b-a
    if np.linalg.norm(d)<1e-8:return cq.Solid.makeSphere(r,cq.Vector(*a))
    return cq.Solid.makeCylinder(r,float(np.linalg.norm(d)),cq.Vector(*a),cq.Vector(*(d/np.linalg.norm(d))))
def bore(shape,a,b,r):return shape.cut(rod(a,b,r))
def ring(radius,width,height):
    return cq.Workplane("XY").circle(radius+width/2).circle(radius-width/2).extrude(height).translate((0,0,-height/2)).val()
def matrix(basis=np.eye(3),at=(0,0,0)):
    out=np.eye(4);out[:3,:3]=basis;out[:3,3]=at;return out
def moved(s,T):return s.moved(cq.Location(cq.Plane(origin=tuple(T[:3,3]),xDir=tuple(T[:3,0]),normal=tuple(T[:3,2]))))
def rot(axis,q):return matrix(rotation(axis,q))
def profile():
    p=json.loads(json.dumps(BASE));p["profile_id"]="physical_humanoid_44_revC_design"
    p["status"]="DIGITAL_DESIGN_CANDIDATE_NOT_CALIBRATED"
    for n in p["nodes"]:
        name=n["id"];pre=name.split(".")[0];v=[0,0,0]
        if name=="pelvis.yaw_frame":v=[0,0,250]
        elif name=="pelvis.pitch_frame":v=[0,0,38]
        elif name=="waist.yaw_frame":v=[0,0,44]
        elif name=="waist.pitch_frame":v=[0,0,35]
        elif name=="chest.yaw_frame":v=[0,0,36]
        elif name=="chest.pitch_frame":v=[0,0,32]
        elif name=="head.yaw_frame":v=[0,0,43]
        elif name=="head.pitch_frame":v=[0,0,28]
        elif name=="head_tip":v=[0,0,44]
        elif name.startswith("clavicle_") and name.endswith("protract_frame"):v=[0,68 if "_l" in name else -68,20]
        elif name.startswith("upperarm_"):
            side=1 if "_l" in name else -1
            if name.endswith("flex_frame"):v=[30,side*40,-20]
            elif name.endswith("abduct_frame"):v=[0,side*56,0]
            else:v=[0,0,-40]
        elif name.startswith("elbow_"):v=[0,0,-90]
        elif name.startswith("forearm_"):v=[0,0,-45]
        elif name.startswith("hand_") and not name.startswith("hand_tip"):
            if name.endswith("flex_frame"):v=[0,0,-85]
        elif name.startswith("hand_tip"):v=[0,0,-40]
        elif name.startswith("thigh_"):
            if name.endswith("flex_frame"):v=[0,75 if "_l" in name else -75,-43]
            elif "." not in name:v=[0,0,-80]
        elif name.startswith("calf_"):v=[0,0,-50]
        elif name.startswith("foot_") and name.endswith("dorsiflex_frame"):v=[0,0,-105]
        elif name.startswith("ball_"):v=[53,0,-18]
        elif name.startswith("sole_"):v=[15,0,-20]
        elif name.startswith("heel_"):v=[-18,0,-20]
        elif name.startswith("toe_tip"):v=[26,0,0]
        n["parent_to_axis"]["translation_m"]=[x/1000 for x in v]
    p["notes_zh"]=["Rev C 紧凑叉架与轴向扭转布局；尚未标定，不可冒用虚拟设备。","44轴ID、顺序、旋转方向保留。参数和 CAD 同源。"]
    return p
def groups(p):
    axis={a["id"]:a for a in p["axes"]}
    def group(id,kind,ids,R,direction,axial_output=False):
        return dict(id=id,kind=kind,axes=ids,radius_mm=R,direction=direction,axial_output=axial_output)
    out=[]
    for prefix in ("pelvis","waist","chest","head"):
        out.append(group(prefix+"_yaw","inline",[prefix+".yaw"],RADII[prefix],[0,0,1]))
        out.append(group(prefix+"_gimbal","gimbal",[prefix+".pitch",prefix+".roll"],RADII[prefix],[0,0,1]))
    for side,sgn in (("l",1),("r",-1)):
        out += [
            group("clavicle_"+side,"gimbal",[f"clavicle_{side}.protract",f"clavicle_{side}.elevate"],RADII["clavicle"],[0,sgn,0]),
            group("shoulder_flex_"+side,"hinge",[f"upperarm_{side}.flex"],RADII["shoulder"],[0,0,-1],True),
            group("shoulder_abduct_"+side,"hinge",[f"upperarm_{side}.abduct"],RADII["shoulder"],[0,0,-1]),
            group("upperarm_twist_"+side,"inline",[f"upperarm_{side}.twist"],14,[0,0,-1]),
            group("elbow_"+side,"hinge",[f"elbow_{side}.flex"],RADII["elbow"],[0,0,-1]),
            group("forearm_twist_"+side,"inline",[f"forearm_{side}.twist"],12,[0,0,-1]),
            group("wrist_"+side,"gimbal",[f"hand_{side}.flex",f"hand_{side}.deviate"],RADII["wrist"],[0,0,-1]),
            group("hip_"+side,"gimbal",[f"thigh_{side}.flex",f"thigh_{side}.abduct"],RADII["hip"],[0,0,-1]),
            group("thigh_twist_"+side,"inline",[f"thigh_{side}.twist"],16,[0,0,-1]),
            group("knee_"+side,"hinge",[f"calf_{side}.flex"],RADII["knee"],[0,0,-1]),
            group("ankle_"+side,"gimbal",[f"foot_{side}.dorsiflex",f"foot_{side}.invert"],RADII["ankle"],[0,0,-1]),
            group("toe_"+side,"hinge",[f"ball_{side}.flex"],RADII["toe"],[1,0,0])
        ]
    assert len({a for g in out for a in g["axes"]})==44
    return out
def geometry(p,pose,include_hardware=True):
    T,A=fk(p,pose);nodes={n["id"]:n for n in p["nodes"]};axes={a["id"]:a for a in p["axes"]}
    pieces=[];attachments={};owner_groups={axes[g["axes"][-1]]["node"]:g["id"] for g in groups(p)};members={a:g["id"] for g in groups(p) for a in g["axes"]}
    def add(group,label,s,M,owner,material="print"):
        if not s.isValid():raise ValueError(group+"/"+label)
        pieces.append(dict(name=group+"__"+label,group=group,shape=moved(s,M),local_shape=s,transform=M,owner=owner,material=material))
    def sensor(group,label,base,axis,distance,stator,rotor,q):
        # Use the exported KiCad assembly, including the real connector and passives.
        global PCB_NATIVE
        if PCB_NATIVE is None:PCB_NATIVE=cq.importers.importStep(str(SENSOR_STEP)).val()
        a=np.array(axis,float);z=a;ex=np.array([0,0,1.]) if abs(z[2])<.9 else np.array([1.,0,0])
        ex=ex-z*np.dot(ex,z);ex/=np.linalg.norm(ex);ey=np.cross(z,ex)
        B=base@matrix(np.column_stack([ex,ey,z]))
        pcb_shape=PCB_NATIVE.rotate((0,0,0),(1,0,0),180).translate((0,0,distance+21.6))
        add(group,label+"_pcb_assembly",pcb_shape,B,stator,"pcb")
        magnet=rod((0,0,distance+15),(0,0,distance+17.5),3)
        add(group,label+"_magnet",magnet,B@rot([0,0,1],q),rotor,"magnet")
    for g in groups(p):
        name=g["id"];ids=g["axes"];r=g["radius_mm"];a0=ids[0];node=axes[a0]["node"]
        parent=nodes[node]["parent"];endnode=axes[ids[-1]]["node"];outdir=np.array(g["direction"],float)
        if g["kind"]=="inline":
            v=np.array(nodes[node]["axis_local"],float)
            sign=float(np.dot(v,outdir));v=outdir.copy()
            ex=np.array([1.,0,0])
            if parent in owner_groups and owner_groups[parent] in attachments:
                world_delta=attachments[owner_groups[parent]]["output"][:3]-A[a0]["origin"]
                ex=A[a0]["frame"][:3,:3].T@world_delta
            ex-=v*np.dot(ex,v)
            if np.linalg.norm(ex)<1e-6:ex=np.array([1.,0,0])
            ex/=np.linalg.norm(ex);B=np.column_stack([ex,np.cross(v,ex),v])
            frame=A[a0]["frame"]@matrix(B);turn=frame@rot([0,0,1],pose.get(a0,0)*sign)
            shell=cq.Workplane("XY").circle(r).circle(6).extrude(10).translate((0,0,-10)).val()
            disc=cq.Workplane("XY").circle(r-2).circle(4.2).extrude(4).translate((0,0,1)).val()
            for x in (-.65*r,.65*r):
                shell=bore(shell,(x,0,-12),(x,0,2),1.8)
                disc=bore(disc,(x,0,0),(x,0,6),1.8)
            shell=shell.fuse(rod((r-2,0,-5),(r+6,0,-24),3.5))
            add(name,"stator_shell",shell,frame,parent)
            add(name,"output_flange",disc,turn,endnode,"rotor")
            add(name,"shaft",rod((0,0,-12),(0,0,7),4),turn,endnode,"metal")
            sensor(name,"axis",frame,[0,0,-1],0,parent,endnode,pose.get(a0,0)*sign)
            attachments[name]=dict(input=frame@np.array([r+6,0,-24,1]),output=turn@np.array([r-4,0,5,1]),input_owner=parent,output_owner=endnode)
            continue
        v=np.array(nodes[node]["axis_local"],float)
        if g["kind"]=="gimbal":
            b=np.array(nodes[axes[ids[1]]["node"]]["axis_local"],float)
        else:
            b=np.cross(v,outdir);b/=np.linalg.norm(b)
        z=np.cross(b,v);basis=np.column_stack([b,v,z])
        frame=A[a0]["frame"]@matrix(basis);sign=float(np.sign(np.dot(z,outdir)))
        turn1=frame@rot([0,1,0],pose.get(a0,0))
        axial_side=1 if name.endswith("_r") else -1
        sensor_side=(-axial_side if g["axial_output"] else (-1 if name=="hip_l" else 1))
        q2=pose.get(ids[-1],0) if g["kind"]=="gimbal" else 0
        turn2=turn1@rot([1,0,0],q2)
        input_z=-sign*(r+8)
        fork_back=(-35*sign if name.startswith("hip_") else (-16 if name.startswith(("elbow_","knee_")) else 0))
        fork=rod((fork_back,-r-10,input_z),(fork_back,r+10,input_z),4)
        for side in (-1,1):
            y=side*(r+10)
            fork=fork.fuse(rod((fork_back,y,input_z),(0,y,0),4))
            pod=rod((0,side*(r+6),0),(0,side*(r+14),0),8)
            pod=bore(pod,(0,side*(r+5),0),(0,side*(r+15),0),5.25)
            fork=fork.fuse(pod)
        for side in (-1,1):fork=bore(fork,(0,side*(r+4),0),(0,side*(r+16),0),5.25)
        add(name,"input_fork",fork,frame,parent)
        if g["kind"]=="gimbal":
            middle=ring(r,6,6)
            for side in (-1,1):
                middle=middle.fuse(rod((side*(r-4),0,0),(side*(r+5),0,0),7))
                middle=bore(middle,(side*(r-5),0,0),(side*(r+6),0,0),5.25)
                # Separate aluminium stub axles keep the centre free.
                add(name,"a_stub_"+str(side),rod((0,side*(r-3),0),(0,side*(r+15),0),4),turn1,node,"metal")
            add(name,"middle_yoke",middle,turn1,node,"rotor")
            inner=cube((12,14,10),(0,0,0)).fuse(rod((0,0,0),(0,0,sign*12),3.5))
            inner=inner.fuse(rod((-16,0,sign*12),(16,0,sign*12),3))
            for xx in (-16,16):inner=inner.fuse(rod((xx,0,sign*12),(xx,0,sign*(r+8)),3))
            inner=bore(inner,(-8,0,0),(8,0,0),4.3)
            add(name,"output_hub",inner,turn2,endnode,"rotor")
            add(name,"b_shaft",rod((-r-15,0,0),(r+15,0,0),4),turn2,endnode,"metal")
            sensor(name,"b_axis",turn1,[-sign,0,0],r,node,endnode,q2)
        else:
            inner=cube((14,12,10),(0,0,0))
            if not g["axial_output"]:
                inner=inner.fuse(rod((0,0,0),(0,0,sign*12),3.5))
                inner=inner.fuse(rod((-16,0,sign*12),(16,0,sign*12),3))
                for xx in (-16,16):inner=inner.fuse(rod((xx,0,sign*12),(xx,0,sign*(r+8)),3))
            inner=bore(inner,(0,-8,0),(0,8,0),4.3)
            add(name,"output_hub",inner,turn1,endnode,"rotor")
            add(name,"a_shaft",rod((0,-r-(15 if sensor_side==-1 else 18),0),(0,r+(15 if sensor_side==1 else 18),0),4),turn1,endnode,"metal")
        sensor(name,"a_axis",frame,[0,sensor_side,0],r,parent,node,pose.get(a0,0)*sensor_side)
        output=np.array([0,axial_side*(r+18),0,1]) if g["axial_output"] else np.array([16,0,sign*(r+8),1])
        attachments[name]=dict(input=frame@np.array([fork_back,0,input_z,1]),output=turn2@output,input_owner=parent,output_owner=endnode)
    # Layout connecting members follow the exact kinematic parent group. They are
    # deliberately labelled as routing studies until their attachment geometry is detailed.
    node_groups={g["axes"][-1]:g["id"] for g in groups(p)}
    owner_groups={axes[g["axes"][-1]]["node"]:g["id"] for g in groups(p)}
    for g in groups(p):
        dest=attachments[g["id"]];parent=dest["input_owner"]
        if parent not in owner_groups:continue
        source=attachments[owner_groups[parent]]
        a=source["output"][:3];b=dest["input"][:3]
        if np.linalg.norm(b-a)<1:continue
        if g["id"].startswith("hip_"):
            f=T[parent];sgn=1 if g["id"].endswith("_l") else -1
            c=(f@np.array([-55,sgn*95,24,1]))[:3]
            d=(f@np.array([-55,sgn*95,-10,1]))[:3]
            link=rod(a,c,3.5).fuse(rod(c,d,3.5)).fuse(rod(d,b,3.5))
        elif g["id"].startswith("shoulder_abduct_"):
            parent_inv=np.linalg.inv(T[parent]); al=(parent_inv@np.r_[a,1])[:3]; bl=(parent_inv@np.r_[b,1])[:3]
            c=(T[parent]@np.array([al[0],al[1],bl[2],1]))[:3]
            link=rod(a,c,3.5).fuse(rod(c,b,3.5))
        else:link=rod(a,b,3.5)
        add(g["id"],"link_route_candidate",link,np.eye(4),parent)
    return pieces,attachments
def bbox_overlap(a,b):
    aa,bb=a.BoundingBox(),b.BoundingBox()
    return all(min(getattr(aa,k+"max"),getattr(bb,k+"max"))>max(getattr(aa,k+"min"),getattr(bb,k+"min"))+.01 for k in "xyz")
def collisions(items,within=True):
    hits=[]
    bounds={x["name"]:x["shape"].BoundingBox() for x in items}
    solids={x["name"]:[(s,s.BoundingBox()) for s in x["shape"].Solids()] for x in items}
    for a,b in itertools.combinations(items,2):
        if a["owner"]==b["owner"]:continue
        if not within and a["group"]==b["group"]:continue
        aa,bb=bounds[a["name"]],bounds[b["name"]]
        if not all(min(getattr(aa,k+"max"),getattr(bb,k+"max"))>max(getattr(aa,k+"min"),getattr(bb,k+"min"))+.01 for k in "xyz"):continue
        pairs=[(sa,sb) for sa,ab in solids[a["name"]] for sb,bb in solids[b["name"]] if all(min(getattr(ab,k+"max"),getattr(bb,k+"max"))>max(getattr(ab,k+"min"),getattr(bb,k+"min"))+.01 for k in "xyz")]
        if not pairs:continue
        v=sum(sa.intersect(sb).Volume() for sa,sb in pairs)
        if v>.1:hits.append(dict(a=a["name"],b=b["name"],volume_mm3=round(v,3)))
    return hits
def main():
    p=profile();save(ROOT/"mechanical_manifest/physical_humanoid_44_revC_design.json",p)
    save(ROOT/"mechanical_manifest/module_groups_revC.json",groups(p))
    items,_=geometry(p,{})
    assy=cq.Assembly(name="HW44_RevC_compact_design")
    for item in items:assy.add(item["shape"],name=item["name"],color=cq.Color(*COL[item["material"]]))
    assy.save(str(OUT/"step/HW44_revC_candidate.step"))
    render([(x["name"],x["shape"],COL[x["material"]]) for x in items],OUT/"images/HW44_revC_candidate.png","HW44 Rev C | compact mechanism development | not manufacturing released")
    hits=collisions(items)
    T,A=fk(p,{})
    save(ROOT/"verification/revC_initial_geometry.json",dict(component_count=len(items),axis_count=len(A),head_tip_mm=T["head_tip"][:3,3].tolist(),neutral_collisions=hits,
        status="development_iteration_not_release",source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    print(json.dumps({"components":len(items),"head_tip":T["head_tip"][:3,3].tolist(),"neutral_collisions":len(hits)}))
if __name__=="__main__":main()
