# CookingCoder 菜谱展示方案选型调研报告

> **调研基准**：2026 年 9 月 3 日 ｜ 数据来源：各项目官方文档、GitHub API 实时抓取、官方公告
> **项目背景**：CookingCoder 已有 40 个结构化 Markdown 菜谱（`recipes/*.md`），frontmatter 含五维标签（cuisine 菜系 / taste 口味 / crowd 人群 / tech 技法 / time 耗时），需以"类 GitBook"形态（左侧目录树 + 右侧正文 + 搜索 + 标签筛选）公开展示。

---

## 一、结论先行

| 角色 | 方案 | 核心理由 |
|------|------|----------|
| **首选** | **MkDocs + Material for MkDocs** | 唯一开箱即用支持 frontmatter tags 自动生成分类页；部署极简（pip + yml）；中文界面完整；视觉高度接近 GitBook；纯静态可部署任意平台；Material 主题极活跃（2026-08 仍在更新） |
| **备选** | **vuepress-theme-hope（VuePress 2）** | 中文生态最好（作者为中国开发者）；博客模式原生支持标签页+分类页；直接吃 .md + frontmatter；MIT 开源；2026-05 仍在高频更新；适合偏好 Vue/JS 技术栈的场景 |
| **技术探索向** | Astro Starlight | frontmatter 有类型化 schema 校验；content collections API 开发五维交叉筛选体验最佳；Pagefind 中文搜索好；但社区较小（9k stars）、中文文档少、无内置标签页 |

**已明确淘汰**：Gitee Pages（已正式下线）、看云（已边缘化/迁移期）、Vdoing（基于已停维的 VuePress 1.x，2023 年后无更新）、mdBook（无 frontmatter/标签/中文搜索）、Read the Docs/Sphinx（Markdown 非一等公民）、GitBook 云（不开源+标签不可用）、Wolai（财务危机后状态不明）。

---

## 二、全方案对比总表

> 评分说明：★★★★★ 优秀 / ★★★★ 良好 / ★★★ 一般 / ★★ 较弱 / ★ 不适用 / ⛔ 已不可用

| 方案 | 开源/License | 托管形态 | 部署难度 | 中文支持 | Markdown复用 | 搜索(中文) | 标签/筛选能力 | 生态活跃度 | 菜谱适配度 |
|------|-------------|----------|----------|----------|-------------|-----------|--------------|-----------|-----------|
| **MkDocs + Material** | MIT / BSD-2 | 自托管静态 | 低 | ★★★★ | ★★★★★ | ★★★★ | ★★★★ (唯一内置tags) | ★★★★★ | ★★★★★ |
| **vuepress-theme-hope** | MIT | 自托管静态 | 低-中 | ★★★★★ | ★★★★★ | ★★★★ | ★★★★ (博客模式tags+分类) | ★★★★★ | ★★★★★ |
| **VitePress** | MIT | 自托管静态 | 低 | ★★★★ | ★★★★★ | ★★★ (需配分词) | ★★ (无内置,需开发) | ★★★★★ | ★★★ |
| **Docusaurus** | MIT | 自托管静态 | 低-中 | ★★★★ | ★★★★★ | ★★★ (需Algolia/插件) | ★★★ (blog有tags,docs需开发) | ★★★★★ | ★★★ |
| **Astro Starlight** | MIT | 自托管静态 | 中 | ★★★ | ★★★★ | ★★★★ (Pagefind中文好) | ★★★ (无内置,但开发体验好) | ★★★★ | ★★★★ |
| **Docsify** | MIT | 自托管(零构建) | 极低 | ★★★★ | ★★★★★ | ★★★ (子串匹配无分词) | ★★ (无内置,需开发) | ★★★ (发版停滞3年) | ★★★ |
| **mdBook** | MPL-2.0 | 自托管静态 | 低 | ★★ (中文搜索差) | ★★★ | ★ (无中文分词) | ★ (完全无tags) | ★★★★ | ★ |
| **Read the Docs/Sphinx** | MIT / BSD | 云+自托管 | 云低/自托管高 | ★★★ | ★★ (Markdown非一等公民) | ★★★ | ★ (无tags) | ★★★★ | ★ |
| **GitBook(云)** | 闭源SaaS | 纯云托管 | 低 | ★★★ | ★★★ | ★★★ | ★ (frontmatter不可用) | 商业活跃 | ★★ |
| **Halo** | GPL-3.0 | 纯自托管(需服务器) | 中 | ★★★★★ | ★★ (存数据库非.md) | ★★★ | ★★ (博客标签,非文档目录树) | ★★★★★ | ★★ |
| **语雀** | 闭源SaaS | 纯云托管 | 低 | ★★★★★ | ★★ (导入后转自有格式) | ★★★★ | ★★ (手动目录+标签) | 商业活跃 | ★★ |
| **飞书知识库** | 闭源SaaS | 纯云托管 | 低 | ★★★★★ | ★★ (转自有块格式) | ★★★★ | ★★ (层级目录+标签) | 商业活跃 | ★ |
| **看云** | 闭源SaaS | 纯云托管 | 低 | ★★★★ | ★★★ | ★★ | ★★ | ⚠️ 已边缘化 | ★ |
| **Gitee Pages** | — | 云托管 | — | — | — | — | — | ⛔ **已下线** | ⛔ |
| **Vdoing** | MIT | 自托管静态 | 低 | ★★★★ | ★★★★ | ★★ | ★★★ | ⚠️ 2023后停滞 | ★★ |
| **Wolai** | 闭源SaaS | 纯云托管 | 低 | ★★★★ | ★★ | ★★ | ★★ | ⚠️ 状态不明 | ★ |

