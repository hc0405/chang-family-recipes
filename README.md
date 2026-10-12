# 披薩食譜網站

瑪格麗特、青醬野菇披薩的三種做法，純靜態網站（不需要任何框架）。

- 原版配方・液種
- 嘉禾中筋麵粉版・液種
- 嘉禾中筋麵粉版・當天快速發酵

## 結構

```
site/            ← 要部署的網站（Cloudflare 的輸出目錄）
  index.html     ← 首頁列表
  recipes/       ← 三份食譜頁
  pdf/           ← 可下載的 PDF
assets/          ← 圖片、CSS 原始檔
pdf/             ← PDF 原始檔
tools/build_site.py  ← 產生 site/ 的腳本（食譜內容都在這支檔案裡）
```

## 修改食譜

1. 編輯 `tools/build_site.py` 裡的 `RECIPES`
2. 執行 `python3 tools/build_site.py`
3. commit 並 push，Cloudflare 會自動重新部署

## Cloudflare 設定

- Framework preset：None
- Build command：（留空）
- Build output directory：`site`
