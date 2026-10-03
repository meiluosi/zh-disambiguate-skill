#!/usr/bin/env python3
"""汇总 run.py 的 results.jsonl，生成 report.md。只用标准库。

指标（每道题、每个版本，把所有模型和所有次数的回答放在一起算）：
    一致率   出现最多的那个选项占全部有效回答的比例。1.0 表示所有读者选的一样。
    意图命中 选中作者意图选项的比例。只对 intended 不为 null 的题计算。
    判不清   选「说明不足以判断」的比例。

用法: python3 score.py RESULTS_DIR
"""
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run import PRICES  # noqa: E402


def load(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def stats(rows):
    answers = [r["choice"] for r in rows if r["status"] == "ok"]
    if not answers:
        return None
    counts = Counter(answers)
    top, n_top = counts.most_common(1)[0]
    intended = rows[0]["intended"]
    unclear = rows[0]["unclear"]
    return {
        "n": len(answers),
        "agreement": n_top / len(answers),
        "top": top,
        "dist": dict(sorted(counts.items())),
        "hit": (counts.get(intended, 0) / len(answers)) if intended else None,
        "unclear": counts.get(unclear, 0) / len(answers),
    }


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def fmt(x, pct=True):
    if x is None:
        return "—"
    return f"{x * 100:.0f}%" if pct else f"{x:.2f}"


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    out_dir = argv[0]
    rows = load(os.path.join(out_dir, "results.jsonl"))
    groups = defaultdict(list)
    for r in rows:
        groups[(r["probe"], r["condition"])].append(r)
    probes = sorted({r["probe"] for r in rows})
    kind = {r["probe"]: r["kind"] for r in rows}

    per = {}
    for pid in probes:
        per[pid] = {c: stats(groups[(pid, c)]) for c in ("original", "rewrite")}

    lines = ["# 下游一致率评测报告", ""]
    status = Counter(r["status"] for r in rows)
    cost = 0.0
    for r in rows:
        u = r.get("usage")
        if u:
            pin, pout = PRICES.get(r["model"], (0, 0))
            cost += u["input_tokens"] * pin / 1e6 + u["output_tokens"] * pout / 1e6
    models = sorted({r["model"] for r in rows})
    lines += [f"模型：{', '.join(models)}。调用 {len(rows)} 次：有效 {status['ok']}，"
              f"拒答 {status['refusal']}，出错 {status['error']}。实际花费约 ${cost:.2f}。", ""]

    lines += ["## 汇总", "", "| 题型 | 题数 | 一致率 原文 → 改写 | 意图命中 原文 → 改写 | 判不清 原文 → 改写 |",
              "|---|---|---|---|---|"]
    for k in ("target", "control"):
        ids = [p for p in probes if kind[p] == k and per[p]["original"] and per[p]["rewrite"]]
        if not ids:
            continue
        def m(field, cond):
            return mean([per[p][cond][field] for p in ids])
        lines.append(f"| {k} | {len(ids)} | {fmt(m('agreement', 'original'))} → {fmt(m('agreement', 'rewrite'))} "
                     f"| {fmt(m('hit', 'original'))} → {fmt(m('hit', 'rewrite'))} "
                     f"| {fmt(m('unclear', 'original'))} → {fmt(m('unclear', 'rewrite'))} |")
    lines += ["", "target 是改写稿针对其歧义做了修改的题。control 是两版在这一点上本来就一样的题，"
              "它们的变化应该接近 0。control 变化大，说明评测本身有噪声或偏差。", ""]

    lines += ["## 逐题", "", "| 题 | 题型 | 意图 | 原文分布 | 改写分布 | 一致率变化 |", "|---|---|---|---|---|---|"]
    for pid in probes:
        o, w = per[pid]["original"], per[pid]["rewrite"]
        intended = groups[(pid, "original")][0]["intended"] or "—"
        delta = (w["agreement"] - o["agreement"]) if o and w else None
        dist = lambda s: " ".join(f"{k}:{v}" for k, v in s["dist"].items()) if s else "—"
        lines.append(f"| {pid} | {kind[pid]} | {intended} | {dist(o)} | {dist(w)} | "
                     f"{'—' if delta is None else f'{delta * 100:+.0f} 点'} |")

    lines += ["", "## 按模型", "", "| 模型 | 版本 | 意图命中 | 判不清 |", "|---|---|---|---|"]
    for model in models:
        for cond in ("original", "rewrite"):
            sub = [stats([r for r in groups[(p, cond)] if r["model"] == model]) for p in probes]
            lines.append(f"| {model} | {cond} | {fmt(mean([s['hit'] for s in sub if s]))} "
                         f"| {fmt(mean([s['unclear'] for s in sub if s]))} |")

    lines += ["", "## 局限", "",
              "- 题数少，单道题的波动会明显影响平均值。看逐题表，不要只看汇总。",
              "- 读者都是 Claude 模型，可能有共同偏好。一致率高不等于人类读者也一致。",
              "- 06–11 号的改写稿用到了作者意图（见各目录的 intent.md）。这些题衡量的是"
              "「意图确定后，受控写法能不能让读者读出同一个意思」，不衡量 skill 能否自己猜出意图。"]

    report = os.path.join(out_dir, "report.md")
    with open(report, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines[:12]))
    print(f"\n完整报告：{report}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
