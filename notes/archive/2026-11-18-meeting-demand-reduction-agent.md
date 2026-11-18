# 会议需求控制 agent（准备阶段先裁决"该不该开会"）

讨论日期：2026-11-18。来源：一段外部 AI 对话的建议文本（meeting prep agent 应先做需求控制，而非把会开得更顺），经 `search-blog-articles` 检索 + top 5 篇原文核对后决定不写。

## 事件

- 建议文本的核心主张：AI 降低开会成本 → 会议更多、强度更高（引 Microsoft 2026 synthesis、Berkeley/HBR 研究、"summary fatigue 使澄清邮件多 15%"、"人均年会议成本 $80k 其中 $25k 不必要"）；因此 prep agent 的第一产出应是"不开会"的裁决，配套三问测试、pre-read＋决策队列、question graph 议程、会议预算／常设会议默认过期、决策写入 system of record，考核口径＝避免的会而非产出的纪要。
- **全部实证数字为二手转述，无一手出处**；"2026 study found 15%" fabrication 风险高。未核，不得引用。

## 判断与逻辑链

- 诊断核心（工具降低吸收成本 → 需求膨胀）是站内已发布机制的换参数：缓冲垫§五已给过更强版本——不解决权责倒挂，任何微观"减负工具"都会被吸收为加码武器；48小时§四的焦虑传导解释了开会为何是管理者转嫁焦虑最廉价的通道。Jevons 式"成本降→需求涨"在《认知与预测》已出现（Token 域）。
- 按"机制是否越界"判据：未越界，属验证性案例。信息增益集中在处方侧而非诊断侧，但处方残差不足以独立成文（见下）。
- 事后修正：无（当轮即归档）。

## 残差

站内已有（slug → 对应组件）：

- `malicious-compliance-organization-game` §二/§三/§五：权责倒挂、免费缓冲垫、"数字化减负工具沦为加码武器"——覆盖"AI prep 工具会变成会议加速器"。
- `48-hour-workweek-paradox` §二/§四：上下文切换税、焦虑传导（会议作为廉价焦虑出口）、Goodhart。
- `architect-communication-protocol`：会前预投票（≈pre-read 预对齐）、纪要 WAL（≈决策留痕）、看板 CQRS（≈异步自助）、令牌桶背压（≈个体限流）、输入校验（≈模糊提问先限定）。
- `organization-as-distributed-system` Level 3：Inform vs Consult 接口分类＝"信息同步转异步、决策会保护"。
- `goodhart-law-management` / `ownerless-nouns-real-metrics-detector`：按"生成问题数/纪要数"考核 agent 的陷阱。
- `cognition-prediction-complex-decisions`：Jevons 悖论（Token 成本域）。

真新的（未写，留档）：

1. **裁决前置**：准备阶段第一产出是 necessity verdict（该不该开会），站内全部文章只优化"已排定的会"。
2. **需求侧第三条限流路径**：站内处方只有个体背压（L3 自保）与恶意合规（加速溢出倒逼限流）；"会议预算＋常设会议默认过期＋no pre-read no meeting"是建设性限流。关键约束：预算必须记在召集者头上才是修复权责错配，记在参会者头上就是又一个免费缓冲垫。
3. **Question graph 作为议程**（已知/未知/可异步/必 live＋可接受答案判据）——接的是未发布的提问实践（probe pricing、comparator），站内空白。
4. 决策 artifact 落 system of record（CRM/ticket）而非 sidecar summary——WAL 纪要的落位细化，半新。

## 处置

- **彻底放弃成文**。理由：诊断部分与缓冲垫§五＋48小时§四实质重复；残差 1–3 是处方/设计原则，单独撑不起一篇不重复的文章，且其真实用途是 agent 设计输入而非公开论述。
- 残差去向：若日后做 meeting-prep agent，残差 1–3 直接作为设计原则取用（本文件即来源）；不并入任何已发布文章（未获单独授权，且验证性并入会稀释原文）。
- **重开触发条件**：
  - 提问实践（probe pricing / question graph）正式发布 → 残差 3 并入该篇，届时重评残差 1–2 是否随同落地；
  - 出现把"会议预算记在召集者头上"真实跑通（或跑失败）的一手案例 → 残差 2 从设计原则升级为可写的机制标本，重开；
  - 仅出现新的"AI 让会议变多"报道 → 不重开，属换参数确认。