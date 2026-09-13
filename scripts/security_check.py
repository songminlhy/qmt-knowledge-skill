#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
security_check.py

CI regression gate for qmt-knowledge-skill.

Design:
- qmt_semantic_scan.py = fact extractor
- security-baseline.json = owner-reviewed allowlist after P0-1/P0-2
- this file = fail only on NEW security findings or warning regressions

No third-party dependencies.
Does not modify repository files unless --write-baseline is explicitly used.
"""
from __future__ import print_function

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SCHEMA = "qmt-security-baseline.v1"
RELEVANT_KINDS = {
    "account_like_numeric",
    "quicktrade_2",
}


def repo_root():
    return Path(__file__).resolve().parents[1]


def scanner_path(root):
    return (
        root
        / "scripts"
        / "qmt_semantic_scan.py"
    )


def baseline_path(root):
    return (
        root
        / "scripts"
        / "security-baseline.json"
    )


def sha256_file(path):
    # Normalize line endings to LF so hash is identical
    # on Windows (CRLF checkout) and Linux (LF checkout).
    raw = path.read_bytes()
    normalized = (
        raw.replace(b"\r\n", b"\n")
        .replace(b"\r", b"\n")
    )
    return hashlib.sha256(normalized).hexdigest()


def git_head(root):
    p = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "rev-parse",
            "HEAD",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    return (
        p.stdout.strip()
        if p.returncode == 0
        else None
    )


def normalize_anchor(value):
    return re.sub(
        r"\s+",
        " ",
        (value or "").strip()
    )


def canonical_finding(f):
    """
    Stable across line-number movement.

    Deliberately excludes raw0/editor1 line numbers
    and warning_coverage.

    warning_coverage is enforced separately as a policy.
    """
    return {
        "kind": f.get("kind"),
        "path": f.get("path"),
        "source": f.get("source"),
        "function": f.get("function"),
        "value": f.get("value"),
        "quicktrade_arg": f.get(
            "quicktrade_arg"
        ),
        "anchor": normalize_anchor(
            f.get("anchor")
        ),
    }


def fingerprint(f):
    payload = json.dumps(
        canonical_finding(f),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(
        payload
    ).hexdigest()


def relevant(findings):
    return [
        f
        for f in findings
        if (
            f.get("kind") in RELEVANT_KINDS
            and f.get("active", True)
        )
    ]


def load_scanner(root):
    # Import from scripts/ without
    # requiring package installation.
    scripts_dir = root / "scripts"

    sys.path.insert(
        0,
        str(scripts_dir)
    )

    import qmt_semantic_scan

    return qmt_semantic_scan


def scan_current(root):
    scanner = load_scanner(root)

    return relevant(
        scanner.scan_repo(root)
    )


def unsafe_warning_regressions(findings):
    """
    A quickTrade=2 call may be baseline-allowed
    only if some risk warning still covers it.

    Removing all warning coverage is an
    immediate failure.
    """
    return [
        f
        for f in findings
        if (
            f.get("kind") == "quicktrade_2"
            and f.get(
                "warning_coverage"
            ) == "none_detected"
        )
    ]


def baseline_record(f):
    c = canonical_finding(f)

    return {
        "fingerprint": fingerprint(f),
        "kind": c["kind"],
        "path": c["path"],
        "source": c["source"],
        "function": c["function"],
        "value": c["value"],
        "quicktrade_arg": c[
            "quicktrade_arg"
        ],
        "anchor": c["anchor"],

        # Informational only;
        # not part of the fingerprint.
        "editor1_line_at_freeze":
            f.get("editor1_line"),

        "warning_coverage_at_freeze":
            f.get(
                "warning_coverage"
            ),
    }


def write_baseline(root, findings):
    bad = unsafe_warning_regressions(
        findings
    )

    if bad:
        print(
            "[FAIL] Refusing to freeze baseline: "
            "quickTrade=2 without warning coverage:"
        )

        for f in bad:
            print(
                "  - %s:%s %s"
                % (
                    f.get("path"),
                    f.get("editor1_line"),
                    normalize_anchor(
                        f.get("anchor")
                    ),
                )
            )

        return 1

    sp = scanner_path(root)

    payload = {
        "schema": SCHEMA,
        "generated_from_commit":
            git_head(root),

        "scanner_sha256":
            sha256_file(sp),

        "policy": {
            "mode":
                "regression_only",

            "account_like_numeric":
                "new findings fail",

            "quicktrade_2":
                (
                    "new findings fail; "
                    "warning_coverage="
                    "none_detected always fails"
                ),

            "auto_modify_code":
                False,
        },

        "allowed_findings":
            sorted(
                [
                    baseline_record(f)
                    for f in findings
                ],
                key=lambda x: (
                    x["path"],
                    x["kind"],
                    x["fingerprint"],
                ),
            ),
    }

    bp = baseline_path(root)

    bp.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "[OK] Baseline written: %s"
        % bp
    )

    print(
        "[OK] Allowed findings: %d"
        % len(
            payload["allowed_findings"]
        )
    )

    print(
        "[REVIEW REQUIRED] "
        "Inspect and commit "
        "security-baseline.json manually."
    )

    return 0


def check(root, findings):
    bp = baseline_path(root)

    if not bp.exists():
        print(
            "[FAIL] Missing "
            "scripts/security-baseline.json"
        )

        print(
            "       After owner review, "
            "generate once with:"
        )

        print(
            "       python3 "
            "scripts/security_check.py "
            "--write-baseline"
        )

        return 2

    baseline = json.loads(
        bp.read_text(
            encoding="utf-8"
        )
    )

    if baseline.get("schema") != SCHEMA:
        print(
            "[FAIL] Unsupported "
            "baseline schema: %r"
            % baseline.get("schema")
        )

        return 2

    expected_scanner_hash = baseline.get(
        "scanner_sha256"
    )

    actual_scanner_hash = sha256_file(
        scanner_path(root)
    )

    if (
        expected_scanner_hash
        != actual_scanner_hash
    ):
        print(
            "[FAIL] qmt_semantic_scan.py "
            "changed since baseline freeze."
        )

        print(
            "       baseline: %s"
            % expected_scanner_hash
        )

        print(
            "       current:  %s"
            % actual_scanner_hash
        )

        print(
            "       Review scanner changes, "
            "then regenerate baseline "
            "intentionally."
        )

        return 2

    bad_warning = (
        unsafe_warning_regressions(
            findings
        )
    )

    if bad_warning:
        print(
            "[FAIL] quickTrade=2 call(s) "
            "lost all recognized "
            "warning coverage:"
        )

        for f in bad_warning:
            print(
                "  - %s:%s %s"
                % (
                    f.get("path"),
                    f.get(
                        "editor1_line"
                    ),
                    normalize_anchor(
                        f.get(
                            "anchor"
                        )
                    ),
                )
            )

        return 1

    allowed = {
        item["fingerprint"]
        for item in baseline.get(
            "allowed_findings",
            []
        )
    }

    current = {
        fingerprint(f): f
        for f in findings
    }

    new_keys = sorted(
        set(current)
        - allowed
    )

    if new_keys:
        print(
            "[FAIL] New security finding(s) "
            "not present in "
            "owner-reviewed baseline: %d"
            % len(new_keys)
        )

        for key in new_keys:
            f = current[key]

            print(
                "  - %s:%s [%s] %s"
                % (
                    f.get("path"),
                    f.get(
                        "editor1_line"
                    ),
                    f.get("kind"),
                    normalize_anchor(
                        f.get(
                            "anchor"
                        )
                    ),
                )
            )

        print("")

        print(
            "Do NOT auto-update "
            "the baseline in CI."
        )

        print(
            "Review the finding; fix it "
            "or deliberately regenerate "
            "the baseline in a "
            "reviewed change."
        )

        return 1

    removed = len(
        allowed
        - set(current)
    )

    print(
        "[PASS] No new "
        "QMT security regressions."
    )

    print(
        "[INFO] Current relevant "
        "findings: %d"
        % len(current)
    )

    if removed:
        print(
            "[INFO] %d baseline "
            "finding(s) disappeared; "
            "deletions are allowed."
            % removed
        )

    return 0


def main():
    ap = argparse.ArgumentParser()

    ap.add_argument(
        "--write-baseline",
        action="store_true",
        help=(
            "Explicit owner-reviewed "
            "baseline generation; "
            "never used by CI."
        ),
    )

    ns = ap.parse_args()

    root = repo_root()
    sp = scanner_path(root)

    if not sp.exists():
        print(
            "[FAIL] Missing scanner: %s"
            % sp
        )

        return 2

    findings = scan_current(root)

    if ns.write_baseline:
        return write_baseline(
            root,
            findings
        )

    return check(
        root,
        findings
    )


if __name__ == "__main__":
    raise SystemExit(main())
