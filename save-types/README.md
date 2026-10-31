# Eli 存档类型查看器 v1

在线：<https://elecasper.github.io/eli-pokedex/save-types/>

输入游戏名、四位游戏编号、CRC32或SHA1，查询GBA/NDS原版存档类型与本体容量。支持已有的简繁中文、英文及日文别名，发行地区和修订分别保留。页面内嵌数据，不上传或修改游戏、存档，无账号、追踪、广告和付费服务。

## 范围

- 10,717条原版版本元数据，归并为10,093组；9,902条有明确类型，其中GBA 2,839条、NDS 7,063条。
- 原始目录标题均可搜索；中日文并非全量翻译。中文别名覆盖1,200组，日文别名覆盖277组；另人工整理66个常见作品家族。
- 示例：`绿宝石`、`綠寶石`、`Pokémon Emerald`、`ポケットモンスター エメラルド`、`BPEE`。
- 按GBA原版SHA1匹配open_agb_firm表；少数SHA1缺项只采用mGBA明确的固定容量覆盖。NDS按游戏编号匹配melonDS；不保证所有修订完全相同。
- 编号可跨平台复用，例如GBA的AXVE是宝可梦红宝石，NDS的AXVE是另一款游戏；不会把二者的存档类型混在一起。
- 无记录保持“待核验”，不当作“无存档”。原始目录与类型表编号不一致时，保留目录编号并明确警示；SHA1匹配不按名字相似度改变。

## 不能省略的区别

- `1 Mbit = 128 KiB`；不是1 MB。
- open_agb_firm的源枚举`EEPROM_8k`在其底层源码实际对应512 B（4 Kbit）；大EEPROM为8 KiB（64 Kbit）。容量按源码计算，不按枚举名字猜。
- RTC需求独立于保存介质，只在mGBA明确的硬件覆盖表中记录需要／不需要。未知不等于不需要，Boktai等作品的EEPROM+RTC也不能盲选Flash+RTC。
- SRAM协议不保证物理芯片一定为SRAM，也可能采用兼容协议的FRAM。
- `.sav`本体不等于`.dsv`封装、GBA VC填充、RTC附加段或即时存档；不要只按文件大小反推，更不要直接截断、填充或覆盖唯一原档。
- 中文检索别名部分来自公开汉化目录，仅用于找到对应原版；不把汉化／改版当成原版实测。未读取、下载或提供任何ROM、存档、商业游戏下载链接或密钥。

## 来源

完整固定提交、源文件路径和SHA-256见`sources.json`。构建读取结构化字节／文本，不运行上游代码。

- open_agb_firm `401c3dff900f658d3edf77ababcfaf5dca54a0a8`，GPL-3.0。
- libn3ds子模块 `ccbb6a94d60bea2e6a1901263251636b192bad3f`，其实际容量映射源码随原声明保留。
- melonDS `1e654443e4c0a54b40709c0208aa0eeba41e6142`，GPL-3.0。
- mGBA `52de910807c0178d6cfb088aa350952569e8f08f`，MPL-2.0，原版权和完整许可保留。
- libretro-database / No-Intro `2c93952f3cdf02837d2b34112aea5ee844d42b8b`，仅使用标题、编号、地区和校验等元数据，见各源的声明。
- 部分中文检索名称：OfflineList.DAT `4dec1d8543cca8f870beff5e6ad894bb669c88d7`。只提取名称事实作别名，不重新托管汉化补丁、游戏、图片或整份该目录文件。
- 繁简转换使用`opencc-python-reimplemented`；浏览器不加载外部语言库。

本工具代码及整体组合按GPL-3.0发布，第三方文件保留各自许可；不把所有名称元数据宣称为本站所有。非官方参考工具，不代替实机检查。

## 离线与复现

直接用支持本地HTML的浏览器打开`index.html`即可离线查询。在线来源链接及返回图鉴需要联网；页面不自动请求这些站点。

仓库`src/`保留构建器、原始别名清单、模板、脚本及测试。公开类型数据、相关格式源码与许可在`third-party/save-types/`；未重新分发的名称目录在开发构建时从固定提交读取到`/tmp/eli-save-types-source/`，不会在浏览器运行时下载。

```sh
python3 -m venv /tmp/eli-save-build
/tmp/eli-save-build/bin/pip install opencc-python-reimplemented==0.1.7
/tmp/eli-save-build/bin/python3 src/build-eli-save-types-v1.py
python3 src/test-eli-save-types-v1.py
```

构建器拒绝覆盖成品，先归档旧输出或另开版本。数据测试66项；浏览器验证涵盖多语言等价、跨平台同编号、地区筛选、未知类型、条件展开、分页和手机布局。手机验证为独立Chrome在320/360/390/428px及桌面1280px视口模拟，不是手机或掌机实测。
