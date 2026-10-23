/* Controller family presets for browser Gamepad API standard mapping.
   These are starting points, not guaranteed drivers/RetroArch autoconfigs. */
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;root.RetroVerseProfiles=api;})(typeof globalThis!=="undefined"?globalThis:this,function(){
"use strict";
const standard=Object.freeze({up:12,down:13,axis:1,deadzone:.38,invert:false});
const profiles=Object.freeze({
 standard:{label:"Standard / Generic",mapping:{...standard}},
 xbox:{label:"Xbox (browser standard)",mapping:{...standard}},
 playstation:{label:"PlayStation (browser standard)",mapping:{...standard}},
 switch:{label:"Nintendo Switch (browser standard)",mapping:{...standard}},
 custom:{label:"Custom",mapping:{...standard}}
});
function detect(id){const s=String(id||"").toLowerCase();if(/xbox|xinput|045e/.test(s))return "xbox";if(/dualshock|dualsense|playstation|054c|sony/.test(s))return "playstation";if(/switch|joy-con|nintendo|057e/.test(s))return "switch";return "standard";}
function create(name,override){const preset=profiles[name];if(!preset)throw Error("Unknown profile");const merged={...preset.mapping,...(override||{})};return merged;}
return {profiles,detect,create};
});