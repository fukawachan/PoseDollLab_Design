"""Open this script in CQ-editor and click Render. Choose VIEW below."""
import sys
from pathlib import Path
here=Path(__file__).resolve().parent
if str(here) not in sys.path:sys.path.insert(0,str(here))
# CQ-editor keeps Python modules between renders; reload the parameter-driven CAD.
import importlib
import fits,parts,model,build
for module in (fits,parts,model,build):importlib.reload(module)
from parts import all_parts,hardware_reference
from model import profile
from build import layout,COLORS
VIEW="H1" # "H1", "FULL44", or "FIT"
if VIEW=="FULL44":
    for name,shape,color in layout(profile(),{}):
        show_object(shape,name=name.replace(".","_"),options={"color":color,"alpha":.9})
else:
    import cadquery as cq
    fit_index=0
    for name,(shape,status) in all_parts().items():
        keep=(status=="fit_test") if VIEW=="FIT" else not name.startswith(("H1-00","H1-018","H1-019"))
        if keep:
            if VIEW=="FIT":
                shape=shape.translate((0,fit_index*90,0));fit_index+=1
            show_object(shape,name=name,options={"color":(.3,.55,.7)})
    if VIEW=="H1":
        for name,shape,color in hardware_reference():show_object(shape,name=name,options={"color":color})
