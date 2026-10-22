(()=>{"use strict";
const picker=document.getElementById("music-files"),status=document.getElementById("music-status");
const play=document.getElementById("music-play"),skip=document.getElementById("music-next"),volume=document.getElementById("music-volume");
const selection=document.getElementById("music-soundtrack"),shuffle=document.getElementById("music-shuffle"),continuous=document.getElementById("music-continuous");
const audio=new Audio();audio.volume=0.35;const queue=new RetroVerseMusic.Queue();
let files=[],url=null,playIntent=false;
function revoke(){if(url){URL.revokeObjectURL(url);url=null;}}
function display(message){status.textContent=message;}
function configure(){audio.pause();revoke();audio.removeAttribute("src");audio.load();playIntent=false;play.textContent="Play";
const ids=RetroVerseMusic.eligible(files,selection.value);queue.configure(ids,shuffle.checked);play.disabled=skip.disabled=!ids.length;
display(selection.value==="off"?"Music is off.":ids.length?ids.length+" matching local tracks ready. Press Play.":"No tracks in this soundtrack. Choose matching local files.");}
async function next(){const i=queue.next();if(i===null){playIntent=false;display("No music available for this selection.");return;}
audio.pause();revoke();url=URL.createObjectURL(files[i]);audio.src=url;display("Now playing: "+files[i].name);
try{await audio.play();playIntent=true;play.textContent="Pause";}catch{playIntent=false;play.textContent="Play";display("Ready: "+files[i].name+" — press Play");}}
picker.addEventListener("change",()=>{files=[...picker.files].filter(f=>f.type.startsWith("audio/")||/\.(mp3|ogg|wav|flac|m4a)$/i.test(f.name));configure();});
selection.addEventListener("change",configure);shuffle.addEventListener("change",configure);
continuous.addEventListener("change",()=>display(continuous.checked?"Continuous playback on.":"Continuous playback off; music will stop after this track."));
play.addEventListener("click",async()=>{if(!files.length||selection.value==="off")return;if(!audio.src){await next();return;}if(audio.paused){try{await audio.play();playIntent=true;play.textContent="Pause";}catch{display("Playback unsupported for this audio file.");}}else{audio.pause();playIntent=false;play.textContent="Play";}});
skip.addEventListener("click",next);volume.addEventListener("input",()=>{audio.volume=Number(volume.value)/100;});
audio.addEventListener("ended",()=>{if(continuous.checked&&playIntent)next();else{playIntent=false;play.textContent="Play";display("Playback finished.");}});
audio.addEventListener("error",()=>{playIntent=false;play.textContent="Play";display("Cannot play this audio format. Press Next to skip.");});
window.addEventListener("pagehide",()=>{audio.pause();revoke();});configure();
})();