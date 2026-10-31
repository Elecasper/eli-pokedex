# Eli的宝可梦图鉴 · 中文文学书架

- [打开图鉴](https://elecasper.github.io/eli-pokedex/)
- [打开中文书架](https://elecasper.github.io/eli-pokedex/books/)
- [离线图鉴v2](https://elecasper.github.io/eli-pokedex/eli-pokedex-offline-v2.zip)
- [12本简体文学打包](https://elecasper.github.io/eli-pokedex/books/chinese-literature-12-zh-hans.zip)

免费纯静态页面，无账号、广告或应用内追踪；不需要服务器和付费服务。打开页面后，图鉴数据、图像、搜索均无需额外联网。中文书架只在主动点击下载时获取EPUB。

## 图鉴v2

全国百科扩展为1–9世代1025种、310条特殊形态资料。地点查询仍限GBA／NDS／3DS的22个游戏版本，**不是覆盖所有世代所有作品的完整捕捉地图**。

新增：按作品的升级／学习器／教学／遗传招式表、较新中文招式和特性作用说明、常见形态切换、性别／蛋群／孵化周期／捕获度／努力值。捕获度不是百分比。基础资料按所选世代，较新中文作用文本与招式威力等不冒充逐版历史机制。

PKHeX固定快照补充4117条3DS区域级记录，包含ORAS普通野外，而不再只有群聚记录。**区域级资料不提供全部概率、时段、剧情解锁和坐标**，未可靠换算的概率继续显示「—」，不是0%。没有记录不等于无法获得，旧活动及联机条件也不保证目前仍可达成。

全国百科模式不混合游戏地点。新世代种类在旧作品不能新标记收集；旧版已保存的误标记仍允许取消。原v1收集记录与备份格式继续兼容，按游戏版本与种类保存到当前浏览器，不上传云端，也不细分形态。

## 中文书架

12本中文小说、散文和古典文学，来自Project Gutenberg明确标为美国公版的原文底本；OpenCC繁简转换，未做校勘，保留完整许可与来源。不是现代校注本，其他地区请按所在地版权期限判断。

收录《红楼梦》（120回底本）、《西游记》（100回）、《三国演义》（120回）、《水浒传》（70回底本）、《儒林外史》《聊斋志异》《镜花缘》《老残游记》，以及鲁迅《呐喊》《彷徨》《朝花夕拾》《野草》。不把七十回《水浒传》冒称一百二十回本。

较新中文小说只给起点、微信读书的正版入口；免费、完结和下载权限以平台为准。不抓取付费正文，不提供盗版、网盘合集或DRM绕过。

EPUB先保存，再用Send to Kindle上传；ZIP需先解压，不能把ZIP或EPUB直接用USB当作Kindle原生格式拷入。

## 手机

图鉴、书架和主站均检查320／360／390／428px宽度，无横向溢出。独立页面主要触控控件高度至少44px，搜索输入16px以避免iOS自动放大。图鉴列表与详情分屏，招式表在详情内滚动；书架支持书名、作者、篇名关键词搜索与分类。

图鉴离线包解压后用支持本地HTML的浏览器打开，电脑推荐Chrome。手机优先使用在线版。更换设备或清除浏览器数据前请导出收集记录。

## 来源与许可

- PokéAPI CSV：`6b8db7f3cb31cfaa37cb74e5c3edff124bcba5ce`（BSD-3-Clause）。
- PokéAPI sprites：`1dd55c0436d2a5b6e324c0b780e1b1b416fbfb64`。图像与角色、商标权利仍属于原权利人。
- PKHeX：`61da5c6f68fbc0f8fa5b09212dc8329169a830db`（GPL-3.0），原始补充表、格式源码、中文地点表及完整许可在 `third-party/pkhex/`。
- 中文文学底本、来源URL、SHA-256、底本回数和转换说明在 `books/sources.json`，PG完整许可保留在每本EPUB内。
- 功能参考《口袋图鉴》的按版本查询，自行实现界面，不复制商业App数据、代码或账号内容。

v2整体组合、补充解析器与新增代码遵守GPL-3.0。原v1代码的MIT声明保留在 `LICENSE-MIT-original-v1`；第三方声明见 `sources.txt`。非官方粉丝作品，无原权利人的背书。

## 维护

浏览器端是原生HTML/CSS/JavaScript，数据和图像内嵌。开发构建才需联网下载固定快照；不要把“latest”直接当成已核对数据。

```sh
python3 src/build-eli-pokedex-v2.py
```

生成文件位于 `src/`；检查后将生成的HTML更新为根目录 `index.html`。脚本拒绝覆盖已有成品，下一轮应另存新版本。`src/eli-pokedex-data-v1.json` 保留为v2的固定基线；详细资料模块在构建时内联，不产生运行时网络请求。

中文文学构建需要 `opencc-python-reimplemented`：

```sh
python3 -m venv /tmp/eli-books-venv
/tmp/eli-books-venv/bin/pip install opencc-python-reimplemented
/tmp/eli-books-venv/bin/python3 src/build-eli-chinese-books-v1.py
```

更新前需重新核对版权、版本与底本。不要覆盖用户的原文件，不要上传账号、凭据、个人书库或未授权小说。
