# -*- coding: utf-8 -*-
"""CookingCoder MCP Server。

把 recipes/ 菜谱库封装成 LLM 可调用的 MCP 工具：
- get_recipe: 按菜名查菜谱
- list_recipes: 按标签/难度筛选
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
    version="0.1.0",
    instructions="一个家常菜谱工具，支持按菜名查菜谱、按条件筛选、随机推荐。",
)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """解析 markdown 的 YAML frontmatter，返回 (meta, body)。"""
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
                meta[k] = v
        body = text[m.end():]
    return meta, body


def _load_all_recipes() -> list[dict]:
    """加载所有菜谱，返回 [{file, title, meta, body}]。"""
    recipes = []
    for f in sorted(RECIPES_DIR.glob("*.md")):
        if f.name.startswith("_"):
            continue
        meta, body = _parse_frontmatter(f.read_text(encoding="utf-8"))
        recipes.append({"file": f.name, "title": meta.get("title", f.stem), "meta": meta, "body": body})
    return recipes


# ---- 业务参数 ----

class RecipeQuery(BaseModel):
    name: str = Field(description="菜名关键词，支持模糊匹配")


class FilterQuery(BaseModel):
    tag: str | None = Field(default=None, description="标签，如 家常菜/川菜/快手菜/硬菜")
    difficulty: str | None = Field(default=None, description="难度：简单/中等/进阶")
    limit: int = Field(default=10, description="返回数量上限")


class RecommendQuery(BaseModel):
    difficulty: str | None = Field(default=None, description="限定难度")
    tag: str | None = Field(default=None, description="限定标签")


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
    """列出菜谱，可按标签/难度筛选。"""
    recipes = _load_all_recipes()
    result = []
    for r in recipes:
        meta = r["meta"]
        tags = meta.get("tags", "")
        difficulty = meta.get("difficulty", "")
        if query.tag and query.tag not in tags:
            continue
        if query.difficulty and query.difficulty != difficulty:
            continue
        result.append({
            "title": r["title"],
            "difficulty": difficulty,
            "time": meta.get("time", ""),
            "taste": meta.get("taste", ""),
            "tags": tags,
        })
        if len(result) >= query.limit:
            break
    return {"total": len(result), "recipes": result}


@mcp.tool()
async def recommend_recipe(query: RecommendQuery) -> dict:
    """随机推荐一道菜，可按难度/标签限定。"""
    import random
    recipes = _load_all_recipes()
    pool = []
    for r in recipes:
        meta = r["meta"]
        if query.difficulty and meta.get("difficulty", "") != query.difficulty:
            continue
        if query.tag and query.tag not in meta.get("tags", ""):
            continue
        pool.append(r)
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
