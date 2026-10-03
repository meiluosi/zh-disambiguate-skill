#!/usr/bin/env python3
"""下游一致率评测：同一个情况，不同的 agent 读原文和读改写稿，选出的动作是否一致。

每道题（probes.json）给 agent 一段说明和一个具体情况，让它从固定选项里选一个。
选项末尾总会加一个「说明不足以判断」。每道题分别用原文和改写稿各问一遍，
每个模型问 --reps 次。结果逐行写入 results.jsonl，中断后重跑会跳过已完成的调用。

用法:
    pip install -r requirements.txt
    python3 run.py --dry-run                     # 只打印调用次数和成本估算，不调用 API
    python3 run.py --out results/2026-10-04      # 正式运行
    python3 score.py results/2026-10-04          # 生成 report.md

凭证按 SDK 默认顺序解析：ANTHROPIC_API_KEY、ANTHROPIC_AUTH_TOKEN，或 `ant auth login` 的配置。
"""
import argparse
import json
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Literal

HERE = os.path.dirname(os.path.abspath(__file__))

DEFAULT_MODELS = ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-4-5"]
# 美元 / 百万 token（输入, 输出），只用于 --dry-run 的估算和 report 里的实际花费。
PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-4-5": (1.00, 5.00),
}
UNCLEAR_TEXT = "说明不足以判断"

SYSTEM = (
    "你是一个按说明执行任务的 agent。你会收到一段说明和一个具体情况。"
    "只依据说明本身决定怎么做，不要用常识补出说明没有写的规则。"
    "如果说明有两种以上合理读法，并且不同读法会导致不同的选择，选「说明不足以判断」。"
)

PROMPT = """说明：
<instructions>
{text}
</instructions>

情况：{situation}

问题：{question}

选项：
{options}

从选项里选一个，用 JSON 返回：choice 是选项字母，reason 用一句话说明依据。"""


def strip_kept_line(text):
    """「保留未改：」是写给作者的附注，不随改写稿一起交给 agent。"""
    return "\n".join(l for l in text.splitlines() if not l.startswith("保留未改")).strip()


def load_probes(path):
    with open(path, encoding="utf-8") as fh:
        spec = json.load(fh)
    unclear = spec.get("unclear_option", "D")
    base = os.path.dirname(os.path.abspath(path))
    probes = []
    for p in spec["probes"]:
        pair_dir = os.path.normpath(os.path.join(base, p["pair"]))
        texts = {}
        for cond, fname in (("original", "original.md"), ("rewrite", "rewrite.md")):
            with open(os.path.join(pair_dir, fname), encoding="utf-8") as fh:
                texts[cond] = strip_kept_line(fh.read())
        options = dict(p["options"])
        if unclear in options:
            raise ValueError(f"{p['id']}: 选项 {unclear} 保留给「{UNCLEAR_TEXT}」")
        options[unclear] = UNCLEAR_TEXT
        probes.append({**p, "options": options, "texts": texts, "unclear": unclear})
    return probes


def build_prompt(probe, cond):
    opts = "\n".join(f"{k}. {v}" for k, v in probe["options"].items())
    return PROMPT.format(text=probe["texts"][cond], situation=probe["situation"],
                         question=probe["question"], options=opts)


def plan(probes, models, reps):
    return [(p, cond, m, r) for p in probes for cond in ("original", "rewrite")
            for m in models for r in range(reps)]


def estimate(jobs):
    """粗估：中文 1 字约 1 token；输出含 adaptive thinking，按 400 token 估。"""
    total = 0.0
    for p, cond, m, _ in jobs:
        tin = len(SYSTEM) + len(build_prompt(p, cond))
        pin, pout = PRICES.get(m, (5.0, 25.0))
        total += tin * pin / 1e6 + 400 * pout / 1e6
    return total


def done_keys(path):
    keys = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                row = json.loads(line)
                if row.get("status") in ("ok", "refusal"):
                    keys.add((row["probe"], row["condition"], row["model"], row["rep"]))
    return keys


