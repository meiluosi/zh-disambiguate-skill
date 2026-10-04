# 下游一致率评测

linter 的违规数只能说明改写稿更符合规则，不能说明 agent 更不容易读错。这个评测直接测量后者：给几个不同的模型同一段说明和同一个具体情况，看它们选的动作是否一致，以及是否符合作者意图。

## 怎么测

每道题（[`probes.json`](probes.json)）包含：

- 一组原文和改写稿（`pair` 指向的目录）
- 一个具体情况，例如「磁盘使用率正好是 90%」
- 一个问题和 2–3 个动作选项。运行时会自动加上选项「D. 说明不足以判断」
- 作者意图对应的选项（`intended`），不知道时为 null

原文和改写稿各问一遍，每个模型问 `--reps` 次。默认是 3 个模型，每个模型 3 次。

| 指标 | 含义 |
|---|---|
| 一致率 | 所有回答中，出现最多的那个选项占的比例 |
| 意图命中 | 选中作者意图选项的比例 |
| 判不清 | 选「说明不足以判断」的比例 |

题目分两类：

- **target**：改写稿针对这道题的歧义做了修改，期望一致率和意图命中上升。
- **control**：两版在这一点上本来就一样，期望没有变化。control 的变化大，说明评测本身有噪声或偏差。

`pairs/06`–`11` 是专门为评测写的，每个目录里有一份 `intent.md`，写明作者意图，改写稿按这个意图写成。这几题衡量的是「意图确定后，受控写法能不能让读者读出同一个意思」。它们不衡量 skill 能否自己猜出意图。按 skill 的规则，它不该猜。

## 运行

```bash
pip install -r requirements.txt
python3 run.py --dry-run                        # 调用次数、成本估算、提示词示例
python3 run.py --out results/2026-10-04         # 中断后重跑同一命令会接着跑
python3 score.py results/2026-10-04             # 生成 results/2026-10-04/report.md
```

凭证按 Anthropic SDK 的默认顺序解析：`ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`，或 `ant auth login` 保存的配置。

默认配置是 17 道题 × 2 个版本 × 3 个模型 × 3 次 = 306 次调用，估算花费不到 2 美元。可以用 `--models`、`--reps`、`--only` 缩小范围。

### 没有 API key：在 Claude Code 里用子代理

Claude 订阅额度不能当 API key 用，但可以在 Claude Code 会话里让子代理当读者：

```bash
python3 subagent.py emit results/<日期>-subagent    # 生成 6 个 batch 文件（2 个版本 × 3 次）
```

然后在 Claude Code 里，为每个 batch 文件和每个读者模型（opus / sonnet / haiku）各起一个子代理。让它只读这一个文件，按文件要求返回 JSON 数组。把返回结果存成 `answers/<模型>__<original|rewrite>_r<次>.json`，再运行：

```bash
python3 subagent.py ingest results/<日期>-subagent
python3 score.py results/<日期>-subagent
```

这种方式和 `run.py` 有三点不同，会记在 `manifest.json` 里：

- 一个子代理一次回答一个版本的全部题目，题目顺序按次数打乱。
- 答案格式靠提示词约束，不是 API 结构化输出。
- 子代理继承会话的 effort、用户的 CLAUDE.md 和已安装的 skill。

## 设计取舍

- **用结构化输出限定选项。**答案只能是选项字母，不需要另外的评委模型，打分完全确定。
- **不开 server-side fallback。**回退到另一个模型后，这一行答案就不属于记录的那个模型了。拒答单独计数。
- **「保留未改：」一行不交给 agent。**它是写给作者的附注，不是要发布的文本。
- **读者都是 Claude 模型。**它们可能有共同的偏好。一致率高不等于人类读者也一致。
