"""Explicit fabrication rules for the mini head; apply after pcbnew SaveBoard."""
import json
from pathlib import Path
def configure():
    root=Path(__file__).resolve().parents[1]
    path=root/'electronics/sensor_revM_sh/PoseDoll_AS5048A_revM_sh.kicad_pro'
    pro=json.loads((root/'electronics/sensor_revB/PoseDoll_AS5048A_revB.kicad_pro').read_text(encoding='utf8'))
    pro['meta']['filename']=path.name
    rules=pro['board']['design_settings']['rules']
    rules.update(min_track_width=.15,min_clearance=.15,min_copper_edge_clearance=.25)
    pro['net_settings']['classes'][0].update(track_width=.15,clearance=.15)
    path.write_text(json.dumps(pro,indent=2),encoding='utf8')
if __name__=='__main__':configure()
