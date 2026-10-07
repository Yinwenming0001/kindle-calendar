# Kindle 电子台历

把闲置 Kindle 变成摆在桌上的墨水屏台历：大日期 + 农历节气 + 实时天气 + 节日倒计时 + 每日一句，每天自动更新，一次设置长期不用管。

- 当前配置：常州 · 新北区（31.86°N, 119.96°E）
- 设备：Kindle 第 7 代（2014 款），分辨率 600×800（167ppi）
- 样张见 `preview_kindle7.png`

## 原理

家里不需要常开电脑。图片由 GitHub Actions 每 30 分钟在云端渲染好，发布成一个公开链接；Kindle 定时唤醒 Wi-Fi 拉取这张图并全屏显示，其余时间休眠，一天耗电约 8%。

## 目录说明

```
render_calendar.py                 图片渲染脚本
.github/workflows/calendar.yml     云端定时任务
vendor/                            农历节气库（随仓库一起上传）
kindle/extensions/dashboard_viewer Kindle 端扩展，拷进设备即可用
preview_kindle7.png                样张（600×800，第 7 代）
```

## 台历图片地址（已配置好，直接用）

```
https://yinwenming0001.github.io/kindle-calendar/calendar.png
```

- 仓库：<https://github.com/Yinwenming0001/kindle-calendar>
- 云端每 30 分钟自动重渲一次（Actions 定时任务），Pages 已开启
- 这个地址已经预先填进 `dashboard_viewer_settings.txt` 了，Kindle 端不用手改
- 浏览器打开上面那个地址应该能看到一张 600×800 的灰度台历图，看不到就等两三分钟（Pages 首次部署要一会儿）

## 第一步：搭好云端图片（已由助手完成，仅作记录）

1. 在 GitHub 新建一个 **Public** 仓库（例如 `kindle-calendar`），**不要**勾选自动生成 README
2. 上传文件——二选一：
   - **省事版**：下载本目录下的 `kindle-calendar-repo.zip`，在电脑上解压，进仓库页面点 **Add file → Upload files**，把解压出来的**所有文件和文件夹拖进去**（`.github`、`vendor`、`render_calendar.py`、`requirements.txt` 都要有，结构不能变）→ 底部点 Commit
   - **命令版**（装了 git 的话）：在本目录执行
     `git remote add origin https://github.com/<你的用户名>/kindle-calendar.git && git push -u origin master`
3. 进 **Actions** 标签页 → 左侧点 `Render Kindle Calendar` → 右侧 **Run workflow** → 等它跑完（约 1 分钟，第一次会慢些）
4. 进 **Settings → Pages** → Source 选 **Deploy from a branch** → 分支选 `gh-pages`、目录 `/ (root)` → Save
5. 拿到图片地址：`https://<你的用户名>.github.io/kindle-calendar/calendar.png`
   用浏览器打开确认能显示（打不开就等两三分钟再试，Pages 首次部署要一会儿），把这个地址记下来

> 定时任务会每 30 分钟自动重跑一次。GitHub 对免费账号的 Actions 有额度限制，这个用量远低于上限。
> 默认已按第 7 代的 600×800 出图。想换设备：仓库 Settings → Secrets and variables → Actions → Variables，加一个 `DEVICE`（`basic10`=600×800，`basic11`=1072×1448，`pw5`/`pw6`）；城市直接改 `render_calendar.py` 顶部的默认值。

## 第二步：Kindle 越狱（唯一的硬门槛）

设备已确认：**Kindle 第 7 代（代号 KT2），固件 5.12.2.2** → 用 **WatchThis**，官方兼容表里 KT2 + 5.12.2.2 是明确列出的组合，payload 与设备精确匹配。

**完整操作步骤见 [`JAILBREAK.md`](JAILBREAK.md)**，逐条勾选的清单（备份、删升级包、进演示模式、秘密手势、`.demo` 文件夹、hotfix、装 KUAL、封 OTA、卡点排查），建议在电脑上打开边看边做。

三个最容易翻车的点：

1. **设备代号是 KT2**，payload 必须是 `KT2-5.12.2.2.zip`（KT3 是 Kindle 8、KT4 是 Kindle 10），而且**这个 zip 不能解压**，原样拷进 `.demo`
2. **第 17 步 Kindle 7 要点的不是 Help & User Guides，而是商店购物车图标**——网上多数教程写的是新机型的做法
3. **装插件必须选普通版，不要选 HF/armhf 版**——HF 是 5.16.3 以上固件才用的，5.12.2.2 装不上

补充说明：5.12.2.2 是 Kindle 7 的最终固件，升不上去也不用升；设备 2019 年就已停止支持，越狱后被 OTA 冲掉的风险很低，但仍建议做完文档第 8 节的封禁动作。

