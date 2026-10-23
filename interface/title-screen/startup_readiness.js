/* Read-only startup diagnostics. No server, account, ROM scanning or Wi-Fi connection. */
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;root.RetroVerseReadiness=api;})(typeof globalThis!=="undefined"?globalThis:this,function(){
"use strict";
function check({pads=[],online=false,library=null}={}){
 const connected=Array.from(pads||[]).filter(p=>p&&p.connected!==false);
 const count=connected.length;
 const libraryState=library===true?"configured":library===false?"not-configured":"unknown";
 return {controllers:{count,status:count?"connected":"keyboard-fallback"},network:{status:online?"browser-online":"browser-offline",verified:false},library:{status:libraryState,scanned:false},offlineReady:true,onlineReady:false};
}
function describe(s){return [
 "Input: "+(s.controllers.count?s.controllers.count+" controller(s) detected":"keyboard fallback available"),
 "Library: "+(s.library.status==="unknown"?"not checked (OS integration pending)":s.library.status),
 "Network: "+(s.network.status==="browser-online"?"browser reports online; internet not verified":"browser reports offline"),
 "Offline Mode: available without login"
];}
return {check,describe};
});