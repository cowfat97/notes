# Qwen 系列模型

## 1 发展历程

### 1.1 Qwen（2023.08）

阿里首代大语言模型，对标 LLaMA 2。

| 规格 | Qwen-7B | Qwen-14B | Qwen-72B |
|------|---------|----------|----------|
| 层数 | 32 | 40 | 80 |
| 隐藏维度 | 4096 | 5120 | 8192 |
| 注意力头 | 32 | 40 | 64 |
| 词汇量 | 151,936 | 151,936 | 152,064 |

核心技术选择：

**BPE 分词器**。采用字节级 BPE（Byte-level BPE），词汇量 15 万。对比 LLaMA 的 3.2 万（基于 SentencePiece），Qwen 的词汇表大 4 倍。直接后果：相同的中文文本，Qwen 编码后 token 数更少——平均每个汉字 1.5 个 token，LLaMA 需要 2.5~3 个。更少的 token = 更高效的推理。

**训练数据**。3 万亿 token，中英文混合。数据清洗做了去重（MinHash LSH）、质量过滤（困惑度评分）、敏感内容清洗。

**位置编码**。RoPE（旋转位置编码），和 LLaMA 一致。RoPE 的核心思想是通过旋转矩阵将位置信息注入注意力计算，使得两个 token 的注意力分数只依赖于它们的相对位置而不是绝对位置。

RoPE 的数学形式：

```text
f(q, m) = q · R(m)     对 query 向量 q 施加位置 m 的旋转
f(k, n) = k · R(n)     对 key 向量 k 施加位置 n 的旋转

其中 R(m) 是分块对角旋转矩阵：
R(m) = [[cos mθ₀, -sin mθ₀],
         [sin mθ₀,  cos mθ₀],
         ...
         [cos mθ_d/2-1, -sin mθ_d/2-1],
         [sin mθ_d/2-1,  cos mθ_d/2-1]]

θᵢ = 10000^(-2i/d)，频率从高到低覆盖
```

内积 f(q,m)·f(k,n) = q·R(m-n)·k，只依赖相对位置 (m-n)。

### 1.2 Qwen 1.5（2024.02）

架构升级，引入两个关键技术：

**GQA（分组查询注意力）**。标准多头注意力中，每个头都有独立的 Q、K、V 投影。GQA 将多个 Q 头共享一组 K、V 头：

```text
标准 MHA：32 个 Q 头 + 32 个 K 头 + 32 个 V 头 = 96 组投影
GQA：32 个 Q 头 + 4 组 K 头 + 4 组 V 头 = 40 组投影
      每 8 个 Q 头共享同一组 K、V
```

KV 缓存的显存占用直接降到原来的 1/8。对于长序列推理，这是决定性的优化。GQA 最初由 LLaMA 2 提出，Qwen 1.5 跟进。

**SWA（滑动窗口注意力）**。标准的因果注意力中，每个 token 要关注之前所有 token。SWA 限制每个 token 只关注前面固定窗口内的 token（如 W=4096），超出窗口的直接忽略。

```text
标准因果注意力：
token₁₀₀ 可以关注 token₁ 到 token₁₀₀（100 个）
计算复杂度 O(n²)

SWA (W=4096)：
token₁₀₀ 只关注 token_{100-4096} ~ token₁₀₀
计算复杂度 O(n·W)
```

但实际上 Qwen 1.5 用的是混合策略——一部分层用 SWA，一部分层用全注意力。窗口内的局部信息 + 窗口外的长距离依赖都保留。

**YaRN 位置插值**。直接扩展上下文窗口会导致位置编码分布改变（训练时没见过远处的位置），困惑度飙升。YaRN 将位置索引线性缩放到训练范围内：

```text
目标上下文 128K，训练上下文 4K
缩放因子 s = 128K/4K = 32

直接 RoPE：位置 64000 对应的旋转角度训练时从未见过 → 外推失败
YaRN：每个维度的缩放因子不同
     高频维度（短距离依赖）几乎不缩放
     低频维度（长距离依赖）按 s 缩放
     λᵢ = s^(i/(d/2-1))，i 越小（高频），λᵢ 越接近 1
```

