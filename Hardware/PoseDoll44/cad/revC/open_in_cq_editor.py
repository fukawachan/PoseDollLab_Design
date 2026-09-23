"""Open in CQ-editor and Render. FULL44 is a motion layout; H2 is a separate fixture."""
from pathlib import Path
import sys,importlib
here=Path(__file__).resolve().parent
for p in (here.parent,here):
 if str(p) in sys.path:sys.path.remove(str(p))
 sys.path.insert(0,str(p))
import design
importlib.reload(design)
VIEW="FULL44" # FULL44, H2_S, H2_M, H2_L
if VIEW=="FULL44":
 pieces,_=design.geometry(design.profile(),{})
 for x in pieces:show_object(x["shape"],name=x["name"],options={"color":design.COL[x["material"]]})
else:
 import clutch
 importlib.reload(clutch)
 for x in clutch.cartridge(VIEW[-1]):show_object(x["shape"],name=x["name"],options={"color":clutch.COLORS[x["material"]]})
