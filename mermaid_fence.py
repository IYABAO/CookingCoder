# -*- coding: utf-8 -*-
"""
MkDocs 自定义 superfences format：生成 <div class="mermaid-block">源码</div>
让 mermaid 源码保留在 DOM 中，由前端 JS 自行渲染，
避免 Material for MkDocs 内置 mermaid 组件的介入。
"""

def mermaid_format(source, language, css_class, options, md, classes=None, id_value='', attrs=None, **kwargs):
    """自定义 mermaid fence format：输出带源码的 div.mermaid-block"""
    # 转义 HTML 特殊字符，确保源码安全嵌入
    esc = source.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return '<div class="mermaid-block">%s</div>\n' % esc