### 1.3 Qwen 2（2024.06）

首次推出 MoE 架构，同时保留 Dense 版本。

**MoE 架构（以 Qwen2-57B-A14B 为例）**：

```text
                    输入 token
                       │
               ┌───────┴───────┐
               │  Router（门控） │  ← 一个小网络，决定每个 token 走哪个专家
               └───────┬───────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    专家 0          专家 1    ...   专家 63
   (FFN 层)       (FFN 层)        (FFN 层)
        │              │              │
        └──────────────┼──────────────┘
                       │
                 加权求和（Router 给出的权重）
                       │
                    输出
```

MoE 层替换 Transformer 中的 FFN。有 64 个专家（每个是一个独立的 FFN），但每个 token 只激活 top-2 个专家。Router 是一个线性层 + softmax：

```python
# 简化的 MoE Router 逻辑
def moe_forward(hidden_states):
    # hidden_states: [batch, seq_len, d_model]

    router_logits = router(hidden_states)     # [batch, seq_len, 64]
    routing_weights = softmax(router_logits)   # 归一化为概率

    # 选 top-2 专家
    top2_weights, top2_indices = topk(routing_weights, k=2)

    output = zeros_like(hidden_states)
    for token_i in range(seq_len):
        expert_1 = experts[top2_indices[token_i, 0]]
        expert_2 = experts[top2_indices[token_i, 1]]
        # 两个专家的加权输出
        output[token_i] = (
            top2_weights[token_i, 0] * expert_1(hidden_states[token_i]) +
            top2_weights[token_i, 1] * expert_2(hidden_states[token_i])
        )

    return output
```

**负载均衡**。如果所有 token 都选同一批专家，等于白做了 MoE。需要额外的辅助损失：

```python
aux_loss = α · Σᵢ(fᵢ · Pᵢ)

# fᵢ：分配给专家 i 的 token 比例
# Pᵢ：专家 i 的平均 routing 概率
# 当 fᵢ 和 Pᵢ 分布一致时 aux_loss 最小
```

**为什么 57B 只激活 14B**：64 个专家，每个 FFN 约 7B 参数。每个 token 激活 top-2 = 14B 激活参数。推理时计算量和 14B Dense 模型相当，但模型容量是 57B 级别。这就是 MoE 的核心价值——**推理成本 = 小模型，模型能力 ≈ 大模型**。

**参数 vs 激活参数**：

```text
Qwen2-57B-A14B：
  总参数：57B（所有专家的参数量总和）
  激活参数：14B（每个 token 实际使用的参数量）
  激活率：14/57 = 24.6%

对比 Dense 模型：
  Qwen2-72B：
    总参数：72B
    激活参数：72B
    激活率：100%
```

MoE 在相同计算预算下能获得更高的模型容量，但需要更多显存（所有专家都要加载）。

### 1.4 Qwen 2.5（2024.09）

专项模型矩阵爆发：

**Qwen2.5-Coder**：

- 训练数据：5.5 万亿 token 代码数据（92 种编程语言）
- HumanEval 92.7%，MBPP 90.2%
- 支持代码补全、debug、代码审查、测试生成
- 文件级代码生成（不只是函数级补全）

**Qwen2.5-Math**：

- 训练数据：数学论文、教科书、竞赛题
- 支持 CoT（思维链）和 TIR（工具集成推理——调用 Python 计算）
- MATH 基准 85%+，AIME 数学竞赛超过 GPT-4o

### 1.5 Qwen 3（2025.04）

**混合推理**。一个模型同时拥有 Think 和 No-Think 两种行为模式，通过 token 级别的开关控制：

