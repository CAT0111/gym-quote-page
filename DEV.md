以下是我的健身器材订购网页完整技术架构，请先通读理解整体架构，然后我们来处理：【今天的任务】

---

## 一、项目概述

基于 Jinja2 模板的静态报价页生成工具。Python 脚本读取产品数据（当前为硬编码，后续接入飞书 API），渲染为纯 HTML/CSS/JS 页面，部署至 Cloudflare Pages。支持中英马三语实时切换，产品详情采用浮层底部弹出交互，内嵌 Three.js 3D 健身房俯瞰场景。

---
## 开发者指令（每次会话必读）
- 每次会话开始时，根据任务描述主动列出需要查看的文件清单，且全部以命令行方式写好，必须带上执行完自动粘贴到粘贴板的命令，非必要别让用户手动复制。等用户提供所需的相关代码后再开始工作
- 动手前先说明思路和影响范围，确认后再写代码，务必保全用户数据不要轻易覆盖
- Bug 修复先定位根因，不要只修表面症状，从业务目的出发去推导修改意见，不能因为改 bug，把核心业务逻辑和代码给重写了
- 重构前列出所有改动文件，确保不改变现有功能行为和影响现有的数据安全
- 改完告诉用户需要验证哪些功能点
- 尽可能多用终端来完成，帮助用户节省 API 费用。使用终端时，尽可能一次性提供多个命令行，能用命令行解决的都用命令行，确保开发效果的前提下，节省用户复制粘贴的次数
- 复杂 Python 脚本不要跟其他命令链在一条 heredoc 里，分步写文件、分步执行最稳
- 非绝对必要，别去查看依赖的第三方库，只需确认其接口，以免大量输入无关信息爆上下文

## 二、技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 模板引擎 | Jinja2 (Python 3) | 渲染 HTML，按套餐生成独立页面 |
| 前端标记 | 纯 HTML5 | 语义化结构，`data-en/zh/ms` 属性承载多语言文本 |
| 样式 | 纯 CSS3 | 移动优先，单断点 768px，暗色主题 |
| 交互 | 原生 JavaScript (ES5+) | 无框架、无构建工具、无 npm 依赖 |
| 3D 场景 | Three.js r128 (CDN) | 仅核心库，无 GLTFLoader，几何体手写建模 |
| 部署目标 | Cloudflare Pages | GitHub 仓库自动部署，Build command 为空，输出目录 `/` |
| 公网穿透 | cloudflared | 本地开发时提供临时公网 URL 供手机预览 |

---

## 三、文件结构

~/Projects/gym-quote-page/ ├── build/ │ ├── generator.py # 渲染引擎：读数据 → Jinja2 → 输出 HTML │ ├── data/ │ │ └── test_data.py # 硬编码测试数据（PACKAGE / CATEGORIES / PRODUCTS） │ └── templates/ │ ├── base.html # 主布局：引入所有 section、CSS、JS │ ├── hero.html # 顶部主视觉 │ ├── price_summary.html # 价格摘要 │ ├── trust.html # 信任背书 │ ├── scene_3d.html # 3D 健身房场景容器 │ └── bottom_cta.html # 底部行动号召 ├── static/ │ ├── style.css # 全站样式（含浮层、语言切换器、3D 容器） │ ├── lang.js # 多语言引擎（检测 / 切换 / DOM 更新） │ ├── detail-panel.js # 产品详情浮层（overlay bottom-sheet） │ ├── category-nav.js # 分类导航标签滚动与 active 切换 │ └── gym-3d-scene.js # Three.js 3D 健身房场景 ├── pkg/ │ └── 400a.html # 生成产物：套餐报价页（勿手动编辑） ├── index.html # 生成产物：首页重定向（勿手动编辑） ├── PRD.md # 产品需求文档 └── DEV.md # 本文档


**关键约定**：
- `pkg/*.html` 与 `index.html` 为 `generator.py` 的输出产物，**禁止手动编辑**。
- `static/` 下的文件修改后 live-server 自动刷新，**无需重新运行 generator**。
- `build/templates/` 或 `build/data/` 修改后**必须运行** `python3 build/generator.py`。

---

## 四、核心架构

### 4.1 数据流

test_data.py (硬编码) │ ▼ generator.py ──── Jinja2 模板 ──── pkg/400a.html (静态 HTML) │ ▼ 浏览器加载 ──── lang.js (多语言) │ detail-panel.js (浮层) │ category-nav.js (导航) │ gym-3d-scene.js (3D) ▼ 用户交互界面


