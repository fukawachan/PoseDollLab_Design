from pathlib import Path
import cadquery as cq,json
R=Path(__file__).resolve().parents[2]
s=cq.importers.importStep(str(R/'generated/revK/components/sensor_revC_mini.step')).val()
for i,x in enumerate(s.Solids()):
 b=x.BoundingBox()
 print(i,{'min':[b.xmin,b.ymin,b.zmin],'max':[b.xmax,b.ymax,b.zmax],'volume':x.Volume()},flush=True)
