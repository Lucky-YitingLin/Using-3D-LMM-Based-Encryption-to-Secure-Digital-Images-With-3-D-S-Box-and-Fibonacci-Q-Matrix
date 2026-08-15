# 3DSFF 图像加密——论文复现项目

[English README](README.md) · [论文—代码映射](docs/PAPER_IMPLEMENTATION_MAP.md) · [复现差异说明](docs/REPRODUCTION_NOTES.md) · [实验指南](docs/EXPERIMENTS.md)

本仓库面向以下论文提供一个强调**可追踪、可运行、可验证**的开源复现实现：

> Yunlong Liao, Yiting Lin, Zheng Xing, Qiutong Li, Guoheng Huang, Donglong Chen, and Xiaochen Yuan, **“Using 3D-LMM-Based Encryption to Secure Digital Images With 3-D S-Box and Fibonacci Q-Matrix,”** *IEEE Internet of Things Journal*, vol. 12, no. 24, 2025. DOI: `10.1109/JIOT.2025.3624032`。

论文将完整方案称为 **3DSFF**：首先使用与明文绑定的 3D-LMM 混沌系统生成驱动序列，再构造并扰动 3-D S-box，结合分形排序矩阵（FSM）完成像素替换/位置置乱，随后进行 XOR confusion，并使用由混沌序列动态选择迭代次数的 Fibonacci Q-matrix（FQM）对 2×2 图像块进行数值变换。

> **复现范围说明：**本次提供的材料中只有论文 PDF，没有原始 MATLAB 源码、历史脚本、`.mat` 数据、论文测试图像数据集或 Raspberry Pi 部署代码。因此，本仓库是依据论文正文、公式、流程图和实验描述完成的 **clean-room Python 复现**，不能声称与未提供的历史源码逐字节一致。论文中所有会影响执行的歧义、矛盾和兼容处理均记录在 [`docs/REPRODUCTION_NOTES.md`](docs/REPRODUCTION_NOTES.md)。

> **安全提示：**本项目用于论文复现、研究与教学，不是面向生产环境的密码库；未提供认证加密、生产级密钥管理、常数时间实现或系统级侧信道加固。

## 项目目标

本项目的整理目标是让其他开发者在克隆仓库后能够：

- 快速理解论文提出的 3DSFF 加密逻辑；
- 从“论文章节/公式”直接定位到实现文件和实验脚本；
- 安装依赖并运行加密—解密；
- 通过测试验证可逆性、S-box 与核心模块行为；
- 运行论文中可由现有信息支持的密码分析/实验流程；
- 明确区分“论文报告值”“本项目复现值”“由于论文信息不足而不能精确复现的部分”。

