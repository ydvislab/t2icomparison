# t2icomparison：比较文生图模型的"生成默认"

> **English summary.** When a prompt leaves an attribute unspecified (lighting, framing, palette, medium), a text-to-image model decides it, and newer models increasingly make the same decision every time. This repository contains a visual comparison system that lets model developers and evaluators see *what* each model or generation setting settles on, how two groups differ, and check every reading against the images. Target venue: IEEE Computer Graphics and Applications (regular feature article). Documentation is in Chinese; code and paper are in English.

## 这是什么
用户写"一条城市街道"时，没有说光线、色调、构图、媒介，这些由模型决定，我们称之为**生成默认**。新模型的生成默认越来越统一，而且不同模型、不同设置统一在不同的东西上。一个多样性数字只能说"单一了多少"，说不出"统一在什么上"。

本仓库提供一套方法和一个可视比较系统，帮助**模型开发者和评测者**：
- 把多个模型或生成设置的重复输出放在同一套人工核对过的画面方面上比较；
- 分开看"集中在哪里"（位置）和"有多集中"（范围）；
- 每个读数都能回到图像核实，并始终带着各组的生成设置。

论文目标：**IEEE CG&A 常规稿**，计划 2026 年 11 月中旬投稿。

## 目录
| 位置 | 内容 |
|---|---|
| `docs/PLAN.md` | 投稿要求、时间表、待决定的事、需要负责人做的事 |
| `docs/STATUS.md` | 现在有什么证据、系统做到哪、还缺什么 |
| `docs/OUTLINE.md` | 论文提纲（标题、摘要、结构、图表、20 篇参考文献） |
| `docs/RELATED_WORK.md` | 与最接近工作的区别 |
| `docs/DESIGN_HISTORY.md` | 系统的设计迭代、放弃的做法和原因 |
| `docs/REVIEW_PROTO3.md` | 外部评审意见与改进计划 |
| `docs/RUNBOOK.md` | 环境、模型、数据布局、从头复现的步骤 |
| `experiments/hidden_or_lost/` | 背景实验一：三代模型的默认多样性与可达性（生成 + 测量） |
| `experiments/caption_density/` | 背景实验二：引导、蒸馏、prompt 写法各自的影响（生成 + 测量） |
| `aspects/` | 画面方面的测量：CLIP 特征与 15 个双极方面分数 |
| `system/` | 可视比较系统（当前版本 rev4.1）及其数据构建 |
| `annotation/` | 方面的人工核对：生成两两比较的标注页面、分析结果 |
| `results/` | 背景实验的图表、系统截图、设计迭代截图 |

## 快速运行（已有图像数据时）
图像、模型和中间数据放在外置硬盘上，不进 git，默认路径 `~/va4ext`，可用环境变量 `T2IC_DATA` 改。

```bash
python3 system/build.py
```

```bash
cd ~/va4ext/proto3 && python3 -m http.server 8771 --bind 127.0.0.1
```

浏览器打开 http://127.0.0.1:8771/index.html 。从零开始生成图像的步骤见 `docs/RUNBOOK.md`。

## 许可与数据
代码许可待定（暂未附许可文件，即保留所有权利）。生成图像不在仓库中；所用模型各有许可：FLUX.2 [klein] 4B 为 Apache 2.0，Stable Diffusion 1.5 / SDXL-Turbo 按各自的模型许可使用。