```text
用户输入："证明根号 2 是无理数"
  开关=Think：
    <thinking>假设根号2是有理数，则存在互质的整数p,q使得(p/q)²=2
    → p²=2q² → p²是偶数 → p是偶数 → p=2k → 4k²=2q² → 2k²=q²
    → q²是偶数 → q是偶数 → p,q都是偶数，与互质矛盾
    → 假设不成立，根号2是无理数</thinking>
    根号2是无理数。证明如上。

用户输入："你好"
  开关=No-Think：
    你好！有什么可以帮助你的？
```

实现方式：训练数据中混合了带 `thinking` 标签和不带的样本，模型学会了根据 prompt 前缀判断是否需要思考。也可以通过 API 参数 `enable_thinking` 强制控制。

**开源协议**。Apache 2.0，商用友好，没有任何附加限制。这是目前最宽松的开源协议之一。

---

## 2 注意力机制演进

Qwen 系列跨越了注意力机制的完整演进。

### 2.1 MHA（Qwen 初代）

```text
输入 X: [seq_len, d_model]

Q = X·W_Q          [seq_len, d_head·n_heads]
K = X·W_K          [seq_len, d_head·n_heads]
V = X·W_V          [seq_len, d_head·n_heads]

切分为 n_heads 个头：
  Q → [n_heads, seq_len, d_head]
  K → [n_heads, seq_len, d_head]
  V → [n_heads, seq_len, d_head]

每个头独立计算注意力：
  Attention_i = softmax(Q_i·K_i^T / √d_head)·V_i

拼接所有头：
  Output = concat(Attention_0, ..., Attention_{n_heads-1})·W_O
```

问题：推理时需要缓存所有 K、V 投影。对于 32 个头 × 2（K+V） × d_head × seq_len × n_layers，长序列的 KV 缓存巨大。

### 2.2 GQA（Qwen 1.5+）

```text
标准 MHA：
  32 个 Q 头 → 32 个独立的 W_Q，32 个独立的 W_K，32 个独立的 W_V

GQA（32 个 Q 头，4 组 K/V）：
  32 个 Q 头 → 32 个独立的 W_Q（同上）
  4 组 K 头  → 4 组共享的 W_K
  4 组 V 头  → 4 组共享的 W_V
```

每 8 个 Q 头共享同一组 K 和 V。KV 缓存直接减少 8 倍。对推理吞吐的提升远超对精度的轻微影响（通常 < 0.5% 的困惑度增加）。

### 2.3 RoPE 家族

Qwen 全部使用 RoPE。Qwen 2 之后用 YaRN 扩展上下文到 128K。

**RoPE 的直观理解**：注意力计算 Q·K 时，不改变 Q 和 K 的值，而是根据位置对它们做"旋转"：

```text
二维例子：
q = [q₀, q₁]，位置 m

旋转后：
q' = [q₀·cos(mθ) - q₁·sin(mθ), q₀·sin(mθ) + q₁·cos(mθ)]
```

高维时，每两个维度一组用不同的频率 θᵢ = 10000^(-2i/d)。低频维度对长距离位置敏感（适合捕捉长距离依赖），高频维度对局部位置敏感（适合近距离依赖）。

---

## 3 ChatML 格式

Qwen 全系列对话使用 ChatML。

### 3.1 格式定义

```text
<|im_start|>system
你是一个有帮助的助手。<|im_end|>
<|im_start|>user
北京有哪些必去的景点？<|im_end|>
<|im_start|>assistant
北京必去景点包括故宫、长城、天坛、颐和园...<|im_end|>
```

### 3.2 特殊 Token

| Token | ID | 作用 |
|-------|-----|------|
| `<\|im_start\|>` | 151644 | 标记一段消息的开始 |
| `<\|im_end\|>` | 151645 | 标记一段消息的结束 |
| `\n` | 198 | 分隔 role 和 content |

### 3.3 实现细节

```python
def format_chatml(messages):
    """
    messages = [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什么可以帮助你的？"}
    ]
    """
    text = ""
    for msg in messages:
        text += f"<|im_start|>{msg['role']}\n{msg['content']}<|im_end|>\n"
    # 如果是生成模式（assistant 还没回复），最后加 assistant 前缀
    text += "<|im_start|>assistant\n"
    return text
```

