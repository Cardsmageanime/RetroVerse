(()=>{
"use strict";
const picker=document.getElementById("music-files"),status=document.getElementById("music-status");
const play=document.getElementById("music-play"),skip=document.getElementById("music-next"),volume=document.getElementById("music-volume");
const audio=new Audio();audio.volume=0.35;
const queue=new RetroVerseMusic.Queue();let files=[],url=null;
function revoke(){if(url){URL.revokeObjectURL(url);url=null;}}
function display(message){status.textContent=message;}
async function next(){
 const i=queue.next();if(i===null){display("Add your own music files to start.");return;}
 audio.pause();revoke();url=URL.createObjectURL(files[i]);audio.src=url;
 display("Now playing: "+files[i].name);
 try{await audio.play();play.textContent="Pause";}catch{play.textContent="Play";display("Ready: "+files[i].name+" — press Play");}
}
picker.addEventListener("change",()=>{audio.pause();revoke();files=[...picker.files].filter(f=>f.type.startsWith("audio/")||/\.(mp3|ogg|wav|flac|m4a)$/i.test(f.name));queue.reset(files.length);audio.removeAttribute("src");audio.load();play.disabled=skip.disabled=!files.length;play.textContent="Play";display(files.length?files.length+" local tracks ready. Press Play for random music.":"No playable music selected.");});
play.addEventListener("click",async()=>{if(!files.length)return;if(!audio.src){await next();return;}if(audio.paused){try{await audio.play();play.textContent="Pause";}catch{display("Playback unsupported for this audio file.");}}else{audio.pause();play.textContent="Play";}});
skip.addEventListener("click",next);
volume.addEventListener("input",()=>{audio.volume=Number(volume.value)/100;});
audio.addEventListener("ended",next);
audio.addEventListener("error",()=>{play.textContent="Play";display("Cannot play this audio format. Press Next to skip.");});
window.addEventListener("pagehide",()=>{audio.pause();revoke();});
})();