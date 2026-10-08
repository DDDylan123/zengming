# LibTV 配音与配乐：做法与踩坑

## 基本调用

1. `doctor` → `target_project`（同一部片子用同一个画布项目）。
2. `search_models` 找模型 → `get_model` 读实时 schema，别凭记忆编参数。
3. `create_node`（音频生成节点，填 prompt/参数）→ `update_node` 运行 → `task_status` 回读 → `inspect_media` 拿到音频 URL → `curl` 下载。
4. 付费调用用稳定的幂等键；提交不等于完成，先回读再决定是否重试。

## 实测价格（积分，以用户积分明细为准）

| 用途 | 模型 | 价格 |
|---|---|---|
| 旁白（整篇一次） | Seed Audio 1.0 | 约 2 / 次 |
| 旁白（单句） | Minimax Speech | 约 1 / 条 |
| 旁白（单句） | Eleven V3 TTS | 约 19 / 条 |
| 音色设计 | MiniMax Voice Design | 约 33 |
| 配乐 3 分钟 | Eleven Music V3 | 约 350 |

生成前先用 `libtv-cost-check` 技能报价，大额（配乐）先得到用户点头。

## 配音

- 先出 2–3 个同一句的试听版本。用户对男声的常见否决是"太娘"——需要的是低沉、有年纪感（如"50 岁左右金融高管"）。系统预设音色普遍偏年轻，靠调参压不下去；换引擎或换演法（新闻片播音腔这类有强风格描述的方案更容易出低沉声音）。
- Seed Audio 用文字描述音色，例：
  > 1930 年代老上海新闻片男播音员，四五十岁，低沉洪亮，民国国语腔，字正腔圆，语速稍快，句尾上扬带感叹，像旧新闻片解说。
- **整篇一次生成**：所有台词放进一次请求，要求"每句之间停顿一秒"。原因：
  - 分句各自生成，每句的音色都会漂（用户："听着像换了人"）。
  - 同时提交 20 个任务会撞并发上限，18 个失败；一次最多 2–3 个并行。
- 切分：`python3 scripts/split_vo.py take.mp3 vo-lines.json out_dir`。先 `silencedetect` 找候选停顿，再用动态规划让每句时长贴近"字数 ÷ 语速"，长停顿加分。输出 `NN.mp3`（已做老电视处理）和 `meta.json`。打印的 `exp`（预期时长）和实际时长差太多的句子，最可能切错。
- 老电视处理链：两级 300 Hz 高通 + 两级 3.6 kHz 低通 → 压缩 → tanh 饱和 → 0.7 Hz/7 Hz 颤音（磁带抖动）→ 22 ms 短回声 → 粉噪 + 50 Hz 嗡声 → 限幅。单文件用 `scripts/old_tv.sh`。

## 配乐

- Eleven Music V3：能定时长、能按时间段写结构，适合跟画面对拍。Mureka 偏歌曲、不控时长。
- 提示词骨架（英文效果更稳）：
  > Instrumental only, no vocals. 1930s hot jazz cartoon score, scratchy 78rpm record, small band: tuba, banjo, clarinet, muted trumpet, brushes, honky-tonk piano. Structure: 0:00–0:05 fanfare title sting; 0:05–0:30 bouncy walking tempo; 0:30–0:55 accelerating, frantic; 0:55–1:30 slow, plodding, one grain at a time; 1:30–1:50 heavy lumbering then sudden stop; 1:50–2:10 sparse solo piano, fading; 2:10–2:20 final "ta-da" button.
- 时长选片长 +20–40 秒，留余量；旁白段落 `AU.bus` 自动压到 0.4。

## 云端网络

- 下载生成结果：放行 `libtv-res.liblib.art`。
- 上传参考文件：放行 `libtv-resource-prod.oss-accelerate.aliyuncs.com`。
- 被拦（403）时读 `read_documentation` 的 `environment.network` 页，让用户在环境设置里加白名单。

## 已知限制

- 生成出来的音频节点不能再连到另一个生成节点当参考（API 报"action 组合不允许"），所以"拿上一版声音做克隆"走不通。
- 音色设计的结果不能在其他 TTS 模型里复用。
- 换一句台词就整篇重录（2 积分），比单句补录便宜且声音一致。
