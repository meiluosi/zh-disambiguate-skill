# zh-disambiguate：消歧中文

把中文工具描述、系统提示词和操作步骤改得更明确，让 agent 少误读一点。原文缺少的信息会列成问题，留给作者确认。

[English](#english) · [安装与第一次使用](#安装与第一次使用) · [更多改写示例](examples/before-after.md) · [评测与局限](#评测与局限)

## 一段改写，哪些能改、哪些要问

以下是仓库中的[客服系统提示词示例](examples/before-after.md#3-系统提示词)。

**原文**

> 你是一个客服助手。用户询问退款问题时，你应该先查询订单状态，然后根据情况决定是否需要转人工，对于金额较大的订单不要自行处理。

**改写**

> 你是客服助手。用户询问退款时，按以下顺序处理：
>
> 1. 你应该先查询订单状态。
> 2. 根据情况，判断是否需要转人工客服。
>
> 订单金额较大时，你不得自行处理。
>
> 保留未改：「应该」。原文没有说明这是必须还是建议，请选「必须」或「建议」。「较大」原文没有给出金额阈值，建议补成「超过 X 元」。「根据情况」原文没有说明依据什么情况。

动作顺序更清楚了，但「应该」仍然保留。把它改成「必须」还是「建议」，由作者决定；「较大」的金额阈值也不能靠改写者猜。发布文本前，需要作者处理这些问题，并移除写给作者的「保留未改：」附注。

## 安装与第一次使用

```bash
npx skills add meiluosi/zh-disambiguate-skill
```

或者：

```bash
git clone https://github.com/meiluosi/zh-disambiguate-skill ~/.claude/skills/zh-disambiguate
```

安装后，在 Claude Code 里试一段真实文本：

```text
用 zh-disambiguate 改写下面的系统提示词，并列出仍需作者确认的地方：

你是一个客服助手。用户询问退款问题时，你应该先查询订单状态，然后根据情况决定是否需要转人工，对于金额较大的订单不要自行处理。
```

也可以这样调用：

```text
把这段工具描述改得不会被 agent 误读
消歧这段系统提示词
用 zh-disambiguate 改写这个报错信息
改了哪些地方？给我看对照表
```

## 中文特有的歧义

| 问题 | 例子 | 改法 |
|---|---|---|
| 省略执行者 | 传入 `user_id` 后返回订单列表 | 调用方传入 `user_id`。工具返回订单列表。 |
| 边界含不含本数 | 3 次以上 | ≥ 3 次 / 不少于 3 次 |
| 否定范围 | 并非所有表都支持 | 5 张表中有 2 张不支持 |
| 「和 / 或」混用 | A 和 B 或 C 为空时 | 用列表写清组合 |
| 「的」字链 | 服务器端的连接池的超时时间的默认值 | 连接池超时的默认值 |
| 形式动词 | 对配置进行检查 | 检查配置 |
| 情态强度不明 | 应该、最好、尽量、务必 | 必须 / 建议 / 可以 / 能 / 可能（五级阶梯，对应 RFC 2119） |
| 条件挂靠 | 不建议使用。除非迁移已完成。 | 条件和它约束的动作写在同一句里 |
| 警告位置 | 步骤写完，再在段尾加「注意不要……」 | 把警告放进它约束的那一步 |
| 推荐级没有默认动作 | 不建议覆盖文件 | 默认不覆盖。设置 `force` 时才覆盖。（原文没写时，在「保留未改：」里问作者） |

## 它做什么

1. **选模式。**严格模式用于工具描述、报错、agent 指令、操作步骤。风格模式用于 README、PR 描述，词汇类规则只作建议。
2. **逐句检查**上表的问题，再改写。
3. **保真。**不删推测语气（「可能」「大约」），不补原文没有的执行者、数字或原因。原文本身信息不全时，在 `保留未改：` 一行里说明，不替作者猜。
4. **默认只输出改写结果。**用户要求时，才输出「规则 / 原文 / 改写」对照表。

判断标准只有一个：两个读者各自照这句话去做，动作会不会不同？

## Linter

`scripts/zh-lint.py` 只依赖 Python 3.8+ 标准库，检查能机械判定的规则：分号、句长、「的」字链、形式动词、边界词、阶梯外情态词、双重否定、部分否定、「和 / 或」混用、句首代词、被字句、空转短语、宣传词、模糊词、同义词轮换。

```bash
python3 scripts/zh-lint.py doc.md                   # 严格模式，有硬违规时退出码为 1
python3 scripts/zh-lint.py --mode flavored README.md
python3 scripts/zh-lint.py --json --baseline 10 docs/*.md
python3 scripts/zh-lint.py --selftest
```

它从不要求删除推测语气：「请求可能已经失败。」没有任何发现。省略执行者和条件挂靠需要理解上下文，linter 不查，交给模型。

## 配套：rewrite-fidelity

linter 只看改写稿本身，无法确认改写有没有改变意思。[rewrite-fidelity](https://github.com/meiluosi/rewrite-fidelity-skill) 对比原文和改写稿，检查数字、代码、条件、否定、上下限、情态强度有没有丢失或被改动。装了它之后，本 skill 会在输出前自动运行这项检查。

```bash
FIDELITY=../rewrite-fidelity-skill/scripts/fidelity.py sh examples/run-examples.sh
```

## 评测与局限

评测测量「改写后，agent 读得是否更准」：给读者同一个情况，分别阅读原文和改写稿，检查所选动作是否符合作者意图。完整方法、记录和局限见 [下游一致率评测](evals/agreement/README.md) 与 [真实文本试用](evals/real/README.md)。

**第三轮（2026-10-08）：20 段文字、40 道题，其中 36 道考察歧义，4 道为对照。**改写者起初只能看原文，通过提问向作者模拟器补充信息。以下比例仅对应 36 道考察歧义的题：

| 指标 | 原文 | 改写终稿 |
|---|---|---|
| 读者选中作者意图 | 31% | 84% |
| 回答「说明不足以判断」 | 60% | 13% |

没做到的 7 道题，全部是改写者没有问到的地方，例如下标从 0 还是从 1 开始、`previous` 指哪个版本。4 道对照题的意图命中均为 100%。

这些结果有明确的范围：

- 读者是 3 个 Claude 模型，不是真人；样本小，不能推广到其他文体。原文回答复用第二轮数据。
- 每段文字只改写了一次，没有测量不同改写者或重复改写的方差。
- 作者模拟器的答案与题目来自同一份意图记录，回答有时会多提供信息；真实作者的回答可能更含糊。
- 读者看到的终稿已移除「保留未改：」附注；仍有 14 份文本包含待作者回答的问题，这部分使用流程没有评测。
- 另有 8 段开源工具描述的试用，读者仍是 Claude 扮演的开发者，不构成人类评测。[真人问卷](evals/real/questionnaire/questionnaire.md) 已备好，目前还没有人填写。

结果支持继续研究这套流程，不能保证一段文字改写后就没有歧义。

## 另一个例子：把警告放回对应步骤

| 改写前 | 改写后 |
|---|---|
| 当磁盘使用率达到 90% 以上时，需要对日志目录进行清理，删除 7 天以前的日志文件，清理完成后重启服务，注意不要删除当前正在写入的日志文件。 | 磁盘使用率 ≥ 90% 时，必须按以下步骤清理日志目录：<br>1. 删除最后修改时间在 7 天以前的日志文件。不得删除正在写入的日志文件。<br>2. 清理完成后，重启服务。<br><br>保留未改：「7 天以前」。原文没有说明是否含第 7 天。 |

这是现有的[运维步骤示例](examples/before-after.md#4-运维步骤)。删除警告移到了删除这一步；原文未说清的日期边界仍需作者确认。

## 设计来源

思路来自 [ASD-STE100 简化技术英语](https://www.asd-ste100.org/)，以及把它用在 agent 输出上的 [asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill)。中文的歧义来源和英文不完全一样，所以本项目没有翻译英文规则，而是专门检查中文特有的问题。

## 和相近项目的区别

| 项目 | 读者 | 重点 |
|---|---|---|
| **zh-disambiguate** | agent 和程序 | 消除歧义：执行者、条件、否定范围、边界、情态强度 |
| [jianming-zhongwen](https://github.com/heichaowo/jianming-zhongwen) | 人 | 简明技术中文：README、手册、对话回复 |
| [controlled-technical-chinese](https://github.com/bjo4/controlled-technical-chinese) | 人和模型 | 繁体中文、稽核、待确认标记 |
| [asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) | agent | 英文 |

规则依据和出处见 [`references/rules.md`](references/rules.md)。

## 不做的事

- 不声称符合 ASD-STE100 或任何官方中文标准。中文没有官方的受控语言标准。
- 不改营销文案、文学性文字、法律或标准原文。
- 不处理繁体中文，不做翻译，不处理中英文空格这类排版问题（推荐 [autocorrect](https://github.com/huacnlee/autocorrect)）。
- 不让空洞的内容变得有用。它只修形式。

## 许可证

MIT

---

## English

A Claude Code skill for reducing ambiguity in Simplified Chinese tool descriptions, system prompts, inter-agent instructions, error messages, and runbooks. Missing information becomes a question for the author; the skill must not invent an actor, number, or bound.

### See what changes

The [customer-support example](examples/before-after.md#3-系统提示词) separates a refund instruction into ordered steps. It deliberately keeps `应该` (“should”), because choosing between a requirement and a recommendation belongs to the author. It also asks what counts as a “large” order and what conditions require a handoff. The Chinese before/after text is [shown above](#一段改写哪些能改哪些要问).

### Install and try

```bash
npx skills add meiluosi/zh-disambiguate-skill
```

Or clone it into Claude Code's skills directory:

```bash
git clone https://github.com/meiluosi/zh-disambiguate-skill ~/.claude/skills/zh-disambiguate
```

In Claude Code, provide the source text:

```text
Use zh-disambiguate to rewrite this Chinese tool description.
List information that still needs the author's confirmation.

[paste the original Chinese text here]
```

Resolve the questions before publishing the text and remove the `保留未改：` note addressed to the author.

### Rules and checks

The approach draws on [ASD-STE100](https://www.asd-ste100.org/) and [asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill), with rules specific to Chinese:

- dropped actors
- whether 以上 / 以下 include the bound
- negation scope
- mixed 和 / 或
- 的-chains
- light verbs (进行 / 作出 + noun)
- a five-level modal ladder mapped to RFC 2119
- conditions that detach from the action they limit

It includes a Python 3.8+ stdlib-only linter ([`scripts/zh-lint.py`](scripts/zh-lint.py)) and an optional fidelity pass through [rewrite-fidelity](https://github.com/meiluosi/rewrite-fidelity-skill). Hedges must survive; underspecified details go in a `保留未改：` note. The linter cannot check omitted actors or condition attachment without context.

### Evidence and limits

In round 3, rewriters asked an author simulator questions about 20 texts. On 36 ambiguity probes out of 40 total probes, author-intent accuracy went from 31% to 84%; “insufficient information” responses went from 60% to 13%. The remaining 4 control probes stayed at 100% accuracy. All 7 unresolved probes concerned questions the rewriter did not ask.

Readers were 3 Claude models, each text was rewritten once, and the original-text baseline was reused from round 2. The author simulator and probes shared the same intent records, and its answers sometimes supplied extra information. Reader inputs omitted the author-facing notes; resolving the questions remaining in 14 texts was not evaluated. A separate 8-text trial also used a simulated reader. No human-reader evaluation has been completed.

See the [full evaluation](evals/agreement/README.md), [real-text trial](evals/real/README.md), and [human questionnaire](evals/real/questionnaire/questionnaire.md). These small evaluations do not establish that rewritten text is ambiguity-free.

