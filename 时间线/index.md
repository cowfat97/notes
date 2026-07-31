---
hide:
  - toc
---

# 时间线

<link rel="stylesheet" href="../_components/timeline.css">


<div class="tl-scroll">

<div class="tl-entry">
  <p class="tl-date"><a href="2026-07-30/☕-2026-07-30/">2026-07-30 · 周四 · 深圳 →</a></p>
  <p class="tl-preview">> 连续四天熬夜，腰疼。探讨了台式机 ComfyUI 远程操控方案：frp 隧道 + MCP 可行，也有 Tailscale/ZeroTier 等更轻量的替代。台式机 Codex 一直重连——Clash 代理下 WebSocket 长连接可能不稳定，但 `codex` 命令找不到，npm 全局路径没加到 PATH。LLM 课程继续推。今天早点睡。</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-07-29/☕-2026-07-29/">2026-07-29 · 周三 · 深圳 →</a></p>
  <p class="tl-preview">> 全栈 infra 日。Codex 模型被 DeepSeek 污染——config.toml 里 model_provider=custom 指向本地 DeepSeek，cc-switch-model-catalog.json 只有 DeepSeek V4 Flash/Pro 两个条目。修了 config 删了目录缓存恢复 OpenAI。ChatGPT Plus 55ai.net ¥135 代充到账。树莓派 SD 卡时好时坏——黑屏+绿灯灭，判断文件系统损坏，重刷 Raspberry Pi OS。装好 mihomo（clash）+ flowercloud 订阅，卡在 MMDB 下载（Pi 没代理下不了），Mac 下了传过去解决。frpc 配好双隧道：6002→SSH、7893→代理。allow-lan 开了，iPhone 在家直连 192.168.0.113:7893。出门走 47.93.86.20:7893 需要阿里云安全组开 7893 端口。OpenClaw 停掉。台式机 Google 扫码登录搞定。LLM 课程又推到明天——但今天搞的 infra 比上课值。</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-07-28/☕-2026-07-28/">2026-07-28 · 周二 · 深圳 →</a></p>
  <p class="tl-preview">> 台风走了，晴天。昨晚 48 段碎片、7h19m 有效睡眠，28 分，下午才缓过来。战地 5 开玩，加速器没开画面卡。Node.js 装好，ComfyUI 路径找到了——v0.28.3 便携版，Manager 已内置但需 `--enable-manager` 启动参数。Codex 配置文件之前被 DeepSeek 自定义后端污染（model_provider=custom），修了 config.toml 恢复走 OpenAI 官方。ChatGPT Plus 走 55ai.net 代充 ¥135/月，到账。文明 7 Steam 史低 ¥149 没买。耳机没试。LLM 课程再推一天到 07/29，明天不能再推了。</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-07-27/☕-2026-07-27/">2026-07-27 · 周一 · 深圳 →</a></p>
  <p class="tl-preview">> 台风第三天，熬夜难受但下午缓过来了。内存换 A2 槽解决重启问题，NVIDIA 驱动、Chrome、VSCode、Steam 全装好了。MX Master 3s 蓝牙折腾了 3 小时——能发现但握手失败，Intel 蓝牙模块兼容性问题，最后买了个有线鼠标应急。PS5 手柄蓝牙倒是秒连。Mac Clash LAN 共享给台式机当代理，配好了 ComfyUI MCP。学习计划推后一天，明天正式开始。战地 5 下好了，今晚打游戏。</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-07-26/☕-2026-07-26/">2026-07-26 · 周日 · 深圳 →</a></p>
  <p class="tl-preview">> 睡眠又烂了——31 段碎片，01:50 才睡，质量评分 37/100。跟昨天一样的问题，入睡太晚、碎片太多。需要把入睡时间提前到 23:30 之前，但执行起来总是做不到。今天搞 Windows 11 启动盘，用 dd 写到移动硬盘，等 ISO 下载。</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-07-25/☕-2026-07-25/">2026-07-25 · 周六 · 深圳 →</a></p>
  <p class="tl-preview">> 第一次装机，CPU→内存→SSD→散热→主板进机箱→电源接线→前面板跳线，全程自己对着文档一步步来。最紧张的是 CPU 放下去那一刻，最累的是理线。显卡也到了，装完通电那一刻风扇转起来的感觉很爽。搞了 2-3 小时，累但值得。明天装 Windows 11。</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-07-24/☕-2026-07-24/">2026-07-24 · 周五 · 深圳 →</a></p>
  <p class="tl-preview">> 待补</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-07-23/☕-2026-07-23/">2026-07-23 · 周四 · 深圳 →</a></p>
  <p class="tl-preview">> 梭哈</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-07-21/☕-2026-07-21/">2026-07-21 · 周二 · 深圳 →</a></p>
  <p class="tl-preview">> Google Drive MCP 卡了一下午，根因就两个：gaxios 只读小写 https_proxy、旧进程没杀干净。排查踩坑值得记。</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-07-19/☕-2026-07-19/">2026-07-19 · 周日 · 深圳 →</a></p>
  <p class="tl-preview">> 该断则断</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-07-18/☕-2026-07-18/">2026-07-18 · 周六 · 深圳 →</a></p>
  <p class="tl-preview">> 越压抑欲望越放纵</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-07-17/☕-2026-07-17/">2026-07-17 · 周五 · 深圳 →</a></p>
  <p class="tl-preview">> 光荣在于平淡，艰巨在于漫长</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-06-22/☕-2026-06-22/">2026-06-22 · 周一 · 深圳 →</a></p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-06-11/☕-2026-06-11/">2026-06-11 · 周四 · 包头 →</a></p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-06-07/☕-2026-06-07/">2026-06-07 · 周日 · 包头 →</a></p>
  <p class="tl-preview">计划终于整理干净了。方向清晰：投简历 + 面试准备是第一要务，学习是长线。</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-06-06/☕-2026-06-06/">2026-06-06 · 周六 · 包头 →</a></p>
  <p class="tl-preview">封面对比太明显了——同样的视频，老号 300 播放，新号封面好看直接不一样</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-06-04/☕-2026-06-04/">2026-06-04 · 周四 · 包头 →</a></p>
  <p class="tl-preview">目录重构后仓库结构清晰很多，后续加新内容不容易散乱。CSS 集中管理后改样式只需改一个文件。</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-06-03/☕-2026-06-03/">2026-06-03 · 周三 · 包头 →</a></p>
  <p class="tl-preview">播放量上不去不是内容问题，是账号转型阵痛。坚持一个月再看</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-06-02/☕-2026-06-02/">2026-06-02 · 周二 · 包头 →</a></p>
  <p class="tl-preview">放不下过去，永远不能进步</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-06-01/☕-2026-06-01/">2026-06-01 · 周一 · 包头 →</a></p>
  <p class="tl-preview">开启找工作的一个月</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-05-31/☕-2026-05-31/">2026-05-31 · 周日 · 包头 →</a></p>
  <p class="tl-preview">只有爱自己，才会爱别人</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-05-30/☕-2026-05-30/">2026-05-30 · 周六 · 包头 →</a></p>
  <p class="tl-preview">每个人眼里的价值不一样</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-05-26/☕-2026-05-26/">2026-05-26 · 周二 · 包头 →</a></p>
  <p class="tl-preview">人真的有意思，屁股和脸长在一起</p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-05-25/☕-2026-05-25/">2026-05-25 · 周一 · 包头 →</a></p>
</div>

<div class="tl-entry">
  <p class="tl-date"><a href="2026-05-24/☕-2026-05-24/">2026-05-24 · 周日 · 包头 →</a></p>
  <p class="tl-preview">我需要一个好故事。但是我还没想好这个关于我的故事。</p>
</div>
</div>
