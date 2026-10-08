// 生成网站海报（海报模式：只画标题、空海滩、一道大浪）：node demo/wave/poster.js <输出目录> <v或h> <时刻,…>，网站用的是 h 的 3.8 秒
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [out, ar, list] = process.argv.slice(2);
  const [w, h] = ar === 'v' ? [1080, 1920] : [1920, 1080];
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: w, height: h } });
  await p.goto(`file:///home/user/zengming/demo/wave.html?ar=${ar}&t=0`, { waitUntil: 'networkidle' });
  for (const k of list.split(',')) {
    const d = await p.evaluate(async k => {
      await document.fonts.load("500 40px Caveat"); await document.fonts.ready;
      POSTER = true;
      // 海报专用：空海滩上一道大浪，正要扑向小人
      WAVES = [{ t0: 0, dur: 10, amp: 1.05 * L.maxH, reach: L.figX - 40 }];
      render(+k); return cv.toDataURL('image/png');
    }, k);
    fs.writeFileSync(`${out}/pw_${ar}_${k}.png`, Buffer.from(d.split(',')[1], 'base64'));
  }
  await b.close();
})();
