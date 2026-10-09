# 画面方面的人工核对

**为什么做**：系统的 15 个方面来自 CLIP，只在同一个 prompt 内比较。要确认：CLIP 说"这张更暖"时，人是否也这么看。结果进论文表 1。

**怎么做**：两两比较。每个方面 16 对同 prompt 的图：
- 12 对"差距大"：一张来自该 prompt 在这个方面的前 15%，一张来自后 15%，检验 CLIP 的方向对不对；
- 4 对"差距小"：两张都来自中间 40%，看中间段有多少是人也分不出的。

共 240 对，左右顺序随机，不显示 CLIP 的答案；重复使用的图已排除。

**标注人**：2 人（负责人 + 1 位同学），各约 15–20 分钟。

## 运行
生成标注页面（固定随机种子，可复现；2026-10-10 重新生成，与原页面逐字节相同）：

```bash
python3 make_pairs.py
```

启动页面服务：

```bash
cd ~/va4ext/annotation_aspects && python3 -m http.server 8774 --bind 127.0.0.1
```

打开 http://127.0.0.1:8774/label_aspects.html ，填姓名缩写，用 ← → ↓ 作答（Backspace 回到上一对），做完点"导出 CSV"。两人都标完后：

```bash
python3 analyze.py aspects_A.csv aspects_B.csv
```

结果写到 `results/annotation/aspect_check.csv`。

**判定**：某方面在"差距大"的对子上，人与 CLIP 方向一致率 < 75%，或"看不出"超过 40%，就标为不可靠，在论文和系统里删掉或改名。同时报告两人之间的一致性（Cohen's kappa）。
