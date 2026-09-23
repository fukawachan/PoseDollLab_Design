const {chromium}=require('C:/Users/Ding/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve('Hardware/PoseDoll44'),out=path.join(root,'verification/browser_revN');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1440,height:1050},deviceScaleFactor:1}),errors=[],checks=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.goto('http://127.0.0.1:8874/generated/revN/RevN_Chest_Review.html');
 await page.waitForFunction(()=>window.poseDollFullBody?.state().rendered>0,{},{timeout:90000});
 for(const name of ['manny','quinn']){
  if(name==='quinn'){await page.click('[data-model="quinn"]');await page.waitForFunction(()=>window.poseDollFullBody.state().model==='quinn'&&document.querySelector('#loading').style.display==='none');}
  await page.selectOption('#pose','arms_forward');await page.click('#front');await page.waitForTimeout(900);
  await page.screenshot({path:path.join(out,name+'_front.png'),fullPage:true});
  const front=await page.evaluate(()=>({state:window.poseDollFullBody.state(),status:document.querySelector('#status').textContent}));
  if(front.state.parts!==1994||!front.state.reportMatches)throw Error('Wrong model or stale audit');checks.push(front);
  await page.selectOption('#pose','hands_behind_lower_back');await page.click('#back');await page.waitForTimeout(900);
  await page.screenshot({path:path.join(out,name+'_behind.png'),fullPage:true});
  checks.push(await page.evaluate(()=>({state:window.poseDollFullBody.state(),status:document.querySelector('#status').textContent,class:document.querySelector('#status').className})));
  for(const id of ['cad','bom']){const href=await page.locator('#'+id).getAttribute('href');const response=await page.request.head(new URL(href,page.url()).href);if(!response.ok())throw Error('Missing artifact '+href);}
 }
 await page.setViewportSize({width:390,height:844});await page.waitForTimeout(800);
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);if(overflow)throw Error('Horizontal overflow');
 await page.screenshot({path:path.join(out,'mobile.png'),fullPage:true});await browser.close();if(errors.length)throw Error(errors.join('\n'));
 const inputs=['generated/revN/RevN_Chest_Review.html','generated/revN/manny/viewer.json','generated/revN/quinn/viewer.json','verification/revN_chest_audit.json'];
 fs.writeFileSync(path.join(out,'checks.json'),JSON.stringify({errors,checks,overflow,source_sha256:Object.fromEntries(inputs.map(f=>[f,hash(path.join(root,f))]))},null,2));console.log(JSON.stringify({errors,checks,overflow}));
})().catch(e=>{console.error(e);process.exit(1)});
