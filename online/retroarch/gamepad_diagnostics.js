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
return {family,snapshot};
});