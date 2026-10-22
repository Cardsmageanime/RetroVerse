const assert=require("node:assert/strict");const {Queue,shuffledIndices,soundtrack,eligible}=require("../interface/preview/music.js");
const files=[{name:"Mecha Yokai - Song.wav"},{name:"Cosmic Oblivion - Song.wav"},{name:"personal track.wav"}];
assert.deepEqual(eligible(files),[0,1,2]);assert.deepEqual(eligible(files,"mecha"),[0]);assert.deepEqual(eligible(files,"cosmic"),[1]);assert.deepEqual(eligible(files,"off"),[]);
assert.equal(soundtrack("PHAT PHROG - MECHA YOKAI.wav"),"mecha");assert.equal(soundtrack("Cosmic Oblivion - Arena.wav"),"cosmic");assert.equal(soundtrack("Astral Visit - Cosmic Harmony.wav"),"astral");assert.deepEqual(eligible([{name:"Astral Visit - Cosmic Harmony.wav"},{name:"Cosmic Oblivion.wav"}],"astral"),[0]);
const q=new Queue(()=>0);q.configure([0,1,2],true);const first=[q.next(),q.next(),q.next()];assert.equal(new Set(first).size,3);assert.notEqual(q.next(),first[2]);
q.configure([7,8,9],false);assert.deepEqual([q.next(),q.next(),q.next(),q.next()],[7,8,9,7]);
q.configure([],true);assert.equal(q.next(),null);q.reset(1);assert.equal(q.next(),0);assert.deepEqual(shuffledIndices(0),[]);
console.log("Music soundtrack selection and shuffle tests passed");