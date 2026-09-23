from assembly_core import *
s=cq.importers.importStep(str(ROOT/'electronics/power_revM/power_assembly_work.step')).val();b=s.BoundingBox();print('assembly',[b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax],len(s.Solids()),flush=True)
for i,q in enumerate(s.Solids()):
 b=q.BoundingBox();print(i,[round(x,3) for x in [b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax]],flush=True)
