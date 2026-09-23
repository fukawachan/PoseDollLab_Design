"""Bounded packaging experiment for Rev L; no accepted design output."""
from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'revK'))
import compact_twist as k
from verify_k import poses_all
import numpy as np
h=k.h;cq=k.cq;R=k.R

def overlap(a,b,aa=None,bb=None):
    aa=aa or a.BoundingBox();bb=bb or b.BoundingBox()
    if not all(min(getattr(aa,x+'max'),getattr(bb,x+'max'))-max(getattr(aa,x+'min'),getattr(bb,x+'min'))>1e-4 for x in 'xyz'):return 0
    return a.intersect(b).Volume()

def main():
    rows=[]
    for name in ('quinn','manny'):
        p,parts,meta=k.build(name);T0,A0=h.fk(p,{})
        scenes={label:h.scene(parts,p,q) for label,q in poses_all().items()}
        for items,_,_ in scenes.values():
            for item in items:item['bbox']=item['shape'].BoundingBox()
        for datum in (61.771,62.6):
            for rotation in (0,90):
                hits=[]
                for side,sy in [('l',1),('r',-1)]:
                    S=A0[f'upperarm_{side}.flex']['origin'];owner=f'clavicle_{side}'
                    loc=k.previous.frame_transform((0,-sy,0),(1,0,0),S)
                    probes=[dict(q,local=q['shape'].rotate((0,0,0),(0,0,1),rotation).moved(loc).translate(tuple(-T0[owner][:3,3]))) for q in k.head(datum)]
                    for label,(items,T,A) in scenes.items():
                        for q in probes:
                            sh=h.move(q['local'],T[owner]);bb=sh.BoundingBox()
                            for item in items:
                                if item['role']=='reservation':continue
                                v=overlap(sh,item['shape'],bb,item['bbox'])
                                if v>.02:hits.append(dict(side=side,pose=label,probe=q['name'],part=item['name'],volume_mm3=round(v,4)))
                rows.append(dict(character=name,datum=datum,rotation=rotation,hits=hits))
                print(json.dumps(dict(character=name,datum=datum,rotation=rotation,hit_count=len(hits),first=hits[:4])),flush=True)
    h.save(R/'verification/revL_head_probe.json',dict(scope='PCB/head/FPC stub only; no magnet carrier or mounting structure',candidates=rows))
if __name__=='__main__':main()
