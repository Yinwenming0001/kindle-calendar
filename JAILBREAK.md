# Kindle 第 7 代（代号 KT2）· 固件 5.12.2.2 越狱步骤

> 首选方法：**WatchThis**。官方兼容表里 **KT2 + 5.12.2.2** 是被明确列出的组合，payload 与设备精确匹配，成功率最高。
> 备选方法：**LanguageBreak**（见文末「方案 B」），万一 A 卡住再换。
>
> ⚠️ 整个过程会**清空设备所有数据**，且有一定变砖风险。逐条勾选、别跳步、别自创操作。

## 零、先弄清两个事实

1. **5.12.2.2 是 Kindle 7 的最终固件**（2022 年 1 月发布，之后再没有更新）。所以：
   - 不用纠结"要不要先升到 5.16.2"——这台机器升不上去，就在这个版本上越狱
   - 反过来说，亚马逊早已停止给 K7 推送固件（2019 年 10 月停止支持），**越狱后被 OTA 冲掉的风险很低**，但仍然建议做第 7 节的封锁动作
2. **设备代号是 KT2**。下载越狱文件时别搞混：
   - **KT2 = Kindle 7（你的机器）**
   - KT3 = Kindle 8，KT4 = Kindle 10，PW2 = Kindle Paperwhite 2
   - 用错 payload 会失败，可能要重来

## 一、下载文件

下载 **watchthis-jailbreak-r03.zip**（约 40MB）：

- 书伴教程页（内含百度网盘 / Mega 链接，中文说明最全）：<https://bookfere.com/post/970.html>
- 校验码（下完对照一下，防止文件损坏）：
  - MD5 `d73a76dab7824840972ad51f377dede1`
  - SHA1 `5e828629bb9635e68cbc3221b344bb0902577c7f`

在**电脑上**解压（不要在 Kindle 上解压），得到 `watchthis-release` 文件夹，进入：

```
watchthis-release/KT2/5.12.2.2/
```

把这三个文件挑出来放桌面备用（后面要拷）：

| 文件 | 说明 |
| --- | --- |
| `KT2-5.12.2.2.zip` | **不要再解压**，原样拷进去 |
| `demo.json` | 配置脚本 |
| `Update_hotfix_watchthis_custom.bin` | 收尾用的热修复补丁 |

## 二、开始前必做

- [ ] USB 连电脑，把 Kindle 根目录的 `documents` 文件夹**整个备份**到电脑（书、笔记、标注都在里面）
- [ ] **删掉根目录所有 `.bin` 文件**，以及 `update.bin.tmp.partial`——这是待装的升级包，留着会在重启时被装上，直接毁掉越狱
- [ ] 如果设了锁屏密码，先移除（忘记密码可在输入框输 `111222777` 重置，但会清空资料）
- [ ] 电量 50% 以上，**建议全程插着电操作**（这台机器十二年了，电池大概率已衰减，中途断电最麻烦）

## 三、进演示模式

1. Kindle 上依次点：**设置 → 设备选项 → 重置**，重置设备
2. 重置时选语言：**English → United Kingdom** → Next
3. 出现 WiFi 设置 → 点 **Set up later** → **Finish Later** → 跳过功能指引
4. 顶部搜索框输入 `;enter_demo` 回车
5. **设置 → Device Options → Restart** 重启，重启后进入演示模式
6. 「Register This Demo」界面弹出 WiFi 设置 → 点 **X** 跳过
7. 出现三项信息的表单 → 随便填字符 → **CONTINUE**
8. 「Fetching available demo types」→ 点 **Skip** → 选 **standard**
9. 「Demo Mode: Add Content」→ 点 **Done**，等它自动配置（可能白屏一阵）
10. 进入屏保 → 点一下屏幕，出现「CONFIGURE DEVICE」错误提示 → 用**秘密手势**跳过
11. 搜索框输入 `;demo` 回车 → 点 **Sideload Content** → 界面提示连 USB

**秘密手势**（不同机器手感不一样，可能需要试十几次，三种都试）：

- 双指轻点屏幕右下角，紧接着单指从右向左水平划一下
- 双指同时按住右下角，右边手指抬起，紧接着左边手指向左划
- 双指同时按住右下角，直接向左划

> 后面只要再出现「CONFIGURE DEVICE」或「展示机无内容或未连接网络」，都用这个手势跳过。

## 四、执行越狱

12. USB 连电脑，在 **Kindle 根目录**（和 `documents` 同级）新建一个名为 `.demo` 的文件夹（**名字前面有个点**）
    - macOS：打开终端 → 输入 `cd ` + 空格 → 把 Kindle 磁盘**拖进终端** → 回车 → 再输入
      `mkdir .demo && open .demo` → 回车
    - Windows：命令提示符里切到 Kindle 盘符（如 `E:`）→ `mkdir .demo && start .demo`
    - 看不到点开头的文件夹：macOS 按 `Command + Shift + .` 切换显示
13. 把 `KT2-5.12.2.2.zip`（**保持压缩包状态，别解压**）和 `demo.json` 拷进 `.demo`
14. 在 `.demo` 里再建一个名为 `goodreads` 的**空文件夹**（里面不放任何东西）

最终结构必须是这样：

```
Kindle 磁盘
└── .demo
    ├── KT2-5.12.2.2.zip
    ├── demo.json
    └── goodreads/        ← 空文件夹
```

15. 安全弹出 USB → 回到 Kindle 点 **Done**（脚本静默安装，没有提示）
16. 点 **Exit** 退出演示菜单
    > 如果点 Exit 后弹「Application Error」：按住电源键 40 秒硬重启 → 重启后搜 `;demo` 重进演示菜单 → 不连 USB，再点一次 **Sideload Content → Done** → **Exit**
