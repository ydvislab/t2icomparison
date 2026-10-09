# CG&A 论文提纲（2026-10-08 草案）

> 限制（官方作者须知，2026-10-07 核对）：CG&A 模板，≤14 页，约 8000 词（含摘要、图注、参考文献、作者简介），摘要 ≤150 词，**参考文献 ≤20 篇**，侧栏 1–3 个（各 200–500 词，侧栏引用不计入 20 篇），录用后需宣传短视频。
> 正文用英文写；本提纲的说明用中文。下面的字数预算合计约 6300 词，留出图注、参考文献和作者简介的空间。

## 标题（候选）
1. **What Did the Model Decide for You? Comparing Generation Defaults Across Text-to-Image Models**
2. Seeing What Text-to-Image Models Settle On: Visual Comparison of Generation Defaults
3. Beyond a Diversity Score: Visually Comparing What Text-to-Image Models Fix by Default

## 摘要草稿（约 140 词）
> When a prompt leaves an attribute unspecified—lighting, framing, palette—the text-to-image model decides it. Newer models increasingly make the same decision every time, and different models and settings settle on different things. A single diversity score cannot show *what* is being fixed or how two models differ. We present a visual comparison approach for model developers and evaluators that places the repeated outputs of many models and generation settings on shared, human-checked visual aspects, separates *where* a group's outputs sit from *how concentrated* they are, and keeps every reading tied to the images and to the declared generation settings. Through case studies with FLUX.2, SDXL-Turbo and Stable Diffusion 1.5 and feedback from [N] experts, we show how the approach reveals guidance- and distillation-driven defaults, prompt-dependent reversals that pooled metrics hide, and measurement errors that only image evidence exposes. We close with lessons for visualizing generative output distributions.

## 结构与字数
| 节 | 内容 | 词数 | 现有材料 |
|---|---|---|---|
| 1 Introduction | 生成默认的现象（用户没写的属性由模型决定，新模型越来越统一）；一个多样性数字说不出"定在什么上"（Turbo 定色调、klein 定构图）；开发者的问题；三项贡献：比较方法（位置 / 集中程度 / 外观占比 + 比较成立的条件）、可视比较系统、案例与设计经验 | 900 | `experiments/*/RESULTS.md`；`docs/STATUS.md` |
| 2 Background and related work | 多样性与默认值度量（Vendi、DIMCIM、DefaultShift；引导和蒸馏降低多样性：CFG、CADS、Distilling Diversity）；生成图像可视分析（CUPID、ViBEx、Varif.ai、POET、PrompTHis、Concept Lens）；可视比较（Gleicher） | 800 | 已核实的文献 |
| 3 Measuring generation defaults | 画面方面（成对文字描述 + CLIP）；只在同一 prompt 内比较、固定的比较基线（隐藏组不改数值，重复使用的图只算一次）；位置（中位数）与集中程度（四分位距比值）分开；自助法区间；**人工核对结果**（表 1）；比较成立的条件（声明设置、多项改动不归因、样本不独立的情形） | 1100 | `aspects/`、`system/`；`annotation/`（待标注） |
| 4 The comparison system | 四个视图及各自回答的问题：投影 + 等高线（找图，不读集中程度）、方面 × 模型矩阵（筛查位置与集中程度）、方面分布条带（全部图像、跨组共用轴刷选）、选中详情（各组占比含 0、相对偏向、图像）；设置溯源与参照组；发现记录 | 1200 | `system/README.md`、`docs/REVIEW_PROTO3.md` |
| 5 Case studies | ① 同一 FLUX.2 家族：引导 1→4 让大多数方面变集中，蒸馏只再降一点，prompt 写法几乎无影响——但集中在**哪些**方面、集中成什么；② 跨世代：SDXL-Turbo 把"城市街道"统一成偏绘画、暖光、复古棕褐，klein 统一在另一处；同一模型在"房子"和"厨房"上构图方向相反，合并后被抵消；③ 测量出错的例子：自动描述与图像矛盾时，系统如何让人发现 | 1100 | 系统截图与数据；（可选）补主流模型 |
| 6 Expert feedback | 3–5 位做生成模型或评测的研究者，每人约 40 分钟：系统走查 + 3 个任务（找出两组差在哪个方面；判断差别是位置还是集中程度；找出一处测量不可信的地方）+ 访谈。报告他们用系统发现了什么、哪里难用 | 600 | 待做 |
| 7 Lessons and limitations | 设计经验：投影图上的包络不能当集中程度读；隐藏数据不应改变统计基线；协同视图需要在各视图重复组别和选择提示；比较必须带上生成设置；自动测量要能回到图像核实。局限：CLIP 代理测量、每组 8–16 张、模型有限、只用极简 prompt | 600 | `docs/DESIGN_HISTORY.md` |

**侧栏**：① "What is a generation default?"（约 250 词，用 klein 画 "a doctor" 的 16 张几乎同一个人作例子）；② "Why one diversity score is not enough"（约 250 词：两个同样单一、但统一在不同东西上的模型）。

## 图表计划
| 编号 | 内容 |
|---|---|
| 图 1（首图） | 同一 prompt，三个模型各 16 张（缩略图墙）+ 系统界面中对应的矩阵行，一眼看出"各自定在什么上" |
| 图 2 | 测量流程：方面定义 → CLIP 分数 → prompt 内标准化 → 位置 / 集中程度 → 人工核对 |
| 图 3 | 系统全貌（标注四个视图与联动） |
| 图 4 | 案例一：引导与蒸馏（矩阵 + 条带） |
| 图 5 | 案例二：跨世代 + 房子 / 厨房的反转 |
| 图 6 | 设计迭代中被放弃的做法及原因（平铺缩略图、簇卡片、把包络当集中程度）——支撑"设计经验" |
| 表 1 | 方面人工核对结果（每个方面与 CLIP 的一致率、"看不出"比例、两人一致性） |

## 参考文献（≤20，已核实 arXiv 编号；DOI 项来自此前会话核实，投稿前再查一遍）
1. Vendi Score — arXiv 2210.02410
2. DIMCIM — arXiv 2506.05108
3. DefaultShift — arXiv 2608.21784
4. Classifier-free guidance — arXiv 2207.12598
5. CADS — arXiv 2310.17347
6. Distilling Diversity and Control — arXiv 2503.10637
7. Adversarial Diffusion Distillation (SDXL-Turbo) — arXiv 2311.17042
8. Latent Diffusion (Stable Diffusion) — arXiv 2112.10752
9. CLIP — arXiv 2103.00020
10. CUPID — arXiv 2406.07699
11. ViBEx — arXiv 2504.19703
12. Varif.ai — arXiv 2506.19644
13. POET — arXiv 2504.13392
14. PrompTHis — arXiv 2403.09615
15. Concept Lens — DOI 10.1109/TVCG.2025.3564537
16. Gleicher et al. 2011, Visual comparison for information visualization — DOI 10.1177/1473871611416549
17. Gleicher 2018, Considerations for visualizing comparison — DOI 10.1109/TVCG.2017.2744199
18. Default Images in T2I (CHI 2026) — arXiv 2505.09166
19. Visual Fingerprints — arXiv 2605.06054
20. （留一个位置：How to Use t-SNE Effectively，Distill 2016，或 FLUX.2 技术报告；投稿前定）

## 待负责人决定
1. 是否补主流开源模型（H200 上 1–2 天）：补了案例更有说服力；不补则在局限里写明。
2. 专家反馈找谁（3–5 位）。
3. 作者顺序与单位（作者简介计入页数）。
