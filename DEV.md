# 报价网页工具 — 开发文档

## 1. 项目状态
当前版本：v2 — Jinja2 模板化架构。CSS / JS / HTML 模板分离，Python 生成脚本从数据源读取数据渲染静态 HTML。产品数据当前使用硬编码测试数据，后续替换为飞书 API。Detail panel 展开交互已稳定（flex-wrap 方案），3D 场景已拆分为独立 JS 文件。Git 已初始化，手机端和公网预览已跑通。

## 2. 技术栈
前端使用纯 HTML + CSS + 原生 JS，无框架依赖。3D 场景使用 Three.js r128（CDN 引入）。模板引擎使用 Jinja2（Python）。CSS 采用移动端优先设计，唯一断点 768px。部署目标为 Cloudflare Pages（GitHub 仓库自动部署）。

## 3. 本地开发环境
操作系统为 macOS（Apple Silicon）。Python 3 + Jinja2 已安装。Node.js 已安装（通过 Homebrew），live-server 全局安装用于本地热刷新，cloudflared 已安装用于公网穿透预览，编辑器使用 VS Code（已配置 code 命令）。

项目路径：~/Projects/gym-quote-page

## 4. 文件结构

~/Projects/gym-quote-page/ ├── build/ # 构建工具（不部署） │ ├── generator.py # 主生成脚本 │ ├── data/ │ │ ├── init.py │ │ └── test_data.py # 硬编码测试数据（后续换飞书 API） │ └── templates/ │ ├── base.html # 页面骨架（引用其他模板） │ ├── hero.html # 首屏冲击区 │ ├── price_summary.html # 总价汇总 │ ├── trust.html # 信任区 │ ├── scene_3d.html # 3D 场景容器 │ └── bottom_cta.html # 底部 CTA ├── static/ # 静态资源（直接部署） │ ├── style.css # 全部 CSS │ ├── category-nav.js # 品类导航交互 │ ├── detail-panel.js # 详情面板交互 │ └── gym-3d-scene.js # 3D 场景渲染 ├── pkg/ # 生成的套餐页面（部署产物） │ └── 400a.html # PKG-400A 套餐页 ├── c/ # 生成的客户方案页面（预留） ├── index.html # 首页重定向到默认套餐 ├── PRD.md └── DEV.md


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

## 6. CSS 架构
全局重置使用 *{margin:0;padding:0;box-sizing:border-box}。配色体系：主背景 #0a0a0a，卡片背景 #111，金色强调 #c8a44e，WhatsApp 绿 #25D366，文字白色配不同透明度层级（1.0 / 0.8 / 0.4 / 0.25）。字体使用系统默认字体栈。

布局方案：产品网格使用 display:flex; flex-wrap:wrap，每个 grid-item 为 flex:0 0 calc(50% - .5px)，768px 以上切换为 calc(33.333% - .67px)。Detail panel 为 flex:0 0 100%，在 flex-wrap 容器中自动独占一行。

## 7. JS 模块说明

### 7.1 品类导航（static/category-nav.js）
IIFE 封装。点击标签滚动到目标分区，偏移量 100px（顶栏 48px + 导航栏约 52px）。滚动监听使用 passive 事件，遍历所有 [id^="sec-"] 元素判断当前可视区域，切换 active 类。首屏向下箭头点击滚动到导航栏。

### 7.2 详情面板（static/detail-panel.js）
IIFE 封装。核心变量：currentDetail（当前展开的 panel DOM 节点）、currentSelectedItem（当前选中的 grid-item）。

openDetail(gridItem) 流程：如果点击同一 item 则关闭；否则先调用 closeDetailImmediate() 同步移除旧 panel；解析 data-specs JSON 构建参数表 HTML；根据 data-video 是否为空决定视频按钮状态（有 URL 显示播放按钮，无 URL 显示灰色"Video coming soon"）；创建 panel DOM 节点；计算插入位置（当前行最后一个 grid-item 之后）；用双重 requestAnimationFrame 触发展开动画（max-height 从 0 到 scrollHeight）；transitionend 后将 max-height 设为 none 以适应后续视频展开。

WhatsApp 号码从 document.body.dataset.whatsapp 读取（由 Jinja2 模板写入 body 的 data-whatsapp 属性）。

closeDetail() 流程：先将 max-height 设为当前 scrollHeight（锁定高度），下一帧过渡到 0；transitionend 后移除 DOM 节点。

