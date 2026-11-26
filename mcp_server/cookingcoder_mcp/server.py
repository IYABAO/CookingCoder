# -*- coding: utf-8 -*-
"""CookingCoder MCP Server。

把 recipes/ 菜谱库封装成 LLM 可调用的 MCP 工具：
- get_recipe: 按菜名查菜谱
- list_recipes: 按五维标签（菜系/口味/人群/技法/耗时）+ 难度筛选
- search_by_constraint: 自然语言约束查询（如"30分钟内、川菜、下饭"）
- recommend_recipe: 随机/按条件推荐
- get_weekly_plan: 获取本周推荐
- get_shopping_list: 按本周推荐汇总买菜清单

用法：
    python -m cookingcoder_mcp.server          # STDIO 模式
    python -m cookingcoder_mcp.server --http   # HTTP 模式
"""
from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# 菜谱库根目录（仓库根目录 /recipes，即 mcp_server 的上两级）
RECIPES_DIR = Path(__file__).resolve().parents[2] / "recipes"

# 每周推荐轮换的锚点：2026-08-31 是 ISO 2026-W36 的周一，index.md 明确从 W36 起算
WEEKLY_INDEX_FILE = RECIPES_DIR / "_index.md"
WEEKLY_ANCHOR = date(2026, 8, 31)
WEEKLY_HEADING = "## 每周推荐轮换"

mcp = FastMCP(
    "cookingcoder",
    version="2.0.0",
    instructions="一个家常菜谱工具，支持按菜名查菜谱、按五维标签（菜系/口味/人群/技法/耗时档）筛选、自然语言约束查询、随机推荐、本周推荐与本周买菜清单。",
)


# ---- frontmatter 解析 ----

def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """解析 markdown 的 YAML frontmatter，返回 (meta, body)。

    适配五维标签：cuisine/taste/crowd/tech 为 YAML 数组（如 ["川菜","下饭菜"]），
    解析为 Python list；其余字段按字符串处理。
    """
    meta: dict = {}
    body = text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if m:
        yaml_block = m.group(1)
        for line in yaml_block.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                # YAML 数组适配：以 [ 开头则解析为列表
                if v.startswith("["):
                    v = _parse_yaml_list(v)
                meta[k] = v
        body = text[m.end():]
    return meta, body


def _parse_yaml_list(s: str) -> list[str]:
    """解析 YAML 内联数组字符串，如 '["川菜", "下饭菜"]' → ['川菜','下饭菜']。"""
    inner = s.strip()[1:-1].strip()  # 去掉首尾 []
    if not inner:
        return []
    items = []
    for part in inner.split(","):
        item = part.strip().strip('"').strip("'").strip()
        if item:
            items.append(item)
    return items


def _field_contains(field_value, keyword: str) -> bool:
    """判断 frontmatter 字段值是否包含筛选关键词。

    field_value 可能是 list（五维标签）或 str（旧格式 tags 等）。
    """
    if field_value is None:
        return False
    if isinstance(field_value, list):
        return any(keyword in item for item in field_value)
    return keyword in str(field_value)


def _load_all_recipes() -> list[dict]:
    """加载所有菜谱，返回 [{file, title, meta, body}]。"""
    recipes = []
    for f in sorted(RECIPES_DIR.glob("*.md")):
        if f.name.startswith("_"):
            continue
        meta, body = _parse_frontmatter(f.read_text(encoding="utf-8"))
        recipes.append({"file": f.name, "title": meta.get("title", f.stem), "meta": meta, "body": body})
    return recipes


# ---- 五维标签取值字典（用于自然语言解析） ----

CUISINE_KEYWORDS = {
    "川菜": ["川菜", "川味", "四川"],
    "粤菜": ["粤菜", "粤式", "广东", "广式"],
    "湘菜": ["湘菜", "湘味", "湖南"],
    "鲁菜": ["鲁菜", "鲁味", "山东"],
    "江浙": ["江浙", "沪菜", "上海", "杭帮", "江浙菜"],
    "西式": ["西式", "西餐", "欧式", "美式"],
    "无国界": ["无国界", "融合", "家常"],
}

