"""Read-only consistency checks for an architecture plan, not hardware validation.

Usage:
  python tools/check_plan.py
  python tools/check_plan.py --repo C:\\Projects\\DollSimulation
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def validate(architecture: dict[str, Any], allocation: dict[str, Any], targets: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    def check(name: str, result: bool) -> None:
        checks.append({"check": name, "passed": bool(result)})

    entries = allocation.get("axes", [])
    order = allocation.get("axis_order", [])
    regions = allocation.get("regions", [])
    check("44 unique axis ids", len(order) == 44 and len(set(order)) == 44)
    check("exactly 44 allocation records", len(entries) == 44)
    check("allocation uses protocol order", [a.get("axis_id") for a in entries] == order)
    check("protocol indices cover 0..43", [a.get("protocol_index") for a in entries] == list(range(44)))
    check("six unique regional nodes", len(regions) == 6 and len({r["node_id"] for r in regions}) == 6)
    check("all axes allocated once to regional ports", len({(a["region_node"], a["logical_port"]) for a in entries}) == 44)
    check("regions partition all indices", sorted(i for r in regions for i in r["sensor_indices"]) == list(range(44)))
    check("regional axis totals equal 44", sum(r["axis_count"] for r in regions) == 44)
    check("regional list counts agree", all(r["axis_count"] == len(r["sensor_indices"]) for r in regions))
    check("port capacity is not exceeded", all(0 < r["axis_count"] <= r["port_capacity"] <= 10 for r in regions))
    region_map = {r["node_id"]: r for r in regions}
    check("regional membership agrees with allocation", all(
        a["region_node"] in region_map and a["protocol_index"] in region_map[a["region_node"]]["sensor_indices"]
        for a in entries))
    check("ports sequential within region", all(
        [a["logical_port"] for a in entries if a["region_node"] == r["node_id"]]
        == [f"P{i:02d}" for i in range(1, r["axis_count"]+1)] for r in regions))
    check("reference rotation axes are normalized", all(
        len(a["reference_axis_local"]) == 3 and abs(sum(x*x for x in a["reference_axis_local"])-1.0) < 1e-9
        for a in entries))
    check("unreleased mechanical limits not fabricated", all(a["physical_limits_deg"] is None for a in entries))
    check("unreleased connector pinouts not fabricated", all(a["connector_pinout"] is None for a in entries))
    check("no manufacturing or procurement gates released", all(v is False for v in architecture["release_gates"].values()))
    check("sensor count matches scope", architecture["scope"]["measured_rotary_axes"] == len(entries))
    check("gateway and node count matches architecture", architecture["scope"]["gateway_nodes"] == 1 and architecture["scope"]["acquisition_nodes"] == len(regions))
    check("external CAN transceiver required", architecture["electronics_baseline"]["external_can_transceiver_required"] is True)
    check("classic CAN specified", architecture["electronics_baseline"]["can_format"] == "classic_11bit_not_CAN_FD")
    check("preferred part envelope below printer volume", all(
        a < b for a,b in zip(architecture["mechanical_targets"]["preferred_part_envelope_mm"], architecture["mechanical_targets"]["printer_volume_mm"])))
    check("all physical targets explicitly untested", all(m["status"] == "not_run" and m["evidence"] is None for m in targets["metrics"]))
    check("all hardware stages explicitly untested", all(s["status"] == "not_run" and s["evidence"] is None for s in targets["release_stages"]))
    frames = sum(math.ceil(r["axis_count"]/3) for r in regions)
    timing=architecture["timing_targets"]
    bitrate=architecture["electronics_baseline"]["can_bitrate"]
    load=((frames+1)*timing["acquisition_hz"]+len(regions)*timing["diagnostic_node_hz"])*135/bitrate
    check("estimated bus load below budget", load < timing["normal_bus_load_budget_fraction"])
    return {
        "scope": "PLAN_INTERNAL_CONSISTENCY_ONLY_NOT_HARDWARE_VALIDATION",
        "checks": checks,
        "passed": all(c["passed"] for c in checks),
        "calculations_not_measurements": {
            "axis_count": len(entries), "regional_data_frames_per_epoch": frames,
            "frames_including_sync_per_epoch": frames+1,
            "nominal_can_load_fraction": round(load,6),
            "assumed_bits_per_full_can_frame":135,
            "epoch_u16_wrap_seconds_at_target_rate":65536/timing["acquisition_hz"],
            "encoder_quantization_deg":360/architecture["electronics_baseline"]["encoder_counts_per_turn"],
            "sensor_only_current_ceiling_ma_from_15ma_per_part":15*len(entries)
        },
        "not_verified": ["CAD geometry", "manufacturability", "electrical design", "power safety", "actual parts availability", "sensor accuracy", "mechanical strength", "physical wear", "new firmware", "UE hardware integration"]
    }


def inspect_repo(repo: Path, architecture: dict[str,Any], allocation: dict[str,Any]) -> dict[str,Any]:
    profile_path=repo/architecture["baseline_profile_path"]
    calibration_path=repo/architecture["baseline_calibration_path"]
    result: dict[str,Any]={"read_only":True, "repository_path":str(repo), "warnings":[]}
    if not profile_path.is_file() or not calibration_path.is_file():
        result["compatible_axis_order"]=False
        result["warnings"].append("Expected virtual profile/calibration files not found; inspect current layout. No files changed.")
        return result
    profile=load_json(profile_path)
    result["compatible_axis_order"]=profile.get("axis_order")==allocation["axis_order"]
    for key,path,expected in [
        ("virtual_profile",profile_path,architecture["baseline_profile_sha256"]),
        ("virtual_calibration",calibration_path,architecture["baseline_calibration_sha256"])
    ]:
        current=hashlib.sha256(path.read_bytes()).hexdigest()
        result[key]={"sha256":current,"matches_reviewed_baseline":current==expected}
        if current!=expected:
            result["warnings"].append(f"{key} differs from reviewed baseline: re-audit before integration; do NOT overwrite/reset it.")
    return result


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",type=Path,help="Optional existing DollSimulation checkout, read-only")
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    try:
        a=load_json(root/"contracts/architecture.json")
        m=load_json(root/"contracts/axis_allocation.json")
        t=load_json(root/"contracts/acceptance_targets.json")
        report=validate(a,m,t)
        if args.repo:
            report["repository_comparison"]=inspect_repo(args.repo.resolve(),a,m)
            if not report["repository_comparison"]["compatible_axis_order"]:
                report["passed"]=False
        print(json.dumps(report,ensure_ascii=False,indent=2))
        return 0 if report["passed"] else 1
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({"passed":False,"scope":"PLAN_CHECK_ERROR","error":str(exc)},ensure_ascii=False,indent=2))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
