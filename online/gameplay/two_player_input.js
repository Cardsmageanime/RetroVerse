/* RetroVerse two-player controller input, shared by network gameplay pages.
   Standard Gamepad mapping (D-pad 12/13, left stick Y). No uploads. */
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;root.RetroVerseTwoPlayer=api;})(typeof globalThis!=="undefined"?globalThis:this,function(){
"use strict";
const DEADZONE=.38;
const DEFAULT_MAPPING={up:12,down:13,axis:1,deadzone:DEADZONE,invert:false};
function validateMapping(m){if(!m||typeof m!=="object")throw Error("Invalid mapping");const x={...DEFAULT_MAPPING,...m};for(const k of ["up","down","axis"])if(!Number.isInteger(x[k])||x[k]<0||x[k]>31)throw Error("Invalid "+k);if(x.up===x.down)throw Error("Up and down must differ");if(typeof x.deadzone!=="number"||!Number.isFinite(x.deadzone)||x.deadzone<.05||x.deadzone>.95)throw Error("Invalid deadzone");if(typeof x.invert!=="boolean")throw Error("Invalid invert");return x;}
function direction(pad,mapping=DEFAULT_MAPPING){
 const m=validateMapping(mapping);
 if(!pad||pad.connected===false)return 0;
 const buttons=pad.buttons||[],axes=pad.axes||[];
 const axis=(Number(axes[m.axis])||0)*(m.invert?-1:1);
 const up=!!buttons[m.up]?.pressed || axis < -m.deadzone;
 const down=!!buttons[m.down]?.pressed || axis > m.deadzone;
 return up===down?0:up?-1:1;
}
function connected(pads){return Array.from(pads||[]).filter(p=>p&&p.connected!==false).sort((a,b)=>a.index-b.index)}
class Input {
 constructor(){this.selected=null;this.keys=new Set();this.last=null;this.mapping={...DEFAULT_MAPPING};}
 setMapping(mapping){this.mapping=validateMapping(mapping);this.last=null;return {...this.mapping};}
 select(index,pads){if(!connected(pads).some(p=>p.index===index))return false;this.selected=index;this.last=null;return true;}
 keyboard(key,pressed){if(!["ArrowUp","ArrowDown","w","W","s","S"].includes(key))return false;const k=key.toLowerCase();if(pressed)this.keys.add(k);else this.keys.delete(k);return true;}
 sample(pads){const list=connected(pads);const active=list.find(p=>p.index===this.selected)||list[0]||null;if(active)this.selected=active.index;else this.selected=null;
 const keyUp=this.keys.has("arrowup")||this.keys.has("w"),keyDown=this.keys.has("arrowdown")||this.keys.has("s");
 const keyboard=keyUp===keyDown?0:keyUp?-1:1;
 const value=active?direction(active,this.mapping):keyboard;
 return {direction:value,controllers:list.map(p=>({index:p.index,name:String(p.id||"Gamepad").slice(0,70)})),active:this.selected,source:active?"gamepad":"keyboard"};
 }
 changed(state){if(state.direction===this.last)return false;this.last=state.direction;return true;}
 reset(){this.keys.clear();this.last=null;this.selected=null;}
}
return {Input,direction,connected,DEADZONE,DEFAULT_MAPPING,validateMapping};
});