TASTE_KEYWORDS = {
    "麻辣": ["麻辣", "辣", "重口", "川辣"],
    "酸甜": ["酸甜", "糖醋", "酸", "甜口", "开胃"],
    "咸鲜": ["咸鲜", "咸香", "下饭", "鲜", "原味", "咸"],
    "清甜": ["清甜", "清淡", "甜", "鲜甜", "清爽"],
    "酱香": ["酱香", "红烧", "酱", "浓郁"],
    "蒜香": ["蒜香", "蒜蓉", "蒜"],
    "鱼香": ["鱼香"],
    "五香": ["五香", "卤味", "香料"],
    "奶香": ["奶香", "奶油", "芝士"],
}

CROWD_KEYWORDS = {
    "新手": ["新手", "入门", "简单易做", "零失败", "小白"],
    "上班族": ["上班族", "快手", "省时", "工作日", "忙碌"],
    "家庭": ["家庭", "全家", "一家人", "日常"],
    "孩子": ["孩子", "小孩", "儿童", "宝宝", "不辣", "小朋友"],
    "健身": ["健身", "低脂", "健康", "减脂", "低卡", "轻食"],
    "宴客": ["宴客", "请客", "待客", "硬菜", "体面", "大菜"],
    "滋补": ["滋补", "养生", "补身体", "炖汤", "营养"],
}

TECH_KEYWORDS = {
    "炒": ["炒", "爆炒", "快炒", "清炒", "煸炒"],
    "炖": ["炖", "慢炖", "炖菜", "煲汤"],
    "蒸": ["蒸", "清蒸", "蒸菜"],
    "煎": ["煎", "煎饼", "煎制"],
    "炸": ["炸", "油炸", "香炸", "酥炸"],
    "焖": ["焖", "焖烧", "油焖", "黄焖"],
    "卤": ["卤", "卤制", "卤水"],
    "烧": ["烧", "红烧", "干烧", "烧制"],
    "煮": ["煮", "白灼", "水煮", "汤煮"],
    "凉拌": ["凉拌", "凉菜", "拌菜", "生拌"],
    "烤": ["烤", "烤制", "烧烤", "焗烤"],
}

TIME_KEYWORDS = {
    "快手": ["快手", "10分钟", "15分钟", "20分钟内", "半小时内", "30分钟内", "快速", "省时"],
    "常规": ["常规", "30分钟", "45分钟", "半小时", "中等时间"],
    "硬菜": ["硬菜", "大菜", "1小时", "60分钟", "90分钟", "慢炖", "费时间", "功夫菜"],
}


def _parse_constraint(constraint: str) -> dict:
    """将自然语言约束描述解析为五维筛选条件。

    返回 dict，键为 cuisine/taste/crowd/tech/time，值为匹配到的标签或 None。
    """
    result = {"cuisine": None, "taste": None, "crowd": None, "tech": None, "time": None}
    text = constraint.lower()

    for label, keywords in CUISINE_KEYWORDS.items():
        if any(kw in constraint for kw in keywords):
            result["cuisine"] = label
            break

    for label, keywords in TASTE_KEYWORDS.items():
        if any(kw in constraint for kw in keywords):
            result["taste"] = label
            break

    for label, keywords in CROWD_KEYWORDS.items():
        if any(kw in constraint for kw in keywords):
            result["crowd"] = label
            break

    for label, keywords in TECH_KEYWORDS.items():
        if any(kw in constraint for kw in keywords):
            result["tech"] = label
            break

    for label, keywords in TIME_KEYWORDS.items():
        if any(kw in constraint for kw in keywords):
            result["time"] = label
            break

    return result


