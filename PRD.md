# 报价网页工具 — 产品需求文档（PRD）

## 1. 产品定位
面向马来西亚健身器材经销商和终端健身房客户的移动端报价展示网页。客户通过 WhatsApp 收到链接，手机点开即可浏览整馆器材方案，包含每台器材的图片、参数、价格和试机视频，无需下载任何文件。

## 2. 目标用户
主要用户是马来西亚健身器材经销商（通过 WhatsApp 接收链接），次要用户是经销商的下游客户（健身房老板）。95% 的用户使用手机访问（从 WhatsApp 点开链接），以 Android 和 iPhone 为主。

## 3. 核心用户场景

**场景一：快速总览。** 客户想用 30 秒扫一眼"这单一共多少台、都有什么、总价多少"。需要信息密度高，一屏尽量多看。

**场景二：逐台细看。** 客户对某台器材感兴趣或想换品，需要看大图、完整参数、试机视频。需要信息完整、沉浸感强。

**场景三：发起沟通。** 客户看完后想询价、换品或下单，需要一键跳转 WhatsApp 并自动预填消息（包含套餐编号和产品 SKU）。

## 4. 页面结构（从上到下）

### 4.1 固定顶栏
始终钉在顶部，高度 48px。左侧品牌 Logo 文字"ProvenLift"，右侧绿色 WhatsApp 按钮。背景半透明深色带毛玻璃效果，不遮挡内容但始终可见。WhatsApp 链接预填消息"Hi, I'm interested in PKG-400A"，套餐编号由 Jinja2 模板变量 package.id 自动填入。

### 4.2 首屏冲击区（Hero）
全屏高度的健身房实景照片做背景，底部向上有深色渐变遮罩。叠三层信息：套餐名称白色粗体大字、两个关键数字（台数 + FOB 总价）用金色强调、一个信任标签"Every machine tested before shipping"。底部有向下箭头动画暗示继续滑动。背景图压缩到 200KB 以内保证首屏秒开。

### 4.3 品类快速导航
Sticky 定位在顶栏下方，横向滑动的分区标签栏：Selectorized / Plate Loaded / Racks / Bench / Cardio。点击跳转到对应分区，滚动时自动高亮当前分区。

### 4.4 采购清单（页面主体）
按健身房功能区分组，每组开头一个深色标题条显示分区名称和台数。

**默认状态（总览模式）：** 移动端两列紧凑网格，每个格子只显示缩略图（正方形）、产品简称和价格。一屏可见 6-8 台设备。

**展开状态（详情模式）：** 点击任何格子，该格子所在行下方展开一个全宽详情面板，包含大图、完整产品名、SKU、规格参数表、价格、"Watch 60s Test Video"按钮（视频原位展开播放）、单品 WhatsApp 询价链接。点击其他格子自动关闭当前展开项并打开新的。再次点击同一个格子关闭。无视频 URL 时按钮显示"Video coming soon"并置灰不可点击。

**分区顺序：** Selectorized → Plate Loaded → Free Weight / Racks → Bench → Cardio。

### 4.5 总价汇总条
深色渐变背景全宽横条。显示总台数、FOB 总价（最大字号金色）、预估 CIF 到 Port Klang 价格（灰色小字）。

### 4.6 信任锚点区（Why Work With Us）
深色背景区，竖排 4 个信任点，每个信任点左侧图标右侧标题加说明。内容依次为：100% Tested（真人试机视频保证）、Custom Maintenance Kit（随柜配件弹药箱）、On-Site Commissioning（飞到现场调试）、48h Spare Parts（马来西亚本地备件 48 小时送达）。

### 4.7 3D 整馆布局展示区
深灰背景。标题"Your Gym Layout"。嵌入 Three.js 构建的 3D 场景，包含房间墙体、地面网格、分区标签、各类器材模型（用基础几何体表示）。支持手指拖动旋转和双指缩放。下方提示文字引导客户发送平面图获取定制布局。

如果当前套餐/方案没有对应的 3D 场景，此区块可降级显示 2D 平面图或直接隐藏。

### 4.8 底部行动号召
深色背景区。大字"Like this setup?"，说明文字"Tell me which machines you'd like to swap — I'll update your plan within 24 hours."，全宽绿色 WhatsApp 大按钮预填询价消息。

### 4.9 页脚
极简，一行品牌名 + 年份。

## 5. 交互规格

**详情面板展开/关闭：** 使用 max-height + opacity 过渡动画，展开 0.3s ease-out，收起 0.25s ease-in。展开后取消 max-height 限制以适应视频展开。关闭时先播放收起动画再移除 DOM 节点。

**视频播放：** 点击"Watch 60s Test Video"按钮后视频在详情面板内原位展开，使用 HTML5 video 标签加载 mp4 直链。再次点击收起。支持 playsinline 属性以适配 iOS。无视频 URL 时按钮禁用。

**品类导航滚动联动：** 滚动页面时自动高亮当前可视区域对应的品类标签。点击标签平滑滚动到目标分区，偏移量为顶栏高度 + 导航栏高度（约 100px）。

**WhatsApp 预填消息：** 顶栏按钮预填套餐编号，底部按钮预填套餐编号 + 换品意图，单品询价链接预填 SKU + 产品名。WhatsApp 号码从模板变量 package.whatsapp_number 读取。

## 6. 多语言方案（待实现）
所有页面框架文案通过 HTML data 属性存储三种语言版本（data-en / data-ms / data-zh），JS 检测 navigator.language 自动切换。产品名称只显示英文（行业通用语言），不做多语言。

## 7. 技术约束
移动端优先设计，断点 768px 以上切换为 3 列网格。图片使用 Unsplash 占位（后续替换为真实产品图，从飞书 T_Product 表的 CDN URL 字段读取）。Three.js 从 CDN 加载（r128 版本）。页面通过 Jinja2 模板 + Python 生成脚本（build/generator.py）渲染为静态 HTML，部署到 Cloudflare Pages。

## 8. 数据来源
产品数据来自飞书多维表格 T_Product，套餐配置来自 T_Package，客户方案来自 T_Client_Plan。通过 Python 生成脚本（build/generator.py）读取数据，使用 Jinja2 模板渲染生成静态 HTML 到 pkg/ 目录。

**当前状态：** 使用硬编码测试数据（build/data/test_data.py），后续替换为飞书 API 调用。

## 9. SKU 编码规范
品类代码 2-3 位大写字母 + 短横线 + 系列字母 1 位 + 序号 2-3 位数字。品类包括：SC（固定力量）、PL（挂片式）、FM（自由力量/架类）、CB（有氧）、BN（训练凳）、CA（线缆/龙门架）、AC（配件）、ST（存储架）。套餐编号格式 PKG-面积+版本字母，客户方案编号格式 CLT-日期-序号。

## 10. 当前测试数据
共 20 台设备分 5 个分区：Selectorized 6 台（SC-A01 至 SC-A06）、Plate Loaded 4 台（PL-A01 至 PL-A04）、Free Weight / Racks 3 台（FM-A01、FM-A02、ST-A01）、Bench 3 台（BN-A01 至 BN-A03）、Cardio 4 台（CB-A01 至 CB-A04）。FOB 总价 $12,800，预估 CIF Port Klang ~$14,200。