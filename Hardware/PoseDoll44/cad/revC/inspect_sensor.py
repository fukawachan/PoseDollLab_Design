from design import *
s=cq.importers.importStep(str(OUT/"step/sensor_revB.step")).val()
b=s.BoundingBox()
data={"bbox_mm":[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],"solids":[]}
for i,x in enumerate(s.Solids()):
 b=x.BoundingBox();data["solids"].append({"id":i,"bbox_mm":[round(v,4) for v in [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]],"volume_mm3":round(x.Volume(),4)})
save(ROOT/"verification/sensor_revB_step_dimensions.json",data)
print(json.dumps(data))
