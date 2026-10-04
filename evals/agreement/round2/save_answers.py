#!/usr/bin/env python3
"""把子代理返回的答案存成 answers/<model>__<cond>_r<rep>.json（只存题号和选项）。
用法: save_answers.py MODEL COND REP "01-a A,01-b B,..." """
import json, sys, os
model, cond, rep, data = sys.argv[1:5]
rows = [{"id": p.split()[0], "choice": p.split()[1]} for p in data.split(",")]
assert len({r["id"] for r in rows}) == len(rows), "duplicate ids"
if len(rows) != 40:
    print(f"warning: {model} {cond} r{rep} has {len(rows)} answers, not 40 (missing ones stay missing)")
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "2026-10-04-subagent", "answers")
os.makedirs(d, exist_ok=True)
json.dump(rows, open(os.path.join(d, f"{model}__{cond}_r{rep}.json"), "w"), ensure_ascii=False)
