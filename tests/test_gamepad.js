const assert=require("node:assert/strict");
const {Controller,decode}=require("../interface/preview/gamepad.js");
function pad({buttons=[],axes=[0,0],index=0}={}){return {index,axes,buttons:Array.from({length:16},(_,i)=>({pressed:buttons.includes(i)}))};}
assert.equal(decode(pad({axes:[0.2,0.2]})).down,false);
assert.equal(decode(pad({axes:[0,0.8]})).down,true);
assert.equal(decode(pad({buttons:[12]})).up,true);
const controller=new Controller();
assert.deepEqual(controller.update(pad({buttons:[13]}),0),["down"]);
assert.deepEqual(controller.update(pad({buttons:[13]}),200),[]);
assert.deepEqual(controller.update(pad({buttons:[13]}),320),["down"]);
assert.deepEqual(controller.update(pad({buttons:[13]}),400),[]);
assert.deepEqual(controller.update(pad({buttons:[0,13]}),470),["down","select"]);
assert.deepEqual(controller.update(pad({buttons:[0,13]}),500),[]);
assert.deepEqual(controller.update(pad({buttons:[1]}),510),["back"]);
assert.deepEqual(controller.update(null,520),[]);
assert.deepEqual(controller.update(pad({buttons:[0],index:2}),530),["select"]);
console.log("RetroVerse gamepad mapping/deadzone/repeat/button tests passed");
