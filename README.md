# CookingCoder 🍳👨‍💻

> **Cook Think In Coder** —— 把做菜当成写代码：每周末一道菜，用交作业的方式记录，让厨艺像 GitHub 绿格子一样可视化成长。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-4.0-brightgreen)](https://github.com/jlowin/fastmcp)

---

## 这是什么？

一个**程序员风格的做饭打卡项目**。核心玩法：

1. **周末做一道菜**（菜谱库已备好 21 道）
2. **按模板交作业**（`homework/week-XX.md`）
3. **push 到 GitHub**，形成贡献绿格子
4. **解锁成就徽章**（打卡/连续/积分系统）

做菜和写代码其实是一回事：**输入（食材）→ 处理（烹饪）→ 输出（成品），翻车就是 bug，改进就是重构。**

## 快速上手

```bash
# 1. clone
git clone git@github.com:IYABAO/CookingCoder.git
cd CookingCoder

# 2. 看菜谱
# 打开 recipes/_index.md，本周推荐第一道

# 3. 交作业
cp homework/templates/weekly-template.md homework/week-36.md
# 编辑 week-36.md：做了什么、食材、翻车点、心得
# 成品图放 assets/week-36/finish.jpg

# 4. 提交
git add .
git commit -m "homework: week-36 青椒肉丝"
git push

# 5. 看成就
python achievements/scripts/stats.py
```

## 目录结构

```
CookingCoder/
├── recipes/               # 菜谱库（21 道，带 frontmatter）
│   ├── _index.md          # 菜谱索引 + 每周推荐轮换
│   └── *.md               # 每道菜的完整做法
├── homework/              # 每周交作业
│   ├── templates/         # 作业模板
│   └── week-XX.md         # 你的作业记录
├── achievements/          # 成就系统
│   ├── README.md          # 积分/徽章规则
│   └── scripts/           # 统计脚本 + CI 自动更新
├── assets/                # 成品图
├── mcp_server/            # MCP Server（AI 查菜谱）
└── .github/workflows/     # 自动更新作业统计
```

## 🍳 菜谱库（recipes/）

21 道家常菜，覆盖不同难度和口味，从新手到进阶都有：

- **新手友好**：西红柿炒鸡蛋、青椒肉丝、可乐鸡翅、手撕包菜
- **下饭硬菜**：麻婆豆腐、鱼香肉丝、红烧排骨、宫保鸡丁
- **进阶挑战**：水煮肉片、红烧牛肉、糖醋排骨、番茄炖牛腩
- **全家滋补**：香菇炖鸡汤、清蒸鲈鱼、油焖大虾

每个菜谱都带 frontmatter（难度/耗时/份量/口味/季节），方便筛选。

> 完整索引见 [recipes/_index.md](recipes/_index.md)

## 🏆 成就系统（achievements/）

交作业不是白交的：

- 完成一次作业 **+10 分**
- 拍照 **+5 分**
- 自创菜谱 **+10 分**
- 记录翻车点 **+5 分**

徽章从「🥚 新手厨师」到「👑 家庭厨神」，连续打卡还有专属徽章。

```bash
python achievements/scripts/stats.py   # 看积分和徽章
```

## 🤖 MCP Server（mcp_server/）

菜谱库已封装成 **MCP 工具**，AI 可以直接回答"今晚吃什么"：

- `get_recipe`：按菜名查菜谱
- `list_recipes`：按标签/难度筛选
- `recommend_recipe`：随机推荐

配合 Claude Code / Cursor 使用，让 AI 当你的私人厨艺助手。

```bash
cd mcp_server
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -e .
python -m cookingcoder_mcp.server
```

> 详细用法见 [mcp_server/README.md](mcp_server/README.md)

## 🤝 一起玩

- **Fork 这个项目**，用自己的方式记录每周做饭
- 提交**新菜谱**（PR 到 `recipes/`）
- 提出**成就玩法**建议（Issue）

做饭是生活，打卡是坚持，push 是见证。**Bon appétit!**

## License

[MIT](LICENSE)