### 4.2 多语言系统（三层架构）

第一层：数据源 test_data.py 中每个产品/分类/套餐包含 name / name_zh / name_ms 字段

第二层：模板属性 Jinja2 渲染时将各语言文本写入 HTML data 属性：

第三层：JS 引擎 lang.js 在运行时读取 data-* 属性并替换 textContent


**语言检测优先级**（由高到低）：
1. URL 参数 `?lang=zh`
2. `localStorage` 存储的用户选择 (`ql_lang`)
3. `navigator.language` 浏览器语言
4. 兜底：`en`

**当前支持**：`en`（English）、`zh`（中文）、`ms`（Bahasa Melayu）
**预留扩展**：`fr`（Français）、`es`（Español）— 仅占位，暂未填充翻译

### 4.3 Detail 浮层系统

**交互模式**：fixed overlay bottom-sheet（从底部滑入的浮层卡片）

**DOM 结构**：
.detail-overlay (fixed, inset:0, z-index:2000) ├── .detail-backdrop (半透明黑色遮罩) └── .detail-sheet (白色/深色卡片, 12px边距, 16px圆角, max-height:80vh) ├── .detail-handle (顶部拖拽手柄) ├── .detail-header (SKU + 关闭按钮) ├── .detail-scroll (可滚动内容区) │ ├── .detail-media (视频播放器 或 图片 + badge) │ ├── 产品名称 + 价格 │ ├── 规格参数表 (SPEC_KEYS / SPEC_VALS 多语言翻译) │ ├── 备件包按钮（占位，coming soon） │ └── WhatsApp 咨询链接 └── (无固定底栏)


**媒体区逻辑**：
- 有 `video_url` → 直接嵌入 `<video>` 播放器，顶部叠加金色标签"观看60秒试机视频"
- 无 `video_url` → 显示产品图片，右下角叠加 badge"视频即将上线"

**关闭方式**：点击遮罩 / 点击关闭按钮 / 手柄区域下滑 >80px

**多语言支持**：
- `TEXTS` 对象：UI 按钮文案（观看视频、关闭、WhatsApp 咨询等）
- `SPEC_KEYS` 对象：规格键翻译（Weight Stack→配重片、Dimensions→尺寸 等 18 项）
- `SPEC_VALS` 对象：规格值翻译（Back→背部、Chest→胸部 等 30+ 项）
- `prodName()` 函数：根据当前语言从 `data-name` / `data-name-zh` / `data-name-ms` 取值

### 4.4 3D 场景系统

**渲染配置**：
- Canvas 容器 `#gym-canvas`，宽高比 5:2，最大高度 200px
- PerspectiveCamera FOV=40，默认俯瞰角度 phi=0.6, theta=π/4, radius=20
- 四光源布局：环境光 + 主光 + 填充光 + 背光（金色点缀 #c8a44e）

**场景内容**（手写几何体）：
- 地面（深木纹色 #1c1c1c）
- 四面墙体（#2a2a2a）+ 半透明镜面墙（#334455）
- 器械模型：力量选择器、自由力量架、哑铃架、跑步机、动感单车、长凳

**触摸交互**：
- 水平拖拽 → 旋转场景（preventDefault）
- 垂直拖拽 → 透传至页面滚动（touch-action: pan-y）
- 双指捏合 → 缩放（调节 radius）
- 鼠标拖拽 + 滚轮 → 同上

### 4.5 分类导航

`category-nav.js` 实现：
- 顶部 tab 栏横向滚动
- 点击 tab 平滑滚动到对应分类区块
- 页面滚动时自动高亮当前可见分类的 tab

---

## 五、样式体系

### 5.1 色彩

| 用途 | 色值 |
|------|------|
| 页面背景 | `#0a0a0a` |
| 卡片/面板背景 | `#111` / `#1a1a1a` |
| 主强调色（金色） | `#c8a44e` |
| WhatsApp 绿 | `#25D366` |
| 正文白 | `#fff` |
| 次要文字 | `rgba(255,255,255,0.5)` ~ `rgba(255,255,255,0.7)` |

### 5.2 布局

- 全局 `* { margin:0; padding:0; box-sizing:border-box }`
- 产品网格：`flex-wrap`，手机端 2 列，≥768px 3 列
- 移动优先，唯一断点 `@media (min-width: 768px)`

### 5.3 语言切换器

