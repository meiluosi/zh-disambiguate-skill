#!/usr/bin/env python3
"""zh-disambiguate 的确定性 linter：检查简体中文里能机械判定的歧义和结构问题。

只查能用正则指出具体字词的规则。省略主语、「了」的时态、
指代对象是否唯一，需要理解上下文，留给模型（见 SKILL.md）。

和 asd-ste100 的 ste-lint.py 一样，本 linter 从不要求删掉情态或 hedge：
「可能已经失败」原样通过。情态词规则只要求把阶梯外的词换成同强度的
阶梯内的词，不要求删除。

用法:
    zh-lint.py FILE [FILE ...]
    echo "文本" | zh-lint.py [--json]
    zh-lint.py --mode flavored FILE        # 风格模式：词汇类规则降为建议
    zh-lint.py --baseline 5 FILE           # 硬违规不超过 5 条时通过
    zh-lint.py --disable weak-verb,de-chain FILE
    zh-lint.py --max-chars 50 --step-max-chars 30 FILE
    zh-lint.py --selftest

退出码：硬违规数超过 --baseline（默认 0）时为 1。建议级（advisory）从不导致失败。
仅用标准库，Python 3.8+。
"""
import argparse
import json
import re
import sys
from collections import defaultdict

CJK = "一-鿿"

# ---------------------------------------------------------------------------
# 规则表
# (名称, 类别, 严格模式级别, 风格模式级别, 正则, 说明)
# 类别 structural 在两种模式下都同样执行；lexical 在风格模式下降为 advisory。
# ---------------------------------------------------------------------------

WEAK_VERB_OBJECTS = (
    "处理|分析|检查|配置|部署|验证|测试|修改|调整|优化|更新|升级|安装|卸载|删除|清理|备份|恢复|重启|"
    "监控|评估|审核|审查|确认|说明|解释|讨论|研究|调查|排查|修复|设置|管理|维护|记录|统计|计算|比较|"
    "对比|转换|迁移|同步|初始化|改进|改造|规划|设计|开发|编译|构建|发布|回滚|扫描|校验|签名|加密|"
    "解密|压缩|解压|匹配|过滤|排序|合并|拆分|切换|连接|断开|授权|认证|登录|注册|通知|提醒|反馈|"
    "响应|判断|决策|选择|预测|诊断|采集|收集|上传|下载|导入|导出|解析|渲染|训练|推理|标注|重试|"
    "调用|请求|查询|检索|索引|缓存|限流|降级|扩容|缩容|调度|编排|封装|重构|审批|核对|核查|整改"
)
WEAK_VERB = re.compile(
    r"(?:进行|作出|做出|予以|加以|开展|实施|给予|执行)了?"
    r"(?:一次|一下|一些|一定的?|相应的?|必要的?|全面的?|详细的?|深入的?|进一步的?|有效的?|统一的?|批量的?|集中的?)?"
    r"(?:" + WEAK_VERB_OBJECTS + r")"
    r"|(?:进行|执行|实施)了?[^，。！？,\n]{0,8}?操作"
)

