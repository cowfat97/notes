#!/usr/bin/env python3
"""解析 Apple Watch 睡眠记录，输出分析摘要。

用法: python3 _components/sleep_analyzer.py [日期]
      日期格式 YYYY-MM-DD（默认昨天）
输出: JSON，字段见 SleepReport
"""

import sys
import re
import json
from datetime import date, timedelta, datetime
from pathlib import Path
from dataclasses import dataclass, asdict

OBSIDIAN_SLEEP_DIR = Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/郝鑫磊/健康/睡眠"


@dataclass
class SleepReport:
    date: str
    fragment_count: int
    total_sleep_min: int       # 实际睡着时间（分钟）
    bed_start: str              # 上床时间
    bed_end: str                # 起床时间
    bed_duration_min: int       # 卧床时长（分钟）
    efficiency: float           # 睡眠效率 = 有效/卧床
    score: int                  # 0-100 自适应伸缩评分
    energy: int                 # 建议精力值 1-5
    summary: str                # 一句话解读


def find_sleep_file(target: date) -> Path | None:
    """在 Obsidian 睡眠目录中查找指定日期的记录。文件名格式: 2026年7月25日-睡眠记录.md"""
    for f in sorted(OBSIDIAN_SLEEP_DIR.glob("*.md"), reverse=True):
        stem = f.stem.replace("-睡眠记录", "")
        # 尝试中文日期
        match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", stem)
        if match:
            d = date(int(match[1]), int(match[2]), int(match[3]))
            if d == target:
                return f
    return None


def parse_duration(s: str) -> int:
    """解析时长字符串为秒数。支持: 1:59, 59, 1:01:53"""
    s = s.strip()
    parts = s.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    else:
        return int(parts[0])


