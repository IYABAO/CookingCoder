# CookingCoder 一键部署脚本（Windows PowerShell）
# 作用：构建并部署到 gh-pages。CNAME 已放在 docs/CNAME，gh-deploy 会自动带上 gh-pages 分支，锁定 cook.plbear.com 域名。
# 用法：在项目根目录运行  powershell -ExecutionPolicy Bypass -File scripts\deploy.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$py = "C:\Users\iyaba\AppData\Local\Programs\Python\Python312\python.exe"

Write-Host "==> 1/2 构建并部署到 gh-pages (gh-deploy --force)" -ForegroundColor Cyan
& $py -m mkdocs gh-deploy --force
if ($LASTEXITCODE -ne 0) { throw "gh-deploy 失败" }

Write-Host "==> 2/2 验证 gh-pages 分支 CNAME" -ForegroundColor Cyan
git fetch origin gh-pages 2>&1 | Out-Null
$cname = git show "origin/gh-pages:CNAME" 2>$null
if ($cname -eq "cook.plbear.com") {
    Write-Host "CNAME 已锁定: cook.plbear.com ✅" -ForegroundColor Green
} else {
    Write-Host "警告: gh-pages 分支未检测到 CNAME，请检查 docs/CNAME 是否提交" -ForegroundColor Yellow
}

Write-Host "部署完成 ✅ https://cook.plbear.com/ (等待 GitHub Pages 部署约 1-2 分钟生效)" -ForegroundColor Green
