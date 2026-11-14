# 心金魂银详细图文攻略：进度

2026-11-15：全部 32 节已翻译并发布（1–16 主线，17–32 通关后：关都、白银山、赤红、传说宝可梦、狩猎地带、对战开拓区）。

## 流程
- 原文：source/part-N.json（Bulbapedia API，经 Chrome 取得；站点拦截 curl）
- 译文：zh/part-N.txt，每行「KEY: 中文」。前缀各自独立编号：H 标题、P 段落、D 道具位置、C 表格单元格、M 野生/训练家表注释、X 折叠框内容。
- 草稿：python3 -I src/bulba-walkthrough-v1.py draft pokemon-hgss-full N（只打印还没翻译的键）
- 构建：python3 -I src/bulba-walkthrough-v1.py build pokemon-hgss-full && python3 -I src/export-sprites-v1.py pokemon-hgss-full && python3 -I src/build-eli-guides-tr-v1.py && python3 -I src/build-eli-guides-v1.py
- 改了转换脚本后如果 build 报 WARNING（键错位），运行 python3 -I src/bulba-remap-v1.py pokemon-hgss-full <parts>，按 git HEAD 的 keys.json 用英文原文对齐。
- 人名对照：src/bulba-names-v1.json（普通训练家名字保留英文）。

## 未做
- 地图截图（205 张）需要在 Chrome 里允许「访问本地网络」才能转存。
