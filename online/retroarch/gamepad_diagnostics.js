/* Read-only browser Gamepad API diagnostics for the RetroVerse Netplay editor.
   Browser indices are hints and NEVER automatically become RetroArch indices. */
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;root.RetroVerseGamepadDiagnostics=api;})(typeof globalThis!=="undefined"?globalThis:this,function(){
"use strict";
function family(id){const s=String(id||"").toLowerCase();if(/dualsense|dualshock|playstation|sony|054c/.test(s))return "PlayStation";if(/xbox|xinput|045e/.test(s))return "Xbox";if(/nintendo|switch|joy.con|057e/.test(s))return "Nintendo";return "Generic / Unknown";}
function snapshot(pads){return Array.from(pads||[]).filter(p=>p&&p.connected!==false).map(p=>({
 browserIndex:Number.isInteger(p.index)?p.index:null,
 name:String(p.id||"Unknown controller").slice(0,100),
 family:family(p.id),
 mapping:p.mapping||"unknown",
 buttonCount:(p.buttons||[]).length,
 axisCount:(p.axes||[]).length,
 buttons:Array.from(p.buttons||[],b=>!!b.pressed),
 axes:Array.from(p.axes||[],a=>Number.isFinite(a)?Math.round(a*100)/100:0)
}));}
function activity(previous,current,deadzone=.3){const before=new Map((previous||[]).map(p=>[p.browserIndex,p]));return (current||[]).map(p=>{const old=before.get(p.browserIndex);return {browserIndex:p.browserIndex,name:p.name,buttonsPressed:p.buttons.map((v,i)=>v?i:null).filter(v=>v!==null),movedAxes:p.axes.map((value,i)=>Math.abs(value)>deadzone&&Math.abs(value-(old?.axes[i]||0))>.12?i:null).filter(v=>v!==null),connected:true};});}
function readiness(pads){const indexes=new Set((pads||[]).map(p=>p.browserIndex));return {connected:indexes.size,hasTwo:indexes.size>=2,warning:"Browser gamepad indices are not RetroArch joypad indices; verify assignments inside RetroArch."};}
return {family,snapshot,activity,readiness};
});