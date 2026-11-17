# 心金魂银详细图文攻略：进度

2026-11-15：全部 32 节已翻译并发布（1–16 主线，17–32 通关后：关都、白银山、赤红、传说宝可梦、狩猎地带、对战开拓区）。

## 流程
- 原文：source/part-N.json（Bulbapedia API，经 Chrome 取得；站点拦截 curl）
- 译文：zh/part-N.txt，每行「KEY: 中文」。前缀各自独立编号：H 标题、P 段落、D 道具位置、C 表格单元格、M 野生/训练家表注释、X 折叠框内容。
- 草稿：python3 -I src/bulba-walkthrough-v1.py draft pokemon-hgss-full N（只打印还没翻译的键）
- 构建：python3 -I src/bulba-walkthrough-v1.py build pokemon-hgss-full && python3 -I src/export-sprites-v1.py pokemon-hgss-full && python3 -I src/build-eli-guides-tr-v1.py && python3 -I src/build-eli-guides-v1.py
- 改了转换脚本后如果 build 报 WARNING（键错位），运行 python3 -I src/bulba-remap-v1.py pokemon-hgss-full <parts>，按 git HEAD 的 keys.json 用英文原文对齐。
- 人名对照：src/bulba-names-v1.json（普通训练家名字保留英文）。

- G 前缀：地图/插图链接的说明文字。原文里单独一行的 [[File:…|thumb|…]] 会变成「🗺 地点名 · Bulbapedia 原图」链接（不转存图片：图库禁止直接下载，图片也是任天堂版权）。地点名能自动译出的不生成 G 键。

## 地图
- 2026-11-17：240 个地图链接，指向 Bulbapedia 的文件页。
