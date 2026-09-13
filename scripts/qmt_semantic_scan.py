#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qmt_semantic_scan.py

Purpose:
  Freeze evidence before editing qmt-knowledge-skill.
  - Verify the checkout is at the expected commit SHA.
  - Scan Markdown fenced code semantically for active quickTrade=2 calls.
  - Scan account-context numeric string literals without treating all numbers as accounts.
  - Separate active code, commented code, declared/obvious placeholders, and output fields.
  - Produce JSON + Markdown reports.

No third-party packages required.

Example:
  python qmt_semantic_scan.py /path/to/qmt-knowledge-skill \
      --expected-sha 4dbdc8036baa43fdfa39784b632dd25382a5e68f \
      --out-dir ./scan-out

Self-test:
  python qmt_semantic_scan.py --self-test
"""
from __future__ import print_function
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

TARGET_CALLS = ("passorder", "algo_passorder", "smart_algo_passorder")
ACCOUNT_ARG_FUNCS = {
    "get_assure_contract": 0,
    "get_enable_short_contract": 0,
    "get_option_subject_position": 0,
    "get_comb_option": 0,
    "get_unclosed_compacts": 0,
    "get_closed_compacts": 0,
    "get_debt_contract": 0,
    "get_hkt_exchange_rate": 0,
}
LAST_ARG_ACCOUNT_FUNCS = {
    "order_lots", "order_value", "order_percent",
    "order_target_value", "order_target_percent", "order_shares",
    "buy_open", "buy_close_tdayfirst", "buy_close_ydayfirst",
    "sell_open", "sell_close_tdayfirst", "sell_close_ydayfirst",
}
NUMERIC_STRING = re.compile(r"""^(['"])(\d{5,15})\1$""")
ASSIGN_ACCOUNT = re.compile(
    r"""(?ix)
    \b(?:ContextInfo\.)?
    (?:account|accountid|account_id|accid|acc_id|account_str)
    \s*=\s*(['"])(\d{5,15})\1
    """
)
DICT_ACCOUNT = re.compile(
    r"""(?ix)
    ['"](?:m_strAccountID|accountID|accountId|account_id)['"]
    \s*:\s*(['"])(\d{5,15})\1
    """
)
MASKED = re.compile(r"(?i)(\*{2,}|<\s*(?:MASKED|ACCOUNT_ID)\s*>|test(?:account)?$)")


def git_head(root):
    p = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if p.returncode != 0:
        raise RuntimeError("not a git checkout: %s" % p.stderr.strip())
    return p.stdout.strip()


def strip_py_comment(line):
    """Remove # comment outside quotes, keeping code before it."""
    out = []
    quote = None
    esc = False
    for ch in line:
        if esc:
            out.append(ch)
            esc = False
            continue
        if ch == "\\":
            out.append(ch)
            esc = True
            continue
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            out.append(ch)
            continue
        if ch == "#":
            break
        out.append(ch)
    return "".join(out)


def split_top_level_args(s):
    args, cur = [], []
    stack = []
    quote = None
    esc = False
    pairs = {")": "(", "]": "[", "}": "{"}
    for ch in s:
        if esc:
            cur.append(ch)
            esc = False
            continue
        if ch == "\\":
            cur.append(ch)
            esc = True
            continue
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            cur.append(ch)
            continue
        if ch in "([{":
            stack.append(ch)
            cur.append(ch)
            continue
        if ch in ")]}":
            if stack and stack[-1] == pairs[ch]:
                stack.pop()
            cur.append(ch)
            continue
        if ch == "," and not stack:
            args.append("".join(cur).strip())
            cur = []
            continue
        cur.append(ch)
    if cur or s.strip():
        args.append("".join(cur).strip())
    return args


def collect_call(lines, start_idx, col):
    """Collect a possibly multiline function call, balancing parentheses."""
    text = lines[start_idx][col:]
    depth = 0
    quote = None
    esc = False
    seen_open = False
    end_idx = start_idx
    for i in range(start_idx, len(lines)):
        part = lines[i][col:] if i == start_idx else lines[i]
        if i != start_idx:
            text += "\n" + part
        for ch in part:
            if esc:
                esc = False
                continue
            if ch == "\\":
                esc = True
                continue
            if quote:
                if ch == quote:
                    quote = None
                continue
            if ch in ("'", '"'):
                quote = ch
                continue
            if ch == "(":
                depth += 1
                seen_open = True
            elif ch == ")":
                depth -= 1
                if seen_open and depth == 0:
                    end_idx = i
                    return text, end_idx
        end_idx = i
    return text, end_idx


def parse_call(call_text):
    m = re.search(
        r"\b(passorder|algo_passorder|smart_algo_passorder)\s*\(",
        call_text
    )
    if not m:
        # Generic support for account functions below.
        m = re.search(r"\b([A-Za-z_]\w*)\s*\(", call_text)
    if not m:
        return None, []

    name = m.group(1)
    open_pos = call_text.find("(", m.start())

    # Find matching final ')' conservatively: call_text is already balanced.
    inner = call_text[open_pos + 1:]
    if inner.rstrip().endswith(")"):
        inner = inner.rstrip()[:-1]

    return name, split_top_level_args(inner)


def numeric_literal(arg):
    a = arg.strip()
    m = NUMERIC_STRING.match(a)
    return m.group(2) if m else None


def quicktrade_arg(name, args):
    if name not in TARGET_CALLS:
        return None

    # QMT supports a short passorder overload:
    #   (..., volume, quickTrade, ContextInfo) => 9 args total,
    #   quickTrade index 7
    #
    # Long passorder/algo/smart forms put quickTrade at index 8.
    if name == "passorder" and len(args) == 9:
        return args[7]

    if len(args) >= 10:
        return args[8]

    return None


def in_fences(lines):
    state = False
    arr = []

    for line in lines:
        stripped = line.lstrip()

        if stripped.startswith("```"):
            arr.append(state)
            state = not state
        else:
            arr.append(state)

    return arr


def scan_markdown(path, root):
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines()
    fenced = in_fences(lines)
    findings = []
    rel = path.relative_to(root).as_posix()

    # Account assignments / output fields in all text, but classify code state.
    for i, line in enumerate(lines):
        for rx, source in (
            (ASSIGN_ACCOUNT, "assignment"),
            (DICT_ACCOUNT, "dict_field"),
        ):
            for m in rx.finditer(line):
                findings.append({
                    "kind": "account_like_numeric",
                    "path": rel,
                    "raw0_line": i,
                    "editor1_line": i + 1,
                    "value": m.group(2),
                    "source": source,
                    "in_code_fence": bool(fenced[i]),
                    "active": not line.lstrip().startswith("#"),
                    "anchor": line.strip()[:240],
                })

    # Collect function calls from active fenced code only.
    i = 0

    while i < len(lines):
        line = lines[i]

        if not fenced[i] or line.lstrip().startswith("#"):
            i += 1
            continue

        code = strip_py_comment(line)

        # Search all supported call names and known account helpers.
        names = (
            list(TARGET_CALLS)
            + list(ACCOUNT_ARG_FUNCS)
            + list(LAST_ARG_ACCOUNT_FUNCS)
        )

        match = None

        for nm in names:
            mm = re.search(r"\b" + re.escape(nm) + r"\s*\(", code)

            if mm and (match is None or mm.start() < match[1].start()):
                match = (nm, mm)

        if not match:
            i += 1
            continue

        nm, mm = match
        call_text, end_i = collect_call(lines, i, mm.start())
        name, args = parse_call(call_text)

        # quickTrade semantic position
        qarg = quicktrade_arg(name, args)

        if qarg is not None and qarg.strip() == "2":
            findings.append({
                "kind": "quicktrade_2",
                "path": rel,
                "raw0_line": i,
                "editor1_line": i + 1,
                "function": name,
                "arg_count": len(args),
                "quicktrade_arg": qarg.strip(),
                "active": True,
                "in_code_fence": True,
                "anchor": " ".join(call_text.split())[:320],
            })

        # direct account arg in passorder-family
        if name in TARGET_CALLS and len(args) >= 3:
            v = numeric_literal(args[2])

            if v:
                findings.append({
                    "kind": "account_like_numeric",
                    "path": rel,
                    "raw0_line": i,
                    "editor1_line": i + 1,
                    "value": v,
                    "source": name + "_account_arg",
                    "active": True,
                    "in_code_fence": True,
                    "anchor": " ".join(call_text.split())[:320],
                })

        # known first-arg account helpers
        if name in ACCOUNT_ARG_FUNCS and args:
            idx = ACCOUNT_ARG_FUNCS[name]

            if idx < len(args):
                v = numeric_literal(args[idx])

                if v:
                    findings.append({
                        "kind": "account_like_numeric",
                        "path": rel,
                        "raw0_line": i,
                        "editor1_line": i + 1,
                        "value": v,
                        "source": name + "_account_arg",
                        "active": True,
                        "in_code_fence": True,
                        "anchor": " ".join(call_text.split())[:320],
                    })

        # helper APIs with optional accId as final argument
        if name in LAST_ARG_ACCOUNT_FUNCS and args:
            v = numeric_literal(args[-1])

            if v:
                findings.append({
                    "kind": "account_like_numeric",
                    "path": rel,
                    "raw0_line": i,
                    "editor1_line": i + 1,
                    "value": v,
                    "source": name + "_accId",
                    "active": True,
                    "in_code_fence": True,
                    "anchor": " ".join(call_text.split())[:320],
                })

        i = max(i + 1, end_i + 1)

    return findings


def warning_coverage(lines, line_idx, fenced=None):
    """
    Lightweight classifier.

    Intentionally does not decide whether a warning is sufficient.
    """
    if fenced is None:
        fenced = in_fences(lines)

    lo = max(0, line_idx - 12)
    near = "\n".join(lines[lo:line_idx])

    if (
        ("🚫" in near or "⚠" in near)
        and (
            "quickTrade" in near
            or "实盘" in near
            or "风险" in near
        )
    ):
        return "local_or_nearby"

    # File opening 12 lines.
    top = "\n".join(lines[:12])

    if (
        ("🚫" in top or "⚠" in top)
        and (
            "quickTrade" in top
            or "实盘" in top
            or "风险" in top
        )
    ):
        return "file_level"

    # Nearest markdown heading block.
    # Must be a real markdown heading (outside fences) — not a python comment.
    h = line_idx - 1

    while h >= 0:
        if fenced[h]:
            h -= 1
            continue
        if re.match(r"^#{1,6}\s+\S", lines[h].rstrip()):
            break
        h -= 1

    if h >= 0:
        block = "\n".join(lines[h:line_idx])

        if (
            ("🚫" in block or "⚠" in block)
            and (
                "quickTrade" in block
                or "实盘" in block
                or "风险" in block
            )
        ):
            return "section_level"

    return "none_detected"


def scan_repo(root):
    out = []

    for p in sorted(root.rglob("*.md")):
        fs = scan_markdown(p, root)
        lines = p.read_text(
            encoding="utf-8-sig",
            errors="replace"
        ).splitlines()
        fenced = in_fences(lines)

        for x in fs:
            x["warning_coverage"] = warning_coverage(
                lines,
                x["raw0_line"],
                fenced
            )

        out.extend(fs)

    # Deduplicate same semantic hit emitted by assignment +
    # function handling if any.
    uniq = {}

    for x in out:
        key = (
            x["kind"],
            x["path"],
            x["raw0_line"],
            x.get("value"),
            x.get("source"),
            x.get("function"),
        )
        uniq[key] = x

    return list(uniq.values())


def self_test():
    tmp = Path(
        os.environ.get("TMPDIR", "/tmp")
    ) / "qmt_semantic_scan_selftest"

    tmp.mkdir(parents=True, exist_ok=True)

    f = tmp / "fixture.md"

    f.write_text(
        """# fixture
> 🚫 risk warning
```python
# long: volume=2 AND quickTrade=2
passorder(35,2101,'1234567','basket1',5,-1,2,'basket',2,'remark',C)
# short overload: quickTrade=2
passorder(60,1101,'test','510030.SH',5,0,1,2,C)
# false positive control: volume=2 but quickTrade=1
passorder(50,1101,'test','10005330.SHO',5,-1,2,1,C)
# commented-out call must be ignored
# passorder(23,1101,'7654321','000001.SZ',5,0,100,'x',2,'r',C)
ContextInfo.accid = '6000000248'
smart_algo_passorder(
  23,1101,account,'600000.SH',12,0,10000,'',
  2,'remark','VWAP','10:25:00','14:50:00',algoParam,C
)
````

""",
    encoding="utf-8"
    )

    findings = scan_markdown(f, tmp)

    q = [
    x for x in findings
    if x["kind"] == "quicktrade_2"
    ]

    a = [
    x for x in findings
    if x["kind"] == "account_like_numeric"
    ]

    assert len(q) == 3, q

    # direct passorder numeric account + assignment = 2;
    # commented numeric account excluded
    assert any(
    x.get("value") == "1234567"
    for x in a
    ), a

    assert any(
    x.get("value") == "6000000248"
    for x in a
    ), a

    assert not any(
    x.get("value") == "7654321"
    for x in a
    ), a

    # Ensure option call volume=2 quickTrade=1 was not flagged.
    assert not any(
    "10005330.SHO" in x.get("anchor", "")
    for x in q
    ), q

    print("SELF_TEST: PASS")
    return 0

def main():
    ap = argparse.ArgumentParser()

    ap.add_argument(
        "repo",
        nargs="?"
    )

    ap.add_argument(
        "--expected-sha"
    )

    ap.add_argument(
        "--out-dir",
        default="scan-out"
    )

    ap.add_argument(
        "--self-test",
        action="store_true"
    )

    ns = ap.parse_args()

    if ns.self_test:
        return self_test()

    if not ns.repo:
        ap.error(
            "repo path required unless --self-test is used"
        )

    root = Path(ns.repo).resolve()

    if ns.expected_sha:
        head = git_head(root)

        if head != ns.expected_sha:
            raise SystemExit(
                "SHA mismatch: expected %s, got %s"
                % (
                    ns.expected_sha,
                    head
                )
            )

    findings = scan_repo(root)

    out_dir = Path(ns.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "repo": str(root),
        "head": git_head(root),
        "findings": findings,
    }

    (
        out_dir / "semantic-scan.json"
    ).write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # Compact Markdown summary
    counts = {}

    for x in findings:
        counts[x["kind"]] = (
            counts.get(x["kind"], 0) + 1
        )

    md = [
        "# Semantic scan",
        "",
        "Commit: `%s`" % result["head"],
        "",
        "## Counts",
        "",
    ]

    for k in sorted(counts):
        md.append(
            "- `%s`: %d"
            % (
                k,
                counts[k]
            )
        )

    md += [
        "",
        "## Findings",
        ""
    ]

    for x in sorted(
        findings,
        key=lambda z: (
            z["path"],
            z["raw0_line"],
            z["kind"]
        )
    ):
        md.append(
            "- `%s:%d` (%s) `%s` — `%s`"
            % (
                x["path"],
                x["editor1_line"],
                x["kind"],
                x.get("anchor", ""),
                x.get(
                    "warning_coverage",
                    ""
                ),
            )
        )

    (
        out_dir / "semantic-scan.md"
    ).write_text(
        "\n".join(md),
        encoding="utf-8"
    )

    print(
        json.dumps(
            counts,
            ensure_ascii=False
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