RULES = [
    ("semicolon", "structural", "hard", "hard",
     re.compile(r"[；;]"),
     "不用分号。拆成两句。"),

    ("weak-verb", "structural", "hard", "hard",
     WEAK_VERB,
     "形式动词加动名词。直接用动词：「进行部署」写成「部署」，「予以删除」写成「删除」。"),

    ("filler", "structural", "hard", "hard",
     re.compile(r"值得注意的是|需要注意的是|需要指出的是|众所周知|综上所述|总而言之|不难看出|显而易见|"
                r"毋庸置疑|不言而喻|在此基础上|在这个过程中|从某种意义上说"),
     "空转短语，不带信息。删掉，直接写事实。"),

    ("slogan", "structural", "hard", "hard",
     re.compile(r"无缝|强大的|极致|一站式|赋能|闭环|抓手|颠覆性?|业界领先|行业领先|毫不费力|全方位|"
                r"全链路|丝滑|极速|高效便捷|轻松(?:实现|搞定|应对)|智能化地|卓越的"),
     "宣传词，只声称质量，不给证据。删掉，或换成能证明它的数字。"),

    ("double-negation", "structural", "hard", "hard",
     re.compile(r"(?<!是)不是不|并非不|(?<!能)不能不|不得不|没有不|无不|(?<!会)不会不|未必不|不可不|非[" + CJK + r"]{1,4}不(?![同仅过])"),
     "双重否定，读者要多做一次取反。改成肯定句：「不得不重启」写成「必须重启」。"),

    ("boundary", "structural", "hard", "advisory",
     re.compile(r"[0-9０-９一二两三四五六七八九十百千万]+\s*(?:%|％|[A-Za-z]{1,3}|毫秒|秒钟?|分钟|小时|天|周|个月|"
                r"年|岁|次|个|条|项|位|人|台|倍|元|行|字节?|MB|GB|KB)?\s*(?:以上|以下|以内|之内|之上|之下|上下)"),
     "边界是否含本数不明确。人和模型对「以上」的理解不一致。写成「≥ 3 次」「不少于 3 次」，或者写明「含 3 次」。"),

    ("modal-off-ladder", "lexical", "hard", "advisory",
     re.compile(r"应该|应当|理应|最好|尽量|务必|尽可能|原则上"),
     "情态词不在阶梯内，强度不明：「应该」可以读成必须，也可以读成建议。"
     "换成同强度的阶梯词（必须/不得、建议/不建议、可以/不必、能/不能、可能），不要删除。"),

    ("hedge-variant", "lexical", "advisory", "advisory",
     re.compile(r"也许|或许|大概(?!\s*\d)|似乎|恐怕|兴许"),
     "推测词变体。统一写成「可能」，保留推测语气，不要删除。"),

    ("partial-negation", "structural", "advisory", "advisory",
     re.compile(r"不都|不全(?!面)|没有全部|没全|未全部|并非全部|并非所有|不是所有|不是全部|并不都"),
     "部分否定，读者容易读成全部否定。写明哪些满足、哪些不满足，或者写成「至少有一个……不……」。"),

    ("vague-quantity", "lexical", "advisory", "advisory",
     re.compile(r"适当的?|尽快|尽早|及时(?!性)|定期|大量的?|少量的?|若干|较大|较小|较多|较少|一段时间|"
                r"必要时|酌情|合理的?(?!性)|相关的?(?!性)|一定程度上?"),
     "模糊词，无法判定是否满足。能写成可判定的条件就写（「定期」写成「每 24 小时」）。"
     "系统确实不知道时（如「请稍后再试」）可以保留。"),

    ("pronoun-start", "structural", "advisory", "advisory",
     re.compile(r"(?:^|(?<=[。！？!?\n；;，,]))\s*(?:它们?|其(?![中他余次实])|这(?![里儿时些个种样次条项])|"
                r"此(?![外时前后处次])|该(?=[，,会将可能把被在已]))"),
     "句首代词：前文有两个以上名词时，读者不知道它指哪个。重复名词，或确认先行词唯一。"),

    ("and-or-mix", "structural", "advisory", "advisory",
     re.compile(r"(?=[^。！？\n]*?(?:和|与|及|以及|并且))(?=[^。！？\n]*?(?:(?<!或许)或(?![许多]|是说)|或者))[^。！？\n]+"),
     "同一句里「和」「或」混用，组合范围不明：「A 和 B 或 C」是 (A和B)或C，还是 A和(B或C)？用列表或拆句写清。"),

    ("nested-passive", "structural", "hard", "hard",
     re.compile(r"被[^。！？，,\n]{1,12}所|得到了?(?:妥善|有效|及时|充分|很好|合理)?的?(?:处理|解决|配置|修复|验证|保障|提升|改善|落实)"),
     "名词化被动或叠套被动，看不出谁做了什么。写成主动句并写明执行者：「已经得到了妥善的配置」写成「管理员已经配置好」。"),

    ("bei-passive", "structural", "advisory", "advisory",
     re.compile(r"被(?!动|告|子|迫|窝|单|褥)"),
     "被字句。执行者已知时改成主动句。只在执行者确实未知或无关时保留。"),

    ("dash-join", "structural", "advisory", "advisory",
     re.compile(r"——|—|--(?=[" + CJK + r"])"),
     "破折号常把两个陈述塞进一句。拆成两句，或者用「因为」「例如」写明关系。"),
]

