# zh-disambiguate：消歧中文

[English](#english)

一个 Claude Code skill，把简体中文改写成只有一种读法的文字。读者是 agent 或程序：工具描述、系统提示词、agent 间指令、报错信息、运维步骤。读错了，也没有人可以问。

思路来自 [ASD-STE100 简化技术英语](https://www.asd-ste100.org/)，以及把它用在 agent 输出上的 [asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill)。中文的歧义来源和英文不完全一样，所以本项目没有翻译英文规则，而是专门检查中文特有的问题。

## 改写前后

| 改写前 | 改写后 |
|---|---|
| 当磁盘使用率达到 90% 以上时，需要对日志目录进行清理，删除 7 天以前的日志文件，清理完成后重启服务，注意不要删除当前正在写入的日志文件。 | 磁盘使用率 ≥ 90% 时，必须按以下步骤清理日志目录：<br>1. 删除最后修改时间在 7 天以前的日志文件。不得删除正在写入的日志文件。<br>2. 清理完成后，重启服务。<br><br>保留未改：「7 天以前」。原文没有说明是否含第 7 天。 |
| 你是一个客服助手。用户询问退款问题时，你应该先查询订单状态，然后根据情况决定是否需要转人工，对于金额较大的订单不要自行处理。 | 你是客服助手。用户询问退款时，按以下顺序处理：<br>1. 你应该先查询订单状态。<br>2. 根据情况，判断是否需要转人工客服。<br><br>订单金额较大时，你不得自行处理。<br><br>保留未改：「应该」。原文没有说明是必须还是建议。「较大」没有给出金额阈值。 |

第二个例子里的「应该」故意没有改。改成「必须」还是「建议」，应该由作者决定，不由改写者替作者选。更多示例见 [`examples/before-after.md`](examples/before-after.md)。

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

## 评测

[`evals/agreement/`](evals/agreement/) 直接测量改写是否让 agent 更不容易读错：把同一个情况交给多个模型，分别读原文和改写稿，比较它们选出的动作是否一致、是否符合作者意图。一共 17 道题，覆盖边界、「和 / 或」、指代、条件挂靠、双重否定和情态强度。题目还包括对照组，用来检查评测本身的偏差。

## 安装

```bash
npx skills add meiluosi/zh-disambiguate-skill
```

或者：

```bash
git clone https://github.com/meiluosi/zh-disambiguate-skill ~/.claude/skills/zh-disambiguate
```

## 使用

```
把这段工具描述改得不会被 agent 误读
消歧这段系统提示词
用 zh-disambiguate 改写这个报错信息
改了哪些地方？给我看对照表
```

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

A Claude Code skill that rewrites Simplified Chinese into text with exactly one reading, for agent and program readers: tool descriptions, system prompts, inter-agent instructions, error messages, and runbooks. It follows the approach of ASD-STE100 and [asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill). The rules target ambiguity sources specific to Chinese:

- dropped actors
- whether 以上 / 以下 include the bound
- negation scope
- mixed 和 / 或
- 的-chains
- light verbs (进行 / 作出 + noun)
- a five-level modal ladder mapped to RFC 2119
- conditions that detach from the action they limit

It has a stdlib-only linter (`scripts/zh-lint.py`) and an optional fidelity pass through [rewrite-fidelity](https://github.com/meiluosi/rewrite-fidelity-skill). It never removes hedges, and it never invents a missing actor, number, or bound. When the source is underspecified, it says so in a single `保留未改：` line.