---

## 三、国外方案分方案简评

### 1. MkDocs + Material for MkDocs ⭐ 首选

- **开源**：MkDocs 核心 BSD-2-Clause（约 22.4k stars）；Material 主题 MIT（约 27.4k stars）
- **托管**：纯自托管静态站，`mkdocs build` 产出纯 HTML/CSS/JS
- **部署**：`pip install mkdocs-material` → 写 `mkdocs.yml` → `mkdocs build`，约 2 小时上线
- **中文**：Material 内置 60+ 语言含简体中文，界面中文化完整；搜索基于 lunr.js，配置 `search.separator` 后中文可用
- **Markdown**：原生吃 .md，frontmatter（meta）完整支持，Material 扩展了 admonition/tabs/grids 等丰富语法
- **搜索**：内置客户端全文搜索（lunr.js），零外部依赖
- **标签/筛选**：★ 8 方案中**唯一开箱即用支持 frontmatter tags 自动生成分类索引页**（`/tags/`）；另有 blog 插件支持分类/标签/归档。五维标签需映射为带前缀的一维标签（如 `cuisine:川菜`、`taste:麻辣`）
- **复用成本**：放入 `docs/` 目录 + 配置 nav 即可，frontmatter 标签可直接被利用
- **活跃度**：Material 主题极活跃（最后推送 2026-08-30，6764 commits）；MkDocs 核心进入稳定成熟期（最后推送 2025-10，功能稳定）
- **劣势**：① Python 生态，插件开发需 Python 知识（但日常使用零代码）；② Material Insiders 版部分高级功能需付费赞助；③ 内置 tags 是一维标签云，五维交叉筛选（同时按菜系+口味+人群）超出开箱能力，需自定义开发；④ MkDocs 核心更新缓慢
- **地址**：[Material 官网](https://squidfunk.github.io/mkdocs-material/) ｜ [Material GitHub](https://github.com/squidfunk/mkdocs-material) ｜ [MkDocs 官网](https://www.mkdocs.org/)

### 2. Docusaurus

- **开源**：MIT，约 66.2k stars（8 方案中最高）
- **托管**：纯自托管静态站，React 技术栈
- **部署**：`npm init docusaurus@latest` 脚手架，约半天上线
- **中文**：官方维护中文文档站，i18n 内置成熟；搜索默认推荐 Algolia DocSearch（开源项目免费），也可用 `docusaurus-search-local` 社区插件（支持中文分词）
- **Markdown**：原生支持 .md 和 .mdx（可嵌入 React 组件），frontmatter 完整支持
- **搜索**：默认无内置搜索，需配置 Algolia 或社区插件
- **标签/筛选**：blog 插件内置 tags 功能可自动生成标签索引页；但 docs 核心内容按自定义 frontmatter 字段做多维筛选需自行开发 React 组件
- **复用成本**：放入 `docs/` 目录即可，需配置 sidebar（可自动生成）
- **活跃度**：Meta 官方维护，极活跃（最后推送 2026-09-01，最新 v3.10.2）
- **劣势**：① React 技术栈锁定，定制主题需懂 React/JSX；② 默认不带搜索，需额外配置；③ 构建产物较重（React runtime）；④ docs 多维筛选非开箱即用
- **地址**：[官网](https://docusaurus.io/) ｜ [中文文档](https://docusaurus.io/zh-CN) ｜ [GitHub](https://github.com/facebook/docusaurus)

### 3. VitePress

- **开源**：MIT，约 18.3k stars
- **托管**：纯自托管静态站，Vite + Vue
- **部署**：一个 `.vitepress/config.ts` + `docs/` 目录，Vite 构建秒级，约 2-3 小时上线
- **中文**：Vue 团队维护，官方有中文版；中文社区活跃；内置本地搜索基于 FlexSearch，中文需手动配置 `search.options.locales`
- **Markdown**：原生吃 .md，frontmatter 完整支持，可在 md 中使用 Vue 组件
- **搜索**：内置本地全文搜索（FlexSearch，零外部依赖），也支持 Algolia
- **标签/筛选**：侧边栏可自动从文件结构生成（`sidebar: 'auto'`）；**无内置 tags/分类页**，五维筛选需自行开发 Vue 组件（可利用 `createContentLoader` API）
- **复用成本**：放入目录即用，frontmatter 原样保留
- **活跃度**：Vue 团队/VoidZero 维护，极活跃（最后推送 2026-09-02，v2.0.0-alpha 已发布）
- **劣势**：① 无内置标签/分类页，五维筛选完全需自定义开发；② 中文搜索默认质量一般，需配分词；③ v2.0 仍在 alpha
- **地址**：[官网](https://vitepress.dev/) ｜ [GitHub](https://github.com/vuejs/vitepress)

### 4. Astro Starlight

- **开源**：MIT，约 9.2k stars
- **托管**：纯自托管静态站，Astro 构建（默认零 JS）
- **部署**：需了解 content collections 概念，约半天上手
- **中文**：i18n 内置有中文界面；搜索基于 Pagefind（Rust 静态搜索引擎），**对中文分词支持较好**；中文社区文档相对较少
- **Markdown**：原生支持 .md 和 .mdx，frontmatter 有**类型化 schema 校验**（zod），可强类型约束五维标签字段——独特优势
- **搜索**：内置 Pagefind 本地全文搜索，中文支持好，零外部依赖
- **标签/筛选**：无内置 tags 分类页，但可通过 `getCollection()` API 查询所有文档 frontmatter，自行构建按任意字段筛选的动态页面。由于 frontmatter 有类型 schema，多维筛选开发体验在 8 方案中最好
- **复用成本**：需放入 `src/content/docs/` 并定义 collection schema（可宽松配置）
- **活跃度**：Astro 官方团队维护，活跃（最后推送 2026-09-02，最新 @astrojs/starlight@0.41.3，已支持 Astro 7）
- **劣势**：① star 数相对较少（9k+），社区和插件生态不如 Docusaurus/VitePress/MkDocs；② 中文社区文档不够丰富；③ 无内置标签页；④ 版本号仍在 0.x；⑤ Astro 学习曲线
- **地址**：[官网](https://starlight.astro.build/) ｜ [GitHub](https://github.com/withastro/starlight)

### 5. Docsify

- **开源**：MIT，约 31.5k stars
- **托管**：纯自托管，**无需构建**——一个 index.html + CDN 引入即可
- **部署**：极低，约 30 分钟上线。零构建、零配置
- **中文**：官方有完整中文版；中文社区活跃；搜索插件支持中文但**基于子串匹配无分词**
- **Markdown**：原生吃 .md（运行时加载 marked 渲染），frontmatter 需插件
- **搜索**：内置全文搜索插件（客户端 IndexedDB），中文为子串匹配无分词
- **标签/筛选**：无内置 tags/分类，frontmatter 五维标签需插件 + 自定义客户端开发
- **复用成本**：直接放入目录即用，零配置——8 方案中复用成本最低
- **活跃度**：develop 分支极活跃（最后推送 2026-09-03 当天），但**正式 release 停在 v4.13.1（2023-06），已超 3 年未发新版**，v5 在 develop 分支开发中。处于"开发活跃但发版停滞"状态
- **劣势**：① 客户端渲染，**SEO 极差**（百度等国内搜索引擎难以索引）；② 正式版 3 年未发新 release；③ 无构建步骤导致首屏加载慢（每页异步加载 md 再渲染）；④ frontmatter/标签生态弱；⑤ 大型项目（100+ 页）性能下降
- **地址**：[官网](https://docsify.js.org/) ｜ [中文文档](https://docsify.js.org/#/zh-cn/) ｜ [GitHub](https://github.com/docsifyjs/docsify)

### 6. mdBook

- **开源**：MPL-2.0，约 22.1k stars
- **托管**：纯自托管静态站，Rust 单二进制
- **部署**：`cargo install mdbook` + `book.toml` + `SUMMARY.md`，约 2 小时
- **中文**：界面有中文翻译；**内置搜索对中文支持差**（基于英文空格分词逻辑，连续中文无法切分）
- **Markdown**：原生吃 .md；**frontmatter 支持非常有限**，非核心功能
- **搜索**：内置客户端搜索，但中文分词差
- **标签/筛选**：目录树必须手动在 `SUMMARY.md` 中定义（不自动生成）；**完全没有 tags/分类筛选功能**
- **复用成本**：需手动编写 SUMMARY.md 逐个列出 40 个文件；frontmatter 五维标签基本无法利用——复用成本偏高
- **活跃度**：Rust 官方维护，活跃（最后推送 2026-09-02，最新 v0.5.3），但迭代偏保守
- **劣势**：① 中文搜索质量差；② frontmatter 支持极弱；③ 无标签/分类筛选；④ 目录树需手动维护；⑤ 主题定制能力有限；⑥ 生态偏 Rust 社区
- **结论**：菜谱核心需求（frontmatter 标签 + 中文搜索 + 分类筛选）全部不满足，**不推荐**
- **地址**：[官方文档](https://rust-lang.github.io/mdBook/) ｜ [GitHub](https://github.com/rust-lang/mdBook)

### 7. Read the Docs / Sphinx

- **开源**：平台代码 MIT（约 8.4k stars）；Sphinx BSD-2-Clause
- **托管**：两者皆可——readthedocs.org 云平台免费托管开源文档；自托管复杂度高（Django + Celery + Redis + PostgreSQL）
- **部署**：云平台低（关联仓库自动构建）；自托管高
- **中文**：Sphinx 有官方中文文档；搜索基于 Whoosh，中文支持一般
- **Markdown**：★ **Sphinx 原生使用 reStructuredText，Markdown 非一等公民**，需安装 MyST-Parser 扩展
- **搜索**：内置服务端全文搜索（Whoosh），中文一般
- **标签/筛选**：目录树通过 toctree 手动定义；无 frontmatter 标签筛选
- **复用成本**：较高——需配置 MyST 解析 Markdown，手动编写 toctree，frontmatter 无法利用
- **活跃度**：Read the Docs Inc. 维护，活跃（最新 release 2026.05.26）；Sphinx 成熟稳定
- **劣势**：① Markdown 非一等公民；② 自托管复杂度高；③ 无标签/分类筛选；④ 默认主题老旧；⑤ 中文搜索一般；⑥ 对菜谱非技术文档场景，Sphinx 的 API 文档等核心能力无用
- **结论**：技术栈与 Markdown 菜谱文件不匹配，**不推荐**
- **地址**：[云平台](https://readthedocs.org/) ｜ [GitHub](https://github.com/readthedocs/readthedocs.org) ｜ [Sphinx](https://www.sphinx-doc.org/)

### 8. GitBook（云产品）

- **开源**：当前云产品**不开源**；旧版前端 GPL-3.0（遗留），旧版 CLI 无 License 且已实质停止维护（最后推送 2024-06）
- **托管**：纯云托管 SaaS，不支持自托管
- **部署**：低，注册后 Git Sync 关联仓库即可
- **中文**：界面有基础多语言，中文 UI 覆盖一般；中文搜索分词有限
- **Markdown**：支持 .md，有自家 block 扩展；frontmatter 支持有限
- **搜索**：内置全文搜索 + AI Assistant，中文一般
- **标签/筛选**：目录树手动组织；**不支持按自定义 frontmatter 字段做筛选或自动生成分类页**——菜谱场景硬伤
- **复用成本**：可 Git Sync 批量导入，但需按页面层级重组，frontmatter 五维标签无法被利用
- **活跃度**：商业公司维护，云产品迭代活跃（AI 功能持续更新）；旧版开源 CLI 已死
- **劣势**：① 不开源、无法自托管；② frontmatter 自定义字段无法驱动筛选/分类，五维标签完全无法利用；③ 主题定制受云平台限制；④ 免费版有成员和功能限制
- **结论**：开源项目通常要求可自托管，且标签体系无法利用，**不推荐**
- **地址**：[官网](https://www.gitbook.com/) ｜ [旧版前端(遗留)](https://github.com/GitBookIO/gitbook)

---

## 四、国内方案分方案简评

### 1. vuepress-theme-hope（VuePress 2）⭐ 备选

- **开源**：MIT，约 3.5k stars
- **托管**：纯自托管静态站，可部署任意静态托管
- **部署**：`npm init vuepress-theme-hope@latest` 一键初始化，约 1-2 小时上线
- **中文**：★ **原生中文支持极好**——作者为中国开发者（Mister-Hope），文档完整中文版，界面默认中文，内置中文搜索，中文社区活跃
- **Markdown**：直接吃 .md，VuePress 2 原生支持 frontmatter，可解析自定义字段
- **搜索**：内置搜索插件（支持中文全文检索），也可接入 Algolia DocSearch
- **标签/筛选**：★ 左侧目录树自动生成；**博客模式原生支持标签页和分类页**；frontmatter 自定义字段可通过 blog 配置生成分类/标签索引页，支持多维度标签。五维交叉筛选需少量自定义客户端组件
- **复用成本**：低，直接放入 `docs/` 目录即可，frontmatter 原生支持
- **活跃度**：★ 非常活跃（5777 commits，482 releases，最新 v2.0.0-rc.107 2026-05-14，基于 VuePress 2 + Vite 7 + Vue 3）
- **劣势**：① v2 仍在 RC 阶段（功能稳定但正式版未发布）；② 构建产物较大（含 Vue 3 运行时）；③ 五维交叉筛选非开箱即用
- **地址**：[官网](https://theme-hope.vuejs.press) ｜ [GitHub](https://github.com/vuepress-theme-hope/vuepress-theme-hope)

### 2. Halo

- **开源**：GPL-3.0（社区版），约 32k+ stars
- **托管**：纯自托管，需自有服务器（Docker 部署），无官方云托管
- **部署**：中——Docker 一键启动，但需自有服务器、域名备案、反向代理、HTTPS
- **中文**：原生中文，国内最活跃的开源 CMS 之一，中文社区非常活跃
- **Markdown**：编辑器支持 Markdown，但**文章存储在数据库中（H2/MySQL/PostgreSQL），不是直接吃 .md 文件**
- **搜索**：需安装搜索插件，中文分词质量一般
- **标签/筛选**：支持文章分类和标签（原生），可生成分类页/标签页；但**左侧目录树不是原生功能**，需主题支持；五维交叉筛选无法实现
- **复用成本**：中-高——需批量导入到数据库，frontmatter 映射需额外开发
- **活跃度**：★ 非常活跃（6192 commits，265 releases，最新 v2.25.4 2026-06-24，已商业化）
- **劣势**：① 定位是博客/CMS，不是文档站，类 GitBook 目录树需主题插件拼凑；② 需要服务器运维（数据库、备份、升级），对 40 篇菜谱的轻量项目过重；③ Markdown 文件不是 source of truth，与仓库 md 无法双向同步，破坏"文档即代码"工作流；④ GPL-3.0 协议要求二次开发开源
- **结论**：功能强大但定位不匹配 + 运维成本过重，**不推荐用于菜谱展示**
- **地址**：[官网](https://halo.run) ｜ [GitHub](https://github.com/halo-dev/halo) ｜ [Gitee](https://gitee.com/halo-dev/halo)

### 3. 语雀（Yuque）

- **开源**：闭源 SaaS（蚂蚁集团）
- **托管**：纯云托管
- **部署**：低，注册即用
- **中文**：原生中文，中文搜索质量好（自研搜索引擎），中文社区活跃
- **Markdown**：编辑器支持 Markdown，但**导入后转为语雀自有富文本格式**；frontmatter 会被当作正文，不会被解析为元数据；批量导出能力有限
- **搜索**：内置全文检索，中文搜索质量较好
- **标签/筛选**：支持知识库目录树（手动编排）和文档标签，但**不支持按自定义 frontmatter 字段自动生成分类筛选页**
- **复用成本**：中——可批量导入，但 frontmatter 丢失、目录需手动重建、标签需重新关联
- **活跃度**：用户量千万级，蚂蚁集团持续运营，2025-2026 年仍有更新
- **劣势**：① 数据锁定严重，导入后转自有格式，frontmatter 完全丢失，不利于"源码即文档"工作流；② 免费版有空间和成员限制，自定义域名/高级搜索需付费；③ 不支持 Git PR/版本 diff 等开源协作流程
- **结论**：适合内部协作，不适合开源项目公开展示，**不推荐**
- **地址**：[官网](https://www.yuque.com)

### 4. 飞书知识库（Feishu Wiki）

- **开源**：闭源 SaaS（字节跳动）
- **托管**：纯云托管
- **部署**：低，注册即用，支持"互联网公开"分享
- **中文**：原生中文，中文搜索质量好（字节搜索技术）
- **Markdown**：支持 Markdown 导入，但**导入后转为飞书自有块格式**，frontmatter 不被解析
- **搜索**：内置全文检索，中文质量好
- **标签/筛选**：支持层级目录树和文档标签，但不支持按自定义字段生成分类筛选页
- **复用成本**：中——批量导入需 API 或工具，frontmatter 丢失
- **活跃度**：字节跳动核心产品，用户量亿级，持续高频更新
- **劣势**：① 公开分享 URL 是飞书域名（`feishu.cn/wiki/...`），无法绑定自定义域名，品牌感差；② 数据锁定 + 不支持 Git 驱动的开源协作；③ 定位是企业协作，公开分享不是核心场景
- **结论**：不适合开源项目专业展示，**不推荐**
- **地址**：[官网](https://www.feishu.cn)

### 5. 看云（KanCloud）⚠️ 已边缘化

- **开源**：闭源 SaaS（顶想信息/ThinkPHP 团队旗下）
- **托管**：纯云托管
- **部署**：低，注册即用，专注"书籍"形态
- **中文**：原生中文
- **Markdown**：原生 Markdown 编辑器，支持导入 GitHub 文档、导出 EPUB/PDF/WORD
- **搜索**：内置书籍内搜索，中文质量一般
- **标签/筛选**：章节目录树是核心形态，但不支持按自定义字段生成分类筛选页
- **活跃度**：⚠️ **已边缘化**——官网首页明确标注"看云写作服务已经迁移到更适合企业的知识管理"，引导用户迁移至"顶想云知识管理"；看云本身仍可访问但处于维护状态，2022 年宣布迁移后新功能投入极少
- **劣势**：① 产品已进入维护/迁移期，官方主动引导迁移，未来存在停服风险；② 生态停滞，插件/主题几乎不更新；③ 开源协作能力差
- **结论**：有停服风险，**不推荐作为长期展示平台**
- **地址**：[官网](https://www.kancloud.cn)

### 6. Gitee Pages ⛔ 已下线

- **状态**：⛔ **功能已正式下线**。Gitee 官方帮助页面（https://gitee.com/help/articles/4136）标题已明确标注"Gitee Pages（功能已下线）"
- **历史情况**：此前仅支持 Jekyll/Hugo/Hexo 三种静态生成器自动编译，不支持 MkDocs/VitePress/Docusaurus/VuePress/Docsify；曾因合规要求暂停新用户开通（需实名认证），后续正式下线
- **结论**：已不可用，**菜谱项目不能依赖此方案**。应转向 GitHub Pages + 国内 CDN 加速，或阿里云 OSS/ESA、Vercel、Cloudflare Pages 等替代托管

### 7. Vdoing（vuepress-theme-vdoing）⚠️ 已停滞

- **开源**：MIT，约 3.8k stars
- **托管**：纯自托管静态站
- **中文**：原生中文，作者为中国开发者（xugaoyi）
- **Markdown**：直接吃 .md，VuePress 1.x 支持 frontmatter
- **标签/筛选**：左侧目录树自动生成是核心卖点；支持博客标签页和分类页
- **活跃度**：⚠️ **已停滞**——最新版 v1.12.9（2023-08-04），**主题代码最后更新为 2023 年 8 月**；基于**已停止维护的 VuePress 1.x**；作者已基本停止功能更新
- **劣势**：① 基于已停维的 VuePress 1.x，存在安全漏洞和兼容性风险；② 搜索能力较弱；③ 生态停滞，无新功能/bug 修复，无 VuePress 2.x 迁移计划
- **结论**：不适合新项目，**不推荐**。如需 VuePress 生态应选 vuepress-theme-hope（基于 VuePress 2）
- **地址**：[官网](https://doc.xugaoyi.com) ｜ [GitHub](https://github.com/xugaoyi/vuepress-theme-vdoing)

### 8. Wolai（我来）⚠️ 高风险

- **开源**：闭源 SaaS
- **状态**：⚠️ **待核实/高风险**——曾是国内最知名的 Notion 替代品，但 2023-2024 年经历严重财务困难，团队大规模裁员，产品更新停滞；后被收购（具体收购方和运营状态待核实），2025-2026 年产品状态不明朗
- **结论**：存在数据安全和停服风险，**不建议作为开源项目的长期展示平台**
- **地址**：[官网](https://www.wolai.com)（状态待核实）

---

## 五、推荐结论与理由

### 首选：MkDocs + Material for MkDocs

**推荐理由（按权重排序）**：

1. **唯一开箱即用的 frontmatter 标签分类**：Material 主题内置 tags 功能，在 frontmatter 中写 `tags:` 即可自动生成 `/tags/` 标签索引页和按标签筛选的列表页。这是所有调研方案中唯一不需要额外开发就能利用 frontmatter 元数据生成分类的方案，与菜谱五维标签体系天然契合。
2. **部署极简，零代码日常维护**：`pip install mkdocs-material` + 一个 `mkdocs.yml` 配置文件 + `mkdocs build`，不需要写 React/Vue/Astro 组件。对一个 Go/PHP 全栈开发者而言，YAML 配置比前端框架学习成本低得多。
3. **中文界面完整**：Material 内置 60+ 语言含简体中文，界面中文化开箱即用，不需要额外配置 i18n。
4. **视觉高度接近 GitBook**：默认左侧目录树 + 右侧正文 + 顶部导航，是公认的最美观的 MkDocs 主题，定制通过 CSS 变量即可，无需前端框架知识。
5. **纯静态产物，部署灵活**：构建产物为纯 HTML/CSS/JS，可部署到 GitHub Pages、Vercel、Cloudflare Pages、阿里云 OSS/ESA 等任意静态托管。Gitee Pages 已下线不影响。
6. **生态极活跃**：Material 主题最后推送 2026-08-30，持续高频更新；MkDocs 核心虽更新慢但功能稳定成熟。
7. **40 个 md 复用成本极低**：直接放入 `docs/` 目录即可，frontmatter 标签可直接被 Material 的 tags 功能利用。

**五维标签的落地方式**：将现有 frontmatter 中的五个独立字段映射为带维度前缀的标签，例如：
```yaml
tags:
  - cuisine:川菜
  - taste:麻辣
  - crowd:儿童
  - tech:炒
  - time:30分钟
```
Material 会自动生成 `/tags/` 索引页，点击任一标签即可筛选出对应菜谱。如需五维交叉筛选（同时选菜系+口味），可通过 Material 的 tags 额外开发一个客户端过滤组件，或使用 blog 插件的分类功能。

### 备选：vuepress-theme-hope（VuePress 2）

**适用场景**：如果偏好 Vue/JS 技术栈、希望中文社区支持更好、或未来需要更复杂的前端交互（如五维交叉筛选组件），vuepress-theme-hope 是最佳替代。

**与首选的差异**：
- 中文生态更好（作者为中国开发者，文档/社区/问题解答全中文）
- 博客模式原生支持标签页 + 分类页，多维度标签配置更灵活
- 技术栈为 Vue 3 + Vite，前端定制能力更强（但需要 Vue 知识）
- v2 仍在 RC 阶段，正式版未发布（但功能已稳定）
- 构建产物比 MkDocs 大（含 Vue 运行时）

### 技术探索向：Astro Starlight

**适用场景**：如果愿意投入开发资源实现真正的五维交叉筛选（同时按菜系+口味+人群+技法+耗时过滤），Starlight 的 content collections + 类型化 frontmatter schema 提供了最好的开发体验。Pagefind 中文搜索也是所有方案中质量最好的。但社区较小、中文文档少、无内置标签页，需要更多自行开发。

---

## 六、迁移落地路径（以首选 MkDocs + Material 为例）

### 步骤 1：环境初始化（约 30 分钟）

```bash
# 安装 Python（如未安装，推荐 3.11+）
pip install mkdocs-material

# 在项目根目录初始化
cd E:\github\CookingCoder
mkdocs new .
```

这会生成 `mkdocs.yml` 配置文件和 `docs/` 目录。

### 步骤 2：配置 mkdocs.yml（约 30 分钟）

```yaml
site_name: CookingCoder 菜谱
site_url: https://iyabao.github.io/CookingCoder/
theme:
  name: material
  language: zh
  features:
    - navigation.tabs          # 顶部导航标签
    - navigation.sections      # 左侧目录分组可折叠
    - navigation.expand        # 默认展开目录
    - search.suggest           # 搜索建议
    - search.highlight         # 搜索高亮
    - content.tabs.link        # 内容标签
    - tags                      # 启用标签功能
  palette:
    - scheme: default
      toggle:
        icon: material/brightness-7
        name: 切换深色模式
    - scheme: slate
      toggle:
        icon: material/brightness-4
        name: 切换浅色模式
plugins:
  - search:
      separator: '[\s\-,:!=\[\]()"/]+|(?!\b)(?=[A-Z][a-z])|\.(?!\d)|&[lg]t;'
  - tags:
      tags_file: tags.md
nav:
  - 首页: index.md
  - 菜谱:
    - 按菜系: cuisine/index.md  # 可后续生成
    - 全部菜谱:  # 自动从 recipes 目录生成
  - 标签: tags.md
  - 关于: about.md
markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - tables
  - footnotes
```

### 步骤 3：迁移 40 个菜谱 md（约 1 小时，可脚本化）

将 `recipes/*.md` 复制到 `docs/recipes/` 目录。需要做的 frontmatter 适配：

**现有格式**（示例）：
```yaml
---
title: 红烧肉
cuisine: 川菜
taste: 甜咸
crowd: 全家
tech: 烧
time: 60分钟
---
```

**适配为 Material tags 格式**：
```yaml
---
title: 红烧肉
tags:
  - cuisine:川菜
  - taste:甜咸
  - crowd:全家
  - tech:烧
  - time:60分钟
---
```

可以写一个简单的 Python 脚本批量转换（约 20 行代码），避免手动修改 40 个文件。

### 步骤 4：生成标签索引页和分类页（约 30 分钟）

Material 会自动生成 `/tags/` 页面。如需按菜系/口味等维度分别生成分类索引页，可：
- 使用 Material 的 blog 插件（需 Insiders 赞助版），或
- 写一个简单的构建脚本，在 `mkdocs build` 前扫描所有 md 的 frontmatter，自动生成 `docs/cuisine/川菜.md`、`docs/taste/麻辣.md` 等分类页（每个分类页列出对应菜谱的链接）

### 步骤 5：本地预览与构建

```bash
mkdocs serve    # 本地预览 http://127.0.0.1:8000
mkdocs build    # 构建到 site/ 目录
```

### 步骤 6：部署（选择以下任一方案）

#### 方案 A：GitHub Pages（推荐，免费 + 国内可加速）

```bash
# 安装 gh-deploy 插件
pip install mkdocs-gh-deploy

# 一键部署到 GitHub Pages
mkdocs gh-deploy
```

部署后访问 `https://iyabao.github.io/CookingCoder/`。国内访问 GitHub Pages 不稳定，建议：
- 绑定自定义域名 + 使用阿里云 CDN/Cloudflare CDN 加速，或
- 同时部署到阿里云 OSS + CDN（见方案 C）

#### 方案 B：Vercel / Cloudflare Pages（免费，国内访问一般）

将 GitHub 仓库关联到 Vercel 或 Cloudflare Pages，构建命令设为 `mkdocs build`，输出目录设为 `site/`。Cloudflare Pages 在国内有边缘节点，访问速度优于 Vercel。

#### 方案 C：阿里云 OSS + ESA 边缘构建（国内访问最快，用户已有链路）

1. 在阿里云 OSS 创建静态网站托管 Bucket
2. 本地 `mkdocs build` 后将 `site/` 目录上传到 OSS（可使用 `ossutil` 或 CI 自动化）
3. 配置阿里云 ESA（边缘安全加速）CDN 加速 OSS 源站
4. 绑定自定义域名（需备案）

用户已有阿里云 ESA 链路，此方案国内访问速度最快，且完全在自有基础设施内。

#### 推荐部署组合

> **GitHub Pages（主，面向国际/开源社区）+ 阿里云 OSS+ESA CDN 加速（面向国内访问）**
>
> 通过 GitHub Actions 自动化：push 到 main 分支后，自动 `mkdocs build`，同时部署到 GitHub Pages 和阿里云 OSS。两套站点共享同一份构建产物，维护成本为零。

### 步骤 7：CI/CD 自动化（可选，约 1 小时）

在 `.github/workflows/deploy.yml` 中配置：

```yaml
name: Deploy CookingCoder
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install mkdocs-material
      - run: mkdocs build
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
      # 可选：同时部署到阿里云 OSS
      - name: Deploy to Aliyun OSS
        uses: manyuanrong/setup-ossutil@v2
        with:
          endpoint: ${{ secrets.OSS_ENDPOINT }}
          access-key-id: ${{ secrets.OSS_ACCESS_KEY_ID }}
          access-key-secret: ${{ secrets.OSS_ACCESS_KEY_SECRET }}
      - run: ossutil cp -rf site/ oss://your-bucket-name/
```

---

## 七、已淘汰方案速查表

| 方案 | 淘汰原因 | 严重程度 |
|------|----------|----------|
| Gitee Pages | 官方已正式下线，无法新部署 | ⛔ 硬伤 |
| 看云 | 已边缘化，官方引导迁移，存在停服风险 | ⚠️ 高风险 |
| Vdoing | 基于已停维的 VuePress 1.x，主题代码 2023 年后无更新 | ⚠️ 高风险 |
| Wolai | 财务危机后被收购，产品状态不明朗 | ⚠️ 高风险 |
| mdBook | 无 frontmatter 支持、无标签筛选、中文搜索差 | ❌ 需求不匹配 |
| Read the Docs/Sphinx | Markdown 非一等公民、无标签筛选、主题老旧 | ❌ 需求不匹配 |
| GitBook 云 | 不开源无法自托管、frontmatter 标签不可用 | ❌ 开源项目不适用 |
| 语雀 | 数据锁定严重、frontmatter 丢失、不支持 Git 协作 | ❌ 开源项目不适用 |
| 飞书知识库 | 无法绑定自定义域名、数据锁定、不支持 Git 协作 | ❌ 开源项目不适用 |
| Halo | 定位博客/CMS 非文档站、需服务器运维、md 非 source of truth | ❌ 定位不匹配 |

---

## 八、关键来源汇总

### 国外方案
- MkDocs Material：[官网](https://squidfunk.github.io/mkdocs-material/) ｜ [GitHub](https://github.com/squidfunk/mkdocs-material) ｜ [MkDocs 核心](https://github.com/mkdocs/mkdocs)
- Docusaurus：[官网](https://docusaurus.io/) ｜ [中文文档](https://docusaurus.io/zh-CN) ｜ [GitHub](https://github.com/facebook/docusaurus)
- VitePress：[官网](https://vitepress.dev/) ｜ [GitHub](https://github.com/vuejs/vitepress)
- Astro Starlight：[官网](https://starlight.astro.build/) ｜ [GitHub](https://github.com/withastro/starlight)
- Docsify：[官网](https://docsify.js.org/) ｜ [中文文档](https://docsify.js.org/#/zh-cn/) ｜ [GitHub](https://github.com/docsifyjs/docsify)
- mdBook：[官方文档](https://rust-lang.github.io/mdBook/) ｜ [GitHub](https://github.com/rust-lang/mdBook)
- Read the Docs：[云平台](https://readthedocs.org/) ｜ [GitHub](https://github.com/readthedocs/readthedocs.org) ｜ [Sphinx](https://www.sphinx-doc.org/)
- GitBook：[官网](https://www.gitbook.com/) ｜ [旧版前端(遗留)](https://github.com/GitBookIO/gitbook)

### 国内方案
- vuepress-theme-hope：[官网](https://theme-hope.vuejs.press) ｜ [GitHub](https://github.com/vuepress-theme-hope/vuepress-theme-hope)
- Halo：[官网](https://halo.run) ｜ [GitHub](https://github.com/halo-dev/halo) ｜ [Gitee](https://gitee.com/halo-dev/halo)
- 语雀：[官网](https://www.yuque.com)
- 飞书：[官网](https://www.feishu.cn)
- 看云：[官网](https://www.kancloud.cn)
- Gitee Pages（已下线）：[官方帮助页](https://gitee.com/help/articles/4136)
- Vdoing：[官网](https://doc.xugaoyi.com) ｜ [GitHub](https://github.com/xugaoyi/vuepress-theme-vdoing)
- Wolai：[官网](https://www.wolai.com)（状态待核实）

---

> **报告生成时间**：2026-09-03 ｜ **数据基准**：GitHub API 实时抓取 + 各项目官方文档核验