### 3.4 ChatML 和 LLaMA Chat Template 的区别

| | ChatML（Qwen） | LLaMA Chat Template |
|------|------|------|
| system 提示 | 独立 `<\|im_start\|>system` | 嵌入在第一条 user 中 |
| 多轮对话 | 每轮独立段落 | 每轮独立段落 |
| 工具调用 | `<\|tool_calls\|>` 内嵌 | 用特殊标记 `[TOOL_CALLS]` |
| 可读性 | 高（类似纯文本对话） | 中 |

---

## 4 多模态能力

### 4.1 Qwen-VL 架构

```text
图像输入：一张图片 → Vision Encoder（ViT） → 图像特征序列
文本输入："这张图片里有什么？" → 分词 → 文本 token 序列

拼接：图像特征 + 文本 token → 送入 LLM → 生成回答
```

Vision Encoder 是 ViT-G（约 2B 参数），LLM 底座是 Qwen2。图像被切分成 448×448 的 patch，每个 patch 经 ViT 编码成一个 4096 维向量。LLM 把这些向量当"特殊 token"处理，和文本 token 一起做注意力计算。

### 4.2 支持的输入

- 单图 + 文本（"这张图片里有什么动物？"）
- 多图 + 文本（"比较这两张发票的金额"）
- 视频帧（拆成多帧图片）+ 文本（"这个视频讲了什么？"）
- 文档（PDF/Word 截图）+ 文本（"这份合同的甲方是谁？"）

---

## 5 部署方案

部署前必须先算清楚显存。否则要么 OOM，要么买了用不上的卡。

### 5.1 显存规划（30K 面试必问）

大模型推理的显存占用 = 模型权重 + KV Cache + 其他开销。

**模型权重**：

```text
FP32：参数数 × 4 bytes
FP16/BF16：参数数 × 2 bytes
INT8：参数数 × 1 byte
INT4：参数数 × 0.5 byte

Qwen3-8B FP16：8B × 2 = 16 GB
Qwen3-8B INT4：8B × 0.5 = 4 GB
Qwen3-32B FP16：32B × 2 = 64 GB（单卡装不下）
Qwen3-235B-A22B INT4：235B × 0.5 = 117.5 GB（仍需多卡）
```

**KV Cache**：

```text
KV Cache = 2 × n_layers × n_kv_heads × d_head × seq_len × dtype_bytes

Qwen3-8B（GQA, 8 个 KV 头, 128 维）：
  单 token：2 × 32 × 8 × 128 × 2 = 128 KB
  4096 token 序列：128 KB × 4096 = 512 MB
  32 个并发请求（每个 4096 token）：512 MB × 32 = 16 GB
```

这就是为什么 8B 模型跑 32 并发可能爆 24GB 显存——权重占 16GB，KV cache 占 16GB，加起来 32GB，超了。

**显存规划公式**：

```text
总需求 = 权重显存 + 并发数 × 单请求 KV Cache + 1~2GB（框架开销）

Qwen3-8B FP16 + 4090(24GB) + 1 并发：16 + 0.5 + 1 = 17.5 GB ✅
Qwen3-8B FP16 + 4090(24GB) + 32 并发：16 + 16 + 1 = 33 GB ❌ OOM
Qwen3-8B INT4 + 4090(24GB) + 32 并发：4 + 16 + 1 = 21 GB ✅
```

**Qwen 系列显存估算速查**：

| 模型 | FP16 权重 | INT4 权重 | 单请求 KV(4K) | 推荐显卡（FP16） | 推荐显卡（INT4） |
|------|:---:|:---:|:---:|------|------|
| Qwen3-8B | 16 GB | 4 GB | 0.5 GB | RTX 4090(24G) | RTX 4060(8G) |
| Qwen3-14B | 28 GB | 7 GB | 0.8 GB | A100(40G) / 双 4090 | RTX 4090(24G) |
| Qwen3-32B | 64 GB | 16 GB | 1.5 GB | A100-80G / H20 | A100(40G) |
| Qwen3-72B | 144 GB | 36 GB | 2.5 GB | 2×A100-80G / 4×A100 | H20(96G) / 2×A100-80G |
| Qwen3-235B-A22B | — | 117 GB | 3.2 GB | 4×H20 / 4×A100-80G | 同左 |

