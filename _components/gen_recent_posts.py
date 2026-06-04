import os
import re
import datetime

NOTES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_DIR = os.path.join(NOTES_DIR, "文章")
OUTPUT_FILE = os.path.join(ARTICLES_DIR, "最新文章.md")


def extract_date_and_title(filepath):
    """从文件 frontmatter 提取 date 和第一个 # 标题。"""
    try:
        with open(filepath, "r") as f:
            content = f.read()
    except Exception:
        return None, None

    # 提取 date
    date_match = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", content, re.MULTILINE)
    date_str = date_match.group(1) if date_match else None

    # 提取标题（第一个 # 开头的行）
    title_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.splitext(os.path.basename(filepath))[0]

    return date_str, title


def generate():
    articles = []
    for root, dirs, files in os.walk(ARTICLES_DIR):
        for f in files:
            if not f.endswith(".md"):
                continue
            filepath = os.path.join(root, f)
            rel_path = os.path.relpath(filepath, NOTES_DIR)

            date_str, title = extract_date_and_title(filepath)
            if not date_str:
                continue

            try:
                date_obj = datetime.date.fromisoformat(date_str)
            except ValueError:
                continue

            articles.append((date_obj, title, rel_path))

    # 按日期倒序
    articles.sort(key=lambda x: x[0], reverse=True)

    lines = [
        "---",
        "hide:",
        "  - toc",
        "---",
        "",
        "# 最新文章",
        "",
        "| 日期 | 标题 |",
        "|------|------|",
    ]

    for date_obj, title, rel_path in articles:
        # 去掉 文章/ 前缀使链接相对
        link_path = rel_path.replace("文章/", "", 1)
        lines.append(f"| {date_obj} | [{title}]({link_path}) |")

    lines.append("")
    lines.append(f"> 共 {len(articles)} 篇 · 自动生成于 {datetime.date.today()}")

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(lines))

    print(f"Generated {OUTPUT_FILE} with {len(articles)} articles")


if "__main__" == __name__:
    generate()
