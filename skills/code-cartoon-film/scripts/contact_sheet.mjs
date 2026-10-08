// 逐时间点截图并拼成总览图，检查每场画面和字幕。
// 用法：FILM=file:///abs/path/index.html node contact_sheet.mjs out_dir 3 14 30 ...
// 依赖页面暴露 window.READY 和 window.__film.render(t)；playwright 用环境里预装的 chromium。
import { execSync as sh } from 'node:child_process';
// 先找本地 playwright，找不到就用全局安装（npm root -g）
let pw; try { pw = await import('playwright'); } catch { pw = await import(`${sh('npm root -g').toString().trim()}/playwright/index.mjs`); }
const { chromium } = pw;
import { execSync } from 'node:child_process';
const [out, ...ts] = process.argv.slice(2);
execSync(`mkdir -p ${out}`);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
const errs = []; p.on('pageerror', e => errs.push(e.message));
await p.goto(process.env.FILM); await p.waitForFunction(() => window.READY, null, { timeout: 30000 });
for (const t of ts.map(Number)) {
  await p.evaluate(t => { window.__frozen = true; document.getElementById('start')?.classList.add('hidden'); const bar = document.getElementById('bar'); if (bar) bar.style.display = 'none'; __film.render(t); }, t);
  await p.locator('canvas').screenshot({ path: `${out}/t${t.toFixed(1).padStart(6, '0')}.png` });
}
await b.close();
execSync(`ffmpeg -loglevel error -y -pattern_type glob -i '${out}/t*.png' -vf "crop=1440:1080:240:0,scale=480:360,tile=4x${Math.ceil(ts.length / 4)}" -frames:v 1 ${out}/sheet.png`);
console.log('errors:', errs, '→', `${out}/sheet.png`);