> MoE 模型（235B-A22B）全量参数 235B 必须全部加载到显存，即使是 INT4 也需要约 117GB。但每次推理只激活 22B 参数，所以**计算速度快，显存占用大**。

### 5.2 vLLM 深入

vLLM 是生产环境部署 Qwen 的首选。核心是 PagedAttention 和 Continuous Batching。

**PagedAttention**。传统推理中 KV cache 是连续分配的——每个请求预留 `max_seq_len` 长度的连续内存。预留多了浪费，预留少了截断。PagedAttention 把 KV cache 切成固定大小的 page（类似操作系统的内存分页），按需分配，不连续存储也无所谓——注意力计算时通过页表索引找到对应的 page。

```text
传统 KV Cache：
  请求A（实际用了 1024 token，预留了 4096）：
  [████████░░░░░░░░░░░░░░░░░░░░░░░░] 浪费 75%

PagedAttention（page_size=256）：
  请求A（1024 token）：
  [page0][page1][page2][page3] → 刚好 4 个 page，零浪费
```

内存在请求之间共享——请求 A 释放的 page 可以给请求 B 用。显存利用率从 20%~40% 提升到 90%+。

**Continuous Batching**。传统批处理：等一批请求全部完成才能处理下一批，快的等慢的。Continuous Batching：每步推理后立即检查哪些请求完成了，完成的踢出，新的加入。GPU 永远不等人。

```text
传统 Batch：
  [req1 ████████░░░░]  ← req1 早就完了，等 req2 req3
  [req2 ████████████]
  [req3 ██████████░░]
  时间 →

Continuous Batching：
  [req1 ████████] → 完成，立即踢出
  [req2 ████████████████] → 完成，踢出
  [req3 ██████████] → 完成
  [req4        ████████████] → req1 完成后立即加入
  时间 →
```

**关键参数**：

```bash
vllm serve Qwen/Qwen3-8B \
  --dtype auto \                    # 自动检测模型精度
  --max-model-len 32768 \           # 最大上下文长度（Qwen3 支持 128K，但越长 KV cache 越大）
  --max-num-seqs 32 \               # 最大并发请求数（和显存强相关）
  --gpu-memory-utilization 0.90 \   # 显存利用率上限（留 10% 给框架开销）
  --enable-prefix-caching \         # 前缀缓存：system prompt 相同时复用 KV cache
  --max-num-batched-tokens 8192 \   # 每步最大 token 数（prefill 阶段的 batch 大小）
```

**Prefix Caching**。多个请求共享同一个 system prompt 时，vLLM 只计算一次 system prompt 的 KV cache，后续请求直接复用。对数字员工这种 system prompt 很长的场景，prefix caching 可以节省大量计算。

### 5.3 SGLang

SGLang 的核心差异化是 **RadixAttention**——基于前缀树的 KV cache 复用。

```text
vLLM Prefix Caching：
  只有"完全相同的前缀"才能复用。
  system prompt A + user prompt B ≠ system prompt A + user prompt C

SGLang RadixAttention：
  前缀树自动识别公共前缀。
  
  "你是一个助手。帮我写一封邮件。"   ─┐
  "你是一个助手。帮我翻译这段话。"   ─┤  "你是一个助手。" 只算一次
  "你是一个助手。帮我总结这个文档。" ─┘
  
  "你是客服。帮我查订单 EXP504。"    ← 不同的 system prompt，从头算
```

RadixAttention 用 LRU 淘汰不常用的前缀，把显存留给热点前缀。多轮对话、JSON 结构化输出、批量同质请求的场景下，SGLang 比 vLLM 快 30%~50%。

