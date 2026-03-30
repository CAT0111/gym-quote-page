# 项目结构快照 (自动生成于 2026-03-30 12:27)

## 本地文件结构
```
.cfignore  (14行, 03-29 15:05)
.gitignore  (18行, 03-29 22:50)
DEV.md  (307行, 03-26 16:05)
PRD.md  (79行, 03-25 14:51)
PROJECT_MAP.md  (185行, 03-30 01:49)
check-social-preview.sh  (78行, 03-29 20:15)
gym_layout_400sqm.png  (232KB, 03-26 14:44)
index.html  (5行, 03-30 12:25)
inject_maintenance.py  (128行, 03-26 23:13)
maintenance_data.py  (1299行, 03-27 00:17)
preview-models.html  (349行, 03-26 13:46)
preview-models.html.bak-v1  (146行, 03-26 12:02)
preview-models.html.bak-v2  (261行, 03-26 12:06)
.claude/
  settings.local.json  (26行, 03-29 18:26)
build/
  .env  (8行, 03-29 19:24)
  admin_server.py  (1478行, 03-30 11:55)
  admin_server.py.bak  (117行, 03-29 17:23)
  admin_server.py.bak2  (573行, 03-29 17:45)
  admin_server.py.bak3  (1206行, 03-29 22:50)
  backup_feishu.py  (58行, 03-29 19:16)
  feishu_client.py  (242行, 03-29 19:24)
  fix_syntax_fatal_error.py  (55行, 03-30 12:11)
  generator.py  (126行, 03-30 12:24)
  generator.py.bak-phase0  (63行, 03-29 10:56)
  migrate_fulldata.py  (246行, 03-30 02:43)
  migrate_testdata_to_feishu.py  (166行, 03-29 12:28)
  project_map.py  (225行, 03-29 20:32)
  setup_media_task_table.py  (133行, 03-29 19:23)
  setup_record_type_field.py  (99行, 03-29 17:20)
  sync_specs_to_feishu.py  (150行, 03-30 00:57)
  transform.py  (273行, 03-30 02:56)
  admin_templates/
    admin.html  (1621行, 03-30 11:55)
    freight.html  (483行, 03-30 12:18)
    portal.html  (375行, 03-30 01:23)
    shoot.html  (1055行, 03-30 12:20)
  data/
    __init__.py  (0行, 03-25 14:12)
    test_data.py  (4867行, 03-27 10:13)
    test_data.py.bak  (315行, 03-27 00:18)
  templates/
    (9个 .html 文件, 最新:03-30 11:30)
    base.html.bak-pre3d  (78行, 03-26 12:19)
pkg/
  (5个 .html 文件, 最新:03-30 12:25)
  au-250m/
    latest.html  (1216行, 03-29 23:38)
    v1/
      index.html  (1216行, 03-29 23:38)
  my-jason-400m/
    latest.html  (1762行, 03-29 23:58)
    v1/
      index.html  (1762行, 03-29 18:15)
    v2/
      index.html  (1762行, 03-29 22:55)
    v3/
      index.html  (1762行, 03-29 23:04)
    v4/
      index.html  (1762行, 03-29 23:12)
    v5/
      index.html  (1762行, 03-29 23:19)
    v6/
      index.html  (1762行, 03-29 23:58)
  plan001/
    latest.html  (1970行, 03-30 12:25)
    v1/
      index.html  (1846行, 03-29 22:46)
    v2/
      index.html  (1970行, 03-30 01:28)
    v3/
      index.html  (1970行, 03-30 11:54)
    v4/
      index.html  (1970行, 03-30 12:15)
    v5/
      index.html  (1970行, 03-30 12:25)
  sku/
    (63个 .html 文件, 最新:03-29 18:51)
static/
  category-nav.js  (47行, 03-27 00:44)
  detail-panel.js  (395行, 03-30 01:24)
  gym-3d-scene.js  (186行, 03-27 09:42)
  gym-3d-scene.js.bak-glb  (184行, 03-25 20:02)
  gym-3d-scene.js.bak-v2  (307行, 03-26 12:22)
  lang.js  (91行, 03-25 15:02)
  sop_data.js  (446行, 03-30 12:02)
  style.css  (761行, 03-27 13:12)
  style.css.bak  (182行, 03-27 01:48)
  style.css.bak-pre3d  (120行, 03-26 12:19)
  models/
    changguanhuanjing-400sqm.glb  (2.8MB, 03-26 14:27)
    changguanhuanjing-optimized.glb  (3.4MB, 03-26 11:41)
    gym-scene-v2.glb  (197KB, 03-25 22:44)
  og-images/
    (58个 .jpg 文件, 共6.1MB, 最新:03-29 18:26)
```

