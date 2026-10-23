/* RetroVerse startup preferences — browser prototype only; no authentication. */
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;root.RetroVerseStartup=api;})(typeof globalThis!=="undefined"?globalThis:this,function(){
"use strict";
const KEY="retroverse.startup.v1";
const defaults=Object.freeze({theme:"classic",lastMode:"offline",sound:false});
const THEMES=["classic","cyber","sunset","forest","dark","galaxy"];
function validate(obj){if(!obj||typeof obj!=="object")return {...defaults};return {theme:THEMES.includes(obj.theme)?obj.theme:defaults.theme,lastMode:obj.lastMode==="offline"?"offline":defaults.lastMode,sound:obj.sound===true};}
function load(store){try{return validate(JSON.parse(store.getItem(KEY)))}catch(_){return {...defaults}}}
function save(store,settings){const clean=validate(settings);store.setItem(KEY,JSON.stringify(clean));return clean}
function launch(mode,store,session){if(mode!=="offline"&&mode!=="start")throw Error("Unsupported launch mode");const current=load(store);save(store,{...current,lastMode:"offline"});session.setItem("retroverse_launch_mode","offline");return "../neon-showcase/index.html"}
return {KEY,THEMES,defaults,validate,load,save,launch};
});