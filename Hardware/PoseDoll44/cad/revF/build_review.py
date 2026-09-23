"""Offline mechanical review: tessellation for display, STEP remains the CAD source."""
from arm_packaging import *

def mesh(parts):
 result=[]
 for p in parts:
  vertices,triangles=p['shape'].tessellate(.35,.3)
  result.append({'name':p['name'],'owner':p['owner'],'material':p['material'],'color':COL[p['material']],'note':p['note'],'vertices':[[round(c,4) for c in v.toTuple()] for v in vertices],'triangles':[list(t) for t in triangles]})
 return result

def main():
 data={'arms':{},'joint':mesh(neutral_joint('M6')[0])}
 for name in ('manny','quinn'):
  parts,meta=geometry(name);data['arms'][name]={'parts':mesh(parts),'meta':meta,'mass_g':sum(mass(p) for p in parts)}
 template=(HERE/'review.template.html').read_text(encoding='utf8')
 (OUT/'RevF_Mechanical_Review.html').write_text(template.replace('__CAD_DATA__',json.dumps(data,separators=(',',':'))),encoding='utf8')
 # Front-oblique comparison from the exact same neutral CAD objects.
 items=[]
 for name,offset in [('manny',-100),('quinn',100)]:
  for p in geometry(name)[0]:items.append((name+'_'+p['name'],p['shape'].translate((0,offset,0)),COL[p['material']]))
 render(items,OUT/'images/Manny_Quinn_arm_comparison.png','MANNY (left) / QUINN (right) | 1:3 limb centres | elbow + wrist-flex populated',camera=(900,-1500,0))
 save(ROOT/'verification/revF_viewer_geometry.json',{'display_only':True,'manufacturing_released':False,'arms':{n:{'parts':len(v['parts']),'triangles':sum(len(p['triangles']) for p in v['parts'])} for n,v in data['arms'].items()},'joint_parts':len(data['joint'])})
 print('Rev F offline mechanical viewer and comparison rendered.',flush=True)
if __name__=='__main__':main()
