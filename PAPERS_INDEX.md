# FPGA & Hardware Acceleration Papers Knowledge Base (v1.0)

本知识库汇编了 28 篇针对 **FPGA 硬件加速、大语言模型（LLM）端侧推理、脉动阵列微架构、片上存储（BRAM/URAM/HBM）层次优化及 RISC-V 处理器扩展** 的前沿与经典论文。

所有论文均已预先校验并可在 GitHub Release `v1.0` 中下载压缩归档包：[`fpga_papers_knowledgebase_v1.0.zip`](https://github.com/chippareyner-glitch/fpga-papers-rag-toolkit/releases/tag/v1.0)。

---

## 目录分类

### 1. 大模型（LLM）边缘与端侧 FPGA 硬件加速

| 文件名 | 标题 / 会议年份 | 核心要点与硬件洞察 |
| :--- | :--- | :--- |
| `Paper_2401.03868_FlightLLM_FPGA24.pdf` | **FlightLLM** (FPGA 2024) | 高吞吐端侧大模型 FPGA 加速器，提出高带宽稀疏解压引擎与计算数据流重构。 |
| `Paper_2407.21325_EdgeLLM.pdf` | **EdgeLLM** (arXiv 2024) | 边缘资源极度受限（针对嵌入式 FPGA / SoC）的大语言模型量化与微架构协同设计。 |
| `Paper_2312.15159_Understanding_FPGA_Spatial_LLM.pdf` | **Understanding Spatial LLM on FPGA** | 深度剖析大语言模型在空间计算架构（FPGA）上的计算瓶颈与Roofline上限。 |
| `Paper_2504.17376_On_Device_Qwen2.5_on_FPGA.pdf` | **On-Device Qwen2.5 on FPGA** | 聚焦千问（Qwen2.5）在 FPGA 平台上的轻量化算子映射与端到端延迟优化。 |
| `Paper_2505.03745_AccLLM_Roofline_Analysis.pdf` | **AccLLM: Roofline Analysis** | 基于 Roofline 模型对各主流 LLM 算子在 FPGA 上的显存受限与算力受限区域建模。 |
| `Paper_2602.06063_Mapping_Gemma3_Edge_Dataflow.pdf` | **Mapping Gemma3 Edge Dataflow** | 针对新一代 Gemma3 架构在边缘 FPGA 上定制的多流水级数据流引擎。 |
| `Paper_2603.14785_SkipOPU_FlashAttention_FPGA.pdf` | **SkipOPU FlashAttention FPGA** | 结合 FlashAttention 片上分块算法与动态稀疏跳过（Sparsity Skip）的高性能 Attention 硬件设计。 |

---

### 2. 片上存储体系、BRAM / URAM / HBM 带宽优化

| 文件名 | 标题 / 会议年份 | 核心要点与硬件洞察 |
| :--- | :--- | :--- |
| `Paper_2410.07546_The_BRAM_is_the_Limit.pdf` | **The BRAM is the Limit** | 深入探讨高并发片上缓存对 BRAM/URAM 读写端口争用限制及 Banking 拆分最优解。 |
| `Paper_2502.10659_Pushing_Memory_Bandwidth_Embedded_FPGA.pdf` | **Pushing Memory Bandwidth on Embedded FPGA** | 针对嵌入式 FPGA 外存 DDR 控制器读写效率，最大化 Burst 传输与总线饱和度方案。 |
| `Paper_2507.03308_Hummingbird_GQA_DDR4.pdf` | **Hummingbird: GQA DDR4** | 面向 Grouped Query Attention (GQA) 的 DDR4 低突发开销连续访存调度机制。 |
| `Paper_2005.04324_Benchmarking_HBM_DRAM_FPGAs.pdf` | **Benchmarking HBM vs DRAM on FPGAs** | 全面横向对比高带宽内存（HBM2）与传统 DDR 内存对计算密集型算子的吞吐影响。 |
| `Paper_2104.07776_Demystifying_Memory_Access_Patterns_FPGA.pdf` | **Demystifying Memory Access Patterns on FPGA** | 系统化总结 FPGA 数据流应用中的合并访存、Strided 访存和 Banking 冲突消解模式。 |
| `Paper_1908.01261_IO_Cache_Coherency_SoC_FPGA.pdf` | **I/O Cache Coherency SoC-FPGA** | 针对异构 SoC-FPGA（如 ARM/RISC-V + PL）的 ACP/HPC 硬件缓存一致性协议研究。 |

---

### 3. 脉动阵列（Systolic Array）与经典卷积神经网络计算架构

| 文件名 | 标题 / 会议年份 | 核心要点与硬件洞察 |
| :--- | :--- | :--- |
| `Paper_2021_AutoSA_Systolic_Arrays_FPGA.pdf` | **AutoSA: Polyhedral-Based Systolic Arrays** | 基于多面体模型的 FPGA 脉动阵列自动生成框架，矩阵乘法与张量计算硬件基石。 |
| `AutoSA_Tutorial_IO_Network_Double_Buffering.pdf` | **AutoSA I/O Network & Double Buffering** | 脉动阵列的双缓冲（Ping-Pong Buffer）与 I/O 互联网络时钟周期级流水线精解。 |
| `Paper_2015_ChenZhang_Optimizing_FPGA_CNN.pdf` | **Optimizing FPGA CNN (Chen Zhang 2015)** | FPGA 深度学习加速奠基之作，系统化提出计算与带宽 Roofline 匹配模型。 |
| `Paper_2019_D_SWIM_Line_Buffer.pdf` | **D-SWIM Line Buffer** | 高能效 2D/3D 窗口滑窗行缓存结构（Line Buffer）与流水线特征复用。 |

---

### 4. RISC-V 处理器架构扩展与 NPU 指令集

| 文件名 | 标题 / 会议年份 | 核心要点与硬件洞察 |
| :--- | :--- | :--- |
| `pulp_nn_garofalo2020.pdf` | **PULP-NN: Accelerated Deep Learning on RISC-V** | PULP 平台基于 RISC-V 扩展的低位宽（1/2/4/8-bit）神经网络加速指令集与内核库。 |
| `ri5cy_tvlsi_gautschi2017.pdf` | **RI5CY Core (IEEE TVLSI 2017)** | 支持 DSP 扩展、硬件循环（Hardware Loops）与定点 SIMD 的开源 RISC-V 处理器核。 |
| `rvcorep_32im_islam2020.pdf` | **RVCoreP: 32IM RISC-V** | 面向边缘嵌入式系统的五级流水线高能效 RISC-V 软核设计与评测。 |
| `RISC-V_VeeR_EL2_PRM.pdf` | **Western Digital VeeR EL2 PRM** | Western Digital 高性能双发射超标量开源 RISC-V 核心编程与架构参考手册。 |

---

### 5. Xilinx / AMD 官方微架构与 AXI 总线指南

| 文件名 | 类别 / 编号 | 核心内容 |
| :--- | :--- | :--- |
| `ug573-ultrascale-memory-resources.pdf` | UG573 | UltraScale/UltraScale+ 架构 Block RAM、UltraRAM (URAM) 及分布式 RAM 详尽使用指南。 |
| `ug1037-vivado-axi-reference-guide.pdf` | UG1037 | Vivado AXI4 / AXI4-Lite / AXI4-Stream 规范与互联性能基准指南。 |
| `pg058-blk-mem-gen.pdf` | PG058 | Block Memory Generator IP 核心时序、时钟域与双端口配置全解。 |
| `pg059-axi-interconnect.pdf` | PG059 | AXI Interconnect 仲裁、跨时钟域转换与突发处理机制。 |
| `pg037_axi_perf_mon.pdf` | PG037 | AXI Performance Monitor (APM) 硬件吞吐量与总线延迟实时抓取指南。 |
| `ZipCPU_AXI_Address_Limits_and_Burst.pdf` | ZipCPU 专栏 | AXI4 4KB 边界跨界限制与突发传输规避踩坑实录。 |
| `ZipCPU_Measuring_AXI_Latency_and_Throughput.pdf` | ZipCPU 专栏 | 硬件逻辑如何精准测量 AXI 总线端到端时延与吞吐瓶颈。 |
