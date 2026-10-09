# 背景实验

两个实验都只作论文的动机证据（发现本身已有人发表），同时提供比较系统的 13 组图像。

| 目录 | 问题 | 进入比较系统的组 |
|---|---|---|
| `hidden_or_lost/` | 三代模型（SD1.5、SDXL-Turbo、FLUX.2 klein）的默认多样性与"明确要求时能否做到" | 3 个模型 × 6 个共同 prompt × 16 个种子 |
| `caption_density/` | 同一模型家族内，引导、蒸馏、prompt 写法各自的影响 | 10 个条件 × 6 个 prompt × 8 个种子 |

结果和结论见各自的 `RESULTS.md`；运行步骤见 `docs/RUNBOOK.md`。
