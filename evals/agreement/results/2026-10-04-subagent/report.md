# 下游一致率评测报告

模型：claude-haiku-4-5, claude-opus-5-5, claude-sonnet-5-5。调用 306 次：有效 306，拒答 0，出错 0。没有 token 用量数据（子代理方式不返回 usage）。

## 汇总

| 题型 | 题数 | 一致率 原文 → 改写 | 意图命中 原文 → 改写 | 判不清 原文 → 改写 |
|---|---|---|---|---|
| target | 10 | 82% → 100% | 52% → 100% | 46% → 0% |
| control | 7 | 94% → 89% | 100% → 100% | 27% → 32% |

target 是改写稿针对其歧义做了修改的题。control 是两版在这一点上本来就一样的题，它们的变化应该接近 0。control 变化大，说明评测本身有噪声或偏差。

## 逐题

| 题 | 题型 | 意图 | 原文分布 | 改写分布 | 一致率变化 |
|---|---|---|---|---|---|
| 01-force-default | control | — | B:7 C:1 D:1 | B:1 C:3 D:5 | -22 点 |
| 01-slow-boundary | target | B | B:3 D:6 | B:9 | +33 点 |
| 02-hedge | control | B | B:9 | B:9 | +0 点 |
| 03-amount-threshold | control | — | D:9 | D:9 | +0 点 |
| 03-order-strength | control | — | B:2 D:7 | B:3 D:6 | -11 点 |
| 04-active-log | control | B | B:9 | B:9 | +0 点 |
| 04-disk-boundary | target | A | A:9 | A:9 | +0 点 |
| 04-order | control | A | A:9 | A:9 | +0 点 |
| 05-all-done | control | B | B:9 | B:9 | +0 点 |
| 06-host-only | target | A | A:7 B:1 D:1 | A:9 | +22 点 |
| 06-socket-only | target | B | B:3 D:6 | B:9 | +33 点 |
| 07-what-times-out | target | A | A:1 D:8 | A:9 | +11 点 |
| 07-who-requeues | target | A | A:1 D:8 | A:9 | +11 点 |
| 08-day-30 | target | B | B:3 D:6 | B:9 | +33 点 |
| 09-unless | target | B | B:9 | B:9 | +0 点 |
| 10-auth | target | A | A:9 | A:9 | +0 点 |
| 11-omit-header | target | B | A:1 B:2 D:6 | B:9 | +33 点 |

## 按模型

| 模型 | 版本 | 意图命中 | 判不清 |
|---|---|---|---|
| claude-haiku-4-5 | original | 81% | 20% |
| claude-haiku-4-5 | rewrite | 100% | 6% |
| claude-opus-5-5 | original | 60% | 47% |
| claude-opus-5-5 | rewrite | 100% | 18% |
| claude-sonnet-5-5 | original | 57% | 47% |
| claude-sonnet-5-5 | rewrite | 100% | 16% |

## 局限

- 题数少，单道题的波动会明显影响平均值。看逐题表，不要只看汇总。
- 每个格子只有 3 个模型 × 3 次 = 9 个回答，而且同一模型的回答彼此相关。
- 读者都是 Claude 模型，可能有共同偏好。一致率高不等于人类读者也一致。
- 题目是在改写稿写好之后才出的，每道题的「意图」选项也按改写稿的写法定。这有一定循环性：题目天然更容易被改写稿答对。
- 「意图命中」会惩罚谨慎。原文真有歧义时，读者选「说明不足以判断」是对的，但在这个指标里算没命中。所以先看「判不清」和「一致率」，再看「意图命中」。
- 有的 target 题原文本来就没有歧义（读者全部答对），这样的题没有提升空间，会把平均值往下拉。
- 06–11 号的改写稿用到了作者意图（见各目录的 intent.md）。这些题衡量的是「意图确定后，受控写法能不能让读者读出同一个意思」，不衡量 skill 能否自己猜出意图。
