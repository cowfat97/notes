import os
import re
import datetime

NOTES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIMELINE_DIR = os.path.join(NOTES_DIR, "时间线")
OUTPUT_FILE = os.path.join(TIMELINE_DIR, "index.md")

CSS = """---
hide:
  - toc
  - navigation
---

# 时间线

<style>
.tl-entry {
  border-left: 2px solid #00897b;
  margin: 1.5rem 0;
  padding-left: 1.5rem;
  position: relative;
}
.tl-entry::before {
  content: "";
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #00897b;
  position: absolute;
  left: -6px;
  top: 0.35rem;
}
.tl-date {
  font-size: 0.95rem;
  font-weight: 600;
}
.tl-date a {
  color: #00897b;
}
.tl-preview {
  font-size: 0.82rem;
  color: var(--md-default-fg-color--light);
  margin: 0.3rem 0 0 0;
}
</style>
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
    """Extract section headers + first line of each filled section."""
    try:
        with open(filepath, "r") as f:
            content = f.read()

        items = []
        current_section = None
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("## "):
                current_section = stripped[3:]  # remove "## "
                continue
            if current_section and stripped.startswith("- ") and len(stripped) > 3:
                val = stripped[2:]
                if val != "无":
                    items.append(val)
                current_section = None  # one line per section

        return " · ".join(items[:4]) if items else ""
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

        diary_file = (
            "daily-note.md" if "daily-note.md" in md_files else md_files[0]
        )
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

        entries.append((dirname, date_display, preview))

    output = [CSS]

    for dirname, date_display, preview in entries:
        output.append("")
        output.append('<div class="tl-entry">')
        output.append(
            f'  <p class="tl-date"><a href="{dirname}/daily-note/">{date_display} →</a></p>'
        )
        if preview:
            output.append(f'  <p class="tl-preview">{preview}</p>')
        output.append("</div>")

    output.append("")

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(output))

    print(f"Generated {OUTPUT_FILE} with {len(entries)} entries")


if __name__ == "__main__":
    generate_timeline()
