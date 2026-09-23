const fs=require('fs'),assert=require('assert'),crypto=require('crypto');
(async()=>{
 const tabs=await(await fetch('http://127.0.0.1:8877/json/list')).json();
 const tab=tabs.find(t=>t.url.includes('Human_Form_and_Shoulder_Review.html'));
 if(!tab)throw new Error('Review tab not found: '+JSON.stringify(tabs));
 const ws=new WebSocket(tab.webSocketDebuggerUrl),pending=new Map(),errors=[];let id=0;
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result);}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params);};
 await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 const send=(method,params={})=>new Promise((resolve,reject)=>{const i=++id;pending.set(i,{resolve,reject});ws.send(JSON.stringify({id:i,method,params}));});
 const ev=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw r.exceptionDetails;return r.result.value;};
 await send('Runtime.enable');await send('Page.enable');
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1080,deviceScaleFactor:1,mobile:false});
 await send('Page.reload',{ignoreCache:true});
 await ev('new Promise(r=>setTimeout(r,800))');
 const neutral=await ev('({state:poseDollShoulderReview.state(),metric:poseDollShoulderReview.metric()})');
 assert.equal(neutral.metric,'0.0 mm');assert.equal(neutral.state.character,'quinn');assert(neutral.state.triangles>100);
 await ev("document.querySelector('[data-pose=forward]').click()");
 const forward=await ev('poseDollShoulderReview.metric()');assert.equal(forward,'39.2 mm');
 await ev("document.querySelector('[data-pose=forward_up]').click()");
 const quinnCombined=await ev('poseDollShoulderReview.metric()');assert.equal(quinnCombined,'54.7 mm');
 fs.writeFileSync('Hardware/PoseDoll44/generated/revG/images/shoulder_review_desktop.png',Buffer.from((await send('Page.captureScreenshot',{format:'png'})).data,'base64'));
 await ev("document.querySelector('#character').value='manny';document.querySelector('#character').dispatchEvent(new Event('change'));document.querySelector('#side').click()");
 const mannyCombined=await ev('({state:poseDollShoulderReview.state(),metric:poseDollShoulderReview.metric()})');assert.equal(mannyCombined.metric,'63.7 mm');assert.equal(mannyCombined.state.az,Math.PI/2);
 await ev("document.querySelector('#anchors').click()");
 assert.equal(await ev('poseDollShoulderReview.state().anchors'),false);
 const controls=[];
 for(const model of ['manny','quinn']){
  await ev("document.querySelector('#character').value='"+model+"';document.querySelector('#character').dispatchEvent(new Event('change'))");
  for(const pose of ['neutral','forward','backward','shrug','down','forward_up','asymmetric']){
   await ev("document.querySelector('[data-pose="+pose+"]').click()");
   controls.push(await ev('({state:poseDollShoulderReview.state(),metric:poseDollShoulderReview.metric()})'));
  }
 }
 await send('Emulation.setDeviceMetricsOverride',{width:760,height:1050,deviceScaleFactor:1,mobile:false});
 await ev('new Promise(r=>requestAnimationFrame(()=>r()))');
 const responsive=await ev('({scroll:document.documentElement.scrollWidth,width:innerWidth,canvasWidth:document.querySelector("canvas").getBoundingClientRect().width})');
 assert(responsive.scroll<=responsive.width);
 const links=await ev('Array.from(document.querySelectorAll("a")).map(a=>a.href)');
 const linkResults=[];for(const url of links){const response=await fetch(url);assert.equal(response.status,200);await response.arrayBuffer();linkResults.push({url,status:response.status});}
 const report={neutral,forward,quinnCombined,mannyCombined,poseCases:controls.length,responsive,linkResults,errors,htmlSha256:crypto.createHash('sha256').update(fs.readFileSync('Hardware/PoseDoll44/generated/revG/Human_Form_and_Shoulder_Review.html')).digest('hex')};
 fs.writeFileSync('Hardware/PoseDoll44/verification/revG_browser_check.json',JSON.stringify(report,null,2));
 assert.equal(errors.length,0);console.log(JSON.stringify(report));ws.close();
})().catch(e=>{console.error(e);process.exit(1)});
