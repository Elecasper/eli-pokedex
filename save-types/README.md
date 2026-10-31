# Eli 存档类型查看器 v2

在线：<https://elecasper.github.io/eli-pokedex/save-types/?v=2>

查询GBA/NDS存档协议、本体容量与RTC资料。支持已有简繁中、英、日别名，编号、CRC32、SHA1，以及有记录的改版SHA256。不读取、上传、修改或下载游戏与存档；无账户、追踪和运行时API。

## 本次变化

- 同一游戏的已知协议、容量和RTC标注一致时，地区与修订归并成一张卡；所有编号、校验值、来源和open_agb_firm配置编号保留在逐版本详情。未知类型/容量不作为相同的证据。RTC同为未知仍显示未核验。
- 绿宝石六个地区编号合并显示；搜索BPEE、完整商品编号、精确哈希或筛选日本时，只呈现命中的版本，不把其他地区混进详情。
- 只有人工明确关联的作品家族才跨不同原始标题归并；其他作品仅按相同原始标题身份归并。不同平台、不同协议/容量/RTC结论分开，汉化与改版绝不因沿用原版编号而合并。
- 改版独立收录：漆黑的魅影、水银、解放Unbound、激进红Radical Red。每条标版本和依据。水银不是Liquid Crystal，主线也不等同对战塔特别版。

## 改版覆盖与缺项

| 条目 | 范围 | 当前容量资料 |
|---|---|---|
| 漆黑的魅影 | 5.0EX / EX+ BW、DP分支；具体补丁待核验 | 协议、容量、RTC均待核验，不继承绿宝石 |
| 水银 | FC主线1.3.3，不含对战塔版及翻译补丁 | 协议、容量、RTC均待核验，不继承火红 |
| 解放 Unbound | 英文2.1.1.1 | FLASH 128 KiB；RTC采用社区公开配置参考，原报告未标版本 |
| 激进红 Radical Red | 英文4.1 | FLASH 128 KiB；RTC未核验 |

“已收录名称”不等于已实测硬件。版本资料详见`hacks.json`；已知容量来自固定提交PUSE配置中的`container.flash_size`，不是看用户文件大小推断。PUSE原文件SHA256与限定的英文游戏校验在`src/eli-save-hack-profile-evidence-v2.json`和`sources.json`中。本站未读取或分发ROM，也不提供商业游戏下载链接。

## 原版数据与边界

保留v1全部10,717条原版版本元数据、10,093个源分组和所有硬件结论；其中9,902条有明确类型。原版SHA1、CRC32、地区、修订、别名、警告与源配置值未改变。另加4个改版条目，合计10,097个源分组，按显示规则可归并为7,669张配置卡；这不是7,669个独立游戏或硬件全覆盖的保证。

- GBA优先按原版SHA1匹配open_agb_firm；少数缺项只使用mGBA明确固定容量覆盖。NDS按平台内四字节编号匹配melonDS，不保证所有修订已逐一验证。
- 原版RTC依据mGBA硬件覆盖表，改版独立引用资料。未知不等于不需要；配置相同不代表存档互通或VC一定兼容。
- 1 Mbit = 128 KiB，不是1 MB。open_agb_firm枚举EEPROM_8k按libn3ds实际移位表对应512 B，不能按名字猜容量。
- SRAM协议不保证物理介质一定是SRAM；EEPROM与RTC是独立事实，不能为了RTC盲选FLASH。
- .sav本体不等于.dsv、VC填充、RTC附加段或即时存档；不得只按大小截断、填充和覆盖旧档。
- 中日别名非全覆盖；搜索Unbound也可能命中Line Rider 2 - Unbound，完整别名的精确命中优先显示，不隐藏名称相近的其他作品。

## 来源、许可和复现

完整原版固定提交与文件摘要见`sources.json`。保留open_agb_firm、libn3ds、melonDS、mGBA、libretro/No-Intro和已提取中文标题的原声明。原始v1构建器及其格式输入在仓库`src/`和`third-party/save-types/`；新增的改版事实与引用不是游戏文件或作者资料的整站副本。整体新增代码与组合GPL-3.0，第三方权利不转移。

离线包：`eli-save-types-offline-v2.zip`。直接打开包内`index.html`，数据与脚本均内嵌；只有主动点击来源链接才联网。

```sh
python3 src/build-eli-save-types-v2.py
node src/test-eli-save-types-v2.js
```

v2构建只需要Python标准库。`src/eli-save-types-base-v1.json.gz`是固定v1基线（gzip mtime=0），新增条目、事实摘录、别名身份表和原来源清单随源码提供，不执行上游代码。构建输出到`src/eli-save-types-v2/`，拒绝覆盖成品；测试基于该输出。原v1的源解析器仍可独立复现原始基线。

数据回归逐条确认10,093个原分组所有既有字段未改变，并验证不同协议/容量/RTC/平台/身份不误合并。另有43项UI检查，覆盖320/360/390/428px和桌面尺寸。均为独立Chrome模拟，不是手机或掌机实测。
