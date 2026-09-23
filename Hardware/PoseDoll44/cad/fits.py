"""Project fit assumptions; these values are not a measured printer calibration."""
from pathlib import Path
import json

PROFILE_PATH = Path(__file__).resolve().parents[1] / "mechanical_manifest/print_fit_profile_revB.json"
FITS = json.loads(PROFILE_PATH.read_text(encoding="utf8"))

def clearance(thread, aligned_frame=False):
    if aligned_frame:
        if thread != "M3":
            raise ValueError("Only the M3 frame has a separate alignment allowance")
        return FITS["aligned_frame_M3_mm"]
    return FITS["clearance_holes_mm"][thread]
