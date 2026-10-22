/* Local, offline music queue. No bundled audio or network requests. */
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;root.RetroVerseMusic=api;})(typeof globalThis!=="undefined"?globalThis:this,function(){
"use strict";
function shuffledIndices(count,random=Math.random){const result=Array.from({length:count},(_,i)=>i);for(let i=count-1;i>0;i--){const j=Math.max(0,Math.min(i,Math.floor(random()*(i+1))));[result[i],result[j]]=[result[j],result[i]];}return result;}
function soundtrack(name){const s=String(name||"").toLowerCase();if(s.includes("mecha yokai"))return "mecha";if(s.includes("cosmic oblivion"))return "cosmic";return "other";}
function eligible(files,selection="all"){if(selection==="off")return [];return files.map((f,i)=>({f,i})).filter(({f})=>selection==="all"||soundtrack(f.name)===selection).map(({i})=>i);}
class Queue{
 constructor(random=Math.random){this.random=random;this.items=[];this.pending=[];this.last=null;this.shuffle=true;}
 configure(items,shuffle=true){this.items=[...items];this.shuffle=!!shuffle;this.pending=[];this.last=null;}
 reset(count){this.configure(Array.from({length:count},(_,i)=>i));}
 next(){if(!this.items.length)return null;if(!this.pending.length){this.pending=this.shuffle?shuffledIndices(this.items.length,this.random).map(i=>this.items[i]):[...this.items];if(this.shuffle&&this.pending.length>1&&this.pending[0]===this.last){const i=this.pending.findIndex(v=>v!==this.last);[this.pending[0],this.pending[i]]=[this.pending[i],this.pending[0]];}}const next=this.pending.shift();this.last=next;return next;}
}
return {Queue,shuffledIndices,soundtrack,eligible};
});
