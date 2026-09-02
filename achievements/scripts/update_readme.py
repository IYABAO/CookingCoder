# -*- coding: utf-8 -*-
"""更新 homework/README.md 的「已交作业」表格（供 GitHub Actions 调用）。

用法：在仓库根目录运行  python achievements/scripts/update_readme.py
"""
import re
import sys
from pathlib import Path

# 复用 stats.py 的统计函数
sys.path.insert(0, str(Path(__file__).resolve().parent))
from stats import HOMEWORK_DIR, ROOT, collect_homework, calc_points


def _extract_recipe(week_file: Path) -> str:
    """从作业文件提取菜名（从标题行或「本周菜」）。"""
    try:
        text = week_file.read_text(encoding="utf-8")
    except Exception:
        return "?"
    m = re.search(r"本周菜[：:]\s*([^\n]+)", text)
    if m:
        return m.group(1).strip()
    # 回退：取第一个 h2 标题
    m = re.search(r"##\s+(.+)", text)
    return m.group(1).strip() if m else "?"


def main() -> None:
    weeks = collect_homework()
    readme = HOMEWORK_DIR / "README.md"
    text = readme.read_text(encoding="utf-8")

    if not weeks:
        rows = "| （暂无） | | | |"
    else:
        lines = []
        # 周数反序，最新的在最上面
        for w in reversed(weeks):
            f = HOMEWORK_DIR / f"week-{w}.md"
            recipe = _extract_recipe(f)
            # 日期从文件 mtime 近似（GitHub 环境用 git log 更准，这里简化）
            date = "待补充"
            lines.append(f"| week-{w} | {recipe} | {date} | ✅ |")
        rows = "\n".join(lines)

    # 替换表格区域
    pattern = re.compile(r"\| 周数 \| 菜名 \| 日期 \| 状态 \|\n\| ---.*?\n(.*?)\n\n", re.DOTALL)
    new_table = (
        "| 周数 | 菜名 | 日期 | 状态 |\n"
        "| --- | --- | --- | --- |\n"
        f"{rows}\n"
    )
    if pattern.search(text):
        text = pattern.sub(new_table + "\n", text, count=1)
    else:
        # 没找到表格，追加
        text += "\n## 已交作业\n\n" + new_table + "\n"

    readme.write_text(text, encoding="utf-8")
    print(f"已更新 homework/README.md，共 {len(weeks)} 次作业")


if __name__ == "__main__":
    main()
