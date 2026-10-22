/* Browser Gamepad API detection and stable active-controller selection. */
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;root.RetroVerseDetection=api;})(typeof globalThis!=="undefined"?globalThis:this,function(){
"use strict";
function describe(p){return {index:p.index,name:String(p.id||"Unknown controller").slice(0,100),mapping:p.mapping||"unknown",connected:p.connected!==false};}
class Registry{
 constructor(){this.active=null;}
 update(pads){
  const list=Array.from(pads||[]).filter(p=>p&&p.connected!==false).sort((a,b)=>a.index-b.index);
  const previous=this.active;
  if(!list.some(p=>p.index===this.active))this.active=list.length?list[0].index:null;
  return {controllers:list.map(describe),active:this.active,changed:previous!==this.active,pad:list.find(p=>p.index===this.active)||null};
 }
 select(index,pads){
  const list=Array.from(pads||[]).filter(Boolean);
  if(!list.some(p=>p.index===index&&p.connected!==false))return false;
  this.active=index;return true;
 }
}
return {Registry,describe};
});
