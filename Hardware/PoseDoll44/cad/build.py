"""Generate revision-A engineering artifacts. CAD validity is not a physical release."""
from pathlib import Path
import json, math, csv, hashlib, random, itertools, sys, zipfile
import numpy as np
import cadquery as cq
from model import *
from parts import *
OUT=ROOT/"generated"; VERIFY=ROOT/"verification"; MAN=ROOT/"mechanical_manifest"
for d in (OUT/"step",OUT/"stl_fit",OUT/"stl_draft",OUT/"images",VERIFY,MAN,ROOT/"harness"):d.mkdir(parents=True,exist_ok=True)
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def tube(a,b,r=4):
    a=np.array(a);b=np.array(b);delta=b-a;length=float(np.linalg.norm(delta))
    return cq.Solid.makeCylinder(r,length,cq.Vector(*a),cq.Vector(*(delta/length))) if length>1e-6 else cq.Solid.makeSphere(r,cq.Vector(*a))
def capsule(center,direction,r,length):
    a=np.array(center)-np.array(direction)*length/2
    return cq.Solid.makeCylinder(r,length,cq.Vector(*a),cq.Vector(*direction))
COLORS={"N1":(0.3,0.5,0.9),"N2":(0.4,0.65,0.9),"N3":(0.2,0.75,0.65),"N4":(0.3,0.8,0.6),"N5":(0.95,0.6,0.25),"N6":(0.9,0.5,0.25)}
def render(items,dest,title,camera=None,labels=False):
    import importlib, types
    vtk=types.SimpleNamespace()
    for mod in ('vtkCommonCore','vtkCommonDataModel','vtkFiltersCore','vtkRenderingCore','vtkRenderingOpenGL2','vtkRenderingFreeType','vtkIOImage','vtkInteractionStyle'):
        m=importlib.import_module('vtkmodules.'+mod)
        for k in dir(m):
            if k.startswith('vtk'):setattr(vtk,k,getattr(m,k))
    renderer=vtk.vtkRenderer();renderer.SetBackground(0.94,0.96,0.98)
    for name,shape,color in items:
        verts,faces=shape.tessellate(0.6);points=vtk.vtkPoints()
        for v in verts:points.InsertNextPoint(v.x,v.y,v.z)
        cells=vtk.vtkCellArray()
        for f in faces:
            cells.InsertNextCell(3)
            for i in f:cells.InsertCellPoint(i)
        poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
        norm=vtk.vtkPolyDataNormals();norm.SetInputData(poly);norm.ComputePointNormalsOn()
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(norm.GetOutputPort())
        actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(*color)
        renderer.AddActor(actor)
    caption=vtk.vtkTextActor();caption.SetInput(title);caption.GetTextProperty().SetFontSize(24);caption.GetTextProperty().SetColor(.12,.17,.22);caption.SetDisplayPosition(30,25);renderer.AddActor2D(caption)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1200,1000);win.AddRenderer(renderer)
    if labels:
        renderer.SetViewport(0,0,.72,1);renderer.SetLayer(1)
        background=vtk.vtkRenderer();background.SetBackground(.94,.96,.98);background.SetLayer(0)
        win.SetNumberOfLayers(3);win.AddRenderer(background)
    bb=cq.Compound.makeCompound([s for _,s,_ in items]).BoundingBox()
    center=((bb.xmin+bb.xmax)/2,(bb.ymin+bb.ymax)/2,(bb.zmin+bb.zmax)/2)
    direction=camera or (900,-1200,900)
    cam=renderer.GetActiveCamera();cam.SetPosition(*(center[i]+direction[i] for i in range(3)));cam.SetFocalPoint(*center);cam.SetViewUp(0,0,1);renderer.ResetCamera();cam.ParallelProjectionOn();renderer.ResetCameraClippingRange()
    win.Render()
    if labels:
        overlay=vtk.vtkRenderer();overlay.SetLayer(2);overlay.SetInteractive(0);win.AddRenderer(overlay)
        names={"M6_stationary_sleeve_OD8_ID6p4_L31":"Sleeve OD8 / ID6.4 / L31","POM_bushing_6":"POM bushings x2",
            "steel_thrust_0":"Steel rings + pressure ring","friction_fibre_4.5":"Friction rings x2",
            "magnet_6x2p5":"Diametric magnet 6 x 2.5","sensor_revA_PCB":"Custom sensor PCB Rev A",
            "M6x55_screw_envelope":"M6 x 55 screw","M3x90_frame_-5":"M3 x 90 frame screws x2","printed_stop_0":"H1-019 stops x2"}
        points=[]
        for name,shape,color in items:
            if not name.startswith("H1-") and name not in names:continue
            bb=shape.BoundingBox()
            renderer.SetWorldPoint((bb.xmin+bb.xmax)/2,(bb.ymin+bb.ymax)/2,(bb.zmin+bb.zmax)/2,1)
            renderer.WorldToDisplay();px,py,pz=renderer.GetDisplayPoint()
            points.append((py,px,names.get(name,name)))
        for i,(py,px,name) in enumerate(sorted(points)):
            ly=70+i*850/max(1,len(points)-1)
            label=vtk.vtkTextActor();label.SetInput(name);label.SetDisplayPosition(890,int(ly));label.GetTextProperty().SetFontSize(14);label.GetTextProperty().SetColor(.12,.17,.22);overlay.AddActor2D(label)
            pp=vtk.vtkPoints();pp.InsertNextPoint(px,py,0);pp.InsertNextPoint(876,ly+7,0)
            cells=vtk.vtkCellArray();cells.InsertNextCell(2);cells.InsertCellPoint(0);cells.InsertCellPoint(1)
            poly=vtk.vtkPolyData();poly.SetPoints(pp);poly.SetLines(cells)
            mapper=vtk.vtkPolyDataMapper2D();mapper.SetInputData(poly)
            actor=vtk.vtkActor2D();actor.SetMapper(mapper);actor.GetProperty().SetColor(.52,.61,.67);overlay.AddActor2D(actor)
        win.Render()
    f=vtk.vtkWindowToImageFilter();f.SetInput(win);f.Update()
    w=vtk.vtkPNGWriter();w.SetFileName(str(dest));w.SetInputConnection(f.GetOutputPort());w.Write();win.Finalize()
