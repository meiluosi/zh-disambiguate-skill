#!/usr/bin/env sh
# 检查每个示例改写稿的硬违规数是否等于 expected-hard。
# 如果设置了 FIDELITY（rewrite-fidelity 的 fidelity.py 路径），顺便运行保真检查。
set -u
here=$(cd "$(dirname "$0")" && pwd)
lint="$here/../scripts/zh-lint.py"
fail=0
for dir in "$here"/pairs/*/; do
  name=$(basename "$dir")
  expected=$(cat "$dir/expected-hard")
  got=$(python3 "$lint" --json "$dir/rewrite.md" | python3 -c \
    "import json,sys; print(sum(f['level']=='hard' for f in json.load(sys.stdin)['findings']))")
  if [ "$got" -eq "$expected" ]; then
    echo "ok    $name (硬违规 $got)"
  else
    echo "FAIL  $name: 期望硬违规 $expected，实际 $got"
    fail=1
  fi
  if [ -n "${FIDELITY:-}" ]; then
    if ! python3 "$FIDELITY" "$dir/original.md" "$dir/rewrite.md" >/dev/null; then
      echo "FAIL  $name: 保真检查报告 error"
      fail=1
    fi
  fi
done
exit $fail
