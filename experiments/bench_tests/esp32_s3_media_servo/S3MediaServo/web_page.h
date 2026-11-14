#pragma once
#include <Arduino.h>
const char PHONE_PAGE[] PROGMEM = R"CECEHTML(<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cece camera and microphone</title>
<style>
body{font:17px system-ui;background:#111b29;color:#f5f7fa;margin:0;padding:20px;max-width:720px;margin:auto}h1{margin-bottom:6px}p{line-height:1.5}.panel{padding:18px;background:#1c2a3d;border-radius:16px;margin:18px 0}img{width:100%;min-height:180px;object-fit:contain;background:#080e16;border-radius:12px}button,input{font:inherit;border-radius:10px;padding:12px;border:1px solid #526880}button{background:#75e2ce;color:#122022;font-weight:700;margin:6px 8px 6px 0;cursor:pointer}button:disabled{opacity:.45}input{box-sizing:border-box;width:100%;background:#101b29;color:white;margin:6px 0 14px}label{display:block}small,.muted{color:#b7c8dc}a{color:#75e2ce}meter{width:100%}summary{cursor:pointer;font-weight:700}.error{color:#ffb9b9}#message{min-height:48px}form button{width:100%}
</style>
<h1>Cece</h1><p class="muted">Live camera and robot microphone</p>
<div class="panel"><h2>Movement</h2><p id="servoStatus" role="status">Checking driver...</p>
<label><input id="servoConfirmed" type="checkbox" style="width:auto"> I checked the 5 V servo supply and the legs can move freely.</label>
<p><button id="walk" disabled>Start walking forward</button><button id="servoStop">Stop movement</button></p>
<label for="joint">Individual servo</label>
<select id="joint"><option value="1">1 · Left hip</option><option value="2">2 · Right hip</option><option value="3">3 · Left foot</option><option value="4">4 · Right foot</option></select>
<p><button class="manual" data-offset="-100" disabled>−10°</button><button class="manual" data-offset="0" disabled>Center</button><button class="manual" data-offset="100" disabled>+10°</button><button id="test" disabled>Test sweep</button></p>
<small>Angles are approximate offsets from center. Each individual command releases the selected servo after two seconds. Support Cece for the first test.</small>
<p><button id="servoScan">Rescan driver</button></p><p id="servoMessage" role="status"></p></div>
<div class="panel"><img id="camera" alt="Tap Start camera to see Cece's view">
<button id="videoStart">Start camera</button><button id="videoStop">Stop camera</button>
<p id="videoMessage">Camera stopped.</p></div>
<div class="panel"><button id="listen">Listen to robot mic</button><button id="stopAudio" disabled>Stop listening</button>
<p id="message">Tap Listen and turn up your phone's media volume.</p>
<label for="volume">Playback volume</label><input id="volume" type="range" min="0" max="3" step="0.1" value="1">
<label for="level">Microphone level</label><meter id="level" min="0" max="1" value="0"></meter>
<small>Audio comes from Cece's microphone, not your phone's microphone.</small></div>
<div class="panel"><p id="hardware">Checking board...</p><p id="network"></p>
<details id="setup"><summary>Connect Cece to home Wi-Fi</summary>
<p>Use a 2.4 GHz Wi-Fi network. Enter its details here; they are saved on the ESP, not in the program.</p>
<form action="/wifi" method="post"><label>Wi-Fi name (SSID)<input name="ssid" maxlength="32" required autocomplete="off"></label>
<label>Wi-Fi password<input name="password" type="password" maxlength="63" autocomplete="off"></label>
<button>Save and connect</button></form>
<p>Once connected, switch your phone back to that same Wi-Fi and open the home-network address shown above.</p></details></div>
<script>
'use strict';
const $=id=>document.getElementById(id);
let cameraAllowed=false, micAllowed=false, audioSession=null;
let walkSentAt=0;
let driverReady=false, activeServo=0, walking=false, pending=false, owner='', beatBusy=false;
function enableServoButtons(){
  const busy=pending || walking || !!activeServo || !!owner;
  for(const b of document.querySelectorAll('.manual,#walk,#test'))
    b.disabled=busy || !driverReady || !$('servoConfirmed').checked;
  $('servoScan').disabled=busy;
}
async function sendServo(action,fields={},keepalive=false){
  const res=await fetch('/servo',{method:'POST',keepalive,
    headers:{'X-Cece-Control':'__SERVO_TOKEN__'},
    body:new URLSearchParams({action,confirmed:$('servoConfirmed').checked?'1':'0',...fields})});
  if(!res.ok)throw new Error(await res.text());
}
function stopMotion(){
  owner=''; enableServoButtons();
  return sendServo('stop',{},true).then(()=>{$('servoMessage').textContent='Stop requested.';})
    .catch(e=>{$('servoMessage').textContent='Stop delivery failed: '+e.message;});
}
async function startMotion(action,fields={}){
  if(pending)return;
  pending=true;
  if(action==='walk'){
    const id=crypto.getRandomValues(new Uint32Array(1))[0] || 1;
    walkSentAt=performance.now();owner=id.toString(16).padStart(8,'0');fields.owner=owner;
  }
  enableServoButtons();
  try {
    await sendServo(action,fields);
    if(action==='walk' && !owner) await stopMotion();
    else $('servoMessage').textContent=action==='walk'?'Keep this page open while walking.':'Command sent.';
  } catch(e){owner='';$('servoMessage').textContent=e.message;}
  finally{pending=false;await status();enableServoButtons();}
}
setInterval(async()=>{
  if(!owner || beatBusy || pending)return;
  beatBusy=true;
  try{await sendServo('heartbeat',{owner});}
  catch(e){await stopMotion();}
  finally{beatBusy=false;}
},650);
$('walk').onclick=()=>startMotion('walk');
$('servoStop').onclick=stopMotion;
$('servoScan').onclick=()=>startMotion('scan');
$('test').onclick=()=>startMotion('test',{socket:$('joint').value});
for(const b of document.querySelectorAll('.manual'))
  b.onclick=()=>startMotion('position',{socket:$('joint').value,offset:b.dataset.offset});
$('servoConfirmed').onchange=()=>{if(!$('servoConfirmed').checked)stopMotion();enableServoButtons();};
function stopOnLeave(){if(owner || activeServo || pending)stopMotion();}
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopOnLeave();});
window.addEventListener('pagehide',stopOnLeave);
const streamUrl=port=>`http://${location.hostname}:${port}`;
$('videoStart').onclick=()=>{if(!cameraAllowed){$('videoMessage').textContent='Camera not detected. Check the Sense add-on board and ribbon with USB disconnected.';return;}$('camera').src=streamUrl(81)+'/video?t='+Date.now();$('videoMessage').textContent='Camera streaming.';};
$('videoStop').onclick=()=>{$('camera').removeAttribute('src');$('videoMessage').textContent='Camera stopped.';};
$('camera').onerror=()=>{$('videoMessage').textContent='Camera stream disconnected. Tap Start camera to reconnect.';};
function cancelSources(session){for(const source of session.sources){try{source.stop();}catch(e){}}session.sources.clear();}
function stopAudio(){const session=audioSession;if(!session)return;audioSession=null;session.abort.abort();cancelSources(session);session.context.close().catch(()=>{});$('listen').disabled=!micAllowed;$('stopAudio').disabled=true;$('level').value=0;$('message').textContent='Microphone playback stopped.';}
$('stopAudio').onclick=stopAudio;
$('volume').oninput=()=>{if(audioSession)audioSession.gain.gain.value=Number($('volume').value);};
$('listen').onclick=async()=>{
  if(!micAllowed||audioSession)return;
  const AudioCtx=window.AudioContext||window.webkitAudioContext;
  if(!AudioCtx){$('message').textContent='This browser has no Web Audio support. Try current Safari or Chrome.';return;}
  const context=new AudioCtx();const gain=context.createGain();gain.gain.value=Number($('volume').value);gain.connect(context.destination);
  const session={context,gain,abort:new AbortController(),sources:new Set(),next:0};audioSession=session;
  $('listen').disabled=true;$('stopAudio').disabled=false;$('message').textContent='Connecting microphone...';
  try{
    await context.resume();
    const response=await fetch(streamUrl(82)+'/audio',{signal:session.abort.signal,cache:'no-store'});
    if(!response.ok)throw new Error('Microphone HTTP '+response.status);
    if(!response.body)throw new Error('Streaming audio is not supported in this browser.');
    const reader=response.body.getReader();let carry=null;session.next=context.currentTime+0.15;
    $('message').textContent='Listening to Cece. Speak or tap gently near the robot microphone.';
    while(audioSession===session){
      const {value,done}=await reader.read();if(done)break;
      let bytes=value;
      if(carry!==null){const joined=new Uint8Array(bytes.length+1);joined[0]=carry;joined.set(bytes,1);bytes=joined;carry=null;}
      if(bytes.length%2){carry=bytes[bytes.length-1];bytes=bytes.subarray(0,bytes.length-1);}
      if(!bytes.length)continue;
      const buffer=context.createBuffer(1,bytes.length/2,16000),samples=buffer.getChannelData(0),view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);let peak=0;
      for(let i=0;i<samples.length;i++){samples[i]=view.getInt16(i*2,true)/32768;peak=Math.max(peak,Math.abs(samples[i]));}
      $('level').value=Math.min(1,peak);
      // Bound queue latency after a network stall instead of accumulating seconds of old audio.
      if(session.next<context.currentTime||session.next>context.currentTime+0.7){cancelSources(session);session.next=context.currentTime+0.12;}
      const source=context.createBufferSource();source.buffer=buffer;source.connect(gain);session.sources.add(source);source.onended=()=>session.sources.delete(source);
      source.start(session.next);session.next+=buffer.duration;
    }
    if(audioSession===session){stopAudio();$('message').textContent='Microphone disconnected. Tap Listen to reconnect.';}
  }catch(error){if(audioSession===session){stopAudio();$('message').textContent='Audio: '+error.message;}}
};
async function status(){const queriedOwner=owner,requestTime=performance.now();try{const response=await fetch('/status',{cache:'no-store'});const s=await response.json();cameraAllowed=s.camera;micAllowed=s.microphone;driverReady=s.servo_driver;activeServo=s.servo_socket;walking=s.walking;
  if(!walking && !pending && owner && owner===queriedOwner && performance.now()-requestTime<1500 && requestTime>walkSentAt+500)owner='';
  enableServoButtons();
  $('servoStatus').textContent=!driverReady?'Driver unavailable. Check I²C wiring and rescan.':walking?'Walking forward':activeServo?'Moving servo '+activeServo:'Stopped · driver ready';
  $('listen').disabled=!micAllowed||!!audioSession;
  $('hardware').textContent=`Camera: ${s.camera?'ready (sensor '+s.sensor+')':'NOT DETECTED'} | Mic: ${s.microphone?'ready':'NOT DETECTED'} | PSRAM: ${Math.round(s.psram/1048576)} MB`;
  $('network').replaceChildren();if(s.connected){const link=document.createElement('a');link.href='http://'+s.ip;link.textContent='http://'+s.ip;$('network').append('Home Wi-Fi connected. Open ',link,` on your phone (${s.rssi} dBm).`);}else{$('network').textContent='Home Wi-Fi not connected. Open Wi-Fi setup below.';$('setup').open=true;}
}catch(e){driverReady=false;enableServoButtons();$('servoStatus').textContent='Connection lost';$('hardware').textContent='Board not reachable. Check that your phone and Cece are on the same Wi-Fi.';}}
status();setInterval(status,2500);window.addEventListener('pagehide',()=>{stopAudio();$('camera').removeAttribute('src');});
</script></html>)CECEHTML";