17. **点商店购物车图标（store）** ← 这是 Kindle 7 / KT2 专属的一步，别按别的机型教程去点 Help & User Guides
18. 设备重启，**启动过程中屏幕上会滚过一段脚本日志**——看到就说明越狱脚本跑起来了

## 五、装热修复补丁并退出演示模式

19. 重启后会再次进入演示模式 → 用秘密手势进主界面
20. 搜索框输入 `;uzb` 回车（演示模式下打开 USB 传文件）→ USB 连电脑
21. 把 `Update_hotfix_watchthis_custom.bin` 拷到 **Kindle 根目录**
22. 安全弹出 → 搜索框输入 `;dsts` 回车进设置
23. **Device Options → Update Your Kindle → OK**
24. 自动重启，**这次会退出演示模式进入正常界面**，越狱完成

## 六、验证 + 切回中文

- [ ] USB 连电脑，看 Kindle 根目录有没有出现 **`mkk`** 文件夹 → 有就是成功
- [ ] 搜索框输入 `;log runme` 回车 → 左上角出现 **No user script found.** → 正常
- [ ] 切回中文：**Setting → Language & Dictionaries → Language** → 滑到底部选 **简体中文** → 两次 OK → 自动重启

## 七、装 MRPI 和 KUAL（台历要靠它们启动）

1. 下载插件包 **kual-mrinstaller-1.7.N-xxx.tar.xz**（书伴插件下载页：<https://bookfere.com/post/311.html>）
   - **必须是普通版，不要下 HF / armhf 版**——HF 是 5.16.3 以上固件才用的，5.12.2.2 装不上
   - 解压**务必用 7-Zip（Windows）或 Keka / 命令行 `tar`（macOS）**，用 WinZip 解压 `.xz` 会损坏文件，导致后面报 "MRPI is not installed"
2. 解压得到 `extensions` 和 `mrpackages` 两个文件夹 → 拷到 Kindle 根目录（根目录已有 `extensions` 就把里面的内容**合并**进去，别整个覆盖）
3. 下载 KUAL（Kindle 7 走**方法 2**）：`KUAL-v2.x.xx-xxx.tar.xz` → 解压出 `Update_KUALBooklet_v2.x.xx_install.bin` → 放进 Kindle 根目录的 `mrpackages` 文件夹
4. 安全弹出 → 搜索框输入 `;log mrpi` 回车 → 自动安装
5. 装完 Kindle 书库里会出现一本 **KUAL**，点开就是插件菜单

## 八、封死自动更新

- 越狱后**永远不要**在 Kindle 上点「更新您的 Kindle」（除非装上面那个 hotfix）
- 平时留意根目录有没有冒出 `.bin` 文件，有就删
- 最省事的做法：**长期开飞行模式**（台历只需要定时唤醒 Wi-Fi 拉图，脚本会自己处理；如果发现拉不到图，就改用「连着 Wi-Fi 但根目录有 .bin 就删」的办法）
- 想彻底封死：KUAL 里装 `renameotabin` 扩展，点一次即可永久屏蔽

---

## 卡住了怎么办

| 现象 | 怎么办 |
| --- | --- |
| 秘密手势没反应 | 三种手法轮流试十几次；或在根目录建一个名为 `DONT_CHECK_BATTERY` 的**空文件**，再输 `;demo` 进演示模式 |
| 点 Done 后没任何反应 | 正常，脚本是静默安装。继续点 Exit，按第 17 步走 |
| 点 Exit 后 Application Error | 按住电源键 40 秒硬重启 → `;demo` → Sideload Content → Done → Exit（不连 USB） |
| 重启后没看到脚本日志 | payload 拷错了，确认是 `KT2-5.12.2.2.zip` 且**没有解压**，`.demo/goodreads` 是空文件夹 |
| 弹出「Collecting Debug Info」 | 说明前面某步有误，重置设备从头再来 |
| 演示模式里要重置设备 | 输 `;uzb` → USB 连电脑 → 根目录建空文件 `DO_FACTORY_RESTORE`（无扩展名）→ 长按电源键重启 |
| 越狱后 WiFi 异常 | 搜索框 `;demo` → 点右边的 **Yes** → 设备自动重置进正常模式 → 重装一次 hotfix |
| 装插件提示 MRPI is not installed | 换 7-Zip / Keka 重新解压 MRPI 包，确认 `extensions` 和 `mrpackages` 都拷到了根目录 |

## 方案 B：LanguageBreak（A 走不通时用）

- 下载：<https://github.com/notmarek/LanguageBreak/releases/latest> → 取 `LanguageBreak.tar.gz`
- 适用：固件 ≤ 5.16.2.1.1 全系（含 5.12.2.2）。但作者明确说"在 5.16.2 附近效果最好"，你这台升不上去，所以成功率略低于 WatchThis
- 流程差异：`;enter_demo` 进演示 → `;demo` → 导入内容 → 拷 `LanguageBreak` 文件夹里的 `documents`、`DONT_CHECK_BATTERY`、`jb`、`patchedUks.sqsh` 四项到根目录 → 销售设备 → **屏幕出现"按电源键"示意图时立刻连电脑再拷一次（窗口只有十几秒）** → 按电源键 → 语言选 **简体中文** → 日志滚动即成功 → 装 `update_hotfix_languagebreak-zh-Hans-CN.bin`
- 官方 README：<https://github.com/notmarek/LanguageBreak>
