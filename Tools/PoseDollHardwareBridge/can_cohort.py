"""Offline reference for six-node synchronized acquisition; no CAN hardware I/O.
Firmware must flush old transmit queues before acknowledging a new 64-bit epoch.
Each cohort starts empty. Incomplete, duplicated, late or rebooted node results
remain missing; data from an older cohort never fill a newer one.
"""
from pd41_protocol import CFG,NODE_INDICES,FIXED,MISSING,word_state

class Cohort:
 def __init__(self,epoch,boots):
  if not 0<epoch<2**64 or set(boots)!=set(NODE_INDICES) or any(not 0<b<2**64 for b in boots.values()):raise ValueError('epoch/node boot identities')
  self.epoch=epoch;self.boots=dict(boots);self.blocked=set(boots);self.seq=0;self.active=False;self.errors=[]
 def boot(self,node,boot):
  if node not in self.boots or not 0<boot<2**64:raise ValueError('node/boot identity')
  if self.boots[node]!=boot:
   self.boots[node]=boot;self.blocked.add(node)
   if self.active:self.bad.add(node)
   return False
  return True
 def acknowledge_epoch(self,node,epoch,boot):
  if epoch!=self.epoch or self.boots.get(node)!=boot:return False
  self.blocked.discard(node);return True
 def begin(self,seq,now_us):
  if self.active:raise ValueError('finish previous cohort before next sync')
  if not self.seq<seq<2**32:raise ValueError('nonmonotonic cohort; new epoch required on wrap')
  self.seq=seq;self.start=now_us;self.deadline=now_us+CFG['can']['cohort_deadline_us'];self.active=True
  self.groups={n:{} for n in NODE_INDICES};self.ends={};self.bad=set(self.blocked)
 def _accept(self,node,seq,now):
  return self.active and node in NODE_INDICES and seq==self.seq and self.start<=now<self.deadline and node not in self.blocked and node not in self.bad
 def pair(self,node,seq,group,words,now_us):
  if not self._accept(node,seq,now_us):return False
  groups=(len(NODE_INDICES[node])+1)//2
  if not 0<=group<groups or len(words)!=2 or group in self.groups[node] or node in self.ends:
   self.bad.add(node);self.errors.append((seq,node,'duplicate_or_invalid_group'));return False
  try:
   for j,w in enumerate(words):
    port=2*group+j
    if port==len(NODE_INDICES[node]):
     if w!=FIXED:raise ValueError('padding sentinel')
    else:
     status,_,_=word_state(w)
     if status=='missing':raise ValueError('node must report read failure explicitly')
  except ValueError:self.bad.add(node);self.errors.append((seq,node,'invalid_word'));return False
  self.groups[node][group]=tuple(words);return True
 def end(self,node,seq,delay_us,span_us,now_us):
  if not self._accept(node,seq,now_us):return False
  expected=set(range((len(NODE_INDICES[node])+1)//2))
  if node in self.ends or set(self.groups[node])!=expected or delay_us<0 or span_us<=0 or delay_us+span_us>CFG['can']['maximum_node_sample_window_us'] or delay_us+span_us>now_us-self.start:
   self.bad.add(node);self.errors.append((seq,node,'incomplete_or_invalid_window'));return False
  # The node clock is not synchronized to the gateway clock. Include CAN delay
  # rather than presenting relative node timings as a precise shared timestamp.
  self.ends[node]=(0,now_us-self.start);return True
 def finish(self,now_us):
  if not self.active:raise ValueError('no active cohort')
  if now_us<self.deadline and len(self.ends)<6:raise ValueError('cohort deadline has not arrived')
  words=[FIXED]*3+[MISSING]*41;timings=[[0,0] for _ in range(6)];presence=0;window=0
  for node,inds in NODE_INDICES.items():
   if node not in self.ends or node in self.bad or node in self.blocked:continue
   vals=[v for group in sorted(self.groups[node]) for v in self.groups[node][group]][:len(inds)]
   for i,w in zip(inds,vals):words[i]=w
   timings[node-1]=list(self.ends[node]);presence |= 1<<(node-1);window=max(window,sum(self.ends[node]))
  self.active=False
  return dict(words=words,timings=timings,presence=presence,window_us=window,sequence=self.seq)
