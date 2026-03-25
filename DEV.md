# 报价网页工具 — 开发文档

## 1. 项目状态
当前版本：v3 — Jinja2 模板化架构 + 多语言 + 浮层详情。CSS / JS / HTML 模板分离，Python 生成脚本从数据源读取数据渲染静态 HTML。产品数据当前使用硬编码测试数据（含中英马来三语翻译），后续替换为飞书 API。多语言切换已实现（en / zh / ms），预留 fr / es 扩展位。Detail panel 已从行内展开重构为全屏浮层（overlay bottom sheet），内嵌视频直接播放。3D 场景已拆分为独立 JS 文件。Git 已初始化，手机端和公网预览已跑通。

## 2. 技术栈
前端使用纯 HTML + CSS + 原生 JS，无框架依赖。3D 场景使用 Three.js r128（CDN 引入）。模板引擎使用 Jinja2（Python）。CSS 采用移动端优先设计，唯一断点 768px。部署目标为 Cloudflare Pages（GitHub 仓库自动部署）。

## 3. 本地开发环境
操作系统为 macOS（Apple Silicon）。Python 3 + Jinja2 已安装。Node.js 已安装（通过 Homebrew），live-server 全局安装用于本地热刷新，cloudflared 已安装用于公网穿透预览，编辑器使用 VS Code（已配置 code 命令）。

项目路径：~/Projects/gym-quote-page

## 4. 文件结构

~/Projects/gym-quote-page/
├── build/                        # 构建工具（不部署）
│   ├── generator.py              # 主生成脚本
│   ├── data/
│   │   ├── __init__.py
│   │   └── test_data.py          # 硬编码测试数据（含三语翻译，后续换飞书 API）
│   └── templates/
│       ├── base.html             # 页面骨架（引用其他模板，含语言切换器）
│       ├── hero.html             # 首屏冲击区（多语言 data 属性）
│       ├── price_summary.html    # 总价汇总（多语言 data 属性）
│       ├── trust.html            # 信任区（多语言 data 属性）
│       ├── scene_3d.html         # 3D 场景容器（多语言 data 属性）
│       └── bottom_cta.html       # 底部 CTA（多语言 data 属性）
├── static/                       # 静态资源（直接部署）
│   ├── style.css                 # 全部 CSS
│   ├── lang.js                   # 多语言检测、切换、DOM 更新
│   ├── category-nav.js           # 品类导航交互
│   ├── detail-panel.js           # 详情浮层交互（含多语言字典）
│   └── gym-3d-scene.js           # 3D 场景渲染
├── pkg/                          # 生成的套餐页面（部署产物）
│   └── 400a.html                 # PKG-400A 套餐页
├── c/                            # 生成的客户方案页面（预留）
├── index.html                    # 首页重定向到默认套餐
├── PRD.md
└── DEV.md

