"""Sensitivity bookkeeping, not simulated or measured manufacturing accuracy."""
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/"mechanical_manifest/print_fit_profile_revB.json"
p=json.loads(path.read_text(encoding="utf8"))
scenarios=p["diameter_error_scenarios_mm"]
rows=[]
for thread,d in p["clearance_holes_mm"].items():
    nominal=float(thread[1:])
    rows.append({"interface":thread+"_clearance","cad_d_mm":d,"nominal_hardware_d_mm":nominal,
        "diametral_clearance_by_scenario_mm":[round(d+error-nominal,3) for error in scenarios],
        "in_H1":thread!="M5"})
rows.append({"interface":"M3_aligned_frame","cad_d_mm":p["aligned_frame_M3_mm"],"nominal_hardware_d_mm":3,
    "diametral_clearance_by_scenario_mm":[round(p["aligned_frame_M3_mm"]+e-3,3) for e in scenarios],"in_H1":True})
critical=[]
for name,cad,part in (("POM_housing",p["bushing"]["housing_d_mm"],p["bushing"]["nominal_od_mm"]),
                      ("magnet_seat",p["magnet"]["seat_d_mm"],p["magnet"]["nominal_d_mm"])):
    critical.append({"interface":name,"cad_d_mm":cad,"nominal_part_d_mm":part,
        "diametral_clearance_by_scenario_mm":[round(cad+e-part,3) for e in scenarios],
        "conclusion":"range spans interference and clearance; retention/centring design and later fit test required"})
out={"profile_id":p["profile_id"],"profile_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
    "kind":"sensitivity_only_not_printer_tolerance_or_acceptance","diameter_error_scenarios_mm":scenarios,
    "screw_holes":rows,"precision_interfaces":critical,
    "omissions":["actual fastener dimensional tolerance","hole centre misalignment","horizontal-hole sag","ovality","elephant foot","long-hole straightness","load/creep"],
    "design_blocked_by_missing_user_measurements":False,"user_testing_requested_now":False,"physical_tests":"not_run"}
(ROOT/"verification/print_fit_sensitivity.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf8")
print(json.dumps({"screw_interfaces":len(rows),"precision_interfaces_for_separate_review":len(critical),"physical_tests":"not_run"}))
