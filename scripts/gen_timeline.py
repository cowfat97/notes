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
.timeline {
  position: relative;
  padding-left: 2rem;
}
.timeline::before {
  content: "";
  position: absolute;
  left: 0.5rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #00897b;
  opacity: 0.3;
}
.tl-entry {
  position: relative;
  margin-bottom: 2rem;
  padding-left: 1.5rem;
}
.tl-dot {
  position: absolute;
  left: -1.8rem;
  top: 0.35rem;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #00897b;
}
.tl-date {
  font-size: 0.8rem;
  color: #00897b;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.tl-body {
  background: var(--md-card-bg);
  border-radius: 10px;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
[data-md-color-scheme="slate"] .tl-body {
  background: #1c2128;
  border: 1px solid rgba(255,255,255,0.06);
}
.tl-body h2 {
  margin-top: 0;
  font-size: 0.95rem;
}
.tl-body p {
  font-size: 0.85rem;
  line-height: 1.7;
}
</style>
"""

SECTION_NAMES = {
    "💆": "状态",
    "🏋️": "身体",
    "🧠": "学习",
    "📝": "想法",
    "🛌": "收尾",
    "📖": "阅读",
}


def parse_diary(filepath, date_str):
    """Extract sections from a diary markdown file."""
    with open(filepath, "r") as f:
        lines = f.readlines()

    sections = {}
    current_section = None
    current_content = []

    for line in lines:
        stripped = line.rstrip()
        # Detect section headers like ## 🧠 学习 or ## 💆‍♂️ 状态
        m = re.match(r"^##\s+(.+)", stripped)
        if m:
            if current_section and current_content:
                sections[current_section] = "\n".join(current_content)
            current_section = m.group(1).strip()
            current_content = []
        elif current_section:
            # Skip empty lines at section start
            if not stripped and not current_content:
                continue
            current_content.append(stripped)

    if current_section and current_content:
        sections[current_section] = "\n".join(current_content)

    return sections


def section_to_html(section_title, content):
    """Convert a section to HTML for the timeline card."""
    text = content.strip()
    if not text:
        return ""

    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            if lines and not lines[-1].startswith("<br>"):
                lines.append("<br>")
            continue
        if line.startswith("- ["):
            line = line.replace("- [x]", "✅").replace("- [ ]", "⬜")
            lines.append(line[2:].strip())
        elif line.startswith("- "):
            lines.append("· " + line[2:].strip())
        elif line.startswith(">"):
            lines.append(line[1:].strip())
        elif line.startswith("# "):
            continue
        else:
            lines.append(line)

    if not lines:
        return ""

    content_html = "<br>".join(lines)
    return f'<h2>{section_title}</h2>\n<p>{content_html}</p>\n'


def generate_timeline():
    entries = []

    for dirname in sorted(os.listdir(TIMELINE_DIR), reverse=True):
        dirpath = os.path.join(TIMELINE_DIR, dirname)
        if not os.path.isdir(dirpath):
            continue

        # Match YYYY-MM-DD pattern
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", dirname):
            continue

        # Prefer daily-note.md, fallback to first .md file
        candidate = os.path.join(dirpath, "daily-note.md")
        if not os.path.isfile(candidate):
            md_files = [f for f in os.listdir(dirpath) if f.endswith(".md")]
            if not md_files:
                continue
            candidate = os.path.join(dirpath, md_files[0])
        daily_note = candidate

        try:
            date_obj = datetime.date.fromisoformat(dirname)
            weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date_obj.weekday()]
            date_display = f"{dirname} · {weekday} · 北京"
        except ValueError:
            date_display = dirname

        sections = parse_diary(daily_note, dirname)
        if not sections:
            continue

        entries.append((dirname, date_display, sections))

    # Build output
    output = [CSS, '<div class="timeline">']

    for dirname, date_display, sections in entries:
        output.append("")
        output.append('<div class="tl-entry">')
        output.append('  <div class="tl-dot"></div>')
        output.append(
            f'  <div class="tl-date"><a href="{dirname}/daily-note/">{date_display} →</a></div>'
        )
        output.append("")
        output.append('<div class="tl-body">')

        for title, content in sections.items():
            html = section_to_html(title, content)
            if html:
                output.append(html)

        output.append(f'<p><a href="{dirname}/daily-note/">→ 查看完整日记</a></p>')
        output.append("</div>")
        output.append("</div>")

    output.append("")
    output.append("</div>")

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(output))

    print(f"Generated {OUTPUT_FILE} with {len(entries)} entries")


if __name__ == "__main__":
    generate_timeline()