**选择**：

| 场景 | 推荐引擎 | 理由 |
|------|:---:|------|
| 通用推理、请求差异大 | vLLM | 生态成熟、社区大 |
| 长 system prompt、同质请求多 | SGLang | RadixAttention 前缀复用 |
| structured output（JSON） | SGLang | 原生 constrained decoding |
| 新模型兼容性 | vLLM | 支持模型更多 |
| N 卡极致性能 | TensorRT-LLM | C++ 引擎，但配置复杂 |

### 5.4 量化部署

Qwen 部署时几乎必做量化，否则成本太高。

**量化方法对比**：

| 方法 | 原理 | 显存节省 | 精度损失 | 适用 |
|------|------|:---:|:---:|------|
| **GPTQ** | 逐层量化 + 权重校准，需要校准数据集 | ~75% | 小 | 生产部署首选 |
| **AWQ** | 基于激活值重要性量化，保护关键权重通道 | ~75% | 最小 | 精度要求高的场景 |
| **GGUF** | llama.cpp 格式，CPU/GPU 混合推理 | ~75% | 小 | 消费级硬件、Ollama |
| **INT8 动态量化** | 推理时量化激活值，不改权重 | ~50% | 极小 | 过渡方案 |
| **bitsandbytes INT8** | 在线量化权重，transformer 原生支持 | ~50% | 极小 | 开发测试 |

**你邮件分类用的 INT8 动态量化（150ms→45ms，1.3GB→400MB）是加速方法，不是真正的模型压缩。GPTQ/AWQ 是永久修改权重，模型文件变小，加载快，适合生产部署。**

**GPTQ 实操**：

```bash
# AutoDL 上对 Qwen3-8B 做 INT4 量化
pip install auto-gptq optimum

# 量化（需要约 128 条校准数据）
python -c "
from transformers import AutoTokenizer
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig

model_id = 'Qwen/Qwen3-8B'
tokenizer = AutoTokenizer.from_pretrained(model_id)

quant_config = BaseQuantizeConfig(
    bits=4,              # INT4
    group_size=128,      # 每 128 列一组共享量化参数
    desc_act=False,
)
model = AutoGPTQForCausalLM.from_pretrained(
    model_id, quant_config,
    torch_dtype='auto', device_map='auto'
)
# 校准 → 量化 → 保存
model.quantize([...])  # 需要校准数据
model.save_quantized('./Qwen3-8B-GPTQ-INT4')
"
```

**量化后对比**：

```bash
# FP16 原生
vllm serve Qwen/Qwen3-8B          # 16GB 权重，吞吐 1200 tok/s

# INT4 GPTQ
vllm serve ./Qwen3-8B-GPTQ-INT4 \ # 4GB 权重，吞吐 1800 tok/s
  --quantization gptq               # （显存余量更多 → 可开更大 batch）
```

同样的 24GB 显存，INT4 能跑更多并发，总吞吐反而更高。

### 5.5 本地快速部署（Ollama / transformers）

**Ollama**。适合开发测试，一条命令：

```bash
ollama pull qwen3:latest       # Qwen3-8B，自动 GGUF Q4_K_M 量化，约 4.4GB
ollama pull qwen2.5:14b        # Qwen2.5-14B，约 8.5GB
ollama pull qwen2.5-coder:7b   # 代码专用
```

底层是 llama.cpp + GGUF 量化，CPU/GPU 混合推理。M2 Mac 16GB 能跑 8B，14B 勉强。不适合生产——性能远不如 vLLM。

**transformers**。适合快速验证、微调前 debug：

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen3-8B",
    device_map="auto",
    torch_dtype="auto",
)
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")

messages = [
    {"role": "user", "content": "用 Python 写一个快速排序"}
]

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=True,     # Qwen3 混合推理开关
)

inputs = tokenizer(text, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=1024)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

transformers 不做 PagedAttention，不走 continuous batching，吞吐只有 vLLM 的 5%~10%。**只适合本地 debug，不适合生产。**

