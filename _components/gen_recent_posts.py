import os
import re
import datetime

NOTES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_DIR = os.path.join(NOTES_DIR, "文章")
OUTPUT_FILE = os.path.join(ARTICLES_DIR, "最新文章.md")
INDEX_FILE = os.path.join(NOTES_DIR, "index.md")
TOP_N = 1


def extract_date_and_title(filepath):
    try:
        with open(filepath, "r") as f:
            content = f.read()
    except Exception:
        return None, None

    date_match = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", content, re.MULTILINE)
    date_str = date_match.group(1) if date_match else None

    title_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.splitext(os.path.basename(filepath))[0]

    return date_str, title


def collect_articles():
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

    articles.sort(key=lambda x: x[0], reverse=True)
    return articles


def generate_full_list(articles):
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
        link_path = rel_path.replace("文章/", "", 1)
        lines.append(f"| {date_obj} | [{title}]({link_path}) |")

    lines.append("")
    lines.append(f"> 共 {len(articles)} 篇 · 自动生成于 {datetime.date.today()}")

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(lines))

    print(f"Generated {OUTPUT_FILE} with {len(articles)} articles")


def update_index_recent(articles):
    recent = articles[:TOP_N]
    items = []
    for date_obj, title, rel_path in recent:
        items.append(f"[{title}]({rel_path}) · {date_obj}")

    block = "\n\n".join(items)

    with open(INDEX_FILE, "r") as f:
        content = f.read()

    pattern = r"(<!-- recent-posts-start -->).*?(<!-- recent-posts-end -->)"
    replacement = f"\\1\n\n{block}\n\n\\2"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(INDEX_FILE, "w") as f:
        f.write(content)

    print(f"Updated {INDEX_FILE} with {len(recent)} recent posts")


def generate():
    articles = collect_articles()
    generate_full_list(articles)
    update_index_recent(articles)


if __name__ == "__main__":
    generate()
