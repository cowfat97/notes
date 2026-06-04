import os
import re
import datetime

NOTES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIMELINE_DIR = os.path.join(NOTES_DIR, "时间线")
OUTPUT_FILE = os.path.join(TIMELINE_DIR, "index.md")

CSS = """---
hide:
  - toc
---

# 时间线

<link rel="stylesheet" href="../_components/timeline.css">
"""


def get_location(filepath):
    """Extract location from diary content."""
    try:
        with open(filepath, "r") as f:
            for line in f:
                m = re.match(r"^- 地点：(.*)", line.strip())
                if m:
                    return m.group(1)
    except Exception:
        pass
    return "北京"


def get_preview(filepath):
    """Extract the 想法 section content."""
    try:
        with open(filepath, "r") as f:
            content = f.read()

        in_thought = False
        lines = []
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("## "):
                if in_thought:
                    break
                in_thought = ("想法" in stripped)
                continue
            if in_thought and stripped and not stripped.startswith("#"):
                return stripped.lstrip("- ")
    except Exception:
        return ""


def generate_timeline():
    entries = []

    for dirname in sorted(os.listdir(TIMELINE_DIR), reverse=True):
        dirpath = os.path.join(TIMELINE_DIR, dirname)
        if not os.path.isdir(dirpath):
            continue
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", dirname):
            continue

        md_files = [f for f in os.listdir(dirpath) if f.endswith(".md")]
        if not md_files:
            continue

        diary_file = md_files[0]
        diary_slug = os.path.splitext(diary_file)[0]
        diary_path = os.path.join(dirpath, diary_file)
        preview = get_preview(diary_path)
        location = get_location(diary_path)

        try:
            date_obj = datetime.date.fromisoformat(dirname)
            weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][
                date_obj.weekday()
            ]
            date_display = f"{dirname} · {weekday} · {location}"
        except ValueError:
            date_display = dirname

        entries.append((dirname, date_display, preview, diary_slug))

    output = [CSS]
    output.append("")
    output.append('<div class="tl-scroll">')

    for dirname, date_display, preview, diary_slug in entries:
        output.append("")
        output.append('<div class="tl-entry">')
        output.append(
            f'  <p class="tl-date"><a href="{dirname}/{diary_slug}/">{date_display} →</a></p>'
        )
        if preview:
            output.append(f'  <p class="tl-preview">{preview}</p>')
        output.append("</div>")

    output.append("</div>")

    output.append("")

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(output))

    print(f"Generated {OUTPUT_FILE} with {len(entries)} entries")


if __name__ == "__main__":
    generate_timeline()
