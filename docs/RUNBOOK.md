# 从头复现

## 1. 数据目录
大文件（模型权重、生成图像、特征、标注页面）不进 git，放在 `$T2IC_DATA`（默认 `~/va4ext`，外置 SSD）：

```
$T2IC_DATA/
  env/                    Python 环境（torch、diffusers、transformers）
  models/                 模型权重（见第 3 节）
  hidden_or_lost/<模型>/   背景实验一的图像与 meta.csv
  caption_density/<条件>/  背景实验二的图像与 meta.csv
  proto2/                 aspects/build.py 的输出：CLIP 特征、方面分数、缩略图
  proto3/                 system/build.py 的输出：可直接用静态服务器打开的系统
  annotation_aspects/     annotation/make_pairs.py 的输出：标注页面与图片
```

## 2. Python 环境
两套环境（2026-10-10 在 Mac M4 Pro 上使用的版本）：
- **生成与特征**（`$T2IC_DATA/env`）：Python 3.11.16，torch 2.14.1，diffusers 0.41.0.dev0（从 GitHub 安装，需要含 `Flux2KleinPipeline` 的版本），transformers 5.18.0，numpy 2.4.6，pandas 3.0.6，Pillow 12.3.0。
- **构建、分析与作图**（系统 `python3`）：Python 3.10，scikit-learn 1.2.2，pandas 2.0.1，matplotlib 3.7.1，Pillow。

`requirements.txt` 列出了所需的包。用到新的 diffusers / transformers 功能时，先查已安装版本的文档，写好后实际运行一遍再提交。

## 3. 模型
| 目录（`models/` 下） | 来源 | 用途 |
|---|---|---|
| `sd15` | ModelScope `AI-ModelScope/stable-diffusion-v1-5` | 生成 |
| `sdxl-turbo` | ModelScope `AI-ModelScope/sdxl-turbo` | 生成 |
| `sdxl` | ModelScope `AI-ModelScope/stable-diffusion-xl-base-1.0` | 背景实验一的配置中有，但未进入比较系统 |
| `FLUX.2-klein-4B` | Hugging Face `black-forest-labs/FLUX.2-klein-4B`（Apache 2.0） | 生成 |
| `FLUX.2-klein-base-4B` | Hugging Face `black-forest-labs/FLUX.2-klein-base-4B` | 生成 |
| `clip-vit-large-patch14` | ModelScope `AI-ModelScope/clip-vit-large-patch14` | 方面分数 |
| `dinov2-base` | Hugging Face `facebook/dinov2-base` | Vendi 多样性 |
| `Qwen3.5-4B` | Hugging Face `Qwen/Qwen3.5-4B` | 背景实验的维度判断（bf16，关闭思考，受限多选） |

## 4. 步骤
生成在 Mac 的 MPS 上完成（脚本里写死了 `mps`；换到 CUDA 机器时要改设备）。所有生成脚本可以中断后续跑。

**4.1 背景实验一**（`experiments/hidden_or_lost/`）：对每个模型键（`sd15`、`sdxl_turbo`、`klein4b`）运行：

```bash
~/va4ext/env/bin/python gen.py klein4b
```

然后对每个模型运行 `embed.py <模型键>`（DINOv2 + Vendi）和 `label.py <模型键>`（Qwen 维度判断），最后用系统 `python3` 运行 `stats.py`、`analyze.py`、`figures.py`，结果写到 `results/hidden_or_lost/`。`run_rest.sh` 是当时串起后半段的脚本。

**4.2 背景实验二**（`experiments/caption_density/`）：对 `config.py` 里的 10 个条件逐个运行 `gen.py <条件>`；测量用 `run_measure.sh <条件…>`（复用实验一的 `embed.py`、`label.py`）；再运行 `analyze.py`、`figures.py`，结果写到 `results/caption_density/`。

**4.3 方面测量**（`aspects/`）：

```bash
~/va4ext/env/bin/python build.py
```

**4.4 比较系统**（`system/`）：

```bash
python3 build.py
```

然后按 `system/README.md` 打开。

**4.5 人工核对**（`annotation/`）：见 `annotation/README.md`。

## 5. 加入新模型（计划，尚未执行）
在远程 GPU 服务器上生成，按原生分辨率，6 个共同 prompt × 16 个种子；把图像和 `meta.csv`（列与现有的一致：job、subject、probe、prompt、seed、model、year、size、steps、cfg、seconds）放到 `$T2IC_DATA/hidden_or_lost/<新模型键>/`，在 `experiments/hidden_or_lost/config.py` 的 `GENERATORS`、`aspects/build.py` 的 `DATASETS` 和 `system/build.py` 的 `GROUPS`、`CKPT` 中各加一行，再依次运行 4.3、4.4。服务器的登录信息只放在本人的 `~/.ssh/config`，不进仓库。