### 5.6 百炼 API

不想管部署时直接调阿里云百炼：

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-dashscope-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

response = client.chat.completions.create(
    model="qwen3-235b-a22b",
    messages=[{"role": "user", "content": "你好"}],
    extra_body={"enable_thinking": True},
)
```

| 模型 | 输入（¥/1K tokens） | 输出（¥/1K tokens） |
|------|:---:|:---:|
| Qwen3-8B | ¥0.0005 | ¥0.002 |
| Qwen3-235B-A22B | ¥0.001 | ¥0.004 |

对比自己部署：4090 一个月电费 + 租卡约 400~600 元。日均 5000 次请求以下用 API 更便宜，以上自己部署划算。

### 5.7 生产部署架构

```text
                        ┌─────────────┐
                        │   Nginx     │  ← 反向代理 / SSL / 限流
                        └──────┬──────┘
                               │
                    ┌──────────┼──────────┐
                    │                     │
            ┌───────┴───────┐     ┌───────┴───────┐
            │  vLLM 实例 1  │     │  vLLM 实例 2  │  ← 多实例负载均衡
            │  Qwen3-8B     │     │  Qwen3-8B     │
            │  GPU: GPU-0   │     │  GPU: GPU-1   │
            └───────────────┘     └───────────────┘
                    │                     │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │    监控 + 日志       │
                    │  GPU 利用率 / 延迟   │
                    │  Token 用量 / 错误率 │
                    └─────────────────────┘
```

**关键组件**：

| 组件 | 作用 | 工具 |
|------|------|------|
| 反向代理 | 统一入口、限流、SSL | Nginx |
| 推理引擎 | 模型加载、批处理、API 暴露 | vLLM / SGLang |
| 模型版本管理 | 灰度发布、回滚 | 模型文件 + 启动参数切换 |
| 监控 | GPU 利用率、P50/P99 延迟、首 token 时间 | Prometheus + Grafana |
| 日志追踪 | 请求链路、token 消耗 | Langfuse |

**灰度发布**：

```bash
# 启动新版本模型到不同端口
vllm serve ./Qwen3-8B-v2 --port 8001

# Nginx 分流：10% 流量到新版本
# 观察 P50/P99 是否恶化 → 全量切换
```

### 5.8 部署方案选型

```text
你的场景是什么？
  ├── 本地开发测试
  │     ├── Mac M 系列 → Ollama（GGUF Q4）或 MLX
  │     └── 消费级 N 卡 → Ollama 或 vLLM + INT4
  │
  ├── 生产环境 API 服务
  │     ├── 8B 模型 + 低并发（<16） → RTX 4090(24G) + vLLM FP16
  │     ├── 8B 模型 + 高并发（32+） → RTX 4090 + vLLM INT4（显存留给 KV cache）
  │     ├── 14B 模型 → A100-40G 或 双 4090（tensor_parallel=2）
  │     ├── 32B/72B 模型 → A100-80G / H20 + vLLM INT4
  │     └── 235B MoE → 4×A100-80G 或 4×H20 + vLLM INT4
  │
  ├── 同质请求多、system prompt 长 → SGLang（RadixAttention）
  ├── 极致性能、N 卡 → TensorRT-LLM（C++ 引擎）
  └── 不想管部署 → 百炼 API（小规模比自建便宜）

---

## 6 Qwen 微调

### 6.1 官方支持

| 方法 | 框架 | 适用 |
|------|------|------|
| 全量微调 | Transformers + DeepSpeed | 多卡 A100 |
| LoRA | PEFT | 单卡 24GB |
| QLoRA | PEFT + bitsandbytes | 单卡 8GB / M2 Mac |
| 官方工具 | ModelScope Swift | 一键启动，推荐阿里生态用户 |

### 6.2 LoRA target_modules

