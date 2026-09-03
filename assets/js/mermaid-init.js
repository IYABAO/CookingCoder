/* CookingCoder: 渲染 mermaid-block（自定义 superfences 输出，避免 Material 内置 mermaid 介入） */
(function () {
  function renderAll() {
    if (typeof mermaid === "undefined") return;
    var blocks = document.querySelectorAll("div.mermaid-block");
    if (!blocks.length) return;
    mermaid.initialize({
      startOnLoad: false,
      theme: "base",
      themeVariables: {
        primaryColor: "#FFE0B2",
        primaryTextColor: "#4E342E",
        primaryBorderColor: "#E64A19",
        lineColor: "#BF360C",
        secondaryColor: "#FFF3E0",
        tertiaryColor: "#FFCCBC",
        fontSize: "14px"
      },
      flowchart: { curve: "basis", nodeSpacing: 40, rankSpacing: 50 },
      securityLevel: "loose"
    });
    blocks.forEach(function (block) {
      if (block.querySelector("svg")) return; // 已渲染
      var src = block.textContent.trim();
      if (!src) return;
      var id = "mermaid-" + Math.random().toString(36).slice(2, 9);
      mermaid.render(id, src).then(function (r) {
        var holder = document.createElement("div");
        holder.className = "mermaid-rendered";
        holder.innerHTML = r.svg;
        block.replaceWith(holder);
      }).catch(function (e) {
        console.error("Mermaid render failed:", e);
        block.classList.add("mermaid-error");
      });
    });
  }

  // Material for MkDocs 的 document$ 事件（若存在）
  if (typeof document$ !== "undefined") {
    document$.subscribe(function () { renderAll(); });
  }
  // 兜底：等 DOM 就绪 + 延迟重试（覆盖首次加载与 SPA 切换）
  window.addEventListener("load", function () {
    setTimeout(renderAll, 300);
    setTimeout(renderAll, 1200);
  });
})();