目录组织借鉴了用户指定参考仓库 [Cryptanalyzing-an-image-cipher-using-multiple-chaos-and-DNA-operations](https://github.com/Lucky-YitingLin/Cryptanalyzing-an-image-cipher-using-multiple-chaos-and-DNA-operations) 在研究代码复现方面的良好做法（如 `src`、`tests`、`examples`、`paper`、`docs` 分离，维护 paper-to-code 映射与实现差异说明），但具体模块完全围绕当前 3DSFF 论文独立设计。**当前论文提出的 3DSFF 算法不包含 DNA 编码或 DNA 运算**，因此本项目不会为了形式完整而加入与论文无关的 DNA 模块。

## 核心算法概述

根据论文 Fig. 1 和 Section II-A–II-D，加密流程整理为：

1. **明文绑定密钥生成**：对明文图像计算 SHA-512，从三个相邻起点开始每隔 8 个十六进制字符抽样，分别组成 16 字符序列并生成 `x0/y0/z0`。
2. **3D-LMM 混沌系统**：按论文 Eq. (1) 迭代，默认参数为 `a=0.5, b=2, c=0.5, d=0.5, e=0.2`，产生 `x_n/y_n/z_n`。
3. **3-D FSM S-box**：混沌值经过丢弃、绝对值、`2^10` 缩放、mod 256、顺序去重、索引重排，并构造 `8×8×4` S-box；之后进行 8 轮 8×8 FSM 扰动。每个 8-bit 像素按 `3:3:2` 位划分索引该 S-box。
4. **FSM 位置置乱**：对 S-box 替换后的图像执行多轮分形排序置乱。论文针对彩色图像采用 16 轮。
5. **XOR confusion**：利用 `Seq2=floor(mod(y_n×10^10,256))` 构造二维掩码并异或。
6. **Fibonacci Q-matrix**：由 `z_n` 生成 `Seq3=floor(mod(z_n×10^10,64))`，保留偶数迭代值；每个 2×2 块右乘 `Q^n`，结果 mod 256。

解密按可逆操作严格逆序执行：**逆 FQM → XOR → 逆序恢复每一轮 FSM → inverse S-box**。论文明确给出 `Q^{-n}`，但没有提供完整解密伪代码，所以完整逆流程被标记为“依据论文可逆结构补充实现”，而不是伪称为原始代码。

完整算法说明见 [`docs/ALGORITHM.md`](docs/ALGORITHM.md)。

## 论文中需要显式处理的歧义

本项目不对矛盾处进行无说明猜测，主要包括：

- SHA-512 的 16 位十六进制样本按正文写法除以 `10^16`，但论文同时称结果位于 `[0,1]`，两者并不总能同时成立；
- FSM 的 Step 1 与 Step 2 文字重复；
- Eq. (2) 若在每一代都固定乘 4，到高阶时会产生重叠值，不能继续作为排序置换；项目采用保持排序矩阵性质的上一代元素数量 `4^(k-1)` 作为块偏移；
- S-box 正文一处写成 `8×4×4`，但 Step 3、Fig. 3 以及 `3:3:2` bit split 均要求 `8×8×4`；
- S-box Step 4 使用了未定义的 `S22`；默认兼容处理使用 Step 2 中最近定义的 `S12` 驱动值；
- Eq. (8) 按标准 Fibonacci Q-matrix 恒等式解释为直接计算 `Q^n`；
- Fig. 5 图注和正文给出了两组互相不一致的 Lyapunov 指数；
- NIST SP 800-22 比特流提取、SSIM 窗口、相关性样本选择、裁剪区域的精确几何位置等没有完整说明。

这些问题及处理理由均记录在 [`docs/REPRODUCTION_NOTES.md`](docs/REPRODUCTION_NOTES.md)，并尽量通过配置项暴露关键兼容选择。

## 项目目录

```text
3dsff-image-encryption-reproduction/
├── src/threedsff/
│   ├── chaos.py                 # 3D-LMM，Eq. (1)
│   ├── key_schedule.py          # SHA-512 明文绑定与 KeyMaterial
│   ├── fsm.py                   # FSM 构造、正向/逆向位置置乱
│   ├── sbox3d.py                # 8×8×4 S-box 构造与替换
│   ├── confusion.py             # Seq2 / XOR，Eqs. (5)–(6)
│   ├── fibonacci.py             # Q^n、Q^-n 与 2×2 FQM
│   ├── cipher.py                # 完整加密/解密流水线
│   ├── io.py                    # 图像 I/O、尺寸检查
│   ├── cli.py                   # `threedsff` 命令行入口
│   └── analysis/
│       ├── metrics.py           # entropy/correlation/NPCR/UACI/SSIM
│       ├── sbox_metrics.py      # bijectivity/NL/SAC/BIC
│       ├── chaos_metrics.py     # Jacobian/Lyapunov/0–1 test
│       └── robustness.py        # crop/noise 扰动
├── experiments/                 # 对应 Section III 的实验脚本
├── tests/                       # 单元测试与回归验证
├── configs/                     # paper-default / smoke 配置
├── examples/                    # 最小示例与合成测试图像
├── scripts/                     # 辅助工具
├── data/                        # 用户自行放置论文测试图像
├── results/
│   ├── paper_reference/         # 从论文表格转录的参考值
│   └── smoke/                   # 本项目合成图像验证结果
├── docs/                        # 算法、映射、审计、实验文档
├── paper/                       # 论文元数据，PDF 不随项目再分发
├── .github/workflows/ci.yml
├── CITATION.cff
├── LICENSE
├── pyproject.toml
└── requirements.txt
```

## 环境要求与安装

建议使用 Python 3.10+。

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e ".[dev]"
```

只安装运行依赖也可以使用：

```bash
pip install -r requirements.txt
pip install -e . --no-deps
```

论文原实验环境为 MATLAB 2022b、64-bit Windows 11、AMD Ryzen 7-7745HX、16 GB RAM。本仓库使用 Python/NumPy 实现，因此运行时间以及长时间混沌序列的浮点轨迹不应被默认视为与历史 MATLAB 运行逐点一致。

## 快速开始

### 1. 运行测试

```bash
pytest
```

测试覆盖：FSM 可逆性、Fibonacci Q-matrix 模 256 逆变换、3-D S-box 双射与逆替换、基础指标、论文 Table I S-box 的非线性/SAC 校验，以及完整加密—解密逐字节恢复。

### 2. Python 示例

```bash
python examples/quickstart.py
```

输出写入 `outputs/`，该目录已在 `.gitignore` 中忽略。

### 3. 命令行加密

```bash
threedsff encrypt \
  --input examples/assets/demo_64.png \
  --output results/generated/demo_cipher.png \
  --key-output results/generated/demo_key.json \
  --config configs/paper_default.json
```

`demo_key.json` 保存由明文派生的初始状态及实际配置，是完成解密所需的**密钥材料**，不应在真实敏感数据场景中公开。

### 4. 命令行解密

```bash
threedsff decrypt \
  --input results/generated/demo_cipher.png \
  --key results/generated/demo_key.json \
  --output results/generated/demo_recovered.png
```

### 5. 核心复现 smoke run

```bash
python experiments/reproduce_core.py \
  --input examples/assets/demo_64.png \
  --config configs/paper_default.json
```

仓库中的 `results/smoke/core/metrics.json` 已记录一次合成 64×64 图像的 exact round-trip。该文件仅用于证明实现可以运行和可逆，其 entropy/correlation **不是**论文 512×512 基准结果。

## 输入数据准备

论文使用 Oakland、Splash、Mandrill、F-16、Sailboat、Peppers、House 等彩色图像，但本次材料中没有这些图片，也没有足够信息唯一确定它们的具体来源版本与预处理方式。因此本项目不打包或伪造论文数据集。

请将合法获取的测试图像放在 `data/raw/`。当前 FSM 复现要求空间尺寸为正方形且边长为 2 的幂，FQM 要求高宽均为偶数；例如可使用 256×256 或 512×512 的 RGB uint8 图像。

仓库提供的 `examples/assets/demo_64.png` 是 `scripts/generate_demo_image.py` 生成的确定性合成图像，仅用于功能验证：

```bash
python scripts/generate_demo_image.py --side 64 --output examples/assets/demo_64.png
```

## 实验与密码分析复现

完整说明见 [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md)。主要入口：

```bash
# Section III-A：S-box 性能
python experiments/run_sbox_analysis.py --paper-table-i

# Section III-B：Lyapunov、分岔、Gottwald-Melbourne 0–1 test
python experiments/run_chaos_analysis.py

# 导出 NIST SP 800-22 用序列（不声称精确复现 Table X p-value）
python experiments/export_nist_bitstream.py

# Section III-G：密钥敏感性（论文 d=1e-16）
python experiments/run_key_sensitivity.py --delta 1e-16 --axis x

# Section III-C/G：明文 +1 扰动、NPCR/UACI
python experiments/run_differential_analysis.py --input data/raw/Mandrill.png --trials 50

# Section III-D/J：当前环境计时
python experiments/benchmark.py --input data/raw/Mandrill.png

# Section III-E：FSM round 与 SSIM
python experiments/run_iteration_study.py --input data/raw/Mandrill.png --max-rounds 25

# Section III-F：直方图、相关性、信息熵
python experiments/run_statistical_analysis.py --input results/generated/mandrill_cipher.png

# Section III-H：全黑/全白 chosen-plaintext probe
python experiments/run_chosen_plaintext.py --side 256

# Section III-I：12.5/25% 裁剪、10/20/30% 椒盐噪声
python experiments/run_robustness.py --input data/raw/Peppers.png
```

`experiments/run_all.py` 运行不依赖论文缺失数据集的自包含实验子集。

## 主要参数

| 参数 | 论文/默认值 | 说明 |
|---|---:|---|
| `lmm.a` | `0.5` | 3D-LMM 缩放参数 |
| `lmm.b` | `2.0` | 正弦耦合参数 |
| `lmm.c` | `0.5` | 余弦分支常数 |
| `lmm.d` | `0.5` | 余弦项系数 |
| `lmm.e` | `0.2` | 正弦分支常数 |
| `fsm_rounds` | `16` | 彩色图像 FSM 置乱轮数 |
| `sbox_fsm_rounds` | `8` | 3-D S-box 的 8×8 FSM 扰动轮数 |
| `sbox_fill_burnin` | `5000` | 构造 `S11` 前丢弃数量 |
| `sbox_index_burnin` | `10000` | 构造索引驱动序列前丢弃数量 |
| `sbox_scale` | `1024` | 论文 `2^10` 缩放 |
| `confusion_scale` | `1e10` | Eq. (5) 缩放 |
| `fqm_scale` | `1e10` | Eq. (10) 缩放 |
| `fqm_modulus` | `64` | FQM 迭代值模数 |
| `pixel_modulus` | `256` | 像素运算最终模数 |
| `hash_normalization` | `paper_literal` | Section II-A Step 2 的兼容解释 |

`configs/paper_default.json` 用于尽量贴近论文描述；`configs/smoke_test.json` 减少部分迭代轮数，用于快速开发测试，不用于声称复现论文实验值。

## 论文报告值与本项目结果的区分

`results/paper_reference/` 保存从论文 PDF 转录的参考值，例如：

- Table I：16×16 reconstructed S-box；
- Table X：NIST SP 800-22 p-value；
- Table XI：不同图像的 NPCR/UACI；
- Table XIV：论文中 proposed 方法的计时（512×512 为 `0.5551 s`，256×256 为 `0.1942 s`）；
- Table XV：Mandrill 不同方向相邻像素相关性；
- Table XVI：加密图像信息熵；
- `paper_reported_summary.json`：摘要/S-box/鲁棒性等关键参考值。

论文摘要给出的平均信息熵为 `7.9993`，加密后相关系数接近 `0.01`。这些均被当作**论文报告参考值**，不会把 64×64 合成图像运行结果冒充为相同实验。

### 直接使用论文 Table I 验证 S-box 指标实现

```bash
python experiments/run_sbox_analysis.py --paper-table-i
```

由论文 Table I 的 256-entry S-box，代码得到 8 个分量非线性
`[106, 104, 102, 104, 102, 102, 102, 108]`，平均值 `103.75`；标准 SAC 平均值为 `0.501708984375`，与论文比较表中的四舍五入值 `0.5017` 一致。由于论文没有给出 BIC-SAC 的精确计算公式，本项目不声称 BIC-SAC 可以逐值复现。

## “论文内容—算法模块—代码文件—实验脚本”映射

详细版见 [`docs/PAPER_IMPLEMENTATION_MAP.md`](docs/PAPER_IMPLEMENTATION_MAP.md)。核心对应关系：

| 论文内容 | 实现文件 | 实验/验证 |
|---|---|---|
| 3D-LMM, Eq. (1) | `chaos.py` | `run_chaos_analysis.py` |
| SHA-512 明文绑定 | `key_schedule.py` | `reproduce_core.py` |
| FSM, Eqs. (2)/(4) | `fsm.py` | `run_iteration_study.py` |
| 3-D S-box, Eq. (3) | `sbox3d.py` | `run_sbox_analysis.py` |
| XOR, Eqs. (5)/(6) | `confusion.py` | core round trip |
| FQM, Eqs. (7)–(12) | `fibonacci.py` | core round trip / tests |
| 完整加密/解密 | `cipher.py` | `reproduce_core.py` |
| NPCR/UACI, Eq. (16) | `analysis/metrics.py` | `run_differential_analysis.py` |
| SSIM, Eq. (17) | `analysis/metrics.py` | `run_iteration_study.py` |
| 相关性, Eq. (18) | `analysis/metrics.py` | `run_statistical_analysis.py` |
| 信息熵, Eq. (19) | `analysis/metrics.py` | `run_statistical_analysis.py` |
| 裁剪/噪声鲁棒性 | `analysis/robustness.py` | `run_robustness.py` |

## 输出目录约定

- `results/paper_reference/`：论文原文转录值，不由实验脚本覆盖；
- `results/smoke/`：合成图像的本地验证快照；
- `results/generated/`：正常实验输出，Git 忽略；
- `outputs/`：quickstart 输出，Git 忽略；
- `*_key.json`：解密所需密钥材料，真实敏感数据场景中不应公开。

## 已知限制

1. **没有提供原始源码。** 无法做“原历史代码逐文件清理”的事实性判断，也不能声称与历史源码逐字节一致。
2. **论文存在若干内部矛盾/信息缺口。** 项目只在执行必需处采取明确、可审计的兼容方案。
3. **论文数据集缺失。** 未拿到完全一致的原图及预处理之前，不能声称重跑得到 Tables XI–XVII 的精确数值。
4. **NIST SP 800-22 参数不足。** 只保存论文 p-value 参考值并提供可控导出工具。
5. **混沌系统对数值实现敏感。** MATLAB/Python 长序列可能因极小浮点差异而逐渐分离。
6. **当前图像尺寸受限。** FSM 复现要求方形、2 的幂；论文自身也指出非方形视频帧适配困难。
7. **大图计算开销较高。** 多轮 FSM 与 FQM 会增加运行时间。
8. **未做侧信道安全工程。** 无常数时间、masking、功耗/电磁防护等实现。
9. **未复现 Raspberry Pi 板端工程。** 论文称在 Raspberry Pi 5 / 4 GB 上部署成功，但本次材料没有板端代码；可使用 `benchmark.py` 在目标机器自行测试。

## 测试与 CI

```bash
pytest
python -m compileall -q src experiments examples scripts
```

GitHub Actions 会在 Python 3.11 环境运行 pytest。若修改论文核心算法行为，应同步提供/更新回归测试，并在文档中说明对论文兼容性的影响。

## 引用

如本项目用于研究，请优先引用原论文。机器可读引用信息见 [`CITATION.cff`](CITATION.cff)。

```bibtex
@article{Liao2025ThreeDSFF,
  author  = {Liao, Yunlong and Lin, Yiting and Xing, Zheng and Li, Qiutong and Huang, Guoheng and Chen, Donglong and Yuan, Xiaochen},
  title   = {Using 3D-LMM-Based Encryption to Secure Digital Images With 3-D S-Box and Fibonacci Q-Matrix},
  journal = {IEEE Internet of Things Journal},
  volume  = {12},
  number  = {24},
  year    = {2025},
  doi     = {10.1109/JIOT.2025.3624032}
}
```

## 许可证

本项目的复现代码采用 [MIT License](LICENSE)。论文 PDF、第三方测试图像或其他外部数据仍受各自版权/许可证约束，本仓库不会改变其许可状态。

## 项目说明

本开源代码受人员变动、实验室搬迁、设备损坏等多种因素影响，代码版本可能存在细微差异，代码可能为早期 Demo 版本或迭代修复过程中的中间版本，但项目对应的核心思想与实现方法保持一致。