def layout(p,pose):
    T,A=fk(p,pose);items=[]
    for n in p["nodes"]:
        if n["parent"]:
            a=T[n["parent"]][:3,3];b=T[n["id"]][:3,3]
            if np.linalg.norm(b-a)>1:items.append(("link_"+n["id"],tube(a,b,4),(0.62,.67,.72)))
    for axis,a in A.items():
        f=FAMILIES[family(axis)];reg=NODE_REGIONS[axis.split(".")[0]];o=a["origin"];v=a["direction"]
        items.append((axis,capsule(o,v,f["radius_mm"],f["axial_mm"]),COLORS[reg]))
        items.append(("axis_"+axis,tube(o-v*27,o+v*27,1.0),(.9,.18,.12)))
        magnet=o+v*(f["axial_mm"]/2+6)
        items.append(("magnet_"+axis,capsule(magnet,v,3,2.5),(.9,.2,.28)))
        # Sensor and mating connector envelope, not a manufacturing PCB
        pl=cq.Plane(origin=tuple(magnet+v*6),normal=tuple(v))
        board=cq.Workplane(pl).box(32,32,1.6).val()
        items.append(("sensor_"+axis,board,(.14,.38,.27)))
    N=node_positions(p,pose)
    for name,xyz in N.items():
        items.append((name+"_PCB_placeholder",box(12,40,58,tuple(xyz)),(.13,.29,.38)))
        items.append((name+"_connector_access",box(18,46,10,tuple(xyz+np.array([-12,0,35]))),(.6,.7,.8)))
    # Locked desk mast and measured-root support.
    items.extend([("metal_stand",tube((-115,0,0),(-115,0,300),10),(.3,.34,.4)),
                  ("locked_support",tube((-115,0,260),A["pelvis.yaw"]["origin"],8),(.3,.34,.4)),
                  ("gateway_envelope",box(70,45,20,(-115,0,12)),(.15,.24,.36))])
    for axis,a in A.items():
        q=N[NODE_REGIONS[axis.split(".")[0]]]
        items.append(("cable_"+axis,tube(q,a["origin"],.65),(.78,.65,.23)))
    return items
