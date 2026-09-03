# -*- coding: utf-8 -*-
"""
CookingCoder -> MkDocs Material 迁移脚本 (v2, 使用 PyYAML)
- 读取 recipes/*.md（排除 _index/_spec/_template）
- 将 frontmatter 五维标签映射为 Material tags（带维度前缀）
- 复制到 docs/recipes/ 并重写 frontmatter
- 生成 tags.md 标签索引页 + cuisine/taste/crowd/tech 分类页
用法: python cook_transfer.py
"""
import os, glob, re
from collections import defaultdict
import yaml

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, 'recipes')
DST = os.path.join(BASE, 'docs', 'recipes')
DOCS = os.path.join(BASE, 'docs')

# 维度前缀映射: frontmatter字段 -> 标签前缀
DIMENSIONS = {
    'cuisine': '菜系',
    'taste': '口味',
    'crowd': '人群',
    'tech': '技法',
    'time': '耗时',
}

# _spec.md 章节锚点映射: §N -> #anchor
SPEC_ANCHORS = {
    '§1': '#size-spec',
    '§2': '#measure',
    '§3': '#heat',
    '§4': '#oil',
    '§5': '#done',
    '§6': '#preprocess',
    '§7': '#frontmatter',
    '§8': '#tags-dict',
}

def linkify_spec(body):
    """将正文中的 _spec §N 引用替换为指向 _spec.md 对应锚点的内链，
    并在正文顶部插入一条指向度量标准库的引用提示条。"""
    # 替换 _spec §N（可能后跟中文内容，保留原后缀）
    for sec, anchor in SPEC_ANCHORS.items():
        body = re.sub(
            rf'(?<!\[)_spec\s*{sec}(?!\])',
            lambda m: f'[_spec {sec}](_spec.md{anchor})',
            body,
        )
    return body

def parse_frontmatter(text):
    """用 PyYAML 解析 frontmatter，返回 (fm_dict, body)"""
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', text, re.DOTALL)
    if not m:
        return {}, text
    fm_raw, body = m.group(1), m.group(2)
    fm = yaml.safe_load(fm_raw) or {}
    return fm, body

def build_frontmatter(fm, body):
    """构造新的 frontmatter 文本（保留原字段 + 生成 tags），用 yaml 序列化保证合法性"""
    new_fm = {}
    for key, val in fm.items():
        if key == 'tags':
            continue
        new_fm[key] = val
    # 生成 tags
    tags = []
    for dim, prefix in DIMENSIONS.items():
        if dim in fm:
            vals = fm[dim]
            if isinstance(vals, str):
                vals = [vals]
            for v in vals:
                tags.append(f'{prefix}:{v}')
    if tags:
        new_fm['tags'] = tags
    # yaml 序列化（allow_unicode 保留中文，sort_keys=False 保序）
    fm_text = yaml.safe_dump(new_fm, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return f'---\n{fm_text}---\n\n{body}'

def main():
    os.makedirs(DST, exist_ok=True)
    files = sorted(glob.glob(os.path.join(SRC, '*.md')))
    real = [f for f in files if not os.path.basename(f).startswith('_')]
    print(f'待迁移菜谱: {len(real)} 道')

    all_tags = defaultdict(list)   # tag -> [filename]

    for f in real:
        text = open(f, encoding='utf-8').read()
        fm, body = parse_frontmatter(text)
        fname = os.path.basename(f)
        # 生成 tags
        for dim, prefix in DIMENSIONS.items():
            vals = fm.get(dim, [])
            if isinstance(vals, str):
                vals = [vals]
            for v in vals:
                all_tags[f'{prefix}:{v}'].append(fname)
        # 写新文件（正文内链化）
        body_linked = linkify_spec(body)
        # 在第一个 # 标题后插入"度量标准"引用提示条
        title_match = re.match(r'^(#\s+[^\n]+\n+)', body_linked)
        if title_match:
            hint = ('\n\n> 📐 **度量标准**：本菜谱所有模糊表述（块/勺/火候/油温/熟度）均以'
                    '[_spec.md（度量标准库）](_spec.md) 为准，可点击各章节锚点查看。\n')
            body_linked = body_linked[:title_match.end()] + hint + body_linked[title_match.end():]
        new_text = build_frontmatter(fm, body_linked)
        with open(os.path.join(DST, fname), 'w', encoding='utf-8') as out:
            out.write(new_text)

    # 复制 _spec.md 和 _template.md 到 docs/recipes/（带锚点的最新版）
    import shutil
    for fn in ['_spec.md', '_template.md']:
        src_f = os.path.join(SRC, fn)
        if os.path.exists(src_f):
            shutil.copy(src_f, os.path.join(DST, fn))

    # 生成 tags.md 索引页（Material tags 插件会自动接管，这里生成精简引导页）
    tag_lines = []
    for tag in sorted(all_tags.keys()):
        count = len(all_tags[tag])
        tag_lines.append(f'- **{tag}**（{count}）')
    tags_md = f"""---
title: 标签索引
---

# 标签索引

> 按五维标签（菜系/口味/人群/技法/耗时）快速筛选菜谱。

{chr(10).join(tag_lines)}
"""
    with open(os.path.join(DOCS, 'tags.md'), 'w', encoding='utf-8') as out:
        out.write(tags_md)
    print(f'标签索引页生成: {len(all_tags)} 个标签')

    # 生成分类页 (cuisine/taste/crowd/tech)
    for dim in ['cuisine', 'taste', 'crowd', 'tech']:
        prefix = DIMENSIONS[dim]
        dim_tags = {k: v for k, v in all_tags.items() if k.startswith(prefix + ':')}
        if not dim_tags:
            continue
        dim_lines = []
        for tag in sorted(dim_tags.keys()):
            label = tag.split(':', 1)[1]
            files_links = ', '.join(f'[{fname[:-3]}](recipes/{fname})' for fname in dim_tags[tag])
            dim_lines.append(f'## {label}\n\n{files_links}')
        dim_md = f"""---
title: {prefix}分类
---

# {prefix}分类

{chr(10).join(dim_lines)}
"""
        with open(os.path.join(DOCS, f'{dim}.md'), 'w', encoding='utf-8') as out:
            out.write(dim_md)
    print('分类页生成完成')

    print(f'迁移完成: {len(real)} 道菜谱 -> docs/recipes/')

if __name__ == '__main__':
    main()
