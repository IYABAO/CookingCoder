# CookingCoder 一键部署脚本（Windows PowerShell）
# 作用：构建并部署到 gh-pages，然后补写 CNAME 文件，确保 cook.plbear.com 自定义域名不被重置。
# 用法：在项目根目录运行  powershell -ExecutionPolicy Bypass -File scripts\deploy.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$py = "C:\Users\iyaba\AppData\Local\Programs\Python\Python312\python.exe"

Write-Host "==> 1/4 构建并部署到 gh-pages (gh-deploy --force)" -ForegroundColor Cyan
& $py -m mkdocs gh-deploy --force
if ($LASTEXITCODE -ne 0) { throw "gh-deploy 失败" }

Write-Host "==> 2/4 在 gh-pages 分支补写 CNAME (cook.plbear.com)" -ForegroundColor Cyan
Set-Content -Path "site\CNAME" -Value "cook.plbear.com" -NoNewline -Encoding ascii
git checkout gh-pages 2>&1 | Out-Null
Copy-Item "site\CNAME" "CNAME" -Force
if (-not (Test-Path "CNAME")) { throw "CNAME 未生成" }

Write-Host "==> 3/4 提交并推送 CNAME" -ForegroundColor Cyan
git add CNAME
git commit -m "chore: ensure CNAME = cook.plbear.com" 2>&1 | Out-Null
git push origin gh-pages
if ($LASTEXITCODE -ne 0) { throw "推送 CNAME 失败" }

Write-Host "==> 4/4 切回 master" -ForegroundColor Cyan
git checkout master 2>&1 | Out-Null

Write-Host "部署完成 ✅ https://cook.plbear.com/ (等待 GitHub Pages 部署约 1-2 分钟生效)" -ForegroundColor Green