## 关键文件摘要

### build/admin_server.py — 26条路由
  @app.route("/pkg/<path:filepath>")
  @app.route("/")
  @app.route("/admin")
  @app.route("/api/plans")
  @app.route("/api/products")
  @app.route("/api/filter-options")
  @app.route("/api/client-plan/create", methods=["POST"])
  @app.route("/api/client-plan/<record_id>/update-info", methods=["POST"])
  @app.route("/api/client-plan/<record_id>")
  @app.route("/api/client-plan/<record_id>/add-sku", methods=["POST"])
  @app.route("/api/client-plan/<record_id>/remove-sku", methods=["POST"])
  @app.route("/api/exchange-rates")
  @app.route("/api/refresh-cache", methods=["POST"])
  @app.route("/api/deploy", methods=["POST"])
  @app.route("/api/generate", methods=["POST"])
  @app.route("/api/qc_clients")
  @app.route("/shoot")
  @app.route("/api/shoot/create-batch", methods=["POST"])
  @app.route("/api/shoot/tasks")
  @app.route("/api/shoot/task/<record_id>/update", methods=["POST"])
  @app.route("/api/shoot/task/<record_id>/approve", methods=["POST"])
  @app.route("/api/shoot/batch-update-status", methods=["POST"])
  @app.route("/freight")
  @app.route("/api/freight/rates")
  @app.route("/api/freight/update", methods=["POST"])
  @app.route("/api/freight/calculate")

## 飞书表结构 (实时拉取)

### product (tblTbEQRKlEzK9AR) — 38个字段, 63条记录
  我的SKU                Text
  分类                   SingleSelect [SC, PL, FM, 固定力量, 挂片式, 力量架, 训练凳, 有氧器械, 自由重量, 功能训练, 辅助配件]
  中文名                  Text
  产品图预览                Attachment
  英文名                  Text
  马来文名                 Text
  采购价RMB               Number
  交期                   Text
  产品主图                 Url
  默认视频                 Url
  器械尺寸mm               Text
  占地面积m²               Number
  净重kg                 Number
  配重kg                 Number
  主训练肌群                MultiSelect [Chest, Back, Legs, Arms, Core, 胸部, 背部, 腿部, 臂部, 核心, 肩部, 全身, 综合多功能, 有氧]
  准入市场认证               MultiSelect [SAA, 通用, CE]
  澳洲专属卖点               Text
  马来专属卖点               Text
  供应商名称                SingleSelect [山东布莱特, 德州宝德龙, 宁津汇祥]
  工厂SKU                Text
  素材任务表-关联SKU          DuplexLink
  利润率                  Number
  毛重kg                 Number
  包装尺寸mm               Text
  详细参数JSON             Text
  英文视频                 Url
  马来文视频                Url
  维保徽章                 SingleSelect [full-kit, long-life, consumable]
  维保承诺(自定义)            Text
  耐用性说明                Text
  耐用性说明中文              Text
  耐用性说明马来文             Text
  保养计划JSON             Text
  备件清单JSON             Text
  产品特点                 Text
  产品备注                 Text
  主要材质                 Text
  最大承重kg               Number

### package (tblkGcwDg5t5U1Lu) — 8个字段, 7条记录
  方案ID                 Text
  客户名                  Text
  包含器材列表               Link
  适用面积m²               Number
  精准运费USD              Number
  目标市场                 SingleSelect [MY, AU, NZ]
  记录类型                 SingleSelect [模板, 客户方案]
  预计交期                 Text

### qc_media (tblLKhngi7gGCDQA) — 3个字段, 3条记录
  客户ID                 Text
  对应SKU                Text
  专属视频链接               Url

### logistics (tblceRTWIg1uNBmK) — 9个字段, 3条记录
  国家                   Text
  柜型                   SingleSelect
  ①起运段费用               Number
  ②海运费                 Number
  ③目的港杂费               Number
  ④综合税率                Number
  ⑤尾程费                 Number
  ⑥安全系数                Number
  更新时间                 DateTime

### media_task (tblahiHJ4Vn8ETza) — 10个字段, 8条记录
  任务批次                 Text
  关联SKU                DuplexLink
  素材类型                 SingleSelect [产品主图, 试机视频, 细节特写, 场景图]
  状态                   SingleSelect [待拍, 已拍, 剪辑中, 待审核, 已完成, 需补拍]
  拍摄人                  Text
  拍摄备注                 Text
  剪辑师                  Text
  成品链接                 Url
  回写目标                 SingleSelect [产品主图, 默认视频]
  完成时间                 DateTime
