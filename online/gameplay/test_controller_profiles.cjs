const assert=require("node:assert/strict");
const {profiles,detect,create}=require("./controller_profiles.js");
assert.equal(Object.keys(profiles).length,5);
assert.equal(detect("Xbox Wireless Controller"),"xbox");
assert.equal(detect("Sony DualSense Wireless Controller"),"playstation");
assert.equal(detect("Nintendo Switch Pro Controller"),"switch");
assert.equal(detect("USB Gamepad"),"standard");
for(const name of Object.keys(profiles)){const m=create(name);assert.equal(m.up,12);assert.equal(m.down,13);assert.equal(m.axis,1)}
assert.equal(create("xbox",{invert:true}).invert,true);
assert.throws(()=>create("not-a-profile"));
console.log("RetroVerse controller preset tests passed");
