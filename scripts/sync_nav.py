#!/usr/bin/env python3
"""扫描仓库中未被 mkdocs nav 收录的 .md 文件，自动添加到 nav 中。"""

import os
import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / ".mkdocs" / "mkdocs.yml"

EXCLUDE = {
    "README.md", "CLAUDE.md", "plan.md", "index.md",
}
EXCLUDE_DIRS = {"posts", ".github", ".mkdocs", "site", ".claude", ".git",
                "scripts", "__pycache__", "Pic", "envs"}

TOP_MAPPING = {
    "Java": "Java", "中间件": "中间件", "数据库": "数据库",
    "LLM": "LLM", "408": "408", "leetcode": "LeetCode", "软考": "软考",
}

SUB_MATCH = {
    ("LLM", "Agent"): "Agent",
    ("LLM", "Rag"): "RAG",
    ("Java", "mybatis"): "MyBatis",
    ("Java", "spring"): "Spring IoC",
}


def find_all_md_files() -> set[str]:
    md_files = set()
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for f in files:
            if not f.endswith(".md") or f in EXCLUDE:
                continue
            rel = os.path.relpath(os.path.join(root, f), REPO_ROOT)
            md_files.add(rel)
    return md_files


def extract_nav_paths(nav_items) -> set[str]:
    """递归提取 nav 中所有文件路径。"""
    paths = set()
    if isinstance(nav_items, str):
        paths.add(nav_items.strip())
    elif isinstance(nav_items, list):
        for item in nav_items:
            if isinstance(item, str):
                paths.add(item.strip())
            elif isinstance(item, dict):
                for val in item.values():
                    paths.update(extract_nav_paths(val))
    return paths


def find_target_list(nav: list, filepath: str):
    """在 nav 中查找文件应该插入的位置，返回目标 list。"""
    parts = Path(filepath).parts
    top_dir = parts[0]
    section_key = TOP_MAPPING.get(top_dir)
    if not section_key:
        return None

    # 定位顶层 section
    top_item = None
    for item in nav:
        if isinstance(item, dict) and section_key in item:
            top_item = item
            break
    if top_item is None:
        return None

    current_list = top_item[section_key]
    if not isinstance(current_list, list):
        return None

    if len(parts) == 1:
        return current_list

    # 有子目录，尝试匹配子 section
    for depth in range(1, len(parts)):
        sub_key = parts[depth].lower()
        # 优先精确匹配
        for item in current_list:
            if isinstance(item, dict):
                for k, v in item.items():
                    if isinstance(v, list) and k.lower().replace(" ", "") == sub_key:
                        current_list = v
                        break
                else:
                    continue
                break

    return current_list


def format_name(filepath: str) -> str:
    return Path(filepath).stem


def dump_nav_yaml(nav, indent=0) -> list[str]:
    """将 nav 结构转为格式化 YAML 行，缩进 4 空格。"""
    lines = []
    pf = "  " + "    " * indent

    if isinstance(nav, str):
        lines.append(f"{pf}- {nav}\n")
    elif isinstance(nav, list):
        for item in nav:
            if isinstance(item, str):
                lines.append(f"{pf}- {item}\n")
            elif isinstance(item, dict):
                for key, val in item.items():
                    if isinstance(val, str):
                        lines.append(f"{pf}- {key}: {val}\n")
                    elif isinstance(val, list):
                        lines.append(f"{pf}- {key}:\n")
                        lines.extend(dump_nav_yaml(val, indent + 1))
    return lines


def _noop(loader, tag_suffix, node):
    return node.value


def main():
    yaml.SafeLoader.add_multi_constructor("tag:yaml.org,2002:python/name", _noop)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    nav = config.get("nav", [])
    nav_paths = extract_nav_paths(nav)
    all_md = find_all_md_files()
    missing = sorted(all_md - nav_paths)

    if not missing:
        print("所有 .md 文件已在 nav 中，无需同步。")
        return 0

    print(f"发现 {len(missing)} 个遗漏文件:")
    for f in missing:
        print(f"  - {f}")

    added = 0
    for filepath in missing:
        target = find_target_list(nav, filepath)
        if target is None:
            print(f"跳过 {filepath}（无法确定所属栏目）")
            continue

        name = format_name(filepath)
        existing_paths = extract_nav_paths(target)
        if filepath in existing_paths:
            continue

        target.append({name: filepath})
        added += 1
        print(f"已添加: {name} → {filepath}")

    if added == 0:
        print("没有可自动添加的文件。")
        return 0

    # 读原始内容，替换 nav 部分
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        original_lines = f.readlines()

    nav_start = None
    for i, line in enumerate(original_lines):
        if line.startswith("nav:"):
            nav_start = i
            break

    new_nav_lines = ["nav:\n"]
    new_nav_lines.extend(dump_nav_yaml(nav))
    new_nav_lines.append("\n")

    result = original_lines[:nav_start] + new_nav_lines
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.writelines(result)

    print(f"已更新 {CONFIG_PATH}，新增 {added} 条导航。")
    return added


if __name__ == "__main__":
    sys.exit(0 if main() else 0)
