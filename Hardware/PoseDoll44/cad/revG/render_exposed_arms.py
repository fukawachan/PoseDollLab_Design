"""Regenerate posed illustrations without repeating collision checks."""
from centerline_study import build,render_exposed
if __name__=='__main__':
 for name in ('manny','quinn'):
  parts,meta=build(name)
  render_exposed(parts,name)
  print(name+': rendered exposed elbow',flush=True)
