// Browser interaction test for the RetroVerse Neon Showcase.
// Requires: npm install --no-save playwright && npx playwright install chromium
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const browser = await chromium.launch({headless:true});
const page = await browser.newPage({viewport:{width:1440,height:900}});
const errors = [];
page.on('pageerror', error => errors.push(error.message));
function check(ok,message){if(!ok)throw Error(message);console.log('PASS:',message)}
try {
 await page.goto(pathToFileURL(resolve('interface/neon-showcase/index.html')).href);
 check(await page.locator('#home').isVisible(),'Home loads');
 await page.locator('.nav[data-view="library"]').click();
 check(await page.locator('#library').isVisible(),'Library navigation');
 await page.locator('#game-search').fill('Dreamcast');
 check(await page.locator('#systems .tile').count() === 1,'Library search filters');
 await page.locator('.nav[data-view="online"]').click();
 check(await page.locator('#online').isVisible(),'Online navigation');
 await page.locator('#room-search').fill('Arcade');
 check(await page.locator('#rooms tr').count() === 1,'Room search filters');
 await page.locator('#room-search').fill('');
 await page.locator('#create-room').click();
 check((await page.locator('#rooms tr').count()) === 5,'Create local demo room');
 await page.locator('.nav[data-view="friends"]').click();
 check(await page.locator('#friends-list .person').count() === 4,'Friends demo list');
 await page.locator('.nav[data-view="multiplayer"]').click();
 await page.locator('#ready').click();
 check((await page.locator('#ready-state').innerText()).includes('You are ready'),'Ready Up state toggles');
 await page.locator('.nav[data-view="chat"]').click();
 await page.locator('#chat-message').fill('browser smoke hello');
 await page.locator('#chat-form button[type="submit"]').click();
 check((await page.locator('#chatlog').innerText()).includes('browser smoke hello'),'Local chat message appears');
 await page.locator('.nav[data-view="spectator"]').click();
 check(await page.locator('#spectator').isVisible(),'Spectator navigation');
 await page.locator('.nav[data-view="themes"]').click();
 await page.locator('.theme-button').filter({hasText:'Cyber Grid'}).click();
 check(await page.locator('body').getAttribute('data-theme') === 'cyber','Theme switching');
 await page.locator('.nav[data-view="settings"]').click();
 await page.locator('#compact').check();
 check(await page.locator('.stage').evaluate(el=>el.style.padding) === '12px','Compact layout');
 await page.keyboard.press('Escape');
 check(await page.locator('#home').isVisible(),'Escape returns Home');
 check(errors.length===0, 'No browser JavaScript exceptions: '+errors.join(' | '));
 console.log('All Neon Showcase Chromium interactions passed.');
} finally {
 await browser.close();
}
