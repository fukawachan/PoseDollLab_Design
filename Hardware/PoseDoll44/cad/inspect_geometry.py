"""Exact solid overlap screen for the H1 sweep and full-layout keyposes.
This checks nominal shapes only, not deflection, print variation or all poses."""
import json,itertools,math,hashlib
import cadquery as cq
from parts import *
from model import *
from build import layout
def bbox_overlap(a,b):
    x,y=a.BoundingBox(),b.BoundingBox()
    return all(min(getattr(x,k+"max"),getattr(y,k+"max"))-max(getattr(x,k+"min"),getattr(y,k+"min"))>1e-5 for k in "xyz")
def intersection(a,b):
    if not bbox_overlap(a,b):return 0.0
    return max(0.,a.intersect(b).Volume())
def main():
    p=all_parts()
    rotating={k:v[0] for k,v in p.items() if k.startswith(("H1-013","H1-014","H1-015"))}
    fixed={k:v[0] for k,v in p.items() if k.startswith(("H1-010","H1-011","H1-012","H1-016","H1-017"))}
    for n,s,c in hardware_reference():
        if n.startswith("magnet_"):rotating[n]=s
        else:fixed[n]=s
    results=[]
    for angle in range(0,146,5):
        hits=[]
        for rn,rs in rotating.items():
            rr=rs.rotate((0,0,0),(0,0,1),angle)
            for fn,fs in fixed.items():
                volume=intersection(rr,fs)
                if volume>.02:hits.append({"rotating":rn,"fixed":fn,"volume_mm3":round(volume,4)})
        results.append({"angle_deg":angle,"interferences":hits})
    full={}
    axes=set(profile()["axis_order"])
    for name,pose in keyposes().items():
        objects=[(n,s) for n,s,c in layout(profile(),pose) if n in axes or n.startswith(("sensor_","N"))]
        hits=[]
        for (na,a),(nb,b) in itertools.combinations(objects,2):
            v=intersection(a,b)
            if v>.1:hits.append({"a":na,"b":nb,"volume_mm3":round(v,3)})
        full[name]={"interference_count":len(hits),"interferences":hits}
    result={"input_sha256":{n:hashlib.sha256((ROOT/"cad"/n).read_bytes()).hexdigest() for n in ("parts.py","fits.py","model.py","build.py","inspect_geometry.py")}, "configuration_sha256":{"mechanical_manifest/print_fit_profile_revB.json":hashlib.sha256((ROOT/"mechanical_manifest/print_fit_profile_revB.json").read_bytes()).hexdigest()}, "method":"OpenCascade nominal solid intersection; tolerance 0.02 mm^3 for H1, 0.1 mm^3 for layout",
        "H1":{"angles":results,"all_sampled_clear":all(not x["interferences"] for x in results),
              "limitations":["nominal dimensions; not loaded","not all nuts/washers/screwheads or tool envelopes modelled","supplier AB module not substituted for our 32mm PCB","field/adhesive strength/bearing fits not verified"]},
        "full44":{"poses":full,"status":"layout_candidates_not_manufacturing_geometry",
              "limitations":["shells/sensors/node PCB and access envelopes only","no collision sweep between samples","no cable flex or grasp/tool path"]}}
    dest=ROOT/"verification/exact_geometry_screen.json"
    dest.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"H1_all_sampled_clear":result["H1"]["all_sampled_clear"],"full44":{k:v["interference_count"] for k,v in full.items()}}))
if __name__=="__main__":main()