```python
LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,
    lora_alpha=32,
    target_modules=[
        "q_proj",    # Query 投影
        "k_proj",    # Key 投影
        "v_proj",    # Value 投影（最重要）
        "o_proj",    # Output 投影
        # Qwen 结构可选：
        # "gate_proj", "up_proj", "down_proj"  # FFN 投影
    ],
)
```

### 6.3 推荐参数

| 参数 | QLoRA 推荐值 | 说明 |
|------|-------------|------|
| r | 8~16 | 复杂度越高 r 越大 |
| alpha | lora_r×2 | 通用 |
| lr | 2e-4 | QLoRA 可用稍大学习率 |
| epochs | 1~3 | 小数据量时选 2~3 |
| max_length | 2048 | 能覆盖大部分任务 |
| batch_size | 4 | 配合 gradient_accumulation=4 |

### 6.4 ChatML 格式的微调数据

```json
{
  "messages": [
    {"role": "system", "content": "你是快递公司客服"},
    {"role": "user", "content": "包裹 EXP_504 三天没更新"},
    {"role": "assistant", "content": "亲，您的包裹在分拣中心暂留，今天下午更新物流。"}
  ]
}
```

训练时拼接成 ChatML 格式，对 assistant 部分计算 loss，system 和 user 部分不计算 loss。

---

## 7 模型对比

### 7.1 规格对比

| 模型 | 总参数 | 激活参数 | 架构 | 上下文 | 语言 | 协议 |
|------|--------|----------|------|--------|------|------|
| Qwen-7B | 7B | 7B | Dense | 8K | 中英 | 自定义 |
| Qwen1.5-7B | 7B | 7B | Dense+GQA | 32K | 中英 | 自定义 |
| Qwen2-7B | 7B | 7B | Dense+GQA | 128K | 30种 | Apache 2.0 |
| Qwen2-57B-A14B | 57B | 14B | MoE(64专家) | 128K | 30种 | Apache 2.0 |
| Qwen2.5-Coder-7B | 7B | 7B | Dense+GQA | 128K | 92种编程语言 | Apache 2.0 |
| Qwen3-8B | 8B | 8B | Dense+GQA | 128K | 119种 | Apache 2.0 |
| Qwen3-235B-A22B | 235B | 22B | MoE(128专家) | 128K | 119种 | Apache 2.0 |

### 7.2 与竞品对比

| 模型 | MMLU | HumanEval | CEval | MATH |
|------|------|-----------|-------|------|
| Qwen2.5-7B-Instruct | 74.3 | 84.8 | 81.2 | 55.4 |
| Llama 3.1-8B-Instruct | 73.0 | 72.6 | — | 51.9 |
| Qwen2.5-72B-Instruct | 86.1 | 91.5 | 89.7 | 73.8 |
| DeepSeek-V2.5 | 85.0 | 90.2 | 89.0 | 73.0 |
| Qwen3-235B-A22B | 87.2 | 93.1 | 90.8 | 77.6 |

Qwen 在中文理解（CEval）和代码（HumanEval）上领先同规模模型。数学方面 Qwen2.5-Math 单独拿第一梯队。

---

## 8 选型决策树

```text
你的目标是什么？
  ├── 日常对话、通用助手
  │     ├── 本地部署 → Qwen2.5-7B-Instruct（Ollama）
  │     └── API 调用 → Qwen3-235B-A22B（百炼）
  │
  ├── 写代码、debug
  │     ├── 本地部署 → CodeQwen2.5-7B-Instruct
  │     └── API 调用 → Qwen3-235B-A22B（代码也强）
  │
  ├── 微调业务模型
  │     ├── 中文+消费级显卡 → Qwen2.5-7B QLoRA
  │     ├── 英文+消费级显卡 → Qwen2.5-7B QLoRA
  │     └── 多卡服务器 → Qwen2.5-32B/72B LoRA
  │
  ├── 数学/推理
  │     ├── 纯推理 → QwQ-32B
  │     └── 数学解答 → Qwen2.5-Math-7B
  │
  └── 看图/文档理解 → Qwen2.5-VL-7B-Instruct
```
