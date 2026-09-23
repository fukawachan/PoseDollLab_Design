from special_travel_stops import *
out={}
for name in ('manny','quinn'):
 A,meta=compact.build(name);ds=descriptors(A);results=[]
 # Add every other stop before testing each target: neighbouring guard geometry matters.
 bare={q['name']:dict(q) for q in A.parts}
 for d in ds:apply_one(A,d,PHASES[d['axis']])
 for axis in ('head.yaw','upperarm_l.twist','upperarm_r.twist'):
  d=next(q for q in ds if q['axis']==axis);original={n:bare[n] for n in (d['fixed'],d['rotor'])};trials=[];selected=None
  if axis=='head.yaw':cases=[{'head.yaw':y,'head.pitch':p,'head.roll':r} for y in (-75,0,75) for p in (-45,0,55) for r in (-35,0,35)]
  else:
   side=axis.split('_')[1].split('.')[0];limits={q['id']:np.degrees(q['limits_rad']) for q in A.profile['axes']};aa=limits['upperarm_'+side+'.abduct'];tt=limits[axis];ff=limits['upperarm_'+side+'.flex'];cases=[{f'upperarm_{side}.abduct':a,axis:t,f'upperarm_{side}.flex':f} for a in (aa[0],0,90,aa[1]) for t in (tt[0],0,tt[1]) for f in (ff[0],0,90,ff[1])]
  for phase in (0,270,90,180,45,135,225,315):
   for n,old in original.items():next(q for q in A.parts if q['name']==n).update(old)
   try:
    g,_=apply_one(A,d,phase);endpoint(A,g);bad=[]
    for pose in cases:
     hits=fast_contacts(A.scene(pose),A.thread_pairs,{d['fixed'],d['rotor']},True)
     hits=[q for q in classify_all(hits,A.parts) if q['classification']=='structural']
     if axis=='head.yaw':hits=[q for q in hits if q['region_a']=='head' or q['region_b']=='head']
     if hits:bad.append(dict(pose=pose,hits=hits));break
    trials.append(dict(phase=phase,bad=bad));print(name,axis,phase,'bad',bad[:1],flush=True)
    if not bad:selected=phase;break
   except Exception as e:trials.append(dict(phase=phase,error=str(e)));print(name,axis,phase,str(e),flush=True)
  results.append(dict(axis=axis,selected=selected,trials=trials));out[name]=results;h.save(ROOT/'verification/revM_combined_T4_phases.json',out)
