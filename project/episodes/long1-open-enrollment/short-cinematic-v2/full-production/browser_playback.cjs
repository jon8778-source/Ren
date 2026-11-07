// Full-duration local Chromium playback; records actual presented frames/errors.
// This verifies browser decoding/playback, not ear-based listening or Android.
const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const output = path.join(root, 'deliverables', 'full-review');
fs.mkdirSync(output, { recursive: true });
(async () => {
 const browser = await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,
  args:['--no-sandbox','--autoplay-policy=no-user-gesture-required']});
 const page = await browser.newPage({viewport:{width:420,height:800}});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 const media=path.join(root,'deliverables','Ren_Health_Short_v2_Final.mp4');
 const mediaSha=crypto.createHash('sha256').update(fs.readFileSync(media)).digest('hex');
 // Managed Chrome blocks file:// navigation. Serve only this local review
 // document/movie over loopback HTTP; preserve all browser/network policies.
 const server=http.createServer((req,res)=>{
  if(req.url==='/video.mp4'){
   const size=fs.statSync(media).size;
   const match=/bytes=(\d+)-(\d*)/.exec(req.headers.range||'');
   const start=match?Number(match[1]):0,end=match&&match[2]?Math.min(Number(match[2]),size-1):size-1;
   res.writeHead(match?206:200,{'Content-Type':'video/mp4','Accept-Ranges':'bytes',
    'Content-Length':end-start+1,...(match?{'Content-Range':`bytes ${start}-${end}/${size}`}:{})});
   fs.createReadStream(media,{start,end}).pipe(res);
  }else{
   res.writeHead(200,{'Content-Type':'text/html'});
   res.end('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#eee}video{display:block;width:360px;height:640px;object-fit:contain}</style><video controls playsinline src="/video.mp4"></video>');
  }
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 await page.goto('http://127.0.0.1:'+server.address().port+'/');
 await page.waitForFunction(()=>document.querySelector('video').readyState>=2,{timeout:30000});
 await page.evaluate(async()=>{
  const v=document.querySelector('video');window.framesSeen=[];window.stalls=[];
  v.addEventListener('waiting',()=>window.stalls.push(v.currentTime));
  const cb=(_,m)=>{window.framesSeen.push({mediaTime:m.mediaTime,presented:m.presentedFrames});v.requestVideoFrameCallback(cb)};
  v.requestVideoFrameCallback(cb);v.muted=true;await v.play();
 });
 let n=0;
 while (!await page.evaluate(()=>document.querySelector('video').ended)) {
  await page.screenshot({path:path.join(output,`browser-${String(n++).padStart(3,'0')}.png`)});
  await page.waitForTimeout(2000);
  if(n>40)throw new Error('Playback failed to finish within expected interval');
 }
 const report=await page.evaluate(()=>{
  const v=document.querySelector('video');
  return {ended:v.ended,duration:v.duration,currentTime:v.currentTime,videoWidth:v.videoWidth,
   videoHeight:v.videoHeight,playbackRate:v.playbackRate,mediaError:v.error,
   quality:{totalVideoFrames:v.getVideoPlaybackQuality().totalVideoFrames,
    droppedVideoFrames:v.getVideoPlaybackQuality().droppedVideoFrames},stalls:window.stalls,frames:window.framesSeen,
   audioListeningPerformed:false,physicalAndroidTest:false};
 });
 report.pageErrors=errors;report.browser='Chromium, headless local full-duration playback';
 report.videoSha256=mediaSha;
 report.videoUnchangedDuringPlayback=crypto.createHash('sha256').update(fs.readFileSync(media)).digest('hex')===mediaSha;
 fs.writeFileSync(path.join(__dirname,'browser-playback.json'),JSON.stringify(report,null,2)+'\n');
 await browser.close();server.close();
 if(!report.ended || report.mediaError || errors.length)throw new Error('Playback errors');
 console.log('Whole video played to ended; '+report.frames.length+' presented-frame callbacks recorded.');
})().catch(e=>{console.error(e);process.exitCode=1});
