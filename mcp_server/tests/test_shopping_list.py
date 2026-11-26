# -*- coding: utf-8 -*-
"""get_shopping_list 的行为验收测试（先写断言，再实现）。

覆盖：工具注册、食材表解析、用量归一、跨菜合并累加、采购分区归类、
Markdown 勾选清单、40 道菜谱解析覆盖率、非法周数报错。
"""
import asyncio
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "mcp_server"))

from fastmcp import Client  # noqa: E402
from cookingcoder_mcp import server  # noqa: E402


def _call_tool(name: str, arguments: dict):
    async def go():
        async with Client(server.mcp) as client:
            return await client.call_tool(name, arguments)

    return asyncio.run(go())


def _recipe_by_title(title: str) -> dict:
    for r in server._load_all_recipes():
        if r["title"] == title:
            return r
    raise AssertionError(f"菜谱不存在：{title}")


def test_tool_list_includes_shopping_list():
    async def go():
        async with Client(server.mcp) as client:
            return await client.list_tools()

    names = {t.name for t in asyncio.run(go())}
    assert len(names) == 6, f"工具数应为 6，实际 {names}"
    assert "get_shopping_list" in names


def test_parse_ingredients_on_known_recipe():
    items = server._parse_ingredients(_recipe_by_title("青椒肉丝")["body"])
    assert len(items) == 4, items
    assert items[0]["name"] == "猪里脊"
    assert items[0]["amount"] == "200g"
    assert items[1]["name"] == "青椒"
    assert items[1]["amount"] == "3个"


def test_all_recipes_parse_at_least_three_ingredients():
    recipes = server._load_all_recipes()
    assert len(recipes) == 40
    for r in recipes:
        items = server._parse_ingredients(r["body"])
        assert len(items) >= 3, f"{r['file']} 只解析出 {len(items)} 个食材"
        for item in items:
            assert item["name"], f"{r['file']} 存在空食材名"
            assert item["amount"], f"{r['file']} 的 {item['name']} 缺用量"


def test_parse_amount_variants():
    assert server._parse_amount("200g") == (200.0, "g")
    assert server._parse_amount("半只(约600g)") == (0.5, "只")
    assert server._parse_amount("1整头(约10瓣)") == (1.0, "整头")
    assert server._parse_amount("1.5勺(22.5ml)") == (1.5, "勺")
    assert server._parse_amount("几滴") == (None, None)


def test_aggregate_sums_same_unit_across_recipes():
    recipes = [
        {"title": "甲菜", "file": "a.md", "meta": {}, "body": "## 食材清单（Input）\n\n| 食材 | 用量 |\n| --- | --- |\n| 青椒 | 3个 |\n| 葱 | 1根 |\n"},
        {"title": "乙菜", "file": "b.md", "meta": {}, "body": "## 食材清单（Input）\n\n| 食材 | 用量 |\n| --- | --- |\n| 青椒 | 2个 |\n| 葱 | 1把(约100g) |\n"},
    ]
    result = server._aggregate_shopping(recipes)
    items = {i["name"]: i for sec in result["sections"] for i in sec["items"]}
    assert items["青椒"]["quantity"] == "5个", items["青椒"]
    assert items["青椒"]["used_in"] == ["甲菜", "乙菜"]
    assert "1根" in items["葱"]["quantity"] and "1把(约100g)" in items["葱"]["quantity"], items["葱"]


def test_sections_classification():
    cases = {
        "猪里脊": "肉禽蛋",
        "鲈鱼": "水产",
        "青椒": "蔬菜菌菇",
        "豆腐": "豆制品",
        "花椒": "调味料",
        "粉丝": "主食干货",
    }
    for name, expected in cases.items():
        assert server._classify_section(name) == expected, (name, server._classify_section(name))


def test_shopping_list_end_to_end_mcp():
    result = _call_tool("get_shopping_list", {"query": {"weeks": 1}})
    payload = json.loads(result.content[0].text)
    assert "error" not in payload
    today_index = server._weekly_index(date.today())
    order = server._load_weekly_order()
    assert payload["weeks"][0]["title"] == order[today_index["index"] - 1]
    assert payload["item_count"] >= 5
    assert payload["markdown"].count("- [ ]") == payload["item_count"], "清单条数必须与 item_count 一致"


def test_shopping_list_covers_every_planned_recipe_ingredient():
    plan = server._weekly_plan(2, today=date(2026, 11, 26))
    recipes = server._load_all_recipes()
    by_title = {r["title"]: r for r in recipes}
    payload = server._shopping_list(2, today=date(2026, 11, 26))
    names = {i["name"] for sec in payload["sections"] for i in sec["items"]}
    for week in plan["weeks"]:
        for item in server._parse_ingredients(by_title[week["title"]]["body"]):
            if server._is_skipped_ingredient(item["name"]):
                continue
            assert item["name"] in names, f"清单漏了 {item['name']}（{week['title']}）"


def test_water_items_are_not_shopped():
    recipes = [
        {"title": "丙菜", "file": "c.md", "meta": {}, "body": "## 食材清单（Input）\n\n| 食材 | 用量 |\n| --- | --- |\n| 冰水/凉开水 | 适量 |\n| 水发木耳 | 50g |\n| 盐 | 1小勺 |\n"},
    ]
    result = server._aggregate_shopping(recipes)
    names = {i["name"] for sec in result["sections"] for i in sec["items"]}
    assert "冰水/凉开水" not in names, "水不属于采购项"
    assert "水发木耳" in names, "水发木耳是真实食材，不能被水规则误杀"
    assert result["item_count"] == 2


def test_shopping_list_weeks_out_of_range():
    assert server._shopping_list(0)["error"]
    assert server._shopping_list(9)["error"]
