const assert=require('node:assert/strict');
const fs=require('node:fs');
const startup=require('./startup_state.js');
function storage(){const map=new Map();return {getItem:k=>map.has(k)?map.get(k):null,setItem:(k,v)=>map.set(k,v),value:k=>map.get(k)}}
const local=storage(),session=storage();
assert.deepEqual(startup.load(local),startup.defaults);
assert.equal(startup.save(local,{theme:'galaxy',lastMode:'offline',sound:true}).theme,'galaxy');
assert.equal(startup.load(local).sound,true);
assert.equal(startup.save(local,{theme:'invalid',lastMode:'online',sound:'yes'}).lastMode,'offline');
assert.equal(startup.launch('start',local,session),'../neon-showcase/index.html');
assert.equal(session.value('retroverse_launch_mode'),'offline');
assert.throws(()=>startup.launch('online',local,session));
local.setItem(startup.KEY,'{corrupted');assert.equal(startup.load(local).theme,'classic');
const title=fs.readFileSync('interface/title-screen/index.html','utf8');
const home=fs.readFileSync('interface/neon-showcase/index.html','utf8');
assert.match(title,/id="loading"/);
assert.match(title,/RetroVerseStartup\.launch/);
assert.match(home,/offlineViews/);
console.log('Startup preferences, offline-first launch, and loading transition checks passed');