def _filter_recipes(recipes: list[dict], filters: dict) -> list[dict]:
    """按五维 + 难度 + tag 筛选菜谱，返回匹配列表。

    filters 可包含: cuisine, taste, crowd, tech, time, difficulty, tag
    """
    result = []
    for r in recipes:
        meta = r["meta"]
        # 五维筛选：字段包含筛选值即匹配
        if filters.get("cuisine") and not _field_contains(meta.get("cuisine"), filters["cuisine"]):
            continue
        if filters.get("taste") and not _field_contains(meta.get("taste"), filters["taste"]):
            continue
        if filters.get("crowd") and not _field_contains(meta.get("crowd"), filters["crowd"]):
            continue
        if filters.get("tech") and not _field_contains(meta.get("tech"), filters["tech"]):
            continue
        if filters.get("time") and meta.get("time", "") != filters["time"]:
            # time 是单值字符串，精确匹配
            if filters["time"] not in str(meta.get("time", "")):
                continue
        # 难度筛选
        if filters.get("difficulty") and meta.get("difficulty", "") != filters["difficulty"]:
            continue
        # 旧格式 tag 兼容
        if filters.get("tag") and not _field_contains(meta.get("tags", ""), filters["tag"]):
            continue
        result.append(r)
    return result


def _recipe_summary(r: dict) -> dict:
    """提取菜谱摘要信息（title + 五维 + difficulty + time）。"""
    meta = r["meta"]
    return {
        "title": r["title"],
        "file": r["file"],
        "difficulty": meta.get("difficulty", ""),
        "time": meta.get("time", ""),
        "cuisine": meta.get("cuisine", []),
        "taste": meta.get("taste", []),
        "crowd": meta.get("crowd", []),
        "tech": meta.get("tech", []),
    }


# ---- 每周推荐轮换 ----


def _load_weekly_order() -> list[str]:
    """从 recipes/_index.md 的「每周推荐轮换」段解析 40 个有序菜名。

    找不到索引文件、标题或编号列表时返回空列表，由调用方显式报错。
    """
    if not WEEKLY_INDEX_FILE.is_file():
        return []
    text = WEEKLY_INDEX_FILE.read_text(encoding="utf-8")
    if WEEKLY_HEADING not in text:
        return []
    section = text.split(WEEKLY_HEADING, 1)[1]
    # 只取本节内容，遇到下一个二级标题就截止，避免把后续章节的编号误收进来
    next_heading = re.search(r"\n##\s+", section)
    if next_heading:
        section = section[: next_heading.start()]
    order: list[str] = []
    for line in section.splitlines():
        m = re.match(r"^\s*\d+\.\s+(.+?)\s*$", line)
        if m:
            order.append(m.group(1).strip())
    return order


def _weekly_index(today: date) -> dict:
    """计算指定日期对应的 ISO 周、轮换序号和轮次（每 40 周一轮）。"""
    order = _load_weekly_order()
    if not order:
        raise ValueError("recipes/_index.md 的「每周推荐轮换」为空或格式不可解析")
    week_start = today - timedelta(days=today.weekday())
    delta_weeks = (week_start - WEEKLY_ANCHOR).days // 7
    idx = delta_weeks % len(order)
    round_no = delta_weeks // len(order) + 1
    iso = week_start.isocalendar()
    return {
        "week": f"{iso.year}-W{iso.week:02d}",
        "week_start": week_start.isoformat(),
        "index": idx + 1,
        "round": max(1, round_no),
    }


def _weekly_plan(weeks: int, today: date | None = None) -> dict:
    """生成从指定日期起连续 N 周的推荐计划。"""
    if not 1 <= weeks <= 8:
        return {"error": "weeks 必须在 1–8 之间"}
    today = today or date.today()
    order = _load_weekly_order()
    if not order:
        return {"error": "每周推荐轮换为空或格式不可解析，请检查 recipes/_index.md"}
    by_title = {r["title"]: r for r in _load_all_recipes()}
    items = []
    for offset in range(weeks):
        d = today + timedelta(weeks=offset)
        info = _weekly_index(d)
        title = order[info["index"] - 1]
        recipe = by_title.get(title)
        if recipe is None:
            items.append({**info, "title": title, "file": None, "missing": True})
        else:
            summary = _recipe_summary(recipe)
            items.append({**info, "title": title, "file": summary["file"], "meta": summary})
    return {"anchor": "2026-W36", "cycle": len(order), "weeks": items}


