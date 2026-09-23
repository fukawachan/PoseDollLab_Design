"""Small deterministic two-layer grid router for this sensor prototype.
All output still passes through KiCad DRC; this is not a signoff authority."""
import math,heapq,collections
import pcbnew as pcb
STEP=.1
LO,HI=1007,1313
def g(v):return round(pcb.ToMM(v)/STEP)
def pos(x,y):return pcb.VECTOR2I(pcb.FromMM(x*STEP),pcb.FromMM(y*STEP))
def route(b):
    occupancy=[collections.defaultdict(set),collections.defaultdict(set)]
    padgroups=collections.defaultdict(list)
    via_positions=[]
    def fill(layer,x0,y0,x1,y1,net):
        for x in range(math.floor(x0),math.ceil(x1)+1):
            for y in range(math.floor(y0),math.ceil(y1)+1):occupancy[layer][(x,y)].add(net)
    for f in b.GetFootprints():
        for p in f.Pads():
            pnet=p.GetNetCode();center=p.GetPosition(); x=pcb.ToMM(center.x)/STEP;y=pcb.ToMM(center.y)/STEP
            size=p.GetSize();sx=pcb.ToMM(size.x)/STEP;sy=pcb.ToMM(size.y)/STEP
            if p.GetAttribute()==pcb.PAD_ATTRIB_NPTH:
                for l in (0,1):fill(l,x-sx/2-4,y-sy/2-4,x+sx/2+4,y+sy/2+4,-1)
            else:
                for l,L in ((0,pcb.F_Cu),(1,pcb.B_Cu)):
                    if p.IsOnLayer(L):fill(l,x-sx/2-3,y-sy/2-3,x+sx/2+3,y+sy/2+3,pnet or -1)
                if pnet:padgroups[pnet].append(p)
    def free(state,net):
        x,y,l=state
        return LO<=x<=HI and LO<=y<=HI and not (occupancy[l].get((x,y),set())-{net})
    def viaok(x,y,net):
        if any(0<(x-a)**2+(y-z)**2<64 for a,z in via_positions):return False
        return all(free((x+dx,y+dy,l),net) for dx in range(-3,4) for dy in range(-3,4) if dx*dx+dy*dy<=10 for l in (0,1))
    def astar(start,goal,net):
        pq=[(0,0,start)];cost={start:0};prev={};iters=0
        while pq:
            _,c,u=heapq.heappop(pq)
            if c!=cost[u]:continue
            if u==goal:
                path=[u]
                while u!=start:u=prev[u];path.append(u)
                return path[::-1]
            iters+=1
            if iters>500000:raise RuntimeError("router search budget")
            x,y,l=u
            neigh=[((x+dx,y+dy,l),10) for dx,dy in ((1,0),(-1,0),(0,1),(0,-1))]
            if viaok(x,y,net):neigh.append(((x,y,1-l),100))
            for v,w in neigh:
                if not free(v,net):continue
                n=c+w
                if n<cost.get(v,10**20):
                    cost[v]=n;prev[v]=u
                    h=(abs(v[0]-goal[0])+abs(v[1]-goal[1]))*10+(100 if v[2]!=goal[2] else 0)
                    heapq.heappush(pq,(n+h,n,v))
        raise RuntimeError("No route for net "+str((net,start,goal,occupancy[start[2]].get(start[:2]),occupancy[goal[2]].get(goal[:2]))))
    def track(a,z,net,layer):
        if a==z:return
        t=pcb.PCB_TRACK(b);t.SetStart(a);t.SetEnd(z);t.SetLayer(pcb.F_Cu if layer==0 else pcb.B_Cu);t.SetWidth(pcb.FromMM(.2));t.SetNetCode(net);b.Add(t)
    logs=[]
    order=[2,7,6,5,4,1,3]
    for net in order:
        pads=padgroups[net];connected=[pads.pop(0)]
        while pads:
            a,z=min(((a,z) for a in connected for z in pads),key=lambda pair:(pair[0].GetPosition()-pair[1].GetPosition()).SquaredEuclideanNorm())
            s=(g(a.GetPosition().x),g(a.GetPosition().y),0);t=(g(z.GetPosition().x),g(z.GetPosition().y),0)
            path=astar(s,t,net)
            track(a.GetPosition(),pos(*s[:2]),net,0);track(pos(*t[:2]),z.GetPosition(),net,0)
            for (x,y,l),(xx,yy,ll) in zip(path,path[1:]):
                if l!=ll:
                    if (x,y) in via_positions:continue
                    via_positions.append((x,y))
                    v=pcb.PCB_VIA(b);v.SetPosition(pos(x,y));v.SetWidth(pcb.FromMM(.6));v.SetDrill(pcb.FromMM(.3));v.SetViaType(pcb.VIATYPE_THROUGH);v.SetLayerPair(pcb.F_Cu,pcb.B_Cu);v.SetNetCode(net);b.Add(v)
                    for layer in (0,1):fill(layer,x-6,y-6,x+6,y+6,net)
                else:
                    track(pos(x,y),pos(xx,yy),net,l)
                    fill(l,min(x,xx)-3,min(y,yy)-3,max(x,xx)+3,max(y,yy)+3,net)
            connected.append(z);pads.remove(z);logs.append({"net":net,"steps":len(path)})
    return logs
