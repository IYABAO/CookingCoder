# -*- coding: utf-8 -*-
"""CookingCoder 打卡统计脚本：计算积分、连续周数、已解锁徽章。

用法：在仓库根目录运行  python achievements/scripts/stats.py
"""
import re
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOMEWORK_DIR = ROOT / "homework"

# 积分规则
POINTS = {"done": 10, "photo": 5, "new_recipe": 5, "original": 10, "improve": 5}

# 徽章：(名称, 类型, 阈值)
BADGES = [
    ("🥚 新手厨师", "count", 1),
    ("🔪 小试牛刀", "count", 5),
    ("👨‍🍳 进阶厨师", "count", 10),
    ("🔥 厨神之路", "count", 20),
    ("👑 家庭厨神", "count", 50),
    ("⛓ 连续作战", "streak", 2),
    ("🔥 燃烧吧厨艺", "streak", 4),
    ("🏃 持之以恒", "streak", 8),
    ("🧘 厨艺修行者", "streak", 12),
]


def parse_week(filename: str) -> int | None:
    m = re.match(r"week-(\d+)\.md$", filename)
    return int(m.group(1)) if m else None


def collect_homework() -> list[int]:
    """返回已交作业的周数列表（升序）。"""
    weeks = []
    for f in HOMEWORK_DIR.glob("week-*.md"):
        w = parse_week(f.name)
        if w:
            weeks.append(w)
    return sorted(set(weeks))


def calc_streak(weeks: list[int]) -> int:
    """计算当前连续打卡周数（从最近一次往前数连续）。"""
    if not weeks:
        return 0
    streak = 1
    for i in range(len(weeks) - 1, 0, -1):
        if weeks[i] - weeks[i - 1] == 1:
            streak += 1
        else:
            break
    return streak


def calc_points(weeks: list[int]) -> dict:
    """计算积分明细（基于作业内容做简单判定）。"""
    total = 0
    breakdown = {"done": 0, "photo": 0, "new_recipe": 0, "original": 0, "improve": 0}
    seen_recipes = set()
    for w in weeks:
        f = HOMEWORK_DIR / f"week-{w}.md"
        text = f.read_text(encoding="utf-8") if f.exists() else ""
        total += POINTS["done"]
        breakdown["done"] += 1
        if "assets/" in text:
            total += POINTS["photo"]
            breakdown["photo"] += 1
        # 简单判定：提到"自创/改编"算原创
        if any(k in text for k in ["自创", "改编", "原创"]):
            total += POINTS["original"]
            breakdown["original"] += 1
        # 提到翻车/改进
        if any(k in text for k in ["翻车", "改进", "教训"]):
            total += POINTS["improve"]
            breakdown["improve"] += 1
    return {"total": total, "breakdown": breakdown}


def unlock_badges(count: int, streak: int) -> list[str]:
    result = []
    for name, kind, threshold in BADGES:
        value = count if kind == "count" else streak
        if value >= threshold:
            result.append(name)
    return result


def main() -> None:
    if not HOMEWORK_DIR.exists():
        print("未找到 homework 目录，请在仓库根目录运行。")
        sys.exit(1)

    weeks = collect_homework()
    count = len(weeks)
    streak = calc_streak(weeks)
    points = calc_points(weeks)

    print("=" * 46)
    print("🍳  CookingCoder 打卡统计")
    print("=" * 46)
    print(f"累计作业：{count} 次   （周数：{weeks if weeks else '暂无'}）")
    print(f"当前连续打卡：{streak} 周")
    print(f"总积分：{points['total']} 分")
    print(f"  明细：{points['breakdown']}")
    print("-" * 46)
    badges = unlock_badges(count, streak)
    print("已解锁徽章：" if badges else "暂无徽章，继续加油！")
    for b in badges:
        print(f"  {b}")
    print("=" * 46)
    if count:
        print(f"下一个目标：累计 {min(x for x in [5,10,20,50] if x > count)} 次 / 连续 {min(x for x in [2,4,8,12] if x > streak)} 周")
    else:
        print("下一个目标：完成第一次作业！🥚 新手厨师在等你")


if __name__ == "__main__":
    main()