# ---- 食材解析与采购清单 ----

INGREDIENT_HEADING = "## 食材清单"

# 不需要采购的「食材」（水、冰水等），不进入买菜清单
SKIP_INGREDIENTS = {"清水", "水", "开水", "热水", "冰水", "温水", "凉水", "凉开水"}


def _is_skipped_ingredient(name: str) -> bool:
    """判断食材是否属于无需采购项；兼容 '冰水/凉开水' 这类并列写法。"""
    parts = [p.strip() for p in name.split("/") if p.strip()]
    if not parts:
        return False
    return all(p in SKIP_INGREDIENTS or p.endswith("水") for p in parts)

# 用量解析：前缀数字（整数/小数/半/分数）+ 单位，单位按长度倒序匹配
_AMOUNT_RE = re.compile(
    r"^(?P<num>\d+(?:\.\d+)?|半|1/\d+)\s*"
    r"(?P<unit>整头|小块|小勺|大勺|ml|kg|g|L|盒|罐|碗|片|瓣|块|颗|段|朵|条|根|把|只|个|勺|张|棵|包|袋|头)"
)

# 采购分区：先按精确名覆盖，再按关键词规则，先命中先归类
SECTION_ORDER = ["肉禽蛋", "水产", "蔬菜菌菇", "豆制品", "主食干货", "调味料", "其他"]
_SECTION_EXACT = {
    "干香菇": "主食干货",
    "干辣椒": "调味料",
    "小米辣": "调味料",
    "郫县豆瓣酱": "调味料",
}
_SECTION_RULES = [
    ("调味料", (
        "花椒", "胡椒", "辣椒", "辣酱", "豆瓣酱", "生抽", "老抽", "酱油", "蚝油", "料酒", "黄酒",
        "醋", "盐", "糖", "冰糖", "淀粉", "生粉", "油", "芝麻", "八角", "桂皮", "香叶", "孜然",
        "五香粉", "鸡精", "味精", "豆豉", "甜面酱", "番茄酱", "咖喱", "椒盐", "泡椒", "酒",
    )),
    ("主食干货", (
        "米饭", "大米", "面条", "挂面", "面粉", "粉丝", "粉条", "年糕", "馄饨皮", "饺子皮",
        "面包糠", "紫菜", "木耳", "腐竹", "银耳", "花生", "坚果",
    )),
    ("水产", ("鱼", "虾", "蟹", "蛤", "贝", "鱿鱼", "海参", "蛏", "海带")),
    ("肉禽蛋", ("猪", "牛", "羊", "鸡", "鸭", "肉", "排骨", "里脊", "五花", "培根", "火腿", "香肠", "午餐肉", "蛋")),
    ("豆制品", ("豆腐", "豆干", "豆皮", "千张")),
    ("蔬菜菌菇", (
        "菜", "椒", "瓜", "豆", "茄", "葱", "姜", "蒜", "萝卜", "土豆", "山药", "藕", "番茄",
        "西红柿", "菇", "笋", "芹", "韭", "菠菜", "生菜", "玉米", "南瓜", "秋葵", "香菜", "莴笋",
    )),
]


def _parse_ingredients(body: str) -> list[dict]:
    """从菜谱正文的「食材清单（Input）」表格解析食材行。

    返回 [{"name": 食材, "amount": 用量, "prep": 切配, "note": 备注}]；
    找不到该表或表为空时返回空列表。
    """
    idx = body.find(INGREDIENT_HEADING)
    if idx < 0:
        return []
    section = body[idx:]
    next_heading = re.search(r"\n##\s+", section)
    if next_heading:
        section = section[: next_heading.start()]

    items: list[dict] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if re.fullmatch(r"\|[\s\-:|]+\|?", stripped):  # 表头分隔行
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells or cells[0] in ("食材", "") or cells[0].startswith("常量"):
            continue  # 表头行
        if len(cells) < 2 or not cells[1]:
            continue
        items.append({
            "name": cells[0],
            "amount": cells[1],
            "prep": cells[2] if len(cells) > 2 else "",
            "note": cells[3] if len(cells) > 3 else "",
        })
    return items


