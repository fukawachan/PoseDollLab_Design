"""Search a bounded deterministic routing order; every result still requires KiCad DRC."""
import os,sys,json,itertools,time
from pathlib import Path
import pcbnew as pcb
from route_sensor_revC_mini import route
R=Path(__file__).resolve().parents[1]; O=R/'electronics/sensor_revM_sh'
orders=['MISO_IC,MISO,MOSI,CS_N,SCK,GND,+3V3','MISO,MISO_IC,CS_N,SCK,MOSI,+3V3,GND','CS_N,SCK,MISO_IC,MOSI,GND,+3V3,MISO','+3V3,GND,CS_N,SCK,MISO_IC,MISO,MOSI','MISO_IC,MISO,+3V3,GND,CS_N,SCK,MOSI']
for order in orders:
    b=pcb.LoadBoard(str(O/'placement.kicad_pcb'));os.environ['PD44_ROUTE_ORDER']=order
    try:logs=route(b)
    except RuntimeError as e: print(order,str(e),flush=True);continue
    pcb.SaveBoard(str(O/'PoseDoll_AS5048A_revM_sh.kicad_pcb'),b)
    (O/'routing_order.txt').write_text(order)
    (O/'routing_log.json').write_text(json.dumps(logs,indent=2))
    from sensor_revM_sh_rules import configure
    configure()
    print('SUCCESS',order,flush=True);break
else:sys.exit(2)
