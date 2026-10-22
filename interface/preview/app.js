(()=>{"use strict";
const views=["home","library","online","settings"];
let current="home";
function open(name){if(!views.includes(name))return;current=name;
for(const v of views)document.getElementById(v).classList.toggle("hidden",v!==name);
for(const b of document.querySelectorAll(".nav")){const active=b.dataset.view===name;b.classList.toggle("active",active);if(active)b.setAttribute("aria-current","page");else b.removeAttribute("aria-current");}
document.getElementById("notice").textContent=name+" section";
}
document.querySelectorAll("[data-view]").forEach(b=>b.addEventListener("click",()=>open(b.dataset.view)));
document.querySelectorAll("[data-open]").forEach(b=>b.addEventListener("click",()=>open(b.dataset.open)));
document.getElementById("contrast").addEventListener("change",e=>document.body.classList.toggle("contrast",e.target.checked));
function controls(){return [...document.querySelectorAll(".nav, .page:not(.hidden) button:not(:disabled), .page:not(.hidden) input")].filter(x=>!x.closest(".disabled"));}
function move(direction){const items=controls();if(!items.length)return;const i=items.indexOf(document.activeElement);items[(i+direction+items.length)%items.length].focus();}
function goBack(){if(current!=="home")open("home");document.querySelector('.nav[data-view="home"]').focus();}
function select(){const active=document.activeElement;if(!controls().includes(active)){controls()[0]?.focus();return;}if(active.type==="checkbox"){active.click();return;}active.click();}
function act(action){if(action==="up"||action==="left")move(-1);else if(action==="down"||action==="right")move(1);else if(action==="back")goBack();else if(action==="select")select();}
document.addEventListener("keydown",e=>{const keys={ArrowDown:"down",ArrowRight:"right",ArrowUp:"up",ArrowLeft:"left",Escape:"back"};if(keys[e.key]){e.preventDefault();act(keys[e.key]);}});
const controller=new RetroVerseGamepad.Controller();
const registry=new RetroVerseDetection.Registry();
let previousSignature="";
function renderControllers(result){
 const status=document.getElementById("controller-status");
 const list=document.getElementById("controller-list");
 if(!status||!list)return;
 status.textContent=result.controllers.length?result.controllers.length+" controller(s) detected":"No controller detected. Connect a gamepad and press a button.";
 list.replaceChildren();
 for(const item of result.controllers){
  const button=document.createElement("button");
  button.className="nav";
  button.textContent=(item.index===result.active?"● ":"○ ")+item.name+" ("+item.mapping+")";
  button.setAttribute("aria-pressed",String(item.index===result.active));
  button.addEventListener("click",()=>{registry.select(item.index,navigator.getGamepads?.()||[]);previousSignature="";});
  list.appendChild(button);
 }
}

function loop(now){
 const pads=navigator.getGamepads?[...navigator.getGamepads()]:[];
 const result=registry.update(pads);
 const signature=JSON.stringify({active:result.active,controllers:result.controllers});
 if(signature!==previousSignature){
  renderControllers(result);
  document.getElementById("notice").textContent=result.controllers.length?"Controller detected: "+result.controllers.find(x=>x.index===result.active)?.name:"Controller disconnected";
  previousSignature=signature;
 }
 for(const event of controller.update(result.pad,now))act(event);
 requestAnimationFrame(loop);
}
open("home");
if(typeof requestAnimationFrame==="function")requestAnimationFrame(loop);
})();