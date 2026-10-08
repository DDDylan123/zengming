// 逐帧渲染 demo/wave.html 为无声 MP4（需要 playwright 和 ffmpeg）：node demo/wave/render.js <v或h> <fps> <起始秒> <结束秒> <输出.mp4>
// 可以把全片切成几段并行渲染，再用 ffmpeg concat 拼接
const { chromium } = require('playwright');
const { spawn } = require('child_process');
(async () => {
  const [ar, fps, t0, t1, out] = process.argv.slice(2);
  const [w, h] = ar === 'v' ? [1080, 1920] : [1920, 1080];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: w, height: h } });
  await p.goto(`file:///home/user/zengming/demo/wave.html?ar=${ar}&t=0`, { waitUntil: 'networkidle' });
  await p.evaluate(async () => { await Promise.all(["500 40px Caveat", "700 40px Caveat", "400 30px 'Noto Sans SC'", "500 30px 'Noto Sans SC'", "700 30px 'Noto Sans SC'", "300 30px 'Noto Sans SC'", "900 30px 'Noto Serif SC'"].map(f => document.fonts.load(f, "反方原话转述补充0123456789亿"))); await document.fonts.ready; for (const k in LAYOUT_CACHE) delete LAYOUT_CACHE[k]; });
  await p.waitForTimeout(500);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', fps, '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const F = +fps, a = Math.round(+t0 * F), z = Math.round(+t1 * F);
  const st = Date.now();
  for (let i = a; i < z; i++) {
    const b64 = await p.evaluate(t => { render(t); return document.getElementById('cv').toDataURL('image/jpeg', 0.94).slice(23); }, i / F);
    if (!ff.stdin.write(Buffer.from(b64, 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if ((i - a) % 300 === 0) console.log(out, 'frame', i - a, '/', z - a, ((Date.now() - st) / 1000).toFixed(0) + 's');
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  await b.close(); console.log('done', out, ((Date.now() - st) / 1000).toFixed(0) + 's');
})();