# 一词一义：常被轮换使用的同义词组。只收真正可互换的词，
# 「验证/校验」在部分领域含义不同，不收。
SYNONYM_GROUPS = [
    ("删除", "移除", "清除"),
    ("配置", "设置"),
    ("修改", "更改", "变更"),
    ("停止", "终止", "中止"),
    ("显示", "展示", "呈现"),
    ("获取", "取得", "拉取"),
    ("检查", "核查", "核对", "检验"),
    ("启动", "开启"),
    ("用户", "使用者"),
    ("报错", "错误信息", "错误消息"),
    ("参数", "入参"),
    ("文件夹", "目录"),
]

DEFAULT_MAX_CHARS = 50       # 描述性句子硬上限
DEFAULT_STEP_MAX_CHARS = 30  # 列表项（步骤）建议上限
DEFAULT_CLAUSE_MAX = 40      # 逗号分句建议上限
DEFAULT_DE_MAX = 2           # 一个分句里「的」的上限

CODE_FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]+`")
URL = re.compile(r"https?://\S+")
MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
LIST_ITEM = re.compile(r"^\s{0,3}(?:[-*+]|\d+[.)、])\s+")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+")
BLOCKQUOTE = re.compile(r"^\s{0,3}>\s?")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
SENT_END = re.compile(r"(?<=[。！？!?])")
CLAUSE_SPLIT = re.compile(r"[，,：:；;、]")
# 「的」的非结构用法：目的、的确、的话、有的、真的、似的
DE_STRUCT = re.compile(r"(?<![目有真似])的(?![确话士])")
TOKEN = re.compile(r"[" + CJK + r"]|[A-Za-z0-9_][\w.\-]*|⁣")


def char_count(s):
    """汉字各计 1，一个英文单词或数字计 1，一个行内代码计 1，标点不计。"""
    return len(TOKEN.findall(s))


def prose_lines(text):
    """逐行返回 (行号, 是否列表项, 清洗后的文本)，跳过代码块和表格分隔行。"""
    in_fence = False
    lines = text.splitlines()
    skip_until = 0
    if lines and lines[0].strip() == "---":            # YAML frontmatter
        for i, raw in enumerate(lines[1:], 2):
            if raw.strip() == "---":
                skip_until = i
                break
    for lineno, raw in enumerate(lines, 1):
        if lineno <= skip_until:
            continue
        if CODE_FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence or not raw.strip() or TABLE_SEP.match(raw):
            continue
        line = BLOCKQUOTE.sub("", raw)
        is_step = bool(LIST_ITEM.match(line))
        line = LIST_ITEM.sub("", line)
        line = HEADING.sub("", line)
        line = INLINE_CODE.sub("⁣", line)   # 行内代码：计 1，规则看不到内容
        line = URL.sub("⁣", line)
        line = MD_LINK.sub(r"\1", line)
        if "|" in line and line.strip().startswith("|"):
            for cell in line.strip().strip("|").split("|"):
                if cell.strip():
                    yield lineno, False, cell.strip()
            continue
        yield lineno, is_step, line


def sentences(line):
    for part in SENT_END.split(line):
        part = part.strip()
        if part:
            yield part


def lint_text(text, mode="strict", disabled=(), max_chars=DEFAULT_MAX_CHARS,
              step_max=DEFAULT_STEP_MAX_CHARS, clause_max=DEFAULT_CLAUSE_MAX,
              de_max=DEFAULT_DE_MAX, path="<stdin>"):
    findings = []

    def add(rule, level, lineno, excerpt, message):
        if rule in disabled:
            return
        findings.append({"file": path, "line": lineno, "rule": rule, "level": level,
                         "excerpt": excerpt.replace("⁣", "`…`"), "message": message})

    lexical_level = "hard" if mode == "strict" else "advisory"
    term_hits = defaultdict(lambda: defaultdict(list))

    for lineno, is_step, line in prose_lines(text):
        for name, kind, strict_level, flavored_level, pattern, message in RULES:
            level = strict_level if mode == "strict" else flavored_level
            for m in pattern.finditer(line):
                excerpt = m.group(0).strip() or line[max(0, m.start() - 6):m.end() + 6]
                if name in ("pronoun-start", "bei-passive"):
                    excerpt = line[m.start():m.start() + 16].strip()
                add(name, level, lineno, _clip(excerpt), message)

        for sent in sentences(line):
            n = char_count(sent)
            if n > max_chars:
                add("sentence-length", "hard", lineno, _clip(sent),
                    f"句子 {n} 字，超过 {max_chars} 字上限。按条件、动作、结果拆句。")
            elif is_step and n > step_max:
                add("step-length", "advisory", lineno, _clip(sent),
                    f"步骤 {n} 字，超过 {step_max} 字。一步只写一个动作。")
            for clause in CLAUSE_SPLIT.split(sent):
                c = char_count(clause)
                if c > clause_max and n <= max_chars:
                    add("clause-length", "advisory", lineno, _clip(clause),
                        f"逗号分句 {c} 字，超过 {clause_max} 字。读者在找不到停顿的地方会读错结构。")
                d = len(DE_STRUCT.findall(clause))
                if d > de_max:
                    add("de-chain", "hard", lineno, _clip(clause),
                        f"一个分句里有 {d} 个「的」，定语层层套叠，读者分不清修饰关系。拆句或改写成动宾结构。")
            commas = len(re.findall(r"[，,]", sent))
            if commas >= 4:
                add("comma-chain", "advisory", lineno, _clip(sent),
                    f"一句用了 {commas} 个逗号串起分句。拆成几句，一句一个意思。")

        for group in SYNONYM_GROUPS:
            for word in group:
                if word in line:
                    term_hits[group][word].append(lineno)

    for group, used in term_hits.items():
        if len(used) >= 2:
            words = " / ".join(f"{w}(第 {','.join(map(str, ls[:3]))} 行)" for w, ls in used.items())
            first_line = min(min(ls) for ls in used.values())
            add("synonym-rotation", lexical_level, first_line, words,
                "同一个概念用了不同的词，读者分不清是一件事还是几件事。全文只用一个词。")

    findings.sort(key=lambda f: (f["file"], f["line"], f["rule"]))
    return findings


def _clip(s, n=40):
    s = s.strip()
    return s if len(s) <= n else s[:n] + "…"


# ---------------------------------------------------------------------------
# 自测
# ---------------------------------------------------------------------------

SELFTEST = [
    # (说明, 文本, 必须出现的硬规则, 不得出现的规则)  {"*"} 表示不得有任何发现
    ("推测语气原样通过", "请求可能已经失败。", set(), {"*"}),
    ("干净的程序性文本", "1. 打开 `config.yaml`。\n2. 把 `timeout` 改成 30。\n3. 重启服务。", set(), {"*"}),
    ("分号", "检查配置；然后重启。", {"semicolon"}, set()),
    ("形式动词", "请对配置文件进行检查。", {"weak-verb"}, set()),
    ("「进行……操作」", "对文件进行批量的重命名操作。", {"weak-verb"}, set()),
    ("「进行中」不算形式动词", "任务正在进行中。", set(), {"weak-verb"}),
    ("「的」字链", "服务器端的连接池的超时时间的默认值是 30 秒。", {"de-chain"}, set()),
    ("「目的」「的确」不计", "这样做的目的的确是为了的话题。", set(), {"de-chain"}),
    ("阶梯外情态词（严格）", "调用方应该先获取令牌。", {"modal-off-ladder"}, set()),
    ("应用 / 响应不是情态词", "应用会返回响应。", set(), {"modal-off-ladder"}),
    ("边界歧义", "重试 3 次以上后报警。", {"boundary"}, set()),
    ("「不少于」不报边界", "重试不少于 3 次后报警。", set(), {"boundary"}),
    ("双重否定", "部署后不得不重启服务。", {"double-negation"}, set()),
    ("空转短语", "值得注意的是，缓存会过期。", {"filler"}, set()),
    ("宣传词", "本工具无缝同步数据。", {"slogan"}, set()),
    ("名词化被动", "访问密钥已经得到了妥善的配置。", {"nested-passive"}, set()),
    ("超长句", "如果用户在配置文件中没有设置超时时间并且网络连接不稳定导致请求在重试三次之后仍然没有成功返回结果那么系统会自动切换到备用节点继续处理剩余请求。",
     {"sentence-length"}, set()),
    ("「会不会不同」是疑问，不是双重否定", "两个读者的动作会不会不同？", set(), {"double-negation"}),
    ("跳过 YAML frontmatter", "---\nname: x；y\n---\n读取文件。", set(), {"*"}),
    ("逗号后的代词", "重试失败后，它会通知管理员。", set(), {"semicolon"}),
    ("同义词轮换（严格）", "删除临时文件。\n然后移除缓存。", {"synonym-rotation"}, set()),
    ("代码块内不检查", "```\na；b 进行处理\n```\n读取文件。", set(), {"*"}),
    ("行内代码不检查", "运行 `rm -rf a;b`。", set(), {"semicolon"}),
    ("「请稍后再试」不是硬违规", "服务繁忙，请稍后再试。", set(), {"semicolon", "weak-verb"}),
]


def selftest():
    failed = 0
    for name, text, must_hard, must_not in SELFTEST:
        found = lint_text(text)
        hard = {f["rule"] for f in found if f["level"] == "hard"}
        allr = {f["rule"] for f in found}
        ok = must_hard <= hard and (not allr if "*" in must_not else not (must_not & allr))
        print(("ok    " if ok else "FAIL  ") + name)
        if not ok:
            failed += 1
            print(f"      期望硬规则 {sorted(must_hard)}，禁止 {sorted(must_not)}，实际 {sorted(allr)}")
    # 风格模式：词汇类规则降级
    flavored = {f["rule"]: f["level"] for f in lint_text("调用方应该先获取令牌。", mode="flavored")}
    if flavored.get("modal-off-ladder") != "advisory":
        failed += 1
        print("FAIL  风格模式下 modal-off-ladder 应为 advisory")
    else:
        print("ok    风格模式下词汇类规则降为 advisory")
    total = len(SELFTEST) + 1
    print(f"\n{total - failed}/{total} 通过")
    return 1 if failed else 0


# ---------------------------------------------------------------------------

def render(findings):
    out = []
    for f in findings:
        tag = "E" if f["level"] == "hard" else "a"
        out.append(f"{f['file']}:{f['line']}: [{tag}] {f['rule']}: 「{f['excerpt']}」 {f['message']}")
    hard = sum(f["level"] == "hard" for f in findings)
    out.append(f"\n{hard} 条硬违规，{len(findings) - hard} 条建议。[E] 硬违规  [a] 建议")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="zh-disambiguate linter：简体中文结构和歧义检查")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--mode", choices=["strict", "flavored"], default="strict",
                    help="strict（默认）：全部执行；flavored：词汇类规则降为建议")
    ap.add_argument("--baseline", type=int, default=0, help="允许的硬违规条数")
    ap.add_argument("--disable", default="", help="逗号分隔的规则名")
    ap.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    ap.add_argument("--step-max-chars", type=int, default=DEFAULT_STEP_MAX_CHARS)
    ap.add_argument("--clause-max-chars", type=int, default=DEFAULT_CLAUSE_MAX)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    disabled = {r.strip() for r in args.disable.split(",") if r.strip()}
    opts = dict(mode=args.mode, disabled=disabled, max_chars=args.max_chars,
                step_max=args.step_max_chars, clause_max=args.clause_max_chars)
    findings = []
    if args.files:
        for path in args.files:
            with open(path, encoding="utf-8") as fh:
                findings += lint_text(fh.read(), path=path, **opts)
    else:
        findings = lint_text(sys.stdin.read(), **opts)

    if args.json:
        print(json.dumps({"findings": findings}, ensure_ascii=False, indent=2))
    else:
        print(render(findings))
    hard = sum(f["level"] == "hard" for f in findings)
    return 1 if hard > args.baseline else 0


if __name__ == "__main__":
    sys.exit(main())
