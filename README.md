# CookingCoder 🍳👨‍💻

> **Cook Think In Coder** —— 把做菜当成写代码：每周末一道菜，用交作业的方式记录，让厨艺像 GitHub 绿格子一样可视化成长。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-4.x-brightgreen)](https://github.com/jlowin/fastmcp)
[![Recipes](https://img.shields.io/badge/recipes-40-orange)](recipes/_index.md)

---

## 这是什么？

一个**程序员风格的做饭打卡项目**。核心玩法：

1. **周末做一道菜**（菜谱库已备好 40 道，带五维标签+度量标准化）
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
├── recipes/               # 菜谱库（40 道，五维标签+度量标准化+程序化菜谱）
│   ├── _spec.md           # 度量标准库（尺寸/单位/火候/油温/熟度/预处理）
│   ├── _index.md          # 菜谱索引 + 按菜系/口味/人群快捷入口 + 每周推荐轮换
│   └── *.md               # 每道菜的完整做法（常量定义/主流程/Bug Report/Test Cases）
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

40 道家常菜，V2.0 全面升级为**程序化菜谱**：

- **五维标签体系**：菜系 / 口味 / 人群 / 技法 / 耗时档，支持 MCP 多维筛选
- **度量标准化**：所有模糊表述（块/勺/火候/油温）统一引用 `_spec.md` 取值+参照物
- **编程化语言**：常量定义、if/while 主流程、Bug Report（翻车预警）、Test Cases（完成标准）
- **公共方法库**：焯水() / 过油() / 炒糖色() / 勾芡() / 爆香()，菜谱直接调用不重复

覆盖从新手到进阶：

- **新手快手**：西红柿炒鸡蛋、青椒肉丝、凉拌黄瓜、醋溜土豆丝、蒸水蛋
- **下饭硬菜**：麻婆豆腐、鱼香肉丝、回锅肉、红烧排骨、宫保鸡丁
- **进阶挑战**：水煮肉片、水煮鱼、粉蒸肉、糖醋排骨、番茄炖牛腩
- **汤羹蒸菜**：香菇炖鸡汤、玉米排骨汤、清蒸鲈鱼、白灼虾、紫菜蛋花汤

每个菜谱都带完整 frontmatter（五维标签+难度+耗时+份量+季节），方便筛选和检索。

> 完整索引见 [recipes/_index.md](recipes/_index.md)，度量标准见 [recipes/_spec.md](recipes/_spec.md)

## 🏆 成就系统（achievements/）

交作业不是白交的：

- 完成一次作业 **+10 分**
- 拍照 **+5 分**
- 自创菜谱 **+10 分**
- 记录翻车点 **+5 分**

徽章从「🥚 新手厨师」到「👑 家庭厨神」，连续打卡还有专属徽章。V2.0 新增项目级成就：
- 🎨 **技法达人**：菜谱库覆盖 ≥5 种技法
- 🌍 **菜系探险家**：菜谱库跨 ≥3 菜系

```bash
python achievements/scripts/stats.py   # 看积分和徽章
```

## 🤖 MCP Server（mcp_server/）

菜谱库已封装成 **MCP 工具**（v2.0），AI 可以直接回答"今晚吃什么"：

- `get_recipe`：按菜名查菜谱
- `list_recipes`：按五维标签（菜系/口味/人群/技法/耗时档）+ 难度筛选
- `search_by_constraint`：自然语言约束查询（如"30分钟内、川菜、下饭、孩子也能吃"）
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
