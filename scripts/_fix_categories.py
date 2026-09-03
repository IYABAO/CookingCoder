# -*- coding: utf-8 -*-
"""CookingCoder 修复脚本：
1) 分类页(crowd/cuisine/taste/tech)中菜谱链接从拼音改为中文菜名
2) tags.md 标签索引改为可点击链接（链接到分类页锚点）
"""
import io, os, re, glob

base = r'E:\github\CookingCoder'
docs_dir = os.path.join(base, 'docs')

# ---------- 1. 建立 拼音文件名 -> 中文菜名 映射 ----------
title_map = {}  # slug -> title
for md in glob.glob(os.path.join(docs_dir, 'recipes', '*.md')):
    name = os.path.basename(md)
    if name in ('index.md', '_spec.md', '_template.md'):
        continue
    with io.open(md, encoding='utf-8') as fh:
        content = fh.read()
    m = re.search(r'^title:\s*(.+)$', content, re.M)
    if m:
        slug = name[:-3]  # 去掉 .md
        title_map[slug] = m.group(1).strip().strip('"\'')
print('提取到菜谱映射 %d 个:' % len(title_map))
for k, v in sorted(title_map.items()):
    print('  %-22s -> %s' % (k, v))

# 校验是否有遗漏（分类页用到的拼音都在映射里）
used_slugs = set()
for f in ['crowd.md', 'cuisine.md', 'taste.md', 'tech.md']:
    with io.open(os.path.join(docs_dir, f), encoding='utf-8') as fh:
        c = fh.read()
    for m in re.finditer(r'\]\(recipes/([\w-]+)\.md\)', c):
        used_slugs.add(m.group(1))
missing = used_slugs - set(title_map.keys())
print()
print('分类页引用到的菜谱 slug 数:', len(used_slugs))
print('缺失映射:', missing if missing else '无')

# ---------- 2. 重写分类页：拼音 -> 中文菜名 ----------
for f in ['crowd.md', 'cuisine.md', 'taste.md', 'tech.md']:
    path = os.path.join(docs_dir, f)
    with io.open(path, encoding='utf-8') as fh:
        content = fh.read()
    def repl(m):
        slug = m.group(1)
        title = title_map.get(slug, slug)
        return '[%s](recipes/%s.md)' % (title, slug)
    new_content = re.sub(r'\[([\w-]+)\]\(recipes/([\w-]+)\.md\)', 
                         lambda m: '[%s](recipes/%s.md)' % (title_map.get(m.group(2), m.group(1)), m.group(2)),
                         content)
    if new_content != content:
        with io.open(path, 'w', encoding='utf-8') as fh:
            fh.write(new_content)
        print('已重写:', f)
    else:
        print('无变化:', f)

print()
print('=== 分类页处理完成 ===')
