# Eli的宝可梦图鉴

- [打开图鉴](https://elecasper.github.io/eli-pokedex/)
- [存档类型查看器（GBA / NDS，多语言名称）](https://elecasper.github.io/eli-pokedex/save-types/)
- [3DS：GBA／NDS桌面图标中文教程](https://elecasper.github.io/eli-pokedex/handheld/)
- [离线图鉴v3.2](https://elecasper.github.io/eli-pokedex/eli-pokedex-offline-v3.2.zip)
- [外部图书入口与风险提示](https://elecasper.github.io/eli-pokedex/books/)

免费纯静态页面，无账号、广告和应用内追踪。数据与图像内嵌，不在运行时请求外部API。工具下载仅在用户主动点击后访问作者公开链接；不提供商业ROM、成品游戏CIA或密钥。

## v3调整

v3.1：默认按全国图鉴编号升序排列；切换平台或作品不重置为常用优先，仍可手动切换排序。

- 手机首屏只留平台、作品、搜索和物种范围。更多筛选、长说明、图鉴描述按需展开；招式改为可展开条目，不再挤大表格。
- GBA／NDS／3DS之外新增NS分类，共32个作品版本，另有全国百科。保留1–9世代1025种、310条特殊形态参考。
- 删除“本作已收集”筛选和收集操作界面；不主动删除或改写浏览器中的旧记录，说明窗口仍可按原schema导出旧记录。
- “本作收录的宝可梦”使用独立的**物种支持名单**，不再把“有地点记录”误当“本作有此物种”。
- 原图书展示、EPUB和文学打包下载从当前站点撤下。`books/`改为带风险提示的外部入口页。经用户明确要求提供`https://z-lib.id/`外链，点击继续后在新标签页打开；不标为官方认证，不嵌入或代理登录，不处理账号、付款与第三方下载。域名仍未核验；历史风险报道保留。不承诺清除其他人的缓存、已下载文件或Git历史。

## 名单的含义

旧作按各版可支持的全国编号范围，而非地区图鉴编号：GBA为386，NDS按493／649，XY及ORAS为721，太阳／月亮802，究极日／月807。

NS按固定PKHeX PersonalTable的物种支持判断：Let's Go153、剑盾664、晶灿钻石／明亮珍珠493、传说阿尔宙斯242、朱紫733、传说Z-A364。包括当前快照的更新／DLC兼容及交换／迁入等物种，**不表示都能在本体单机野外捕捉，也不保证过期活动现在仍可取得**。部分物种仅地区形态可用；默认形态的通用资料不冒充本作实际形态。名单不等于完整地区图鉴编号表。

解析会遵守各表的最大物种编号，再检查默认形态及额外形态的存在位；尤其不能把Z-A表尾的形态行误读成1001号之后的新物种。Let's Go与BDSP采用其上游`IsSpeciesInGame`规则。

## 地点与资料边界

原22个GBA／NDS／3DS版本的地点、概率和条件完整保留；包括4117条3DS区域级补充。新增Let's Go、剑盾及其DLC的公开遭遇表47316条归并记录。NS新表暂不换算概率，显示“待核”；**不会把不同天气、剧情或极巨巢穴条件的概率相加**。

朱紫、阿尔宙斯、BDSP、Z-A本轮增加的是支持名单与源中已有的学习资料，地点仍待补。没有地点不等于无法获得；未收录与缺地点会分别提示。相同地点、方式、等级、概率的多组条件可以合并展示，组间是“或”，不是同时满足。

基础种族值／属性／特性名保留世代差异；招式数值及作用描述为较新参考，不是所有作品历史机制的完整重建。传说系列和Let's Go不套用常规特性／培育系统；这里不是战斗模拟器。形态、进化条件、旧活动状态也不宣传全部齐全。

精灵PNG仅裁透明边缘以改善小屏可读性，不替换角色或像素。缺失形态图继续明确标出。

## 存档类型查看器

新增`save-types/`独立工具。输入简繁中文、英文、已有日文别名、四位游戏编号或校验值，查询GBA/NDS原版存档类型、本体容量和已确认的RTC需求。共10,717条版本元数据，9,902条有明确类型。中日文别名不是全覆盖；无记录显示待核验，不套用相似游戏，更不把汉化／改版当原版实测。编号可能跨平台复用，需先确认GBA/NDS。

详情与全部固定来源见`save-types/README.md`和`sources.json`；对应输入、类型解析源码和许可在`third-party/save-types/`。页面内嵌数据，不上传或修改游戏／存档。图鉴“说明”及掌机教程“存档”页有入口。

## 主机教程

- GBA独立图标：Windows上的NSUI Beta28用自己的合法GBA备份制作CIA，再由FBI安装到3DS HOME；不是提供任天堂发行的成品移植。
- NDS独立图标：Universal-Updater安装ndsForwarder，再从Homebrew Launcher的NDS Forwarder Generator为现有.nds生成入口。原文件和路径仍需保留，不是把NDS变成原生3DS游戏。
- open_agb_firm继续作为原生GBA多游戏菜单方案；单独讲清VC、NDS及原生GBA的存档边界。

中文步骤依据Hacks Guide Wiki和作者文档整理；没有在用户主机上实测。NSUI正式支持Windows，未承诺Mac原生运行。

## 手机验证

独立Chrome在320／360／390／428px宽度检查列表、四个详情页、筛选、说明及四个教程页；无整页或详情横向溢出。主要触控控件至少44px，输入框16px。另检查桌面布局。**这是浏览器视口模拟，不是手机或掌机实测。**

## 来源与许可

- PokéAPI CSV：`6b8db7f3cb31cfaa37cb74e5c3edff124bcba5ce`，BSD-3-Clause。
- Sprites：`1dd55c0436d2a5b6e324c0b780e1b1b416fbfb64`；图像、角色、商标权利属于原权利人。
- PKHeX：`61da5c6f68fbc0f8fa5b09212dc8329169a830db`，GPL-3.0。输入字节表、PersonalInfo／PersonalTable规则、最大编号、地点对照与原有区域解析源码保留于`third-party/pkhex/`。
- 完整出处、风险报道和教程来源见`sources.txt`及教程页面。

整体组合及新增代码按GPL-3.0提供。原v1的MIT声明保留于`LICENSE-MIT-original-v1`。非官方爱好者资料站，不复制商业图鉴App的数据、账号或代码。

## 维护与构建

```sh
python3 -m venv /tmp/eli-dex-build
/tmp/eli-dex-build/bin/pip install Pillow
/tmp/eli-dex-build/bin/python3 src/build-eli-pokedex-v3.py
/tmp/eli-dex-build/bin/python3 src/test-eli-pokedex-v3.py
```

`src/dex-base-v2.json.gz`是固定v2数据基线，保留历史世代差异。脚本仅用结构化字节读取PKHeX数据，不执行上游C#或不可信pickle。优先读取随仓库提供的PKHeX输入；其余CSV首次构建从固定提交下载到`/tmp/eli-pokedex-source/csv/`。需要联网的只有开发构建，生成页面本身不调用网络API。

脚本拒绝覆盖已有成品：先另存、归档或换版本，再生成。生成文件在`src/`；复核后才更新根目录`index.html`与`data.json`。不要把浏览器私有记录、登录凭据、预览令牌或未授权游戏文件提交进仓库。