def _parse_amount(raw: str) -> tuple[float | None, str | None]:
    """把用量文本归一为 (数值, 单位)；无法解析时返回 (None, None)。

    '200g' → (200.0,'g')；'半只(约600g)' → (0.5,'只')；'几滴' → (None, None)。
    """
    m = _AMOUNT_RE.match(raw.strip())
    if not m:
        return None, None
    num, unit = m.group("num"), m.group("unit")
    if num == "半":
        value = 0.5
    elif "/" in num:
        a, b = num.split("/")
        value = float(a) / float(b)
    else:
        value = float(num)
    return value, unit


def _format_sum(value: float, unit: str) -> str:
    """把累加结果格式化为可读用量：最多两位小数，整数不显示小数点。"""
    rounded = round(value, 2)
    text = str(int(rounded)) if abs(rounded - int(rounded)) < 1e-9 else f"{rounded:g}"
    return f"{text}{unit}"


def _classify_section(name: str) -> str:
    """按食材名归入采购分区（肉禽蛋/水产/蔬菜菌菇/豆制品/主食干货/调味料/其他）。"""
    if name in _SECTION_EXACT:
        return _SECTION_EXACT[name]
    for section, keywords in _SECTION_RULES:
        if any(kw in name for kw in keywords):
            return section
    return "其他"


def _merge_quantity(raws: list[str], parsed: list[tuple[float | None, str | None]]) -> str:
    """合并同名食材用量：单位一致则累加，否则按原始写法并列显示。"""
    unique_raw: list[str] = []
    for raw in raws:
        if raw not in unique_raw:
            unique_raw.append(raw)
    values = [p for p in parsed if p[0] is not None and p[1] is not None]
    if len(values) == len(parsed) and len({p[1] for p in values}) == 1:
        unit = values[0][1]
        return _format_sum(sum(p[0] for p in values), unit)
    return " / ".join(unique_raw)


def _aggregate_shopping(recipes: list[dict]) -> dict:
    """把多道菜的食材表合并成按采购分区的清单。

    返回 {"sections": [{"section", "items": [{"name","quantity","used_in"}]}], "item_count"}。
    """
    groups: dict[str, dict] = {}
    for r in recipes:
        for ing in _parse_ingredients(r["body"]):
            name = ing["name"]
            if _is_skipped_ingredient(name):
                continue
            g = groups.setdefault(name, {"name": name, "raw": [], "parsed": [], "used_in": []})
            g["raw"].append(ing["amount"])
            g["parsed"].append(_parse_amount(ing["amount"]))
            if r["title"] not in g["used_in"]:
                g["used_in"].append(r["title"])

    buckets: dict[str, list[dict]] = {s: [] for s in SECTION_ORDER}
    for g in groups.values():
        buckets[_classify_section(g["name"])].append({
            "name": g["name"],
            "quantity": _merge_quantity(g["raw"], g["parsed"]),
            "used_in": g["used_in"],
        })

    sections = [
        {"section": s, "items": sorted(items, key=lambda i: (-len(i["used_in"]), i["name"]))}
        for s, items in buckets.items()
        if items
    ]
    return {"sections": sections, "item_count": len(groups)}


