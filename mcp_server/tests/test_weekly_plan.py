# -*- coding: utf-8 -*-
"""get_weekly_plan 的行为验收测试。

覆盖：MCP 工具注册、固定日期、四周长度、跨 40 周循环、跨年、文件存在性、
以及每周轮换解析为空时显式报错。
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


def _run(coro):
    return asyncio.run(coro)


def _list_tools():
    async def go():
        async with Client(server.mcp) as client:
            return await client.list_tools()

    return _run(go())


def _call_tool(name: str, arguments: dict):
    async def go():
        async with Client(server.mcp) as client:
            return await client.call_tool(name, arguments)

    return _run(go())


def test_list_tools_includes_weekly_plan():
    tools = _list_tools()
    names = {tool.name for tool in tools}
    assert len(names) == 6, f"工具数应为 6，实际 {names}"
    assert names == {
        "get_recipe",
        "list_recipes",
        "search_by_constraint",
        "recommend_recipe",
        "get_weekly_plan",
        "get_shopping_list",
    }


def test_weekly_order_count():
    order = server._load_weekly_order()
    assert len(order) == 40
    assert order[10] == "蒜蓉油麦菜"


def test_all_weekly_titles_map_to_files():
    order = server._load_weekly_order()
    by_title = {r["title"]: r for r in server._load_all_recipes()}
    missing = [title for title in order if title not in by_title]
    assert not missing, f"轮换菜名无法映射到菜谱文件：{missing}"
    for title in order:
        assert (ROOT / "recipes" / by_title[title]["file"]).is_file()


def test_weekly_index_fixed_date():
    info = server._weekly_index(date(2026, 11, 13))
    assert info["week"] == "2026-W46"
    assert info["index"] == 11
    assert info["round"] == 1
    assert info["week_start"] == "2026-11-09"


def test_weekly_plan_fixed_date_and_files():
    plan = server._weekly_plan(4, today=date(2026, 11, 13))
    assert "error" not in plan
    assert len(plan["weeks"]) == 4
    first = plan["weeks"][0]
    assert first["week"] == "2026-W46"
    assert first["index"] == 11
    assert first["title"] == "蒜蓉油麦菜"
    assert first["file"] == "suanrong-youmaicai.md"
    for item in plan["weeks"]:
        assert (ROOT / "recipes" / item["file"]).is_file(), item


def test_weekly_plan_crosses_40_weeks():
    plan = server._weekly_plan(1, today=date(2027, 6, 7))
    assert "error" not in plan
    item = plan["weeks"][0]
    assert item["round"] == 2
    assert item["index"] == 1
    assert item["title"] == "青椒肉丝"
    assert item["file"] == "qingjiao-rousi.md"


def test_weekly_plan_crosses_year():
    plan = server._weekly_plan(1, today=date(2027, 1, 4))
    assert "error" not in plan
    item = plan["weeks"][0]
    assert item["week"] == "2027-W01"
    assert 1 <= item["index"] <= 40
    assert (ROOT / "recipes" / item["file"]).is_file()


def test_mcp_weekly_plan_payload():
    """工具返回结构与当周轮换一致；按当天日期推导，避免硬编码跨周失效。"""
    result = _call_tool("get_weekly_plan", {"query": {"weeks": 4}})
    payload = json.loads(result.content[0].text)
    assert "error" not in payload
    assert len(payload["weeks"]) == 4
    today_info = server._weekly_index(date.today())
    order = server._load_weekly_order()
    assert payload["weeks"][0]["week"] == today_info["week"]
    assert payload["weeks"][0]["title"] == order[today_info["index"] - 1]


def test_empty_order_returns_error(monkeypatch):
    monkeypatch.setattr(server, "_load_weekly_order", lambda: [])
    plan = server._weekly_plan(1, today=date(2026, 11, 13))
    assert plan.get("error"), "每周推荐为空时必须显式报错，不能静默返回空列表"
