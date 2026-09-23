from shoulder_clutch import *
root=h.ROOT
r={}
for label,tip in [('flex',-24),('abduct',-16)]:
 ps=cartridge(tip);hits=exact_hits(ps)
 sweeps=[]
 for angle in range(0,360,15):
  rows=[dict(p,shape=p['shape'].rotate((0,0,0),(0,0,1),angle)) if p['owner']=='rotor' else p for p in ps]
  cross=exact_hits(rows,False);sweeps.append({'angle_deg':angle,'hits':cross})
 bad=[q for q in hits if not q['intentional_thread']]
 print(json.dumps({'module':label,'parts':len(ps),'unexpected':bad,'motion_hits':sum(len(q['hits']) for q in sweeps)}),flush=True)
 r[label]={'parts':len(ps),'assembly_contacts':hits,'unexpected_assembly_contacts':bad,'rotation_checks':sweeps}
h.save(root/'verification/revI_clutch_component_check.json',r)