def _shopping_list(weeks: int, today: date | None = None) -> dict:
    """按指定周数的推荐菜谱，生成买菜清单与可粘贴的 Markdown 勾选表。"""
    if not 1 <= weeks <= 8:
        return {"error": "weeks 必须在 1–8 之间"}
    plan = _weekly_plan(weeks, today=today)
    if plan.get("error"):
        return plan

    by_title = {r["title"]: r for r in _load_all_recipes()}
    selected = []
    week_rows = []
    for item in plan["weeks"]:
        recipe = by_title.get(item["title"])
        if recipe is None:
            continue
        selected.append(recipe)
        week_rows.append({"week": item["week"], "title": item["title"], "file": item["file"]})
    if not selected:
        return {"error": "本周推荐菜谱无法映射到文件，请检查 recipes/_index.md"}

    agg = _aggregate_shopping(selected)
    first = plan["weeks"][0]
    if len(week_rows) == 1:
        heading = f"## {first['week']} 采购清单（{first['title']}）"
    else:
        titles = "、".join(w["title"] for w in week_rows)
        last_week = week_rows[-1]["week"]
        tail = last_week[5:] if last_week[:4] == first["week"][:4] else last_week
        heading = f"## {first['week']}–{tail} 采购清单（{titles}）"
    lines = [heading, ""]
    for sec in agg["sections"]:
        lines.append(f"**{sec['section']}**")
        for item in sec["items"]:
            used = "、".join(item["used_in"])
            lines.append(f"- [ ] {item['name']} {item['quantity']} — {used}")
        lines.append("")

    return {
        "week": first["week"],
        "index": first["index"],
        "week_start": first["week_start"],
        "round": first["round"],
        "weeks": week_rows,
        "sections": agg["sections"],
        "item_count": agg["item_count"],
        "markdown": "\n".join(lines).strip(),
        "note": "用量沿用菜谱原份量；同名食材单位一致时累加，单位不同时并列显示",
    }


# ---- 业务参数 ----

class RecipeQuery(BaseModel):
    name: str = Field(description="菜名关键词，支持模糊匹配")


class FilterQuery(BaseModel):
    tag: str | None = Field(default=None, description="旧格式标签，如 家常菜/川菜/快手菜/硬菜（兼容用）")
    difficulty: str | None = Field(default=None, description="难度：简单/中等/进阶")
    limit: int = Field(default=10, description="返回数量上限")
    cuisine: str | None = Field(default=None, description="菜系筛选：川菜/粤菜/湘菜/鲁菜/江浙/西式/无国界")
    taste: str | None = Field(default=None, description="口味筛选：麻辣/酸甜/咸鲜/清甜/酱香/蒜香/鱼香/五香/奶香")
    crowd: str | None = Field(default=None, description="人群筛选：新手/上班族/家庭/孩子/健身/宴客/滋补")
    tech: str | None = Field(default=None, description="技法筛选：炒/炖/蒸/煎/炸/焖/卤/烧/煮/凉拌/烤")
    time: str | None = Field(default=None, description="耗时档筛选：快手(≤15min)/常规(≤45min)/硬菜(>45min)")


class ConstraintQuery(BaseModel):
    constraint: str = Field(description="自然语言约束描述，如'30分钟内、川菜、下饭、孩子也能吃'")
    cuisine: str | None = Field(default=None, description="显式覆盖菜系筛选")
    taste: str | None = Field(default=None, description="显式覆盖口味筛选")
    crowd: str | None = Field(default=None, description="显式覆盖人群筛选")
    tech: str | None = Field(default=None, description="显式覆盖技法筛选")
    time: str | None = Field(default=None, description="显式覆盖耗时档筛选")
    limit: int = Field(default=10, description="返回数量上限")


class RecommendQuery(BaseModel):
    difficulty: str | None = Field(default=None, description="限定难度")
    tag: str | None = Field(default=None, description="限定标签（旧格式兼容）")
    cuisine: str | None = Field(default=None, description="限定菜系")
    taste: str | None = Field(default=None, description="限定口味")


class WeeklyPlanQuery(BaseModel):
    weeks: int = Field(default=4, ge=1, le=8, description="返回周数，1–8，默认 4")


class ShoppingListQuery(BaseModel):
    weeks: int = Field(default=1, ge=1, le=8, description="采购清单覆盖周数，1–8，默认 1（本周）")


# ---- 工具 ----

