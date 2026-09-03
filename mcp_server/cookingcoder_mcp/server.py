# -*- coding: utf-8 -*-
"""CookingCoder MCP Server。

把 recipes/ 菜谱库封装成 LLM 可调用的 MCP 工具：
- get_recipe: 按菜名查菜谱
- list_recipes: 按五维标签（菜系/口味/人群/技法/耗时）+ 难度筛选
- search_by_constraint: 自然语言约束查询（如"30分钟内、川菜、下饭"）
- recommend_recipe: 随机/按条件推荐
- get_weekly_plan: 获取本周推荐

用法：
    python -m cookingcoder_mcp.server          # STDIO 模式
    python -m cookingcoder_mcp.server --http   # HTTP 模式
"""
from __future__ import annotations

import re
from pathlib import Path

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# 菜谱库根目录（仓库根目录 /recipes，即 mcp_server 的上两级）
RECIPES_DIR = Path(__file__).resolve().parents[2] / "recipes"

mcp = FastMCP(
    "cookingcoder",
    version="2.0.0",
    instructions="一个家常菜谱工具，支持按菜名查菜谱、按五维标签（菜系/口味/人群/技法/耗时档）筛选、自然语言约束查询、随机推荐。",
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