def collision_screen(p,poses):
    result={}
    for name,pose in poses.items():
        T,A=fk(p,pose);hits=[]
        # Conservative enclosing spheres. No exemptions: even adjacent-axis overlaps are retained.
        for (an,a),(bn,b) in itertools.combinations(A.items(),2):
            fa,fb=FAMILIES[family(an)],FAMILIES[family(bn)]
            ra=math.hypot(fa["radius_mm"],fa["axial_mm"]/2)+2
            rb=math.hypot(fb["radius_mm"],fb["axial_mm"]/2)+2
            d=float(np.linalg.norm(a["origin"]-b["origin"]))
            if d<ra+rb:hits.append({"a":an,"b":bn,"distance_mm":round(d,2),"sphere_overlap_mm":round(ra+rb-d,2)})
        result[name]={"status":"requires_detailed_review" if hits else "no_joint_envelope_overlap_in_this_sample","overlaps":hits}
    return {"method":"conservative spheres enclosing joint housings + 2mm; not exact collision and not reachability proof",
            "omissions":["detailed gimbal geometry","connector insertion tool paths","cable flex","hand grasp","external magnets"],
            "poses":result}
def budgets(p,poses):
    # Each module's aggregate mass includes fasteners, magnet, sensor and shell estimate.
    nodes={n["id"]:n for n in p["nodes"]}
    def below(n,ancestor):
        while n is not None:
            if n==ancestor:return True
            n=nodes[n]["parent"]
        return False
    module={a["node"]:FAMILIES[family(a["id"])]["module_mass_g"]/1000 for a in p["axes"]}
    mass=[(n,m,None) for n,m in module.items()]
    for seg,node in p["anatomical_segments"].items():mass.append((node,0.035 if seg in ("pelvis","chest","head") else 0.018,None))
    for reg,node in zip(("N1","N2","N3","N4","N5","N6"),("pelvis","chest","upperarm_l","upperarm_r","calf_l","calf_r")):mass.append((node,.045,reg)) # regional PCB + harness + connectors
    rows=[]
    for axis in p["axes"]:
        downstream=[(n,m,reg) for n,m,reg in mass if below(n,axis["node"])]
        mx=0;worst=None;bound=0
        for name,pose in poses.items():
            T,A=fk(p,pose);o=A[axis["id"]]["origin"];v=A[axis["id"]]["direction"];moment=0;upper=0
            for n,m,reg in downstream:
                location=node_positions(p,pose)[reg] if reg else T[n][:3,3]
                delta=(location-o)/1000
                moment+=float(np.dot(np.cross(delta,[0,0,-m*9.80665]),v))
                upper+=m*9.80665*np.linalg.norm(np.cross(delta,v))
            if abs(moment)>mx:mx=abs(moment);worst=name
            bound=max(bound,upper)
        target=1.5*bound+.02;fam=family(axis["id"]);f=FAMILIES[fam]
        rows.append({"axis_id":axis["id"],"family_candidate":fam,"downstream_estimated_kg":round(sum(m for _,m,_ in downstream),3),
         "sampled_gravity_max_nm":round(mx,4),"worst_pose":worst,"orientation_independent_bound_nm":round(bound,4),
         "holding_design_target_nm":round(target,4),"grip_force_at_target_N":round(target/(f["grip_radius_mm"]/1000),2),
         "family_capacity_hypothesis_nm":f["design_capacity_nm"],"sizing":"requires_larger_clutch_or_mass_reduction" if target>f["design_capacity_nm"] else "within_unverified_capacity_hypothesis"})
    sensor=.015*44;node_mcu=.24*6;can=.06*7;buffer=.015*6
    load_3v3=sensor+node_mcu+can+buffer
    input5=load_3v3*3.3/(5*.85)+.25
    return {"mass_model":"lumped upper estimates, no measured mass; cable torque allowance 0.02Nm; module full mass counted downstream conservatively",
            "estimated_total_kg":sum(m for n,m,_ in mass),"axes":rows,
            "power":{"sensor_max_A_at3v3":sensor,"node_mcu_allowance_A_at3v3":node_mcu,"can_allowance_A_at3v3":can,
            "buffer_allowance_A_at3v3":buffer,"buck_efficiency_assumed":.85,"gateway_allowance_A_at5v":.25,
            "estimated_5v_A":round(input5,3),"with_30_percent_margin_A":round(input5*1.3,3),
            "supply_candidate":"regulated 5V 4A external, isolated from USB VBUS; NOT procurement released",
            "regional_linear_ldo_dissipation_W_at_9_sensors":round((5-3.3)*(.24+.135+.06+.015),3),
            "power_design":"regional buck conversion required; no DevKit LDO full-body supply",
            "AWG24_1m_pair_at_0_5A_voltage_drop_V":.5*.0842*2,
            "AWG20_1m_pair_at_3A_voltage_drop_V":3*.0333*2,
            "connector_thermal_short_circuit_startup_tests":"not_run"},
            "can":{"frames_per_epoch":17,"bitrate":500000,"frame_bound_bits":135,"diagnostic_frames_per_s":60,"budget_fraction":.4752},
            "stand":{"mass_kg":sum(m for n,m,_ in mass),"moment_estimate_Nm_at_150mm_plus_20N_at_400mm":sum(m for n,m,_ in mass)*9.80665*.15+8,"rated_clamp_selection":"not_frozen; vendor rating for moment and actual desk required"}}
