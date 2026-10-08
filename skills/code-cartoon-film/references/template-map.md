# film-template.html 结构图

模板就是《百分之二》成片（约 1450 行）。改新片时按下面的顺序动，行号是近似值，用 `grep -n` 定位。

| 区块 | 符号 | 做新片时 |
|---|---|---|
| 页头 | `<title>`、Google Fonts 链接 | 改片名；换字体后要截图验字形 |
| 许可 | 文件头 lemo-opuscar MIT 注释 | **保留** |
| 基础 | `TAU`、`mulberry`、`hash`、`BEAT=.5`（120 BPM）、`q(t)` 一拍两格、`breath(t)` | 一般不动 |
| 配色 | `P`（灰阶）、`ACC`（唯一强调色） | 可换强调色，但只用在关键数字上 |
| 字体 | `ZH_TITLE`、`ZH_SUB`、`ZH_CARD`（字卡粗宋 900）、`LAT` | |
| 网点 | `dotsPat(col, step, r)` | 灰面用网点，不用平涂彩色 |
| 描线引擎 | `push/pop/translate/rotate/scale`、`shape()`、`spline()`、`noodle()`、`ribbon()`、`union()`、`wtext()`；`S.boil` 每 1/12 秒换一次抖动 | 不动，直接用来画新角色 |
| 零件 | `pieEye`、`brow`、`mouth`、`glove`、`shoe`、`sweat`、`qmark` | 这些偏参考片语法，新角色尽量少用 `glove`/`pieEye` |
| 角色 | `walker(p)`、`LOOK`/`LOOKS`（B/C/D 造型）、`hoseLegs`、`hoseArm`、`face`、`robot(p)`、`pen()` | **重做**：新片的主角/搭档/AI 角色 |
| 样张 | `SHOT_SAMPLE(t)`，`?sample=1&look=X` | 用来出 3–4 张人物样张 |
| 道具/场景 | `road`、`milestone`、`lamp`、`car`、`computer`、`phone`、`newspaper`、`hourglass`、`hangSign`、`log`、`tinyLab` | 换成新片的隐喻道具 |
| 字卡 | `sunburst`、`fatTitle`、`wrapZH(gg,text,maxW)`、`subPlate(gg,text,cx,cy,size)` | 字幕调用在 `render()` 里：`size 60, y 990` |
| 背景 | `wash`、`paintSky`、`drawSky`、`blankPaper` | |
| 旁白 | `VO = [[开始秒, 字幕], …]`、`VO_META`（真实时长，由 split_vo.py 的 meta.json 粘贴）、`STORY_DUR` | 新片的台词与时间 |
| 时间轴 | `WARP`、`toFilm(story)`、`toStory(film)`、`DUR` | 不动。画面按"故事时间"写，旁白真实时长变了会自动伸缩 |
| 分镜 | `SHOTS = [[开始秒,'名字'],…]`、`SHOT = { title(t){…}, open(t){…}, … }`、`heroX(t)`、`world(cam,t)` | **主体工作**：每场一个函数，接收故事时间 t，用 `setCam(x,y,z)` 移镜头 |
| 胶片后期 | `GATE`（4:3 片门 240..1680）、`post(t, jump)`、`GRAIN` | 一般不动；切镜时 `jump` 让画面跳一下 |
| 渲染入口 | `render(T)`：T 是影片时间 → `toStory` → `SHOT[...]` → 字幕 → `post` | |
| 声音事件 | `EV`（`score()` 里按故事时间排好的 `{t,k,…}`）、`PLAY[k]` 合成器 | 拟音保留，按新片改时间点 |
| 配乐 | `USE_MUSIC`、`BAND`（有 music.mp3 时静音的乐器种类）、`startMusic(T, rate)`、`stopMusic` | 放 `music.mp3` 即可 |
| 旁白播放 | `VOBUF` 从 `vo/NN.mp3` 加载，旁白时 `AU.bus` 压到 0.4 | |
| 播放器 | `SPEEDS=[1,1.5,2,3]`、`setSpeed`、`seekTo`、`#src` 原访谈按钮（`T >= toFilm(片尾秒)` 时显示）、`?t=` 跳转 | 改 `#src` 的链接与出现时间 |
| 测试钩子 | `window.__film = { render, DUR, VO, SHOTS }`、`window.READY` | contact_sheet.mjs 依赖它们，保留 |

## 写一场戏的套路

```js
// SHOT 对象里的一场（节选自模板的沙漏戏）
glass(t) {
  const gx = 3720, gy = roadY(gx) + 4;
  const push1 = eio(seg(t, 69.4, 71.0)) * (1 - eio(seg(t, 76.8, 78.0)));   // 推近 → 拉回
  const camW = { x: gx - 160, y: gy - 380, z: .74 }, camN = { x: gx, y: gy - 330, z: 2.6 };
  const cam = { x: lerp(camW.x, camN.x, push1), y: lerp(camW.y, camN.y, push1), z: lerp(camW.z, camN.z, push1) };
  world(cam, t);                       // 同一个世界：路、天空
  const pour = seg(t, 63.8, 68.0);     // seg(t,a,b) = 区间进度 0..1
  hourglass({ x: gx, y: gy, t, top: Math.max(.15, eo(pour)), bot: .08 + seg(t, 56, 90) * .14, breathe: breath(t), … });
  …
},
```

缓动工具：`seg`（区间进度）、`eio`/`eo`（缓入缓出 / 缓出）、`back`（回弹）、`lerp`、`clamp`。

- 所有动画只依赖 `t`（不存状态），这样能拖动、倍速、逐帧截图。
- 角色动作"一拍两格"：用 `q(t)` 把时间量化到 12 fps，线条抖动也按 12 fps 换。
- 镜头跟主角走，不要每场重置世界——"一个世界"靠这个。
