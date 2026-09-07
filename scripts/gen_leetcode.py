#!/usr/bin/env python3
"""扫描 leetcode/*.py，为每个题解生成同名 .md（题目名标题 + 代码块）。

标题映射来自 leetcode/index.md 表格（题号 → 题目名），找不到时退回文件名。
幂等：内容未变不重写。
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEETCODE_DIR = REPO_ROOT / "文章" / "leetcode"
PY_DIR = LEETCODE_DIR / "py"
OUT_DIR = LEETCODE_DIR / "题解"
INDEX = LEETCODE_DIR / "index.md"


def load_title_map() -> dict[str, str]:
    title_map = {}
    if not INDEX.exists():
        return title_map
    text = INDEX.read_text(encoding="utf-8")
    for line in text.splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|", line)
        if m:
            title_map[m.group(1)] = m.group(2).strip()
    return title_map


def main() -> int:
    title_map = load_title_map()
    OUT_DIR.mkdir(exist_ok=True)
    generated = 0
    for py in sorted(PY_DIR.glob("*.py")):
        num = re.match(r"(\d+)", py.stem)
        if num:
            name = title_map.get(num.group(1))
            title = f"{num.group(1)}. {name}" if name else py.stem
        else:
            title = py.stem
        code = py.read_text(encoding="utf-8").rstrip()
        md = OUT_DIR / f"{py.stem}.md"
        content = f"# {title}\n\n```python\n{code}\n```\n"
        if md.exists() and md.read_text(encoding="utf-8") == content:
            continue
        md.write_text(content, encoding="utf-8")
        generated += 1
        print(f"已生成: {md.relative_to(REPO_ROOT)}")
    if generated == 0:
        print("leetcode 题解 md 均已是最新。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
