"""Local UE MCP transport for hardware read-only extraction scripts."""
import json,urllib.request
class UEMCP:
 def __init__(self):
  self.headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'};self.count=0
  self.rpc('initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'posedoll-hardware-reference','version':'1.0'}})
 def rpc(self,method,params):
  self.count+=1
  req=urllib.request.Request('http://127.0.0.1:8000/mcp',data=json.dumps({'jsonrpc':'2.0','id':self.count,'method':method,'params':params}).encode(),headers=self.headers)
  with urllib.request.urlopen(req,timeout=55) as r:
   self.headers.update({k:v for k,v in r.headers.items() if k.lower()=='mcp-session-id'})
   data=json.loads(r.read().decode())
  if 'error' in data:raise RuntimeError(data['error'])
  return data['result']
 def tool(self,name,args):return self.rpc('tools/call',{'name':name,'arguments':args})
 def describe(self,name):return json.loads(self.tool('describe_toolset',{'toolset_name':name})['content'][0]['text'])
 def call(self,toolset,name,args):return self.tool('call_tool',{'toolset_name':toolset,'tool_name':name,'arguments':args})
