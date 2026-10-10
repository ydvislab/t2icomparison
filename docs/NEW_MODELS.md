# 补主流开源模型：方案（2026-10-10 负责人决定补）

> **Superseded on 2026-10-10:** the model list, prompts and sample sizes are now in `PLAN.md` §3–4 and `PROMPTS.md`. The model-card settings below are still the starting point for G5 and G9.

## 1. 为什么补
现有的 13 组只来自 SD1.5、SDXL-Turbo、FLUX.2 klein 4B 及 klein-base 4B，都是小模型或蒸馏模型，分辨率 512 / 768。外部评审已指出"还不算真正的多模型比较"，CG&A 审稿人也很可能会问。

## 2. 加哪两个模型
设置均取自官方模型卡（2026-10-10 核对），按各自推荐设置、原生分辨率生成：

| 模型 | 规模 | 许可 | 步数 | 引导 | 分辨率（1:1） | 作用 |
|---|---|---|---|---|---|---|
| **Qwen-Image-2512**（2025-12-31 发布，Qwen-Image 的更新版） | 约 20B | Apache 2.0 | 50 | true CFG 4.0 | 1328² | 不同于 FLUX 的另一个主流家族，支撑"跨模型" |
| **FLUX.2 [dev]** | 32B | FLUX 非商业许可（研究可用） | 50（模型卡注明 28 步是不错的折中） | guidance 4 | 1024²（待生成时按模型卡最终确认） | 与现有 klein 4B 同一家族的大模型，支撑"同家族内比较" |

注意：
- klein 4B 与 FLUX.2 [dev] 之间同时改了模型规模、步数、引导，系统会提示"不能归因于其中某一项"，论文只描述"这一整套设置"的差别。
- Qwen-Image 的示例代码带负向提示词；为了和其他组一样只用极简 prompt，**负向提示词留空**（写成一个空格），并在设置里记录。
- 本机 diffusers 0.41.0.dev0 已含 `QwenImagePipeline` 和 `Flux2Pipeline`；服务器上装同一版本，写代码前先查该版本的文档，在服务器上实际跑通再提交。

## 3. 生成什么
- 6 个共同 prompt（a city street, a cup of coffee, a doctor, a house, a kitchen, a person reading a book），只写主题。
- 每个 prompt **16 个种子**，与现有 3 个模型组用同样的种子规则（`seed = 1000 × 主题序号 + k`，主题序号按 `experiments/hidden_or_lost/config.py` 的 12 个主题列表）。
- 每个模型 96 张，共 192 张。按推荐设置在 H200 上预计不到半天。
- 输出格式与现有一致：`$T2IC_DATA/hidden_or_lost/<模型键>/` 下的 PNG 和 `meta.csv`。

## 4. 加入后要做的
1. 在 `experiments/hidden_or_lost/config.py`、`aspects/build.py`、`system/build.py` 中各加两行，重算方面分数和系统数据（步骤见 `RUNBOOK.md` 第 5 节）。
2. **基线会变**：方面分数在每个 prompt 内相对全部组标准化，加组后所有组的标准化数值都会变，初步观察要重新核对。
3. 人工核对第二轮：新模型的图进入抽样（见 `annotation/PROTOCOL.md` 第 5 节）。
4. 生成脚本：在服务器可用后写 `experiments/new_models/gen_cuda.py`（现有 `gen.py` 写死了 Mac 的 `mps`），先在服务器上跑通 2 张图再批量生成。

## 5. 需要负责人做的
1. **服务器登录**：这台 Mac 上还没有配置 `h200` 的 SSH 别名。请在自己的 `~/.ssh/config` 里加上（登录信息不进仓库），配好后告诉执行方。
2. **FLUX.2 [dev] 许可**：在 Hugging Face 上用本人账号接受非商业许可，并在服务器上运行 `hf auth login`，token 由本人输入。Qwen-Image-2512 不需要这一步。
3. 确认服务器上可用的磁盘位置（两个模型连同各自的文本编码器，权重合计估计在 150 GB 以上）。