关键约定：pkg/*.html 和 index.html 是生成产物，不要手动编辑，改模板后重新运行 generator.py。static/ 下的 CSS/JS 改完保存即生效（live-server 自动刷新），不需要跑 generator。build/ 目录不会部署到线上，只在本地开发时使用。

## 5. 开发工作流

### 三终端并行架构

终端 1 — 本地预览服务（常驻，不要关）：
cd ~/Projects/gym-quote-page && live-server --port=8080 --host=0.0.0.0

终端 2 — 公网穿透隧道（常驻，不要关）：
cloudflared tunnel --url http://localhost:8080 --protocol http2

终端 3 — 操作台（日常命令都在这里执行）：
cd ~/Projects/gym-quote-page

启动顺序：1 → 2 → 3。

### 日常改代码流程

改 CSS / JS（不需要跑 generator）：编辑 static/ 下的文件 → Cmd+S → 浏览器自动刷新。

改模板或数据（需要跑 generator）：编辑 build/templates/ 或 build/data/ → Cmd+S → 终端 3 执行 python3 build/generator.py → 浏览器刷新。

保存版本：git add . && git commit -m "描述改了什么"

### 预览方式
本机浏览器：http://localhost:8080/pkg/400a.html
同 WiFi 手机：http://<Mac局域网IP>:8080/pkg/400a.html
公网：cloudflared 隧道链接 + /pkg/400a.html
Chrome 模拟手机：Cmd+Option+I → Cmd+Shift+M → 选 iPhone 12 Pro
强制语言预览：在 URL 后加 ?lang=zh 或 ?lang=ms

## 6. CSS 架构
全局重置使用 *{margin:0;padding:0;box-sizing:border-box}。配色体系：主背景 #0a0a0a，卡片/浮层背景 #1a1a1a，金色强调 #c8a44e，WhatsApp 绿 #25D366，文字白色配不同透明度层级（1.0 / 0.8 / 0.4 / 0.25）。字体使用系统默认字体栈。

布局方案：产品网格使用 display:flex; flex-wrap:wrap，每个 grid-item 为 flex:0 0 calc(50% - .5px)，768px 以上切换为 calc(33.333% - .67px)。

Detail 浮层使用 fixed 定位全屏 overlay，内部 detail-sheet 为 bottom sheet 卡片样式：四周留 12px 间距（width: calc(100% - 24px)），max-height 80vh，圆角 16px，带边框和阴影。入场动画为 translateY(100%) + scale(.96) → translateY(0) + scale(1)，使用 cubic-bezier(.32,.72,0,1) 缓动。浮层打开时 body 添加 overlay-open 类锁定滚动。

语言切换器位于顶栏右侧 WhatsApp 按钮左边，三个紧凑按钮 EN | 中 | MS，激活态为金色。

## 7. JS 模块说明

### 7.1 多语言切换（static/lang.js）
IIFE 封装。语言检测优先级：URL 参数 ?lang= → localStorage(ql_lang) → navigator.language → 默认 en。支持语言：en / zh / ms，预留 fr / es 扩展。

applyLang(lang) 遍历所有 [data-en] 元素，读取对应 data-{lang} 属性值写入 textContent，fallback 到 data-en。同时更新 html[data-lang] 和 html[lang] 属性，更新切换器按钮高亮，更新已展开的 detail panel 内的文案。

通过 window.__QL_LANG.current() 暴露当前语言给其他模块读取。

### 7.2 品类导航（static/category-nav.js）
IIFE 封装。点击标签滚动到目标分区，偏移量 100px（顶栏 48px + 导航栏约 52px）。滚动监听使用 passive 事件，遍历所有 [id^="sec-"] 元素判断当前可视区域，切换 active 类。首屏向下箭头点击滚动到导航栏。品类标签本身带 data-en / data-zh / data-ms 属性，由 lang.js 自动切换。

### 7.3 详情浮层（static/detail-panel.js）
IIFE 封装。核心变量：overlay（当前浮层 DOM 节点）、currentSku（当前展开的产品 SKU）、currentSelectedItem（当前选中的 grid-item）。

内置三组多语言字典：TEXTS（框架文案：视频标签、关闭、WhatsApp 链接、备件包按钮等）、SPEC_KEYS（参数表 key 翻译：Weight Stack→配重片 等 18 个）、SPEC_VALS（参数表 value 翻译：Back→背部、Chest→胸部 等 30+ 个）。通过 window.__QL_LANG.current() 读取当前语言。

openDetail(gridItem) 流程：如果点击同一 item 则关闭（closeDetail）；否则先 removeOverlayImmediate() 移除旧浮层；解析 data-specs JSON，用 trSpecKey() 和 trSpecVal() 翻译 key/value 构建参数表 HTML；根据 data-video 是否为空决定媒体区内容 —— 有视频则直接放 video 标签（preload=metadata，poster=产品图，controls+playsinline），左上角叠金色标签"观看60秒试机视频"；无视频则放产品图片，右下角叠灰色标签"视频即将上线"；构建浮层 DOM（overlay > backdrop + sheet > handle + header + scroll > media + body）；append 到 body 并添加 overlay-open 类；绑定关闭按钮、遮罩点击、下滑手势（handle 区域 touchmove dy>80px 触发关闭）、备件包按钮（暂弹 alert 提示 coming soon）；双重 rAF 触发入场动画。

closeDetail() 流程：暂停视频；移除 active 类触发退场动画；transitionend(transform) 后移除 DOM；350ms 兜底强制移除；清除选中态。

removeOverlayImmediate()：同步移除 DOM 不播放动画，用于快速切换产品时清除旧浮层。

产品名多语言：从 grid-item 的 data-name-zh / data-name-ms 属性读取，由 prodName() 函数根据当前语言返回。

WhatsApp 号码从 document.body.dataset.whatsapp 读取（由 Jinja2 模板写入 body 的 data-whatsapp 属性）。

### 7.4 3D 场景（static/gym-3d-scene.js）
IIFE 封装，所有变量不污染全局。场景内容：20x20 单位地面 + 网格辅助线、4 面 3 米高墙体、4 个分区文字标签（Canvas 纹理 Sprite）、6 台固定力量器械（含配重片组）、4 台挂片器械（红色）、3 个力量架、1 个哑铃架（含 10 个哑铃模型）、4 台跑步机、3 台单车、2 条训练凳。

相机控制为手写轨道控制：球坐标系（theta/phi/radius）+ 鼠标拖拽/滚轮缩放 + 触摸单指旋转/双指缩放。phi 限制在 0.2 到 PI/2.1 之间防止翻转，radius 限制在 8 到 40 之间。

渲染使用 requestAnimationFrame 循环。窗口 resize 时更新 canvas 尺寸、相机 aspect 和 renderer size。

## 8. 多语言架构

### 8.1 静态文案（模板层）
所有 Jinja2 模板中的页面框架文案通过 HTML data 属性存储三语版本（data-en / data-zh / data-ms）。运行时由 lang.js 遍历 [data-en] 元素替换 textContent。覆盖范围：hero 标题/统计/badge、品类导航标签、分区标题、总价汇总、信任区标题和全部 4 个信任点、3D 场景标题/副标题/CTA、底部 CTA 标题/说明/按钮/备注、顶栏 WhatsApp 按钮、页脚。

### 8.2 动态文案（JS 层）
detail-panel.js 内置 TEXTS 字典，覆盖浮层内所有框架文案：视频标签、视频即将上线、关闭按钮、WhatsApp 链接文案、备件包按钮文案、FOB 标注。动态生成的 DOM 元素同样带 data-en / data-zh / data-ms 属性，确保 lang.js 切换时也能更新已展开的浮层。

### 8.3 产品数据多语言
test_data.py 中每个产品包含 name / name_zh / name_ms 三个字段。CATEGORIES 包含 label / label_zh / label_ms 和 title / title_zh / title_ms。PACKAGE 包含 name / name_zh / name_ms。模板将多语言字段写入 HTML data 属性，JS 运行时读取。

### 8.4 Spec 参数表多语言
detail-panel.js 内置 SPEC_KEYS 和 SPEC_VALS 两个翻译字典。SPEC_KEYS 翻译 18 个参数名（Weight Stack→配重片 等）。SPEC_VALS 翻译 30+ 个参数值（Back→背部、Multi-grip bar→多握把横杆 等）。数值类参数值（尺寸、重量、角度等）不翻译。

### 8.5 不翻译的内容
产品 SKU、价格数字、WhatsApp 预填消息（统一英文便于业务处理）、3D 场景内分区标签（英文行业术语）。

### 8.6 语言扩展方法
新增语言步骤：1) lang.js SUPPORTED 数组加语言代码，labels 加按钮文字；2) detail-panel.js TEXTS / SPEC_KEYS / SPEC_VALS 加对应语言条目；3) test_data.py 产品/品类/套餐加 name_{code} 字段；4) 所有模板 data 属性加 data-{code}；5) generator.py 可能需要传递新字段到模板。

## 9. 数据结构说明（build/data/test_data.py）

PACKAGE 字典字段：id, name, name_zh, name_ms, area_sqm, total_machines, fob_total_usd, cif_port_klang_usd, fob_location, whatsapp_number。

CATEGORIES 列表，每项字段：key, label, label_zh, label_ms, title, title_zh, title_ms。

PRODUCTS 列表，每项字段：sku, name, name_zh, name_ms, category_key, price_fob_usd, thumb_url, image_url, video_url, specs（dict）。

当前测试数据：20 台设备分 5 个分区，全部产品已配置测试视频 URL（Big Buck Bunny 720p 10s）。

## 10. 生成脚本说明（build/generator.py）

输入：从 build/data/test_data.py 读取 PACKAGE、CATEGORIES、PRODUCTS 数据。

处理：按 category_key 分组产品，加载 Jinja2 模板，注册 tojson 过滤器，渲染 base.html（自动 include 子模板）。

输出：pkg/400a.html（套餐报价页）和 index.html（重定向页）。

后续扩展点：替换 test_data.py 为飞书 API 调用（feishu_api.py）；支持多套餐生成（遍历 T_Package 表）；支持客户方案生成（输出到 c/ 目录）。

## 11. 已知问题与待修项

P1 — 图片全部使用 Unsplash 占位图。需替换为真实产品图（从飞书 T_Product 表读取 CDN URL）。

P2 — 视频源为测试视频（Big Buck Bunny）。需替换为真实试机视频 URL。

P3 — 3D 场景使用基础几何体。后续替换为 GLB 格式真实器材模型。

P4（已完成） — 多语言切换已实现（en / zh / ms），含产品名、spec key/value、全部框架文案。

P5 — 未接入 Cloudflare Pages 部署。GitHub 仓库和 Cloudflare Pages 连接待配置。

P6 — 未接入飞书 API。数据仍为硬编码，需开发 feishu_api.py 模块。

P7 — 备件包和保养维护周期功能为占位状态。点击按钮弹 alert 提示 coming soon，后续需接入真实数据和展示页面。

## 12. 历史重构记录

### v2 → v3：多语言 + 浮层详情重构（2026-03-25）
新增 static/lang.js 多语言切换模块（en / zh / ms）。所有模板加 data-en / data-zh / data-ms 属性。test_data.py 全部产品/品类/套餐加 name_zh / name_ms 翻译。Detail panel 从行内 flex-wrap 展开方案重构为 fixed overlay bottom sheet 浮层方案：四周留边距、80vh 最大高度、圆角阴影悬浮卡片、遮罩关闭、下滑手势关闭。浮层媒体区从"图片 + 视频按钮展开"简化为"有视频直接放播放器 / 无视频放图片"。新增 spec key 和 spec value 的三语翻译字典（18 个 key + 30+ 个 value）。新增备件包按钮占位。顶栏加语言切换器 EN | 中 | MS。

### v1 → v2：单文件拆分为 Jinja2 模板架构（2026-03-25）
将单文件 index.html（CSS + HTML + JS 全内联）拆分为：6 个 Jinja2 模板（build/templates/）、1 个 CSS 文件（static/style.css）、3 个 JS 文件（static/*.js）、1 个 Python 数据文件（build/data/test_data.py）、1 个生成脚本（build/generator.py）。生成产物输出到 pkg/ 目录，live-server 直接服务整个项目根目录实时预览。

### v0 → v1：CSS Grid 改为 flex-wrap（早期）
产品网格从 CSS Grid 改为 flex-wrap，解决 detail panel 动态插入时的双层错位 bug。Detail panel 设为 flex:0 0 100% 独占一行，JS 计算当前行最后一个 item 位置插入 panel，展开/关闭动画改为 JS 控制的 max-height + transition。（注：v3 已废弃此方案，改为 overlay 浮层。）

## 13. 部署配置（待执行）

Git 已初始化。待执行：创建 GitHub 仓库（gh repo create gym-quote-page --public --source=. --push），然后在 Cloudflare Pages 连接该仓库，Build command 留空，Build output directory 填 /。部署后访问 gym-quote-page.pages.dev。

build/ 目录也会被部署（因为 output 是根目录），但不影响功能。如需排除可添加 .cfignore 文件。

## 14. 版本管理命令速查

git add . && git commit -m "描述" — 保存版本
git log --oneline — 查看历史
git checkout -- static/style.css — 撤回单文件修改
git push — 推送到 GitHub，Cloudflare 自动部署
git revert HEAD && git push — 紧急回滚

## 15. 下一阶段开发优先级
1. 替换真实产品图和试机视频
2. Git + Cloudflare Pages 部署上线
3. 接入飞书 API 动态数据（替换 test_data.py）
4. 备件包和保养维护周期功能
5. 视觉精修（间距、字号、动画流畅度）
6. 法语 / 西班牙语扩展
