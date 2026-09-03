# -*- coding: utf-8 -*-
"""扫描所有菜谱的 mermaid 块，检测潜在语法风险"""
import io, glob, os, re

files = [f for f in glob.glob(r'E:\github\CookingCoder\docs\recipes\*.md')
         if not f.endswith(('_spec.md', 'index.md', '_template.md'))]
issues = []
for f in sorted(files):
    with io.open(f, encoding='utf-8') as fh:
        text = fh.read()
    for m in re.finditer(r'```mermaid\n(.*?)```', text, re.S):
        code = m.group(1)
        # 风险1：菱形/节点文本里含半角冒号
        if re.search(r'{[^}]*:[^}]*}', code):
            issues.append((os.path.basename(f), '菱形含冒号', m.group(1)[:80]))
        # 风险2：节点文本含未转义的 [ ] { }
        for lm in re.finditer(r'[A-Za-z0-9_]+\[([^\]]*)\]', code):
            label = lm.group(1)
            if re.search(r'[:|{}\[\]]', label):
                issues.append((os.path.basename(f), '节点标签含保留字符', label[:60]))
        # 风险3：边标签含保留字符
        for em in re.finditer(r'--\s*([^->]+?)\s*-->', code):
            el = em.group(1)
            if ':' in el or '[' in el or ']' in el:
                issues.append((os.path.basename(f), '边标签含保留字符', el[:60]))

if issues:
    print('发现 %d 个潜在问题:' % len(issues))
    for f, typ, ctx in issues:
        print(' -', f, '|', typ, '|', ctx)
else:
    print('所有 mermaid 块语法检查通过')
