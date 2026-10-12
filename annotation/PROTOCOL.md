# 画面方面人工核对：方案与步骤

> 给负责人看的完整方案。标注人只需要读 `ANNOTATOR_GUIDE.md`。判定规则在标注开始前定下，标完后不再改。

## 1. 目的
系统里的 15 个画面方面都是 CLIP 自动打的分（与右端英文描述的相似度 − 与左端的相似度）。论文和系统的每个结论都建立在这些分数上，所以要先回答：**CLIP 说"这张更暖"时，人是否也这么看？** 结果决定每个方面保留、改名还是删除，并作为论文的表 1。

## 2. 设计
- **两两比较，只在同一个 prompt 内**：系统只在同一个 prompt 内比较分数，所以核对也只问"同一个 prompt 的两张图，哪张更偏右端"，不问绝对类别。
- **每个方面 16 对**，平均分布在 6 个 prompt 上：
  - 12 对"差距大"：一张来自该 prompt 在这个方面的前 15%，一张来自后 15%。检验 CLIP 的方向对不对。
  - 4 对"差距小"：两张都来自中间 40%。看中间段有多少是人也分不出的（只报告，不参与判定）。
- 共 240 对；左右顺序随机，题目顺序打乱；不显示 CLIP 的答案；被两组重复使用的图已排除。固定随机种子 20261008，可复现。
- 每题显示方面的中文名、两端的中文和**英文原始定义**（CLIP 实际用的文字）。

## 3. 人员
- 2 位标注人：负责人 + 1 位学生，**独立完成**，做完之前不讨论。
- 每人约 15–20 分钟。不需要事先培训，读 3 分钟的标注说明即可。

## 4. 判定规则（事先定好）
在"差距大"的对子上（每个方面 2 人 × 12 对 = 24 个判断）：
- **与 CLIP 方向一致率**（不算"看不出"的判断）**< 75%**，或
- **"看不出"超过 40%**，

则该方面判为**不可靠**。同时报告一致率的 95% 区间（24 个判断时区间较宽，只作参考，判定按点估计）和两人之间的一致性（Cohen's kappa；< 0.4 说明这个方面的含义两人理解不同，即使与 CLIP 一致也要考虑改名）。

**不可靠的方面怎么处理**：
| 情况 | 处理 |
|---|---|
| 一致率低（人和 CLIP 方向常相反） | 删除 |
| "看不出"多，但看得出时与 CLIP 一致 | 这个方面在这些图里变化太小：保留在系统里，论文中注明 |
| kappa 低、两人各有理解 | 改名或换更具体的英文描述，进入第二轮重新核对 |
| 已知含混的方面（色调、构图、画质）即使通过 | 结合逐对明细看是否需要改名 |

## 5. Round 1 on the study images (change of 2026-10-12, owner decision)
Round 1 no longer uses the 240 pairs drawn from the pilot images (`make_pairs.py`), because the paper does not use those images: every group was regenerated with new settings, 24 prompts and new models. Round 1 now draws its pairs from the study images with `make_pairs_study.py`. The design and the decision rule in §2 and §4 are unchanged: per aspect, 12 large-gap and 4 small-gap pairs, 240 in total, 2 independent annotators, and the agreement and "can't tell" thresholds fixed before labelling. What changes:
- **Source:** the study groups that were generated and CLIP-scored when the package was built: G01 SD1.5, G02 SDXL base, G03 SDXL-Turbo, G06/G07 klein-base 4B (CFG 4 / 1) and G08 klein 4B. The list is stored in `pairs.json`.
- **Subjects:** each aspect's 16 pairs use 16 different subjects of the 24, spread over the 6 categories. An aspect is never asked for a subject that implies it (`prompts.EXCLUDED`, e.g. in/out for "a kitchen").
- **Images:** no image appears in more than one pair. Images are shown as 512 px JPEG.
- **Seed:** 20261012.
- **Steps:** build the package on the server with `python annotation/make_pairs_study.py --zip`, which writes `$T2IC_DATA/annotation_study_package.zip`. Annotators label exactly as in the steps below. Analyse with `python annotation/analyze.py --pairs $T2IC_DATA/annotation_study/pairs.json aspects_X.csv aspects_Y.csv`; results go to `results/annotation_study/`.
- **Round 2** then covers the groups generated later (G04, G05, G09–G12) and any renamed aspects.

## 5a. 步骤（原计划，第一轮已改用研究图像，见上一节）
### 第一轮：现有 13 组（现在开始，目标 10/20 前完成）
1. **执行方**（已完成）：生成标注页面，`python3 make_pairs.py`。
2. **执行方**：打包给学生，`./package.sh`，得到 `~/va4ext/annotation_package.zip`（约 16 MB，含页面、353 张图和标注说明）。
3. **负责人**：把压缩包发给学生；自己在项目电脑上打开 http://127.0.0.1:8774/label_aspects.html （服务没在运行时：`cd ~/va4ext/annotation_aspects && python3 -m http.server 8774 --bind 127.0.0.1`）。
4. **两位标注人**：按 `ANNOTATOR_GUIDE.md` 各自标完，导出 `aspects_<缩写>.csv`。
5. **负责人**：把两个 CSV 放到 `~/va4ext/annotation_aspects/exports/`（**不要提交到 GitHub**：仓库是公开的，原始文件含姓名缩写）。
6. **执行方**：运行分析：
   ```bash
   python3 analyze.py ~/va4ext/annotation_aspects/exports/aspects_X.csv ~/va4ext/annotation_aspects/exports/aspects_Y.csv
   ```
   结果写到 `results/annotation/`：`aspect_check.csv`（每个方面一行）和 `pair_answers.csv`（每对一行，两人的答案与 CLIP 并列）。标注人在结果中按文件顺序记作 A、B，不出现姓名。
7. **三人碰头 15 分钟**（负责人、学生、执行方汇报）：只看两类对子：①两人都与 CLIP 相反的；②两人答案不同的。目的是理解 CLIP 错在哪、方面名称哪里有歧义，**不修改已交的答案**，统计结果以独立标注为准。挑 2–3 个典型的 CLIP 错例，作为论文案例三（"测量出错如何被看图发现"）的素材。
8. **负责人拍板**：按第 4 节逐个方面决定保留、改名或删除；执行方把决定记进本文件第 7 节并提交。

### 第二轮：新加的模型 + 改名的方面（新模型生成后，约第 3 周）
新模型的图会改变"差距大 / 差距小"的取样范围，第一轮的结论不一定能直接推广到新模型，所以补一小轮：
- 每个保留的方面再抽 6 对（4 对差距大 + 2 对差距小），**至少一张来自新加的模型**；改名的方面用新的英文描述重新算分后抽 16 对。
- 预计 90–120 对，每人约 8–10 分钟，同样两人独立完成，同样的判定规则。
- 论文报告两轮合并的结果，并分别列出新模型上的一致率。
- 抽样程序在新模型数据就位后扩展 `make_pairs.py`（加轮次参数），第一轮的对子不变。

## 6. 论文里怎么报告
表 1：每个方面一行，列出两端描述、差距大对子上的与 CLIP 一致率（含区间）、"看不出"比例、两人 kappa、处理结果（保留 / 改名 / 删除）。正文写明：两位标注人、240 + 第二轮对子、判定规则在标注前定下、碰头讨论不改答案。

## 7. 结果与决定
（第一轮完成后填写）