## 第三步：装上端扩展并启动

1. USB 连 Kindle，把 `dashboard_viewer_kindle_install.zip` 解压出来的 `extensions` 文件夹**整个拖到 Kindle 根目录**
   （如果根目录已经有 `extensions`——装 MRPI 后就会有——就只把里面的 `dashboard_viewer` 文件夹拷进去，别覆盖整个 `extensions`）
   结果应该是：`Kindle盘符:/extensions/dashboard_viewer/`
2. 用 **VS Code / 记事本++ / vim** 打开 `Kindle盘符:/extensions/dashboard_viewer/dashboard_viewer_settings.txt`，确认 `url=` 后面是上面那个地址（**默认已经填好了，一般不用动**）
   ⚠️ **不要用 Windows 自带记事本改**，它会把换行符改成 CRLF，脚本会失效
3. 安全弹出 → 打开 KUAL → 「台历 Dashboard」→「启动台历」
4. 等几秒屏幕刷新出台历就成功了。之后白天 30 分钟自动刷新一次，晚上 23:00–07:00 两小时一次

> 设备重启后需要重新在 KUAL 里点一次「启动台历」。
> 一直刷不出图：先点「立即刷新一次」看屏幕提示，再看 `extensions/dashboard_viewer/dashboard_viewer.log` 里的报错。

## 想调整什么

| 需求 | 改哪里 |
| --- | --- |
| 换城市 | `render_calendar.py` 里 `--city/--lat/--lon` 默认值 |
| 换设备尺寸 | 默认 `basic10`=600×800（第 7 代）；新款加 `--device basic11`（1072×1448） |
| 换每日一句 | `render_calendar.py` 里的 `QUOTES` 列表 |
| 日期大小 | 加 `--datefactor 0.8`（更小）或 `1.3`（更醒目），默认 `1.0` |
| 换刷新频率 | Kindle 上 `dashboard_viewer_settings.txt` 的 `dayinterval`（秒） |
| 本地预览效果 | `./.venv/bin/python render_calendar.py --out preview_kindle7.png` |

版式是自动排的：先测量每块文字高度，再把剩余空间均分成间距，所以换分辨率、换长短句子都不会出现大块空白。

日期右侧会自动配一个天气图标（晴 / 多云 / 阴 / 雾 / 雨 / 雪 / 雷，按实时天气码匹配），用来填平右边留白。七种图标的样子见 `preview_icons.png`。

## Kindle 第 7 代（2014 款）特别注意

这台机器有十二年了，有三点和新机器不一样：

1. **没有背光**：屏幕不发光，全靠环境光。台历要放在窗边、台灯下这类有光的位置，晚上关灯后是看不见的
2. **电池多半已经老化**：十年前的锂电池衰减严重，持续常亮可能撑不到一天。建议直接插着 USB 电源当固定台历用；如果要用电池，把 `dashboard_viewer_settings.txt` 里的 `dayinterval` 调到 `3600`（1 小时一刷）会省不少电
3. **Wi-Fi 只支持 2.4GHz**：如果家里路由器开了"双频合一"，Kindle 可能连不上或时断时续。建议在路由器里给 2.4GHz 单独起一个名字，让 Kindle 连那个

## 备选方案（不打算用 GitHub 时）

**离线模式**：Kindle 端脚本在「没配 url」或「下载失败」时，会自动改显 Kindle 根目录的 `calendar.png`。用法：

1. 电脑上跑一次 `./.venv/bin/python render_calendar.py --out calendar.png`（或在 GitHub 仓库手动跑一次 Actions 下载产物）
2. 把 `calendar.png` 拷到 Kindle 根目录
3. KUAL → 台历 →「立即刷新一次」

内容一样，只是要手动更新一次，每天也就几十秒。越狱装好之后随时可以切回自动模式。

**EPUB 封面法**（连越狱都不做）：把日历图片做成 EPUB 的封面推送到 Kindle，打开后锁屏就显示这张图。缺点是不会自动更新，且广告版 Kindle 会隐藏「显示当前阅读封面」这个设置。
路径：Calibre 把 PNG 转成封面 EPUB → 发送到 Kindle → 设置里打开「显示当前阅读封面」。

## 注意事项

- 图片是 8 位灰度 PNG，正是 Kindle 屏幕原生格式，不需要额外转换
- 屏幕一直常亮需要阻止屏保，扩展里已处理；停止台历后会自动恢复
- 如果台历停止后 Kindle 不休眠，在 KUAL 里点一次「停止台历」即可
- 日志在 `Kindle盘符:/extensions/dashboard_viewer/dashboard_viewer.log`，出问题先看它
