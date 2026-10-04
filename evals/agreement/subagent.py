#!/usr/bin/env python3
"""不用 API key、在 Claude Code 里用子代理跑一致率评测的辅助脚本。只用标准库。

run.py 走 Anthropic API，每道题单独调用一次。这里换成另一种方式：每个子代理拿到
一个版本（原文或改写稿）的全部题目，打乱顺序，一次作答。然后把它们的回答汇总成和
run.py 相同格式的 results.jsonl，score.py 可以直接读取。

    python3 subagent.py emit --reps 3 OUT_DIR       # 生成 batch_<condition>_r<rep>.md
    # 在 Claude Code 里，每个 batch 文件交给每个读者模型的一个子代理，
    # 把子代理返回的 JSON 存成 OUT_DIR/answers/<model>__<condition>_r<rep>.json
    python3 subagent.py ingest OUT_DIR             # 生成 OUT_DIR/results.jsonl
    python3 score.py OUT_DIR

和 run.py 的区别（会写进 manifest.json）：
- 一个子代理一次回答 17 道题，不是每题单独调用。题目顺序按 rep 打乱。
- 答案格式由提示词约束，不是 API 结构化输出。ingest 会拒收不在选项里的答案。
- 子代理继承会话的 effort、用户的 CLAUDE.md 和已安装的 skill。
"""
import argparse
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run import HERE, SYSTEM, build_prompt, load_probes  # noqa: E402

BATCH_HEAD = """{system}

下面有 {n} 道互相独立的题。每道题只依据它自己的说明作答，不要用别的题的说明。
除了读取这份题目文件，不要使用任何工具，不要读取或搜索其他文件。

只输出一个 JSON 数组，不要输出其他文字。每道题一个对象：
{{"id": "题号", "choice": "选项字母", "reason": "一句话依据"}}
"""


def emit(args):
    probes = load_probes(args.probes)
    os.makedirs(args.out, exist_ok=True)
    for cond in ("original", "rewrite"):
        for rep in range(args.reps):
            order = probes[:]
            random.Random(f"{cond}-{rep}").shuffle(order)
            parts = [BATCH_HEAD.format(system=SYSTEM, n=len(order))]
            for p in order:
                parts.append(f"\n===== 题号：{p['id']} =====\n\n{build_prompt(p, cond)}")
            path = os.path.join(args.out, f"batch_{cond}_r{rep}.md")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("\n".join(parts).replace(
                    "从选项里选一个，用 JSON 返回：choice 是选项字母，reason 用一句话说明依据。",
                    "（这道题的答案放进最后的 JSON 数组）"))
            print(path)
    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump({"harness": "claude-code-subagent", "reps": args.reps, "system": SYSTEM,
                   "probes": [p["id"] for p in probes],
                   "notes": ["一个子代理一次回答一个版本的全部题目，题目顺序按 rep 打乱",
                             "答案格式由提示词约束，不是 API 结构化输出",
                             "子代理继承会话 effort、用户 CLAUDE.md 和已安装的 skill"]},
                  fh, ensure_ascii=False, indent=2)


ANSWER_NAME = re.compile(r"^(?P<model>[\w.\-]+)__(?P<cond>original|rewrite)_r(?P<rep>\d+)\.json$")


def ingest(args):
    probes = {p["id"]: p for p in load_probes(args.probes)}
    adir = os.path.join(args.out, "answers")
    rows, problems = [], []
    for name in sorted(os.listdir(adir)):
        m = ANSWER_NAME.match(name)
        if not m:
            continue
        with open(os.path.join(adir, name), encoding="utf-8") as fh:
            raw = fh.read()
        start, end = raw.find("["), raw.rfind("]")
        try:
            answers = json.loads(raw[start:end + 1])
        except ValueError:
            problems.append(f"{name}: 不是合法的 JSON 数组")
            continue
        seen = set()
        for a in answers:
            p = probes.get(a.get("id"))
            if p is None:
                problems.append(f"{name}: 未知题号 {a.get('id')}")
                continue
            seen.add(p["id"])
            ok = a.get("choice") in p["options"]
            rows.append({"probe": p["id"], "kind": p["kind"], "condition": m["cond"],
                         "model": m["model"], "rep": int(m["rep"]), "intended": p["intended"],
                         "unclear": p["unclear"], "status": "ok" if ok else "error",
                         **({"choice": a["choice"], "reason": a.get("reason", "")} if ok
                            else {"error": f"选项不合法: {a.get('choice')!r}"})})
        for pid in sorted(set(probes) - seen):
            problems.append(f"{name}: 缺少 {pid}")
    out = os.path.join(args.out, "results.jsonl")
    with open(out, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(rows)} 条回答 → {out}")
    for line in problems:
        print("  " + line, file=sys.stderr)
    return 1 if problems else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--probes", default=os.path.join(HERE, "probes.json"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("emit")
    e.add_argument("--reps", type=int, default=3)
    e.add_argument("out")
    i = sub.add_parser("ingest")
    i.add_argument("out")
    args = ap.parse_args(argv)
    return emit(args) or 0 if args.cmd == "emit" else ingest(args)


if __name__ == "__main__":
    sys.exit(main())
