# -*- coding: utf-8 -*-
"""给分类页的 ## 标题添加显式中文锚点 {#xx}，使 tags.md 的中文锚点链接可用"""
import io, os, re

base = r'E:\github\CookingCoder\docs'
files = ['crowd.md', 'cuisine.md', 'taste.md', 'tech.md']

for f in files:
    path = os.path.join(base, f)
    with io.open(path, encoding='utf-8') as fh:
        lines = fh.readlines()
    out = []
    changed = 0
    for line in lines:
        m = re.match(r'^(##\s+)(.+?)\s*(\{#.*\})?\s*$', line.rstrip('\n'))
        if m and m.group(2) and not m.group(3):
            heading = m.group(2).strip()
            # 只有短中文标题才加锚点，跳过包含 markdown 链接的
            if not re.search(r'[\[\]()]', heading) and len(heading) <= 10:
                out.append('## %s {#%s}\n' % (heading, heading))
                changed += 1
                continue
        out.append(line)
    if changed:
        with io.open(path, 'w', encoding='utf-8') as fh:
            fh.writelines(out)
        print('%s: 添加 %d 个显式锚点' % (f, changed))
    else:
        print('%s: 无需修改' % f)
