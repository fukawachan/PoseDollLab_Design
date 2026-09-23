"""Deterministic local plane fanouts after offline routing; native DRC is mandatory."""
from pathlib import Path
import pcbnew as p,json,math,heapq
D=Path(__file__).resolve().parents[1]/'electronics/regional_revM'
b=p.LoadBoard(str(D/'routed_work.kicad_pcb'))
# One front signal crosses the only conventional through-via escape of U2 VOS.
# Rip up that local segment for a later offline reroute; never leave it disconnected.
removed=[]
for t in list(b.GetTracks()):
 if t.GetNetname()=='/CS5_MCU' and t.GetLayer()==p.F_Cu:
  sh=p.SHAPE_CIRCLE(p.VECTOR2I(p.FromMM(88.65),p.FromMM(104.25)),p.FromMM(.25))
  if t.GetEffectiveShape(p.F_Cu).Collide(sh,p.FromMM(.151)):
   removed.append(dict(net=t.GetNetname(),uuid=t.m_Uuid.AsString()));b.Remove(t)
mm=p.FromMM
vec=lambda xy:p.VECTOR2I(mm(xy[0]),mm(xy[1]))
xy=lambda v:(p.ToMM(v.x),p.ToMM(v.y))
LAYERS=(p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu)
items={q.m_Uuid.AsString():q for q in b.GetTracks()}
for f in b.GetFootprints():
 for q in f.Pads():items[q.m_Uuid.AsString()]=q
obstacles={l:{} for l in LAYERS}
def cells(a,z,margin):
 for i in range(math.floor(min(a[0],z[0])-margin),math.floor(max(a[0],z[0])+margin)+1):
  for j in range(math.floor(min(a[1],z[1])-margin),math.floor(max(a[1],z[1])+margin)+1):yield (i,j)
def index(q):
 for l in LAYERS:
  if q.IsOnLayer(l):
   sh=q.GetEffectiveShape(l);bb=q.GetBoundingBox();a=(p.ToMM(bb.GetLeft()),p.ToMM(bb.GetTop()));z=(p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom()))
   for key in cells(a,z,.2):obstacles[l].setdefault(key,[]).append((q.GetNetCode(),sh))
for q in items.values():index(q)
def clear(a,z,width,net,l):
 sh=p.SHAPE_SEGMENT(vec(a),vec(z),mm(width))
 return not any(n!=net and s.Collide(sh,mm(.151)) for key in cells(a,z,width/2+.16) for n,s in obstacles[l].get(key,[]))
def via_clear(v,net):
 if not (80.75<v[0]<119.25 and 80.75<v[1]<165.25):return False
 sh=p.SHAPE_CIRCLE(vec(v),mm(.25))
 return not any(n!=net and s.Collide(sh,mm(.151)) for l in LAYERS for key in cells(v,v,.41) for n,s in obstacles[l].get(key,[]))
def addtrack(a,z,net,layer,width=.2):
 if a==z:return
 t=p.PCB_TRACK(b);t.SetStart(vec(a));t.SetEnd(vec(z));t.SetWidth(mm(width));t.SetLayer(layer);t.SetNetCode(net);b.Add(t);index(t)
def addvia(v,net):
 if any(isinstance(q,p.PCB_VIA) and q.GetNetCode()==net and q.GetPosition()==vec(v) for q in b.GetTracks()):return
 t=p.PCB_VIA(b);t.SetPosition(vec(v));t.SetWidth(mm(.5));t.SetDrill(mm(.25));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNetCode(net);b.Add(t);index(t)
