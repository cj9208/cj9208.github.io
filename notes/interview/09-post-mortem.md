# 09 — Post-Mortem（面试复盘）

> 面试后立即记录：被问了什么、哪里冷场、哪个桶被深挖、下次怎么改。
> 复盘结果回喂 `01` / `05` / `04`，比重新写 prep 高效。

## 本轮总体判断

- 主线故事成立，基本没有全新的题——都是三桶框架内的高频题变体。
- 内容与 deep dive 都没问题（约 90 分）。扣分点不在知识量，而在**偶尔**：问得很具体的题，一时间没跳出来，陷进细节里点对点接招，没有先归到自己的框架。
- 修正动作：具体题开口前先「归层」，已补进 `01` 核心策略「控场锚点」。

## 本轮核心教训：具体题容易陷进细节，没跳出来归层

- **现象**：不是所有回答都走丢，是**部分具体题**（如 rerank、similarity search）——答得都对，但串起来是"点对点接招"，没有先标出它在我框架里的位置。
- **根因**：问题越具体、信息越密，越容易直接被细节带着走，来不及在开口前完成"归层"这一步。
- **下次动作**：听到具体题，**先停半秒在心里归层**——① 这是三桶里的哪一桶？② 这是我在三层次弧线的哪一层做过的事？③ 怎么在收尾拉回主线（harness / 上游条件化 / 可预测账单）。归完层再开口。

## 细节注意点 1：rerank 被追问（怎么答才不显得傲慢）

**被问**：用不用 rerank？

**当时回答**：我的整个系统比较好，基本不怎么需要 rerank——靠 metadata + intention recognition + query clean + similarity search，基本都精准找到对应 chunk。

**复盘**：
- 这个答案内容自洽，但**容易听成"我的系统完美，不需要这个组件"**，反而像在防守。
- 更好的框架：**rerank 是补偿性组件，不是默认组件**。先把上游条件化做干净（intention + query clean + metadata + 精准检索），rerank 的边际收益自然变小——这不是"不需要"，而是"上游做好后它不再是瓶颈"。这与主线故事（上游条件化产生乘法收益）完全同源，应该主动归到主线上。
- 补一句承认权衡：当语料大、查询意图混、或精度要求极高时，rerank 是合理加法；原则是"先上游后补偿"。

**改进话术**：

> I treat rerank as a compensatory component, not a default one. Because my upstream conditioning is strong — intention recognition, query cleaning, and metadata-filtered retrieval — the candidate set is usually already precise, so rerank adds little. The principle is the same as the RAG economics story: fix upstream first, and the compensation layer becomes less necessary. Where the corpus is large or intent is mixed, I would still add it as a precision lever.

## 细节注意点 2：retrieval 细节——similarity search 被挑战时漏了 hybrid search

**被挑战**：similarity search 不行（不够精准）。

**当时回答**：retrieval 是 agent 模式，会自动 monitor 相关数据——比如这里的 similarity score，低于均值一定幅度就自动触发 fallback 策略：让 LLM 生成 similar query + possible answer，再 search 一次。

**复盘**：
- 答得不算错，但**漏掉了系统里最现成的武器：hybrid search（metadata 那部分）**。
- 面试官说"similarity search 不行"，实际上是在给你递话：**纯向量检索不行时你怎么兜底？** 第一层答案应该是 **hybrid search**（向量 + metadata/结构化过滤），第二层才是 agent 式监控 + fallback。
- metadata 本来就是这套系统的强项（工具注册表、域路由、schema、文档属性），应该主动搬出来，而不是只讲 LLM 重查。

**改进话术（两层递进）**：

> First, I would not rely on pure similarity search alone. I use hybrid search: vector similarity plus metadata filters — document type, domain, permissions, recency, source quality — so the candidate set is already constrained before scoring. Second, the retrieval step is agent-like in a narrow sense: it monitors live signals such as the similarity profile of the top results. If the scores fall meaningfully below the recent mean, it triggers a bounded fallback — the system reformulates the query or synthesizes a likely answer, and searches again within a fixed retry budget. That keeps recall high without open-ended model loops.

## 细节注意点 3：doc parse 没被问——备好了 multiple representation 没用上

**现象**：对方不太关心 doc parse，准备了 multiple representation 的深潜内容，全程没被追问。

**复盘**：
- 这是**备而没用上**的内容，不是回答失误。关键不是"他没问"，而是**这套方案已经想清楚，下次遇到"文档解析怎么做才可靠"时要能讲出来**。
- 可以主动把它并入「文档解析严格验收」案例（`04` 案例 2）作为增强版——既显深度又保持诚实（代理质量门仍在）。

**multiple representation 方案（备好、下次可讲）**：

- 文档解析后**不只取文字**，保留多种表示（文字 + 图片 + 表格结构）。
- **OCR 置信度不足时 fallback**：换用非 OCR 读取（如 PyMuPDF），在电子表格类文档上对齐度通常优于 OCR。
- **图片**：用 LLM 生成一段文字描述（caption），让纯文本检索也能命中图片内容。
- **但最终 generation 仍把原始图片一并传入**——描述只是索引层，不代替真实视觉信息，避免合成信息损失。

> For document parsing, I keep multiple representations, not just extracted text. If OCR confidence is low, I fall back to non-OCR extraction such as PyMuPDF, which usually preserves table alignment better than OCR on spreadsheet-like documents. For images, I generate a caption with an LLM so text retrieval can still hit visual content. But at generation time I still pass the original images into the model — the caption is for indexing, not a substitute for the actual visual information.

## 本轮其他待办

- [x] 把「rerank = 补偿性组件」一句话补进 `03` 深潜 B（RAG Case）追问速答。
- [x] 把「hybrid search = 纯向量检索的兜底第一层」补进 `03` 深潜 B（RAG Case）追问速答。
- [ ] 下次主动覆盖：被挑战检索/召回精度时，先 hybrid search，再 agent 监控 + fallback。
