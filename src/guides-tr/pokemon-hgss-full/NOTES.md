# 心金魂银详细图文攻略：进度（2026-11-15 暂停）

线上：第 1–4 节已发布。第 5 节已翻译（zh/part-5.txt），还没发布。

## 下次继续前要先做的事
1. 转换脚本 src/bulba-walkthrough-v1.py 新增了商店表和通用表格（C 开头的键），
   但 D 键（道具位置）还在用全局计数，和 C 键混在一起会错位。
   要改成每种前缀单独计数（新增 nk(keys, prefix)），改完后把 zh/part-1..5 里的 D 键按顺序重新对齐。
   未完成的改法在 scratchpad 的 bw-backup.py 旁边的尝试里，失败点：item_table 里有 4 处计数要替换，不是 3 处。
2. zh/part-3、4、5 的 P 键已经按新脚本重新编号（表格不再占 P 键），与新脚本一致。
3. 新的 C 键（表格单元格）还没翻译：part-1 操作表、part-3 树果/异常状态/道馆牌、part-4 拼图表、part-5 球果表。
4. 第 4 节有一个折叠框（「Return later」，含拉普拉斯）要按正文处理：渲染成 details 框，内部键用 X 前缀。

## 流程
- 原文：source/part-N.json（Bulbapedia API，经 Chrome 取得；站点有防爬）
- 草稿：python3 -I src/bulba-walkthrough-v1.py draft pokemon-hgss-full N（只打印还没翻译的键）
- 构建：python3 -I src/bulba-walkthrough-v1.py build pokemon-hgss-full && python3 -I src/export-sprites-v1.py pokemon-hgss-full && python3 -I src/build-eli-guides-tr-v1.py && python3 -I src/build-eli-guides-v1.py
- 地图截图（205 张）需要在 Chrome 里允许「访问本地网络」才能转存，尚未取得。