@mcp.tool()
async def get_recipe(query: RecipeQuery) -> dict:
    """按菜名查菜谱，返回完整食材与步骤。"""
    recipes = _load_all_recipes()
    for r in recipes:
        if query.name in r["title"] or query.name in r["file"]:
            return {
                "title": r["title"],
                "meta": r["meta"],
                "body": r["body"].strip(),
            }
    return {"error": f"未找到菜谱：{query.name}，试试 list_recipes 查看全部"}


@mcp.tool()
async def list_recipes(query: FilterQuery) -> dict:
    """列出菜谱，可按五维标签（菜系/口味/人群/技法/耗时档）+ 难度筛选。"""
    recipes = _load_all_recipes()
    filters = {
        "tag": query.tag,
        "difficulty": query.difficulty,
        "cuisine": query.cuisine,
        "taste": query.taste,
        "crowd": query.crowd,
        "tech": query.tech,
        "time": query.time,
    }
    matched = _filter_recipes(recipes, filters)
    result = [_recipe_summary(r) for r in matched[:query.limit]]
    return {"total": len(matched), "recipes": result}


@mcp.tool()
async def search_by_constraint(query: ConstraintQuery) -> dict:
    """自然语言约束查询：输入描述（如'30分钟内、川菜、下饭、孩子也能吃'），
    内部解析为五维筛选条件后返回匹配菜谱。各维度显式参数优先于自然语言解析结果。"""
    recipes = _load_all_recipes()
    # 先解析自然语言
    parsed = _parse_constraint(query.constraint)
    # 显式参数覆盖
    filters = {
        "cuisine": query.cuisine or parsed["cuisine"],
        "taste": query.taste or parsed["taste"],
        "crowd": query.crowd or parsed["crowd"],
        "tech": query.tech or parsed["tech"],
        "time": query.time or parsed["time"],
    }
    matched = _filter_recipes(recipes, filters)
    result = [_recipe_summary(r) for r in matched[:query.limit]]
    return {
        "constraint": query.constraint,
        "parsed_filters": {k: v for k, v in filters.items() if v},
        "total": len(matched),
        "recipes": result,
    }


@mcp.tool()
async def recommend_recipe(query: RecommendQuery) -> dict:
    """随机推荐一道菜，可按难度/菜系/口味限定。"""
    import random
    recipes = _load_all_recipes()
    filters = {
        "difficulty": query.difficulty,
        "tag": query.tag,
        "cuisine": query.cuisine,
        "taste": query.taste,
    }
    pool = _filter_recipes(recipes, filters)
    if not pool:
        return {"error": "没有符合条件的菜谱，放宽条件试试"}
    pick = random.choice(pool)
    return {
        "title": pick["title"],
        "meta": pick["meta"],
        "body": pick["body"].strip(),
    }


@mcp.tool()
async def get_weekly_plan(query: WeeklyPlanQuery) -> dict:
    """获取本周及后续几周的推荐菜谱。

    按 recipes/_index.md 的「每周推荐轮换」顺序，以 2026-W36 为锚点计算；
    返回 ISO 周、轮换序号、轮次、菜名、文件与五维标签摘要。
    """
    return _weekly_plan(query.weeks)


@mcp.tool()
async def get_shopping_list(query: ShoppingListQuery) -> dict:
    """按本周（及后续几周）的推荐菜谱，汇总生成本周买菜清单。

    从每道菜的「食材清单」表提取食材与用量：同名食材单位一致时累加（200g+300g=500g），
    单位不同时并列显示；按肉禽蛋/水产/蔬菜菌菇/豆制品/主食干货/调味料分区，
    并附一份可直接贴到备忘录的 Markdown 勾选清单。清水等无需采购项不计入。
    """
    return _shopping_list(query.weeks)


# ---- 入口 ----

def main() -> None:
    import sys
    if "--http" in sys.argv:
        import uvicorn
        app = mcp.http_app()
        uvicorn.run(app, host="0.0.0.0", port=8081)
    else:
        mcp.run()  # STDIO 模式


if __name__ == "__main__":
    main()
