from assembly_core import *
p=ROOT/'electronics/sensor_revM_side/sensor_revM_side.step'
s=cq.importers.importStep(str(p)).val()
for i,q in enumerate(s.Solids()):
 b=q.BoundingBox();print(i,[round(x,4) for x in [b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax]],flush=True)
