"""Measure representative bore geometry from exported STEP, not from print results."""
from pathlib import Path
import json,hashlib,math
import cadquery as cq
from fits import FITS, PROFILE_PATH, clearance
ROOT=Path(__file__).resolve().parents[1]
features=[
    ("H1-010_base","M6_base",(0,0),-6,0,clearance("M6")),
    ("H1-012_upper_fork","M6_fork",(0,0),31,36,clearance("M6")),
    ("H1-011_spine","M3_long_frame",(-49,-5),0,76,clearance("M3",True)),
    ("H1-012_upper_fork","M3_pressure",(14*math.cos(math.pi/6),14*math.sin(math.pi/6)),34,36,clearance("M3")),
    ("H1-017_sensor_carrier","M2_PCB",(13,13),66,70,clearance("M2")),
    ("H1-013_rotor_lever","M4_load",(95,0),13,19,clearance("M4")),
    ("H1-013_rotor_lever","POM_housing",(0,0),6,25,FITS["bushing"]["housing_d_mm"]),
    ("H1-014_magnet_bridge","magnet_seat",(0,0),62-FITS["magnet"]["seat_depth_mm"],62,FITS["magnet"]["seat_d_mm"])]
for row in FITS["coupon"]["rows_bottom_to_top"]:
    for col,d in enumerate(row["diameters_mm"]):
        features.append(("H1-001_fit_coupon",row["id"]+"_"+chr(65+col),(-44+22*col,row["y_mm"]),0,6,d))
for i,d in enumerate(FITS["magnet"]["coupon_d_mm"]):
    features.append(("H1-002_nut_magnet_coupon","magnet_"+chr(65+i),(-30+i*20,-10),8-FITS["magnet"]["seat_depth_mm"],8,d))
shapes={};records=[]
for name,label,xy,z0,z1,d in features:
    path=ROOT/"generated/step"/(name+".step")
    if name not in shapes:shapes[name]=cq.importers.importStep(str(path)).val()
    shape=shapes[name]
    def probe(diameter):
        return cq.Solid.makeCylinder(diameter/2,z1-z0-0.1,cq.Vector(xy[0],xy[1],z0+0.05))
    inside=max(0.0,shape.intersect(probe(d-0.02)).Volume())
    outside=max(0.0,shape.intersect(probe(d+0.02)).Volume())
    passed=inside<0.001 and outside>0.001
    records.append({"part":name,"feature":label,"design_d_mm":d,"inner_probe_overlap_mm3":round(inside,6),
        "outer_probe_overlap_mm3":round(outside,6),"pass":passed})
out={"profile_sha256":hashlib.sha256(PROFILE_PATH.read_bytes()).hexdigest(),
    "method":"STEP imports: design diameter minus 0.02mm probe is clear and plus 0.02mm intersects; skip 0.05mm at each end",
    "step_sha256":{name:hashlib.sha256((ROOT/"generated/step"/(name+".step")).read_bytes()).hexdigest() for name in shapes},
    "features":records,"all_passed":all(x["pass"] for x in records),
    "limitations":["representative bores only; slots/hex pockets not measured here","nominal CAD only, not printed size, strength, concentricity or procurement tolerance"]}
(ROOT/"verification/fit_geometry_check.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf8")
print(json.dumps({"checked":len(records),"all_passed":out["all_passed"],"failed":[x for x in records if not x["pass"]]}))
if not out["all_passed"]:raise SystemExit(1)