report=[dict(ripped_segments=removed)];done=set()
drc=json.loads((D/'routed_drc_work.json').read_text(encoding='utf8'))
for issue in drc['unconnected_items']:
 for item in issue['items']:
  q=items.get(item['uuid']);
  if q is None:continue
  net=q.GetNetCode()
  if q.GetNetname() not in ('/GND','/+3V3') or q.m_Uuid.AsString() in done:continue
  done.add(q.m_Uuid.AsString());start=(item['pos']['x'],item['pos']['y']);layer=p.F_Cu if q.IsOnLayer(p.F_Cu) else p.B_Cu;fanwidth=.15 if isinstance(q,p.PAD) and q.GetParentFootprint().GetReference()=='U2' else .2
  if layer not in (p.F_Cu,p.B_Cu):continue
  offsets=sorted([(i*.25,j*.25) for i in range(-20,21) for j in range(-20,21)],key=lambda v:v[0]*v[0]+v[1]*v[1]);found=None
  for dx,dy in offsets:
   v=(start[0]+dx,start[1]+dy)
   if via_clear(v,net) and clear(start,v,fanwidth,net,layer):found=v;break
  path=[start]
  if found is None:
   # Local A* to a free through-via site; no board geometry is moved or waived.
   step=.05;queue=[(0.,0.,(0,0))];dist={(0,0):0.};prev={};end=None
   while queue:
    _,cost,u=heapq.heappop(queue)
    if cost>dist[u]+1e-9:continue
    v=(start[0]+u[0]*step,start[1]+u[1]*step)
    if via_clear(v,net):end=u;found=v;break
    for di,dj in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)):
     w=(u[0]+di,u[1]+dj)
     if max(abs(w[0]),abs(w[1]))>160:continue
     nc=cost+math.hypot(di,dj)*step
     if nc>=dist.get(w,1e9):continue
     vv=(start[0]+w[0]*step,start[1]+w[1]*step)
     if not clear(v,vv,fanwidth,net,layer):continue
     dist[w]=nc;prev[w]=u;heapq.heappush(queue,(nc,nc,w))
   if end is None:
    # Bounded local rip-up: protect all pads and choose the fewest crossed tracks.
    candidates=[];allpads=[t for f in b.GetFootprints() for t in f.Pads()]
    for dx,dy in offsets:
     if not .45<math.hypot(dx,dy)<3.01:continue
     vv=(start[0]+dx,start[1]+dy)
     if not (80.75<vv[0]<119.25 and 80.75<vv[1]<165.25):continue
     vc=p.SHAPE_CIRCLE(vec(vv),mm(.25));line=p.SHAPE_SEGMENT(vec(start),vec(vv),mm(fanwidth))
     if any(t.GetNetCode()!=net and t.IsOnLayer(layer) and t.GetEffectiveShape(layer).Collide(line,mm(.151)) for t in allpads):continue
     if any(any(t.IsOnLayer(l) and t.GetEffectiveShape(l).Collide(vc,mm(.151)) for l in LAYERS) for t in allpads):continue
     rip=[]
     for t in b.GetTracks():
      if t.GetNetCode()==net:continue
      if (t.IsOnLayer(layer) and t.GetEffectiveShape(layer).Collide(line,mm(.151))) or any(t.IsOnLayer(l) and t.GetEffectiveShape(l).Collide(vc,mm(.151)) for l in LAYERS):rip.append(t)
     candidates.append((len(rip)*10+math.hypot(dx,dy),vv,rip))
    if not candidates:raise RuntimeError(('no conventional fanout',item))
    _,found,rip=min(candidates,key=lambda q:q[0]);end=(0,0);path=[start,found]
    for t in rip:
     removed.append(dict(net=t.GetNetname(),uuid=t.m_Uuid.AsString()));items.pop(t.m_Uuid.AsString(),None);b.Remove(t)
    obstacles={l:{} for l in LAYERS}
    for t in list(b.GetTracks())+allpads:index(t)
   pts=[]
   while end!=(0,0):pts.append((start[0]+end[0]*step,start[1]+end[1]*step));end=prev[end]
   path+=list(reversed(pts))
  else:path.append(found)
  for aa,zz in zip(path,path[1:]):addtrack(aa,zz,net,layer,fanwidth)
  addvia(found,net);report.append(dict(net=q.GetNetname(),from_mm=start,via_mm=found));print(report[-1],flush=True)
fps={f.GetReference():f for f in b.GetFootprints()}
pad=lambda ref,num:next(x for x in fps[ref].Pads() if x.GetNumber()==str(num))
a=pad('U2',7);z=pad('L1',1);aa=xy(a.GetPosition());zz=xy(z.GetPosition());net=a.GetNetCode()
for width in (.6,.5,.4,.3,.2):
 if clear(aa,zz,width,net,p.B_Cu):addtrack(aa,zz,net,p.B_Cu,width);report.append(dict(net='/SW_BUCK',width_mm=width,from_mm=aa,to_mm=zz));break
else:print('SW_BUCK still requires route',flush=True)
# Remove redundant signal vias flagged by native connectivity. No trace removed.
for issue in drc['violations']:
 if issue['type']=='via_dangling':
  q=items.get(issue['items'][0]['uuid']);
  if q is not None:b.Remove(q)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'connected_work.kicad_pcb'),b)
(D/'connected_work.kicad_pro').write_bytes((D/'placement.kicad_pro').read_bytes())
assert p.ExportSpecctraDSN(b,str(D/'repair_input.dsn'))
(D/'plane_fanout_work.json').write_text(json.dumps(report,indent=2),encoding='utf8')
