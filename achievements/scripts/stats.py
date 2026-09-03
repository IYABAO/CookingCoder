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
RECIPES_DIR = ROOT / "recipes"

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
    ("🎨 技法达人", "tech", 5),
    ("🌍 菜系探险家", "cuisine", 3),
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


def _parse_frontmatter_field(text: str, field: str) -> list[str]:
    """从 markdown 文本中提取 frontmatter 指定字段的值（适配 YAML 数组和字符串）。"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return []
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            if k.strip() == field:
                v = v.strip().strip('"').strip("'")
                if v.startswith("["):
                    inner = v.strip()[1:-1].strip()
                    if not inner:
                        return []
                    return [item.strip().strip('"').strip("'").strip() for item in inner.split(",") if item.strip()]
                return [v] if v else []
    return []


def calc_recipe_coverage() -> dict:
    """扫描 recipes/ 目录，统计菜谱库中 tech 和 cuisine 的去重数量。

    返回 {"tech_count": int, "cuisine_count": int, "tech_list": [...], "cuisine_list": [...]}
    这是项目级成就，代表菜谱库的丰富度。
    """
    tech_set = set()
    cuisine_set = set()
    if not RECIPES_DIR.exists():
        return {"tech_count": 0, "cuisine_count": 0, "tech_list": [], "cuisine_list": []}
    for f in sorted(RECIPES_DIR.glob("*.md")):
        if f.name.startswith("_"):
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        for t in _parse_frontmatter_field(text, "tech"):
            tech_set.add(t)
        for c in _parse_frontmatter_field(text, "cuisine"):
            cuisine_set.add(c)
    return {
        "tech_count": len(tech_set),
        "cuisine_count": len(cuisine_set),
        "tech_list": sorted(tech_set),
        "cuisine_list": sorted(cuisine_set),
    }


def unlock_badges(count: int, streak: int, tech_count: int = 0, cuisine_count: int = 0) -> list[str]:
    result = []
    for name, kind, threshold in BADGES:
        if kind == "count":
            value = count
        elif kind == "streak":
            value = streak
        elif kind == "tech":
            value = tech_count
        elif kind == "cuisine":
            value = cuisine_count
        else:
            continue
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
    coverage = calc_recipe_coverage()

    print("=" * 46)
    print("🍳  CookingCoder 打卡统计")
    print("=" * 46)
    print(f"累计作业：{count} 次   （周数：{weeks if weeks else '暂无'}）")
    print(f"当前连续打卡：{streak} 周")
    print(f"总积分：{points['total']} 分")
    print(f"  明细：{points['breakdown']}")
    print("-" * 46)
    print(f"菜谱库覆盖：技法 {coverage['tech_count']} 种 {coverage['tech_list']}")
    print(f"           菜系 {coverage['cuisine_count']} 种 {coverage['cuisine_list']}")
    print("-" * 46)
    badges = unlock_badges(count, streak, coverage["tech_count"], coverage["cuisine_count"])
    print("已解锁徽章：" if badges else "暂无徽章，继续加油！")
    for b in badges:
        print(f"  {b}")
    print("=" * 46)
    if count:
        next_count = min((x for x in [5, 10, 20, 50] if x > count), default=None)
        next_streak = min((x for x in [2, 4, 8, 12] if x > streak), default=None)
        parts = []
        if next_count:
            parts.append(f"累计 {next_count} 次")
        if next_streak:
            parts.append(f"连续 {next_streak} 周")
        if coverage["tech_count"] < 5:
            parts.append(f"技法覆盖 {5 - coverage['tech_count']} 种")
        if coverage["cuisine_count"] < 3:
            parts.append(f"菜系覆盖 {3 - coverage['cuisine_count']} 种")
        if parts:
            print(f"下一个目标：{' / '.join(parts)}")
    else:
        print("下一个目标：完成第一次作业！🥚 新手厨师在等你")


if __name__ == "__main__":
    main()
