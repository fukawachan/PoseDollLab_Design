const fs=require('fs'),assert=require('assert'),crypto=require('crypto');
const REV=process.argv[2]||'I',PORT=Number(process.argv[3]||8878);
assert(['H','I','J','K','L'].includes(REV));
const root='Hardware/PoseDoll44',file='Rev'+REV+'_Shoulder_Review.html',folder=root+'/generated/rev'+REV;
(async()=>{
 const tabs=await(await fetch('http://127.0.0.1:'+PORT+'/json/list')).json(),tab=tabs.find(t=>t.url.includes(file));assert(tab);
 const ws=new WebSocket(tab.webSocketDebuggerUrl),pending=new Map(),errors=[];let id=0;
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result);}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params);};
 await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 const send=(method,params={})=>new Promise((resolve,reject)=>{const i=++id;pending.set(i,{resolve,reject});ws.send(JSON.stringify({id:i,method,params}));});
 const ev=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw r.exceptionDetails;return r.result.value;};
 await send('Runtime.enable');await send('Page.enable');await send('Emulation.setDeviceMetricsOverride',{width:1460,height:1080,deviceScaleFactor:1,mobile:false});await send('Page.reload',{ignoreCache:true});
 await ev('new Promise(r=>setTimeout(r,700))');
 const baseline=await ev('({state:poseDollShoulderAssembly.state(),counts:poseDollShoulderAssembly.counts()})');
 assert.equal(baseline.state.model,'quinn');assert.equal(baseline.state.hits,0);assert(baseline.state.triangles>1000);
 fs.writeFileSync(folder+'/review_desktop.png',Buffer.from((await send('Page.captureScreenshot',{format:'png'})).data,'base64'));
 const checked=[];
 for(const model of ['manny','quinn']){
  const source=JSON.parse(fs.readFileSync(root+'/verification/rev'+REV+'_'+model+'.json','utf8'));
  assert.equal(baseline.counts[model].parts,source.parts.length);assert.equal(baseline.counts[model].cases,source.motion_checks.length);
  await ev("document.querySelector('#model').value='"+model+"';document.querySelector('#model').dispatchEvent(new Event('change'))");
  for(const c of source.motion_checks){
   await ev("document.querySelector('#pose').value='"+c.pose+"';document.querySelector('#pose').dispatchEvent(new Event('change'))");
   const state=await ev('poseDollShoulderAssembly.state()');assert.equal(state.hits,c.hits.length);assert.equal(await ev("document.querySelector('#status').classList.contains('fail')"),c.structural_hits>0);assert.equal(state.structuralHits,c.structural_hits);assert.equal(await ev("document.querySelector('#status').classList.contains('pose')"),!c.structural_hits&&c.pose_restriction_hits>0);checked.push({model,pose:c.pose,hits:state.hits,structural:state.structuralHits});
  }
 }
 await ev("document.querySelector('[data-pose=crossed_clearance_candidate]').click()");
 fs.writeFileSync(folder+'/review_crossed.png',Buffer.from((await send('Page.captureScreenshot',{format:'png'})).data,'base64'));
 await ev("document.querySelector('#pose').value='arms_crossed';document.querySelector('#pose').dispatchEvent(new Event('change'))");
 fs.writeFileSync(folder+'/review_pose_restriction.png',Buffer.from((await send('Page.captureScreenshot',{format:'png'})).data,'base64'));
 if(['I','J','K','L'].includes(REV)){
  await ev("document.querySelector('#pose').value='neutral';document.querySelector('#pose').dispatchEvent(new Event('change'));document.querySelector('#shoulder').click()");
  assert.equal(await ev('poseDollShoulderAssembly.state().shoulderOnly'),true);
  fs.writeFileSync(folder+'/review_shoulder.png',Buffer.from((await send('Page.captureScreenshot',{format:'png'})).data,'base64'));
  await ev("document.querySelector('#shoulder').click()");
 }
 if(['J','K','L'].includes(REV)){
  await ev("document.querySelector('#encoder').click()");
  assert.equal(await ev('poseDollShoulderAssembly.state().encoderOnly'),true);
  assert((await ev('poseDollShoulderAssembly.state().triangles'))>1000);
  fs.writeFileSync(folder+'/review_sensor.png',Buffer.from((await send('Page.captureScreenshot',{format:'png'})).data,'base64'));
  await ev("document.querySelector('#encoder').click()");
 }
 const withShells=await ev('poseDollShoulderAssembly.state().triangles');await ev("document.querySelector('#shells').click()");
 const withoutShells=await ev('poseDollShoulderAssembly.state().triangles');assert(withoutShells<withShells);
 await ev("document.querySelector('#reserved').click()");const withReserved=await ev('poseDollShoulderAssembly.state().triangles');assert(withReserved>withoutShells);
 await ev("document.querySelector('#side').click()");assert.equal(await ev('poseDollShoulderAssembly.state().az'),Math.PI/2);
 const links=await ev('Array.from(document.querySelectorAll("a")).map(a=>a.href)');for(const url of links){const r=await fetch(url);assert.equal(r.status,200);await r.arrayBuffer();}
 await send('Emulation.setDeviceMetricsOverride',{width:760,height:1050,deviceScaleFactor:1,mobile:false});await ev('new Promise(r=>requestAnimationFrame(r))');
 const responsive=await ev('({scroll:document.documentElement.scrollWidth,width:innerWidth})');assert(responsive.scroll<=responsive.width);assert.equal(errors.length,0);
 const report={baseline,checked_cases:checked.length,collision_free:checked.filter(x=>!x.hits).length,no_local_structural_conflict:checked.filter(x=>!x.structural).length,withShells,withoutShells,withReserved,responsive,errors,links,htmlSha256:crypto.createHash('sha256').update(fs.readFileSync(folder+'/'+file)).digest('hex')};
 fs.writeFileSync(root+'/verification/rev'+REV+'_browser_check.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));ws.close();
})().catch(e=>{console.error(e);process.exit(1)});
