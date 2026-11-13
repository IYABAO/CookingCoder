# CookingCoder MCP Server 🍳

把 `recipes/` 菜谱库封装成 **LLM 可调用的 MCP 工具**。配合 Claude Code / Cursor / 任意 MCP 客户端，AI 可以直接回答"今晚吃什么""红烧排骨怎么做"。

## 功能

| 工具 | 说明 |
| --- | --- |
| `get_recipe` | 按菜名查菜谱（完整食材 + 步骤） |
| `list_recipes` | 按标签/难度筛选菜谱 |
| `search_by_constraint` | 自然语言约束查询（如“30分钟内、川菜、下饭”） |
| `recommend_recipe` | 随机推荐一道菜（可限定难度/标签） |
| `get_weekly_plan` | 本周及后续几周的推荐（按 `recipes/_index.md` 轮换） |

## 安装

```bash
cd mcp_server
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate    # macOS / Linux
pip install -e .
```

## 使用

### STDIO 模式（配合 Claude Code / Cursor）

```bash
python -m cookingcoder_mcp.server
```

在 Claude Code 中配置：

```json
{
  "mcpServers": {
    "cookingcoder": {
      "command": "python",
      "args": ["-m", "cookingcoder_mcp.server"],
      "cwd": "/path/to/CookingCoder/mcp_server"
    }
  }
}
```

### HTTP 模式

```bash
python -m cookingcoder_mcp.server --http
# http://0.0.0.0:8081/mcp
```

### Python 客户端调用

```python
import asyncio
from fastmcp import Client

async def main():
    async with Client("http://localhost:8081/mcp") as client:
        # 查菜谱
        res = await client.call_tool("get_recipe", {"query": {"name": "青椒肉丝"}})
        print(res.content[0].text)
        # 随机推荐
        rec = await client.call_tool("recommend_recipe", {"query": {"difficulty": "简单"}})
        print(rec.content[0].text)
        # 本周及后续四周推荐
        plan = await client.call_tool("get_weekly_plan", {"query": {"weeks": 4}})
        print(plan.content[0].text)

asyncio.run(main())
```

## 目录结构

```
mcp_server/
├── pyproject.toml
└── cookingcoder_mcp/
    └── server.py        # MCP Server 主逻辑
```