def parse_sleep_file(filepath: Path) -> SleepReport | None:
    """解析睡眠记录文件，返回 SleepReport。"""
    text = filepath.read_text(encoding="utf-8")

    # 提取入睡时间戳列表
    asleep_match = re.search(r"｛入睡(.+?)｝ -> ｛醒来(.+?)｝（｛时长(.+?)｝）", text, re.DOTALL)
    if not asleep_match:
        return None

    asleep_raw = asleep_match[1]
    awake_raw = asleep_match[2]
    duration_raw = asleep_match[3]

    # 解析时间戳
    ts_pattern = re.compile(r"(\d{4})年(\d{1,2})月(\d{1,2})日 (\d{2}):(\d{2})")
    asleep_ts = [datetime(*map(int, m.groups())) for m in ts_pattern.finditer(asleep_raw)]
    awake_ts = [datetime(*map(int, m.groups())) for m in ts_pattern.finditer(awake_raw)]
    durations = [parse_duration(d) for d in re.findall(r"(\d{1,2}(?::\d{2}){0,2})", duration_raw)]

    if not asleep_ts or not awake_ts:
        return None

    fragment_count = min(len(asleep_ts), len(awake_ts), len(durations))
    total_sec = sum(durations[:fragment_count])

    # 集群识别：2h 以上的间隔 = 不同睡眠周期
    clusters = []
    current = [(asleep_ts[0], awake_ts[0], durations[0])]
    for i in range(1, fragment_count):
        gap = (asleep_ts[i] - awake_ts[i - 1]).total_seconds()
        if gap > 7200:
            clusters.append(current)
            current = [(asleep_ts[i], awake_ts[i], durations[i])]
        else:
            current.append((asleep_ts[i], awake_ts[i], durations[i]))
    clusters.append(current)

    # 主睡眠集群：总时长最长的集群
    main = max(clusters, key=lambda c: sum(d for _, _, d in c))
    main_asleep = [a for a, _, _ in main]
    main_awake  = [w for _, w, _ in main]
    main_total_sec = sum(d for _, _, d in main)
    main_fragments = len(main)

    bed_start = main_asleep[0]
    bed_end = main_awake[-1]
    bed_sec = (bed_end - bed_start).total_seconds()
    if bed_sec <= 0:
        return None

    efficiency = main_total_sec / bed_sec
    # 评分: 基础分=效率*60 + 片段惩罚 + 入睡惩罚（基于主睡眠集群）
    base = efficiency * 60
    fragment_penalty = min(25, main_fragments * 0.5)
    hour = bed_start.hour + bed_start.minute / 60
    time_penalty = max(0, (hour - 23) * 5) if hour >= 23 else 0
    time_penalty += max(0, (hour - 0) * 8) if hour < 4 else 0
    score = max(0, min(100, int(base - fragment_penalty - time_penalty)))

    # 精力建议（1-5），基于有效睡眠+评分
    sleep_hours = total_sec / 3600
    if sleep_hours >= 8 and score >= 50:
        energy = 5
    elif sleep_hours >= 7 and score >= 30:
        energy = 4
    elif sleep_hours >= 6 and score >= 15:
        energy = 3
    elif sleep_hours >= 4:
        energy = 2
    else:
        energy = 1

    if efficiency >= 0.85 and main_fragments <= 20:
        summary = "质量良好"
    elif efficiency >= 0.75:
        summary = "碎片偏多但尚可"
    elif efficiency >= 0.60:
        summary = "入睡太晚，唤醒过多"
    else:
        summary = "严重透支"

    return SleepReport(
        date=target.isoformat(),
        fragment_count=fragment_count,
        total_sleep_min=total_sec // 60,
        bed_start=bed_start.strftime("%H:%M"),
        bed_end=bed_end.strftime("%H:%M"),
        bed_duration_min=int(bed_sec // 60),
        efficiency=round(efficiency, 2),
        score=score,
        energy=energy,
        summary=summary,
    )


TIMELINE_DIRS = [
    Path.home() / "Desktop/开发/学习/notes/时间线",
    Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/郝鑫磊/时间线",
]


def update_diary(report: SleepReport, dry_run: bool = False) -> list[str]:
    """将睡眠分析结果写入日记的「状态」模块。返回已更新的文件列表。"""
    energy_bar = "⚡" * report.energy + "☆" * (5 - report.energy)
    sleep_line = (
        f"- 精力：{energy_bar} ({report.energy}/5)"
        f" | 睡眠 {report.total_sleep_min // 60}h{report.total_sleep_min % 60}m"
        f" · {report.fragment_count} 段"
        f" · {report.score} 分"
    )

    updated = []
    for base in TIMELINE_DIRS:
        diary = base / report.date / f"☕-{report.date}.md"
        if not diary.exists():
            continue

        lines = diary.read_text(encoding="utf-8").split("\n")
        new_lines = []
        for line in lines:
            if line.startswith("- 精力："):
                new_lines.append(sleep_line)
            else:
                new_lines.append(line)

        if dry_run:
            print(f"[dry-run] 将更新: {diary}")
        else:
            diary.write_text("\n".join(new_lines), encoding="utf-8")
        updated.append(str(diary))

    return updated


if __name__ == "__main__":
    target = date.today() - timedelta(days=1)
    dry = False

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) > 0:
        target = date.fromisoformat(args[0])
    if "--update" in sys.argv or "-u" in sys.argv:
        dry = "--dry" in sys.argv

    filepath = find_sleep_file(target)
    if not filepath:
        print(json.dumps({"error": f"未找到 {target} 的睡眠记录"}, ensure_ascii=False))
        sys.exit(1)

    report = parse_sleep_file(filepath)
    if not report:
        print(json.dumps({"error": f"解析失败: {filepath}"}, ensure_ascii=False))
        sys.exit(1)

    if "--update" in sys.argv or "-u" in sys.argv:
        updated = update_diary(report, dry_run=dry)
        print(f"已更新 {len(updated)} 个日记:")
        for u in updated:
            print(f"  {u}")
        print()
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
