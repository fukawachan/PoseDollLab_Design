from full_packaging import *
from character_reference import reference_character
for name in ('manny','quinn'):
 c=reference_character(name);v=c['surfaces']['head']*1.5
 p=h.profile(name);T,axes=h.fk(p,{})
 N=axes['head.yaw']['origin']
 print(name,'N',N.tolist(),'head_bone',(c['points']['head']*1.5-N).tolist(),'bounds_from_N',(v.min(0)-N).tolist(),(v.max(0)-N).tolist(),flush=True)
