from final_model import *
import inspect
print(inspect.signature(cq.Shape.exportStep));print(cq.Shape.exportStep.__doc__)
folder=ROOT/'generated/revM/manny';data=json.loads((ROOT/'verification/revM_print_mesh_export.json').read_text())
from OCP.ShapeFix import ShapeFix_Shape
for row in data['manny']['prints']:
 if not row['print_process_STEP']:continue
 p=folder/row['print_process_STEP'];s=cq.importers.importStep(str(p)).val();fix=ShapeFix_Shape(s.wrapped);fix.SetPrecision(1e-5);fix.SetMaxTolerance(1e-4);fix.Perform();q=cq.Shape.cast(fix.Shape());print(row['id'],'read',s.isValid(),len(s.Solids()),'heal',q.isValid(),len(q.Solids()),'volume',q.Volume()-row['print_process_volume_mm3'],flush=True)