def ask(client, probe, cond, model):
    import anthropic
    from pydantic import create_model

    letters = tuple(probe["options"].keys())
    Answer = create_model("Answer", choice=(Literal[letters], ...), reason=(str, ...))
    # 不加 server-side fallbacks：回退到别的模型会让这一行的答案不再属于 model 列里的模型。
    # 拒答直接记成 refusal，在报告里单独计数。
    try:
        resp = client.messages.parse(
            model=model,
            max_tokens=4000,
            system=SYSTEM,
            messages=[{"role": "user", "content": build_prompt(probe, cond)}],
            output_format=Answer,
        )
    except anthropic.BadRequestError as e:
        return {"status": "error", "error": f"400: {e.message}"}
    except anthropic.RateLimitError as e:
        return {"status": "error", "error": f"429: {e.message}"}
    except anthropic.APIStatusError as e:
        return {"status": "error", "error": f"{e.status_code}: {e.message}"}
    except anthropic.APIConnectionError as e:
        return {"status": "error", "error": f"connection: {e}"}

    usage = {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}
    if resp.stop_reason == "refusal":
        return {"status": "refusal", "usage": usage}
    if resp.stop_reason == "max_tokens" or resp.parsed_output is None:
        return {"status": "error", "error": f"stop_reason={resp.stop_reason}", "usage": usage}
    out = resp.parsed_output
    return {"status": "ok", "choice": out.choice, "reason": out.reason, "usage": usage}


def main(argv=None):
    ap = argparse.ArgumentParser(description="下游一致率评测")
    ap.add_argument("--probes", default=os.path.join(HERE, "probes.json"))
    ap.add_argument("--models", default=",".join(DEFAULT_MODELS))
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--only", default="", help="只跑 id 匹配这个正则的题")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=os.path.join(HERE, "results", "latest"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    probes = load_probes(args.probes)
    if args.only:
        probes = [p for p in probes if re.search(args.only, p["id"])]
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    jobs = plan(probes, models, args.reps)

    print(f"{len(probes)} 道题 × 2 个版本 × {len(models)} 个模型 × {args.reps} 次 = {len(jobs)} 次调用")
    print(f"估算成本约 ${estimate(jobs):.2f}（粗估，实际花费见 report.md）")
    if args.dry_run:
        p = probes[0]
        print("\n--- 第一道题的提示词示例（rewrite 版）---\n" + SYSTEM + "\n\n" + build_prompt(p, "rewrite"))
        return 0

    import anthropic
    client = anthropic.Anthropic()
    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, "results.jsonl")
    skip = done_keys(out_path)
    todo = [j for j in jobs if (j[0]["id"], j[1], j[2], j[3]) not in skip]
    print(f"已完成 {len(jobs) - len(todo)} 次，剩余 {len(todo)} 次\n")

    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump({"models": models, "reps": args.reps, "system": SYSTEM,
                   "probes": [p["id"] for p in probes]}, fh, ensure_ascii=False, indent=2)

    lock = threading.Lock()
    errors = 0
    with open(out_path, "a", encoding="utf-8") as fh, ThreadPoolExecutor(args.workers) as pool:
        futures = {pool.submit(ask, client, p, cond, m): (p, cond, m, r) for p, cond, m, r in todo}
        for i, fut in enumerate(as_completed(futures), 1):
            p, cond, m, r = futures[fut]
            row = {"probe": p["id"], "kind": p["kind"], "condition": cond, "model": m, "rep": r,
                   "intended": p["intended"], "unclear": p["unclear"], **fut.result()}
            with lock:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
            if row["status"] == "error":
                errors += 1
                print(f"  error {p['id']} {cond} {m}: {row['error']}", file=sys.stderr)
            if i % 20 == 0 or i == len(todo):
                print(f"  {i}/{len(todo)}")
    print(f"\n完成。{errors} 次出错（重跑同一命令会补上）。结果：{out_path}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
