/* Controller mapping for the browser preview. No network calls or device writes. */
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;root.RetroVerseGamepad=api;})(typeof globalThis!=="undefined"?globalThis:this,function(){
"use strict";
const DEADZONE=0.45,INITIAL_DELAY=320,REPEAT_MS=135;
function pressed(pad,index){return !!(pad&&pad.buttons&&pad.buttons[index]&&pad.buttons[index].pressed)}
function decode(pad){
 const axis=pad&&pad.axes||[],x=Number(axis[0])||0,y=Number(axis[1])||0;
 return {up:pressed(pad,12)||y < -DEADZONE,down:pressed(pad,13)||y > DEADZONE,
 left:pressed(pad,14)||x < -DEADZONE,right:pressed(pad,15)||x > DEADZONE,
 select:pressed(pad,0),back:pressed(pad,1)};
}
function Controller(){
 this.previous={};this.nextRepeat=0;this.direction=null;this.activeId=null;
}
Controller.prototype.update=function(pad,now){
 if(!pad){this.previous={};this.direction=null;this.nextRepeat=0;this.activeId=null;return [];}
 const id=pad.index===undefined?0:pad.index;
 if(id!==this.activeId){this.previous={};this.direction=null;this.nextRepeat=0;this.activeId=id;}
 const state=decode(pad),events=[];
 const dir=state.up?"up":state.down?"down":state.left?"left":state.right?"right":null;
 if(dir!==this.direction){this.direction=dir;this.nextRepeat=now+INITIAL_DELAY;if(dir)events.push(dir);}
 else if(dir&&now>=this.nextRepeat){events.push(dir);this.nextRepeat=now+REPEAT_MS;}
 for(const action of ["select","back"]){if(state[action]&&!this.previous[action])events.push(action);}
 this.previous=state;return events;
};
return {Controller,decode,DEADZONE};
});
