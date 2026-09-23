"""Local max-envelope STEP assets. These are not vendor STEP models."""
from compact_axis import *
O=ROOT/'generated/revM/electronic_envelopes';O.mkdir(parents=True,exist_ok=True)
cq.exporters.export(cube((2.15,1.4,1.05),(0,0,.525)),str(O/'GRM219R61E106KA12D_max_with_solder.step'))
print(O)
