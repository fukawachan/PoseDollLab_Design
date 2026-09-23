"""Mechanical contract from actual KiCad board; component-face XY coordinates."""
from pathlib import Path
import json,hashlib
import pcbnew as pcb
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"electronics/sensor_revB"
f=OUT/"PoseDoll_AS5048A_revB.kicad_pcb";b=pcb.LoadBoard(str(f))
footprints={}
for x in b.GetFootprints():
 ref=x.GetReference();p=x.GetPosition();footprints[ref]={"xy_mm":[pcb.ToMM(p.x)-109,pcb.ToMM(p.y)-110],"layer":"front_sensor_face" if x.IsOnLayer(pcb.F_Cu) else "back_connector_face","orientation_deg":x.GetOrientationDegrees()}
d={"schema_version":1,"revision":"B","status":"digital_candidate_not_manufacturing_release","pcb_size_mm":[18,20,1.6],"component_face_axes":"X = KiCad +X; Y = KiCad +Y, toward mounting holes; Z away from magnet","chip_center_in_board_mm":[9,10],"mount_holes_xy_mm":[[-6.5,6.5],[6.5,6.5]],"mount_hole_d_mm":2.2,"mounting_fastener":"M2 nylon + insulating spreaders; do not substitute conductive washers without copper-clearance review","footprints":footprints,"spi_pins":{"1":"GND","2":"+3V3","3":"SCK","4":"MOSI","5":"MISO","6":"CS_N"},"connector_side":"back","source_sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"note":"True component solids are in sensor_revB.step; mated plug and cable bend allowance are not included in that STEP."}
(OUT/"mechanical_interface.json").write_text(json.dumps(d,indent=2)+"\n",encoding="utf8")
print("sensor_revB mechanical contract exported")