def main():
    p=profile();save(MAN/"physical_humanoid_44_revA_layout.json",p);save(MAN/"keyposes_degrees.json",keyposes());save(MAN/"families.json",FAMILIES)
    T,A=fk(p,{})
    region_ports={n:0 for n in COLORS};axis_manifest=[]
    for i,id in enumerate(p["axis_order"]):
        region=NODE_REGIONS[id.split(".")[0]];region_ports[region]+=1
        axis_manifest.append({"protocol_index":i,"axis_id":id,"region":region,"port":region_ports[region],"family":family(id),
          "origin_neutral_mm":A[id]["origin"].tolist(),"axis_neutral":A[id]["direction"].tolist(),
          "physical_limits_deg":None,"print_release":False})
    save(MAN/"axis_manifest.json",axis_manifest)
    parts=all_parts();records=[];assy=cq.Assembly(name="HW44_H1_study");preview=[]
    palette=[(.2,.5,.7),(.3,.65,.7),(.75,.55,.25),(.8,.35,.25)]
    for i,(name,(s,status)) in enumerate(parts.items()):
        bb=s.BoundingBox();dims=[bb.xlen,bb.ylen,bb.zlen]
        if not s.isValid() or len(s.Solids())!=1:raise ValueError("Invalid/multiple solid "+name)
        if max(dims)>160:raise ValueError("A1 mini preferred envelope exceeded "+name)
        # All print files placed on Z=0. Draft orientation still needs slicer review.
        local=s.translate((-bb.xmin,-bb.ymin,-bb.zmin))
        target=OUT/("stl_fit" if status=="fit_test" else "stl_draft")
        cq.exporters.export(local,str(target/(name+".stl")),tolerance=.05,angularTolerance=.10)
        cq.exporters.export(s,str(OUT/"step"/(name+".step")))
        records.append({"part":name,"status":status,"bbox_mm":[round(v,3) for v in dims],"volume_mm3":round(s.Volume(),2),"solid_valid":True,"solids":1,
         "stl_sha256":hashlib.sha256((target/(name+".stl")).read_bytes()).hexdigest()})
        if name.startswith(("H1-00","H1-018","H1-019")):continue
        color=palette[i%len(palette)];assy.add(s,name=name,color=cq.Color(*color));preview.append((name,s,color))
    for name,s,c in hardware_reference():
        preview.append((name,s,c));assy.add(s,name=name,color=cq.Color(*c))
    assy.save(str(OUT/"step/H1_joint_study.step"))
    save(VERIFY/"cad_parts.json",records)
    with zipfile.ZipFile(OUT/"stl_fit/stl_fit.zip","w",zipfile.ZIP_DEFLATED) as archive:
        for file in sorted((OUT/"stl_fit").glob("*.stl")):archive.write(file,file.name)

    render(preview,OUT/"images/H1_joint_study.png","H1 mechanical Rev B | assumed PLA fits | not load-tested",camera=(200,-280,200))
    def explode_delta(name):
        offsets={"H1-010_base":(0,0,0),"H1-011_spine":(-35,0,0),"H1-012_upper_fork":(0,0,88),
            "H1-013_rotor_lever":(0,0,32),"H1-014_magnet_bridge":(85,0,35),"H1-015_magnet_cover":(0,0,148),
            "H1-016_sensor_arm":(0,0,180),"H1-017_sensor_carrier":(0,0,167),
            "M6_stationary_sleeve_OD8_ID6p4_L31":(-62,-20,18),"steel_thrust_0":(0,0,7),
            "steel_thrust_3":(0,0,14),"steel_thrust_26.5":(0,0,60),"steel_thrust_28":(0,0,71),
            "friction_fibre_4.5":(0,0,21),"friction_fibre_25":(0,0,48),"magnet_6x2p5":(0,0,142),
            "M6x55_screw_envelope":(-90,15,24),"M6_nut_envelope":(-90,15,44)}
        if name in offsets:return offsets[name]
        if name.startswith("POM_"):return (-50,0,32)
        if name.startswith("M3x90"):return (-60,0,70)
        if name.startswith("M3x14"):return (0,0,186)
        if name.startswith("printed_stop"):return (20,0,5)
        if name.startswith(("sensor_","AS5048A_")):return (0,0,154)
        return (0,0,0)
    exploded=[(n,s.translate(explode_delta(n)),c) for n,s,c in preview]
    render(exploded,OUT/"images/H1_exploded.png","H1 exploded | assembly review",camera=(240,-320,220),labels=True)
    fit=[(n,s.translate((0,j*90,0)),palette[j%4]) for j,(n,(s,st)) in enumerate((v for v in parts.items() if v[1][1]=="fit_test"))]
    render(fit,OUT/"images/fit_coupons.png","Rev B future fit coupons | no printing requested now",camera=(200,-300,500))
    items=layout(p,{});body=cq.Assembly(name="HW44_layout")
    for n,s,c in items:body.add(s,name=n.replace(".","_"),color=cq.Color(*c))
    body.save(str(OUT/"step/HW44_full_layout.step"))
    render(items,OUT/"images/HW44_full_layout.png","HW44 Rev A | 44 axes + 6 nodes + gateway | envelope study")
    sampled=keyposes().copy();rng=random.Random(44)
    for i in range(64):sampled[f"random_{i:03}"]={a["id"]:rng.uniform(*[math.degrees(x) for x in a["limits_rad"]]) for a in p["axes"]}
    save(VERIFY/"collision_screen.json",collision_screen(p,sampled))
    save(VERIFY/"budgets.json",budgets(p,keyposes()))
    N=node_positions(p,{});harness=[]
    for axis,a in A.items():
        reg=NODE_REGIONS[axis.split(".")[0]];worst=0
        for pose in keyposes().values():
            TT,AA=fk(p,pose);nn=node_positions(p,pose)
            worst=max(worst,float(np.linalg.norm(AA[axis]["origin"]-nn[reg])))
        length=math.ceil((worst+60)/10)*10
        harness.append({"id":"S-"+axis,"from":reg,"to":axis,"minimum_envelope_length_plus_60mm":length,
                        "status":"over_250mm_requires_node_or_SPI_port_redesign" if length>250 else "route_and_bend_validation_pending"})
    save(ROOT/"harness/sensor_lengths.json",harness)
    save(ROOT/"harness/topology.json",{"CAN_linear_order":["G0","N1","N5","N6","N3","N2","N4"],"terminations":["G0","N4"],"local_drop_max_mm_target":30,"power":"separate fused radial feeds from base; no 5V USB/external tie","status":"layout_candidate_not_wire_cut_list"})
    save(VERIFY/"generation_summary.json",{"cadquery":cq.__version__,"mechanical_revision":"B","fit_profile_id":FITS["profile_id"],"fit_profile_sha256":hashlib.sha256((MAN/"print_fit_profile_revB.json").read_bytes()).hexdigest(),"user_testing_requested_now":False,"axis_count":len(A),"regions":region_ports,"part_count":len(records),"neutral_head_tip_mm":T["head_tip"][:3,3].tolist(),"all_part_solids_valid":True,"fit_only_release":True,"manufacturing_full_body_release":False,"physical_tests":"not_run"})
    print(json.dumps({"parts":len(records),"axes":len(A),"height_head_tip_mm":T["head_tip"][2,3],"output":str(OUT)}))
if __name__=="__main__":main()
