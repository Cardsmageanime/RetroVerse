/* Offline local-file soundtrack shuffle. Tracks never leave this browser. */
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;root.RetroVerseMusic=api;})(typeof globalThis!=="undefined"?globalThis:this,function(){
"use strict";
function shuffledIndices(count,random=Math.random){const result=Array.from({length:count},(_,i)=>i);for(let i=count-1;i>0;i--){const j=Math.min(i,Math.max(0,Math.floor(random()*(i+1))));[result[i],result[j]]=[result[j],result[i]];}return result;}
class Queue{constructor(random=Math.random){this.random=random;this.count=0;this.pending=[];this.last=null;}
 reset(count){this.count=count;this.pending=[];this.last=null;}
 next(){if(this.count===0)return null;if(this.pending.length===0){this.pending=shuffledIndices(this.count,this.random);if(this.count>1&&this.pending[0]===this.last){const swap=this.pending.findIndex(x=>x!==this.last);[this.pending[0],this.pending[swap]]=[this.pending[swap],this.pending[0]];}}
 const index=this.pending.shift();this.last=index;return index;}
}
return {Queue,shuffledIndices};
});
