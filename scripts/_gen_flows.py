# -*- coding: utf-8 -*-
"""
批量给菜谱生成"流程总览（Flowchart）" Mermaid 块（v3，边构建更严谨）。

结构：
- 先构造完整节点序列（含判断节点），再连边。
- 每个步骤：步骤节点 S_i；若含判断则后接判断节点 D_i（菱形）
  - if 条件：是→继续下一步；否→回环重试该步骤
  - while 条件：是→回环该步骤；否→继续下一步
- 判断的"下一步"统一指向：下一个步骤节点 / 结束。
"""
import io, glob, os, re

RECIPES_DIR = r'E:\github\CookingCoder\docs\recipes'
SKIP = ('_spec.md', 'index.md', '_template.md')


def extract_title(text):
    m = re.search(r'^title:\s*(.+)$', text, re.M)
    return m.group(1).strip() if m else ''


def parse_main_steps(text):
    """解析主流程：返回 [{base, analogy, title, conds}]"""
    m = re.search(r'## 主流程（Main Logic）(.*?)(?=## |\Z)', text, re.S)
    if not m:
        return []
    body = m.group(1)
    steps = []
    for sm in re.finditer(r'^\s*\d+\.\s+\*\*(.+?)\*\*\s*[:：](.*?)(?=^\s*\d+\.\s+\*\*|\Z)', body, re.M | re.S):
        title = sm.group(1).strip()
        desc = sm.group(2).strip()
        analogy_m = re.search(r'[（(]([^（）()]*)[）)]', title)
        analogy = analogy_m.group(1).strip() if analogy_m else ''
        base = re.sub(r'[（(][^（）()]*[）)]', '', title).strip()
        conds = re.findall(r'`(if|while)\s+([^`]+)`', desc)
        if not conds:
            conds = re.findall(r'(if|while)\s+([^。，；`]+)', desc)
        steps.append({'base': base, 'analogy': analogy, 'title': title, 'conds': conds})
    return steps


def esc(t):
    t = t.replace('[', '（').replace(']', '）').replace('"', '').replace('|', '').replace('{', '（').replace('}', '）').replace('\n', ' ').strip()
    t = t.replace(':', '：').replace("'", '＇')
    return t


def clean_cond(t):
    """清洗判断条件，使其可安全放入 mermaid 菱形节点：
    - 去掉 if/while 前缀
    - 只保留冒号前的条件部分
    - 半角括号/引号转全角（安全字符），去除 : 等保留字符
    """
    t = t.strip()
    t = re.sub(r'^(if|while)\s*', '', t)
    # 取冒号前（若没有冒号则全保留）
    if ':' in t:
        t = t.split(':', 1)[0]
    t = t.replace(':', '')
    # 半角括号/花括号转全角，避免 mermaid 保留字符
    t = t.replace('(', '（').replace(')', '）')
    t = t.replace('{', '（').replace('}', '）')
    t = t.replace('[', '（').replace(']', '）')
    t = t.replace('"', '＂').replace("'", '＇').replace('|', '｜')
    t = t.replace('\n', ' ')
    return t.strip()


def build_mermaid(dish, steps):
    L = ['```mermaid', 'flowchart TD']
    A, B0, E = 'A', 'B0', 'E'
    L.append('    %s[开始]' % A)
    L.append('    %s[%s]' % (B0, esc(dish)))
    L.append('    %s[结束]' % E)

    # 生成节点 id
    node_ids = []  # 依次：B0, (S1[,D1])*, E
    seq = [B0]
    node_defs = []
    for i, st in enumerate(steps):
        sid = 'S%d' % (i + 1)
        label = esc(st['base'])
        if st['analogy']:
            label += '<br>%s' % esc(st['analogy'])
        node_defs.append('    %s[%s]' % (sid, label))
        seq.append(sid)
        if st['conds']:
            kw, cond = st['conds'][0]
            did = 'D%d' % (i + 1)
            node_defs.append('    %s{%s}' % (did, clean_cond(cond)))
            seq.append(did)
    seq.append(E)

    # 连边（带判断回环）
    edges = ['    %s --> %s' % (A, B0)]
    i = 0
    n = len(seq)
    # seq 形如 [B0, S1, (D1), S2, (D2), ..., E]
    idx = 1
    while idx < n - 1:
        cur = seq[idx]
        if cur.startswith('S'):
            # 步骤节点：看下一个是否 D
            nxt = seq[idx + 1] if idx + 1 < n else E
            if nxt.startswith('D'):
                edges.append('    %s --> %s' % (cur, nxt))
                idx += 1  # 跳到 D
            else:
                edges.append('    %s --> %s' % (cur, nxt))
                idx += 1
        elif cur.startswith('D'):
            # 判断节点：确定"下一步"（跳过该 D 后的下一个真实步骤或 E）
            j = idx + 1
            next_real = seq[j] if j < n else E
            while next_real.startswith('D'):
                j += 1
                next_real = seq[j] if j < n else E
            # 回环目标：该 D 对应的 S（D_i 对应 S_i）
            snum = cur[1:]
            sid = 'S%s' % snum
            edges.append('    %s -- 是 --> %s' % (cur, next_real))
            edges.append('    %s -- 否 --> %s' % (cur, sid))
            idx = j
        else:
            idx += 1

    L.extend(edges)
    L.append('')
    L.extend(node_defs)
    L.append('')
    L.append('    style %s fill:#FFE0B2,stroke:#E64A19' % A)
    L.append('    style %s fill:#C8E6C9,stroke:#2E7D32' % E)
    # 判断节点着色
    for did in [x for x in seq if x.startswith('D')]:
        L.append('    style %s fill:#FFF3E0,stroke:#E65100' % did)
    L.append('```')
    return '\n'.join(L)


def main():
    files = [f for f in glob.glob(os.path.join(RECIPES_DIR, '*.md'))
             if not f.endswith(SKIP)]
    only = os.environ.get('GEN_ONLY', '')
    if only:
        files = [f for f in files if os.path.basename(f) == only + '.md']
    print('待处理菜谱数:', len(files))
    done, skipped = 0, 0
    for f in sorted(files):
        with io.open(f, encoding='utf-8') as fh:
            text = fh.read()
        if '## 流程总览' in text:
            skipped += 1
            continue
        dish = extract_title(text)
        steps = parse_main_steps(text)
        if not steps:
            print('  !! 无主流程步骤:', os.path.basename(f))
            continue
        mermaid = build_mermaid(dish, steps)
        anchor = '## 常量定义（Constants）'
        if anchor not in text:
            print('  !! 无常量定义锚点:', os.path.basename(f))
            continue
        insert = '## 流程总览（Flowchart）\n\n' + mermaid + '\n\n'
        text = text.replace(anchor, insert + anchor, 1)
        with io.open(f, 'w', encoding='utf-8') as fh:
            fh.write(text)
        done += 1
        print('  +', os.path.basename(f), '|', dish, '|', len(steps), '步')
    print('完成:', done, '跳过:', skipped)


if __name__ == '__main__':
    main()
