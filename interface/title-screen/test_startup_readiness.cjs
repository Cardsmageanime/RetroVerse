const assert=require('node:assert/strict');const fs=require('node:fs');const r=require('./startup_readiness.js');
let state=r.check({pads:[],online:false});assert.equal(state.offlineReady,true);assert.equal(state.onlineReady,false);assert.equal(state.controllers.status,'keyboard-fallback');assert.equal(state.library.status,'unknown');assert.equal(state.library.scanned,false);
state=r.check({pads:[null,{id:'Pad 1',connected:true},{connected:false}],online:true,library:null});assert.equal(state.controllers.count,1);assert.equal(state.network.verified,false);assert.match(r.describe(state).join(' '),/internet not verified/);
assert.equal(r.check({library:true}).library.status,'configured');
const html=fs.readFileSync('interface/title-screen/index.html','utf8');assert.match(html,/startup_readiness\.js/);assert.match(html,/id="readiness-list"/);assert.match(html,/gamepadconnected/);
console.log('Read-only startup diagnostics and offline access tests passed');