closeDetailImmediate() 流程：同步移除 DOM，不播放动画，用于打开新 panel 前清除旧 panel 避免闪烁。

视频切换：通过 data-action="toggle-video" 属性绑定事件，切换 detail-video-wrap 的 active 类，控制视频显示/隐藏和播放/暂停。

### 7.3 3D 场景（static/gym-3d-scene.js）
IIFE 封装，所有变量不污染全局。场景内容：20x20 单位地面 + 网格辅助线、4 面 3 米高墙体、4 个分区文字标签（Canvas 纹理 Sprite）、6 台固定力量器械（含配重片组）、4 台挂片器械（红色）、3 个力量架、1 个哑铃架（含 10 个哑铃模型）、4 台跑步机、3 台单车、2 条训练凳。

相机控制为手写轨道控制：球坐标系（theta/phi/radius）+ 鼠标拖拽/滚轮缩放 + 触摸单指旋转/双指缩放。phi 限制在 0.2 到 PI/2.1 之间防止翻转，radius 限制在 8 到 40 之间。

渲染使用 requestAnimationFrame 循环。窗口 resize 时更新 canvas 尺寸、相机 aspect 和 renderer size。

## 8. 生成脚本说明（build/generator.py）

输入：从 build/data/test_data.py 读取 PACKAGE、CATEGORIES、PRODUCTS 数据。

处理：按 category_key 分组产品，加载 Jinja2 模板，注册 tojson 过滤器，渲染 base.html（自动 include 子模板）。

输出：pkg/400a.html（套餐报价页）和 index.html（重定向页）。

后续扩展点：替换 test_data.py 为飞书 API 调用（feishu_api.py）；支持多套餐生成（遍历 T_Package 表）；支持客户方案生成（输出到 c/ 目录）。

## 9. 已知问题与待修项

P1 — 图片全部使用 Unsplash 占位图。需替换为真实产品图（从飞书 T_Product 表读取 CDN URL）。

P2 — 视频源为空。所有产品的 video_url 为空字符串，按钮显示"Video coming soon"。需接入真实试机视频 URL。

P3 — 3D 场景使用基础几何体。后续替换为 GLB 格式真实器材模型。

P4 — 未实现多语言切换。

P5 — 未接入 Cloudflare Pages 部署。GitHub 仓库和 Cloudflare Pages 连接待配置。

P6 — 未接入飞书 API。数据仍为硬编码，需开发 feishu_api.py 模块。

## 10. 历史重构记录

### v1 → v2：单文件拆分为 Jinja2 模板架构（2026-03-25）
将单文件 index.html（CSS + HTML + JS 全内联）拆分为：6 个 Jinja2 模板（build/templates/）、1 个 CSS 文件（static/style.css）、3 个 JS 文件（static/*.js）、1 个 Python 数据文件（build/data/test_data.py）、1 个生成脚本（build/generator.py）。生成产物输出到 pkg/ 目录，live-server 直接服务整个项目根目录实时预览。

### v0 → v1：CSS Grid 改为 flex-wrap（早期）
产品网格从 CSS Grid 改为 flex-wrap，解决 detail panel 动态插入时的双层错位 bug。Detail panel 设为 flex:0 0 100% 独占一行，JS 计算当前行最后一个 item 位置插入 panel，展开/关闭动画改为 JS 控制的 max-height + transition。

## 11. 部署配置（待执行）

Git 已初始化。待执行：创建 GitHub 仓库（gh repo create gym-quote-page --public --source=. --push），然后在 Cloudflare Pages 连接该仓库，Build command 留空，Build output directory 填 /。部署后访问 gym-quote-page.pages.dev。

build/ 目录也会被部署（因为 output 是根目录），但不影响功能。如需排除可添加 .cfignore 文件。

## 12. 版本管理命令速查

git add . && git commit -m "描述" — 保存版本
git log --oneline — 查看历史
git checkout -- static/style.css — 撤回单文件修改
git push — 推送到 GitHub，Cloudflare 自动部署
git revert HEAD && git push — 紧急回滚

## 13. 下一阶段开发优先级
1. 视觉精修（间距、字号、动画流畅度）
2. 替换真实产品图和视频
3. Git + Cloudflare Pages 部署上线
4. 接入飞书 API 动态数据（替换 test_data.py）
5. 多语言支持
