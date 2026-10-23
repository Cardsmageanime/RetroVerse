/* Offline library cards. Never inject metadata as HTML or fetch remote artwork. */
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;root.RetroVerseLibraryCards=api;})(typeof globalThis!=="undefined"?globalThis:this,function(){
"use strict";
function clean(entry){
 if(!entry||typeof entry!=="object")throw Error("Invalid game");
 const text=(v,max)=>typeof v==="string"?v.slice(0,max):"";
 return {title:text(entry.title,180)||"Untitled",system:text(entry.system,80)||"Unknown",
 description:text(entry.description,500),year:Number.isInteger(entry.year)&&entry.year>=1970&&entry.year<=2100?entry.year:null,
 cover:typeof entry.cover==="string"&&/^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/=]+$/.test(entry.cover)&&entry.cover.length<=200000?entry.cover:null};
}
function render(list,games){
 list.replaceChildren();
 for(const value of games.slice(0,5000)){
  const game=clean(value),li=document.createElement("li");
  li.className="rv-game-card";
  if(game.cover){const img=document.createElement("img");img.src=game.cover;img.alt="Cover art for "+game.title;img.loading="lazy";li.append(img)}
  const detail=document.createElement("div"),title=document.createElement("strong"),meta=document.createElement("small");
  title.textContent=game.title;meta.textContent=game.system+(game.year?" · "+game.year:"");
  detail.append(title,meta);
  if(game.description){const p=document.createElement("p");p.textContent=game.description;detail.append(p)}
  li.append(detail);list.append(li);
 }
 return list.childElementCount;
}
return {clean,render};
});