# FPGA & Hardware Acceleration Papers RAG Toolkit (v1.0)

[![Release](https://img.shields.io/badge/Release-v1.0-blue.svg)](https://github.com/chippareyner-glitch/fpga-papers-rag-toolkit/releases/tag/v1.0)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.14-green.svg)](https://python.org)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange.svg)](https://docs.trychroma.com)
[![License](https://img.shields.io/badge/License-Apache%202.0-lightgrey.svg)](LICENSE)

一个专为 **FPGA 芯片设计、大模型（LLM）端侧加速、脉动阵列微架构与片上存储（BRAM/URAM/HBM）优化** 打造的高精度本地 RAG 知识库与切片检索工具箱。

涵盖 **28 篇经典与前沿论文** 归档索引，并内置生产级 **Token-Aware 智能切片算法** 与 **Dense+Sparse 混合检索（Hybrid Retrieval）引擎**。

---

## 🌟 核心特性

- 🎯 **Token-Aware 物理切片（无乱码/不断句）**：
  摒弃传统的纯字符计数暴力切分，使用预训练分词器（Tokenizer）真实偏移映射（Offset Mapping）进行滑动窗口分块，完美保留公式、代码片段与中英文专业术语边界。
- ⚡ **增量指纹更新（SHA-256）**：
  基于文件内容散列与分块唯一指纹，支持毫秒级增量检测。新加入 PDF 仅索引差异内容，原文档变更自动替换旧向量，避免冗余开销。
- 🔍 **多路混合检索（Dense 语义向量 + Sparse BM25 关键词）**：
  融合 `intfloat/multilingual-e5-small` 密集语义向量与 BM25 精准技术词召回，既能理解“大模型在片上如何做滑窗缓存”的泛化语义，也能精准命中 `RAMB36E1`、`report_timing`、`GBA/PBA` 等硬件特定名词。
- 📚 **精选硬件加速论文知识库**：
  内附 28 篇精选论文（FlightLLM、AutoSA、EdgeLLM、AccLLM、Chen Zhang 2015、SkipOPU、BRAM Limits、PULP-NN 等），在 [GitHub Releases v1.0](https://github.com/chippareyner-glitch/fpga-papers-rag-toolkit/releases/tag/v1.0) 提供一键下载压缩包。

---

## 📂 项目结构

```text
fpga-papers-rag-toolkit/
├── build_index.py             # 知识库构建入口：文本提取、切片分块、向量计算与 ChromaDB 入库
├── rag_common.py              # 核心切片算法、多语言分词与数据库配置
├── search.py                  # 双路混合检索（Dense 向量 + BM25）与命令行/JSON 查询
├── download_papers.py         # 论文自动化下载器（支持 ArXiv 与 AMD 官网校验）
├── PAPERS_INDEX.md            # 28 篇论文的分类目录、摘要与硬件要点速查
├── docs/                      # 深度工程实战文档与经验总结
│   └── RV32_核对比与提频方法总结_2026-10-18.md # 六核对比、时序瓶颈定位与板上 100MHz 提频实战
├── requirements.txt           # 基础运行环境依赖
└── papers/                    # 论文存放目录（可将 Release 中的 PDF 解压至此）
```

---

## ✂️ 智能切片算法原理

在 `rag_common.py` 中，切片函数直接操作 Tokenizer 的底层偏移量：

```python
def segment_text(text: str, tokenizer):
    """基于分词器 offset 映射切片，保证 chunk 在 Token 限制内且语义不被截断"""
    text = text.replace('\x00', '').replace('\r\n', '\n').replace('\r', '\n')
    if len(text.strip()) < 40:
        return
    offsets = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True,
                        truncation=False)['offset_mapping']
    stride = CHUNK_TOKENS - OVERLAP_TOKENS  # 步长 = 块大小(300) - 重叠(40)
    for i in range(0, len(offsets), stride):
        batch = offsets[i:i + CHUNK_TOKENS]
        if not batch:
            break
        start, end = batch[0][0], batch[-1][1]
        snippet = text[start:end].strip()
        if len(snippet) >= 40:
            yield snippet
        if i + CHUNK_TOKENS >= len(offsets):
            break
```

---

## 🚀 快速上手

### 1. 安装依赖

```bash
python -m pip install -r requirements.txt
```

> **提示**：如果在国内网络环境，可预先配置 HuggingFace 镜像源：
> ```bash
> export HF_ENDPOINT=https://hf-mirror.com
> ```

### 2. 准备论文

可以直接运行脚本自动下载，或者从 [Releases v1.0](https://github.com/chippareyner-glitch/fpga-papers-rag-toolkit/releases/tag/v1.0) 下载 `fpga_papers_knowledgebase_v1.0.zip` 并解压到 `papers/` 目录：

```bash
python download_papers.py
```

### 3. 构建向量与文本索引

```bash
python build_index.py
```

运行后将自动对 `papers/` 目录下的所有 PDF 进行解析、精准切片并持久化到本地 ChromaDB 数据库。

### 4. 检索测试

```bash
# 查询大模型在 FPGA 上的片上缓存与 Roofline 模型
python search.py "FlightLLM sparse decoding and BRAM memory bandwidth" --top-k 3

# 中文混合查询
python search.py "脉动阵列的双缓冲 double buffering 与吞吐优化" --top-k 3

# JSON 模式（便于集成到 IDE 或 Agent 自动化工具链）
python search.py "AutoSA systolic array" --json
```

---

## 📜 论文库目录预览

详细论文导读请参阅 [PAPERS_INDEX.md](./PAPERS_INDEX.md)：
- **LLM 边缘端侧硬件加速**：FlightLLM (FPGA 2024), EdgeLLM, SkipOPU, AccLLM Roofline, Gemma3 Edge Dataflow, Qwen2.5 on FPGA.
- **片上存储与访存带宽突破**：The BRAM is the Limit, Pushing Memory Bandwidth on Embedded FPGA, Hummingbird GQA DDR4, HBM vs DRAM Benchmarking, Demystifying Memory Access Patterns.
- **脉动阵列与经典硬件**：AutoSA, AutoSA Double Buffering Tutorial, Chen Zhang 2015 CNN FPGA 奠基论文, D-SWIM Line Buffer.
- **RISC-V 处理器核与 NPU 扩展**：PULP-NN, RI5CY Core, RVCoreP 32IM, VeeR EL2 PRM.
- **官方微架构设计规范**：UltraScale UG573 Memory Resources, UG1037 AXI Guide, PG058 Block Mem Gen, PG059 AXI Interconnect, PG037 AXI Performance Monitor, ZipCPU AXI 经验专栏.

---

## 📄 License

本项目脚本代码采用 [Apache-2.0 License](LICENSE) 开源；收录的学术论文与手册版权均归其原作者及所属出版社/官方所有。