位于 `.topbar-right`，紧邻 WhatsApp 按钮右侧。三个小按钮 `EN | 中 | MS`，激活态金色高亮 + 白色文字。

---

## 六、数据结构

### 6.1 test_data.py 字段

**PACKAGE**：
```python
{
    "id": "PKG-400A",
    "name": "400m² Commercial Gym Package",
    "name_zh": "400平方米商用健身房套餐",
    "name_ms": "Pakej Gim Komersial 400m²",
    "area_sqm": 400,
    "total_machines": 20,
    "fob_total_usd": 12800,
    "cif_port_klang_usd": 14200,
    "fob_location": "Ningjin",
    "whatsapp_number": "8613800000000"
}
CATEGORIES（5 区）： sel（Selectorized Strength）、pl（Plate Loaded）、fw（Free Weight / Racks）、bn（Benches）、ca（Cardio） 每区含 key、label、label_zh、label_ms、title、title_zh、title_ms

PRODUCTS（20 台）： 每条记录含 sku、name、name_zh、name_ms、category_key、price_fob_usd、thumb_url、image_url、video_url、specs（字典，键为英文规格名，值为英文规格值）

6.2 模板数据属性
所有可见文本元素均携带 data-en、data-zh、data-ms 属性：

Copy<h2 data-en="Trust & Quality" data-zh="信任与品质" data-ms="Kepercayaan & Kualiti"></h2>
产品卡片额外携带：

Copy<div class="grid-item"
     data-sku="SC-A01"
     data-name="Seated Chest Press"
     data-name-zh="坐姿推胸"
     data-name-ms="Tekan Dada Duduk"
     data-price="680"
     data-image="..."
     data-video="..."
     data-specs='{"Weight Stack":"80kg",...}'
     data-wa="8613800000000">
七、开发环境
7.1 系统要求
macOS (Apple Silicon)
Python 3 + Jinja2 (pip3 install jinja2)
Node.js (Homebrew) + live-server (npm i -g live-server)
cloudflared (brew install cloudflared)
编辑器：VS Code
7.2 三终端工作流
终端 1 — 本地预览
cd ~/Projects/gym-quote-page && live-server --port=8080 --host=0.0.0.0

终端 2 — 公网穿透
cloudflared tunnel --url http://localhost:8080 --protocol http2

终端 3 — 操作台
cd ~/Projects/gym-quote-page
# 执行 generator、git 等命令
启动顺序：1 → 2 → 3

7.3 日常开发流程
改 CSS / JS（static/ 下文件）： 保存 → live-server 自动刷新 → 完成

改模板 / 数据（build/ 下文件）： 保存 → 终端 3 执行 python3 build/generator.py → 浏览器刷新 → 完成

7.4 预览 URL
环境	URL
本机	http://localhost:8080/pkg/400a.html
局域网	http://<Mac局域网IP>:8080/pkg/400a.html
公网	Cloudflare 隧道链接 + /pkg/400a.html
追加 ?lang=zh 或 ?lang=ms 可强制指定语言。

八、扩展多语言步骤
添加新语言（例如法语 fr）的完整流程：

static/lang.js — 在 SUPPORTED 数组中加入 'fr'，在 LABELS 中加入按钮文字
static/detail-panel.js — 在 TEXTS、SPEC_KEYS、SPEC_VALS 中加入 fr 条目
build/data/test_data.py — 在 PACKAGE、CATEGORIES、PRODUCTS 中加入 name_fr / label_fr / title_fr
build/templates/*.html — 在所有 data-* 元素上加入 data-fr="..." 属性
build/generator.py — 如需新模板变量则更新渲染上下文
执行 python3 build/generator.py 重新生成
九、Git 与部署
9.1 Git 常用命令
Copygit add . && git commit -m "描述"
git log --oneline
git checkout -- static/style.css      # 回退单文件
git push
git revert HEAD && git push            # 回退最近一次提交
9.2 Cloudflare Pages 部署
Copy# 首次：创建仓库并推送
gh repo create gym-quote-page --public --source=. --push

# Cloudflare Pages 配置
# - 连接 GitHub 仓库
# - Build command: (空)
# - Build output directory: /
# - 可用 .cfignore 排除 build/
十、版本变更记录
版本	日期	变更
v0 → v1	2026-03-25	CSS Grid 改为 Flex-wrap 布局
v1 → v2	2026-03-25	拆分为 Jinja2 模板架构，CSS/JS/HTML 分离
v2 → v3	2026-03-25	新增多语言系统（en/zh/ms）；Detail panel 改为 overlay bottom-sheet；媒体区直接嵌入视频播放器；3D 场景缩小至 200px 高度并优化触控与建模；新增 lang.js；test_data 补充中马文字段和视频 URL
十一、待办事项
编号	优先级	描述	状态
P1	高	替换真实产品图片	待办
P2	高	替换真实 60 秒试机视频	待办
P3	中	3D 场景引入 GLB 模型（需 GLTFLoader）	待办
P4	—	多语言切换（en/zh/ms）	✅ 已完成
P5	中	配置 GitHub → Cloudflare Pages 自动部署	待办
P6	中	接入飞书 API 替换硬编码数据	待办
P7	低	备件包与保养周期功能（当前占位）	待办
P8	低	添加法语 / 西班牙语翻译	待办
十二、JS 模块接口速查
lang.js
window.__QL_LANG.current()    → 'en' | 'zh' | 'ms'
window.__QL_LANG.apply(lang)  → 切换语言并刷新所有 DOM
detail-panel.js
内部 IIFE，自动绑定 .grid-item click 事件
getLang()           → 读取当前语言
t(key)              → UI 文案翻译
specKey(key)        → 规格键翻译
specVal(val)        → 规格值翻译
prodName(el)        → 按语言取产品名
openDetail(el)      → 打开浮层
closeDetail(overlay)→ 关闭浮层
category-nav.js
内部 IIFE，自动绑定 .cat-tab click 和 scroll 事件
gym-3d-scene.js
内部 IIFE，自动初始化 #gym-canvas
支持 mouse drag / wheel / touch drag / pinch-zoom
## 3D 场景集成（2026-03-25）
- gym-3d-scene.js：GLTFLoader 加载 gym-preview.glb + 自定义环境
- gym-preview.glb：3.7MB（原28.9MB减面压缩），46K面，CC-BY
- 器械包围盒：Min(-12,-12,0) Max(28.1,12,8) Size(40.2×24×8) Center(8.1,0,4)
- 房间46×30高10，无天花板，深色分区地面+镜面+LED灯带
- 隐藏原模型环境前缀：FloorTile/Walls/Windows/door/Outlet/Lightswitch/Mat
- BlenderMCP：addon端口9876运行中，Claude Code MCP配置已写入待验证
- 性能预算：手机10-15万面/30fps，GLB 5-10MB，材质10-20个，贴图1K
- 下一步：验证BlenderMCP连接→AI建模环境→混元3D器械→bpy自动组装→客户专属页面

---

### v3 → v4 | 2026-03-26 | 真实 400 平健身房套餐适配

**数据层变更：**
- CATEGORIES: 5 区 → 8 区（新增 `fw` 自由重量、`ft` 功能训练、`ac` 辅助配件）
- PRODUCTS: 20 SKU → 63 SKU，完整覆盖真实 400m² 商用健身房配置
- PRODUCTS 新增字段：`qty`（数量，如跑步机×5）、`zone`（场地分区 A/B/C/D/E）
- 所有 `price_fob_usd` 暂为 None（待填），`specs` 键统一英文
- PACKAGE 的 `fob_total_usd` / `cif_port_klang_usd` 暂为 None

**模板层变更：**
- `base.html`: 卡片新增 qty badge（`.qty-badge`，qty>1 时显示 ×N）；价格为 None 时显示三语"询价"
- `hero.html`: FOB 总价为 None 时显示"待定"
- `price_summary.html`: FOB/CIF 为 None 时显示"待定/待确认"

**样式层变更：**
- `.cat-nav-inner`: 从 `display:flex; min-width:max-content`（单行横滑）改为 `display:grid; grid-template-columns:repeat(4,1fr)`（两行 4+4 布局）
- `.cat-nav`: 移除 `overflow-x:auto` 及滚动条隐藏
- `.cat-tab`: 缩小 padding/font-size 适配两行，新增 `text-align:center`，移除 `text-transform:uppercase`
- 新增 `.qty-badge` 样式（金色背景，绝对定位于缩略图右上角）

**JS 层变更：**
- `detail-panel.js` / `category-nav.js`: 本次未改动，待下一步补充新 SPEC_KEYS 翻译

**待完成：**
- `detail-panel.js`: 补充约 25 个新 specs 键的 SPEC_KEYS / SPEC_VALS 翻译
- `generator.py`: 暂未改动，新字段 qty/zone 已通过模板直接消费
