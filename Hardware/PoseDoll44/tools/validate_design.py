"""Cross-artifact checks; digital success never marks physical acceptance complete."""
import json,hashlib,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding="utf-8-sig"))
def main():
    p=read("mechanical_manifest/physical_humanoid_44_revA_layout.json")
    virtual=json.loads((REPO/"Shared/Profiles/virtual_humanoid_44_v1.json").read_text(encoding="utf8"))
    assert p["axis_order"]==virtual["axis_order"] and len(p["axis_order"])==44
    manifest=read("mechanical_manifest/axis_manifest.json")
    assert [v["axis_id"] for v in manifest]==p["axis_order"]
    assert [sum(v["region"]==n for v in manifest) for n in ("N1","N2","N3","N4","N5","N6")]==[6,6,9,9,7,7]
    assert all(v["physical_limits_deg"] is None and not v["print_release"] for v in manifest)
    nodes={v["id"] for v in p["nodes"]}
    for a in p["axes"]:assert a["node"] in nodes
    for node in p["nodes"]:assert node["parent"] is None or node["parent"] in nodes
    parts=read("verification/cad_parts.json");fit=[]
    for part in parts:
        assert part["solid_valid"] and part["solids"]==1 and max(part["bbox_mm"])<=160
        folder="stl_fit" if part["status"]=="fit_test" else "stl_draft"
        path=ROOT/"generated"/folder/(part["part"]+".stl")
        assert hashlib.sha256(path.read_bytes()).hexdigest()==part["stl_sha256"]
        if folder=="stl_fit":fit.append(part["part"])
    assert len(fit)==3 and len(list((ROOT/"generated/stl_fit").glob("*.stl")))==3
    ec=read("verification/sensor_erc.json")
    assert not any(v["violations"] for v in ec["sheets"])
    dr=read("verification/sensor_parity_drc.json")
    assert not dr["violations"] and not dr["unconnected_items"] and not dr["schematic_parity"]
    pads=read("electronics/sensor_revA/pad_map.json")
    actual={v["pad"]:v["net"].lstrip("/") for v in pads if v["ref"]=="J1" and v["pad"].isdigit()}
    assert actual=={"1":"GND","2":"+3V3","3":"SCK","4":"MOSI","5":"MISO","6":"CS_N"}
    g=read("verification/exact_geometry_screen.json")
    for n,digest in g["input_sha256"].items():assert hashlib.sha256((ROOT/"cad"/n).read_bytes()).hexdigest()==digest,"Stale geometry check; regenerate geometry"
    assert g["H1"]["all_sampled_clear"],"H1 geometry has a new interference"
    fits=read("mechanical_manifest/print_fit_profile_revB.json")
    profile_hash=hashlib.sha256((ROOT/"mechanical_manifest/print_fit_profile_revB.json").read_bytes()).hexdigest()
    for n,digest in g["configuration_sha256"].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==digest,"Stale configuration in geometry check"
    assert read("verification/generation_summary.json")["fit_profile_sha256"]==profile_hash
    assert read("verification/print_fit_sensitivity.json")["profile_sha256"]==profile_hash
    bore=read("verification/fit_geometry_check.json")
    assert bore["all_passed"] and bore["profile_sha256"]==profile_hash
    for n,digest in bore["step_sha256"].items():assert hashlib.sha256((ROOT/"generated/step"/(n+".step")).read_bytes()).hexdigest()==digest
    assert fits["workflow"]["user_testing_requested_now"] is False
    assert fits["status"]=="engineering_assumptions_not_machine_calibration"
    rows={r["id"]:r["diameters_mm"] for r in fits["coupon"]["rows_bottom_to_top"]}
    for thread in ("M2","M3","M4","M6"):assert fits["clearance_holes_mm"][thread] in rows[thread]
    assert fits["aligned_frame_M3_mm"] in rows["M3"]
    assert fits["bushing"]["housing_d_mm"] in rows["POM10"]
    assert fits["nut_M3"]["pocket_af_mm"] in fits["nut_M3"]["coupon_af_mm"]
    assert fits["magnet"]["seat_d_mm"] in fits["magnet"]["coupon_d_mm"]
    with zipfile.ZipFile(ROOT/"generated/stl_fit/stl_fit.zip") as archive:
        assert set(archive.namelist())=={n+".stl" for n in fit}
        for n in fit:assert archive.read(n+".stl")==(ROOT/"generated/stl_fit"/(n+".stl")).read_bytes()

    changed=subprocess.check_output(["git","diff","HEAD","--name-only"],cwd=REPO,text=True).strip().splitlines()
    # This first iteration adds only new directories; existing sources/assets remain untouched.
    protected=[n for n in changed if not n.startswith(("Hardware/PoseDoll44/","Firmware/PoseDollHardware/","Tools/PoseDollHardwareBridge/"))]
    assert not protected,"Existing software outside hardware scope modified: "+str(protected)
    out={"axis_order":"pass","region_counts":"pass","valid_print_part_solids":len(parts),
        "fit_print_exports":fit,"H1_nominal_sweep":"pass at sampled 5-degree intervals",
        "sensor_ERC_DRC_parity":"pass under recorded KiCad rules","old_tracked_sources_unchanged":True,
        "baseline_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO,text=True).strip(),
        "baseline_profile_sha256":hashlib.sha256((REPO/"Shared/Profiles/virtual_humanoid_44_v1.json").read_bytes()).hexdigest(),
        "fit_profile_id":fits["profile_id"],"fit_geometry_features_checked":len(bore["features"]),"user_testing_requested_now":False,"physical_tests":"not_run","full44_manufacturing_release":False}
    (ROOT/"verification/design_consistency.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf8")
    print(json.dumps(out))
if __name__=="__main__":main()
