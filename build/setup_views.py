#!/usr/bin/env python3
"""
setup_views.py — 在飞书产品表中创建 6 个业务视图
每个视图只显示对应角色需要的字段
"""
import sys, os, json, urllib.request, time
sys.path.insert(0, os.path.dirname(__file__))
from feishu_client import get_token, _load_env

_load_env()
APP_TOKEN = os.environ["FEISHU_APP_TOKEN"]
TABLE_ID = "tblTbEQRKlEzK9AR"  # product 表
BASE_URL = "https://open.feishu.cn/open-apis"

# ── 6 个视图定义：名称 → 要显示的字段列表 ──
VIEWS = [
    {
        "name": "📋 文员建档",
        "fields": ["我的SKU", "中文名", "分类", "供应商名称", "工厂SKU", "采购价RMB", "交期"],
    },
    {
        "name": "🔧 技术参数",
        "fields": ["我的SKU", "中文名", "分类", "器械尺寸mm", "净重kg", "毛重kg", "配重kg",
                   "包装尺寸mm", "占地面积m²", "最大承重kg", "主要材质", "主训练肌群", "准入市场认证"],
    },
    {
        "name": "📸 素材管理",
        "fields": ["我的SKU", "中文名", "分类", "产品图预览", "产品主图", "默认视频",
                   "英文视频", "马来文视频", "素材任务表-关联SKU"],
    },
    {
        "name": "🌐 多语言翻译",
        "fields": ["我的SKU", "中文名", "英文名", "马来文名", "产品特点", "产品备注",
                   "澳洲专属卖点", "马来专属卖点", "耐用性说明", "耐用性说明中文", "耐用性说明马来文"],
    },
    {
        "name": "🛡️ 维保信息",
        "fields": ["我的SKU", "中文名", "分类", "维保徽章", "维保承诺(自定义)",
                   "保养计划JSON", "备件清单JSON"],
    },
    {
        "name": "💰 定价商务",
        "fields": ["我的SKU", "中文名", "分类", "采购价RMB", "利润率", "供应商名称", "工厂SKU"],
    },
]


def api_get(path, token):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def api_post(path, token, body):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST",
          headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def api_patch(path, token, body):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="PATCH",
          headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def main():
    token = get_token()

    # Step 1: 获取所有字段 → 建立 字段名→field_id 映射
    print("📡 获取字段列表...")
    fields_resp = api_get(f"/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields?page_size=100", token)
    if fields_resp.get("code") != 0:
        print(f"❌ 获取字段失败: {fields_resp}")
        return

    name_to_id = {}
    for f in fields_resp["data"]["items"]:
        name_to_id[f["field_name"]] = f["field_id"]
    print(f"   共 {len(name_to_id)} 个字段")

    # 检查视图定义里的字段是否都存在
    all_ok = True
    for view in VIEWS:
        for fn in view["fields"]:
            if fn not in name_to_id:
                print(f"   ⚠️ 视图「{view['name']}」引用的字段「{fn}」在飞书中不存在")
                all_ok = False
    if not all_ok:
        print("   请先确认字段名是否正确，再重新运行")
        return

    # Step 2: 获取已有视图，避免重复创建
    print("\n📡 获取已有视图...")
    views_resp = api_get(f"/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/views?page_size=100", token)
    existing_views = {}
    if views_resp.get("code") == 0:
        for v in views_resp["data"]["items"]:
            existing_views[v["view_name"]] = v["view_id"]
    print(f"   已有 {len(existing_views)} 个视图: {list(existing_views.keys())}")

    # Step 3: 逐个创建视图 + 设置可见字段
    for view_def in VIEWS:
        vname = view_def["name"]
        visible_ids = [name_to_id[fn] for fn in view_def["fields"]]
        all_field_ids = list(name_to_id.values())
        hidden_ids = [fid for fid in all_field_ids if fid not in visible_ids]

        print(f"\n{'='*40}")
        print(f"  视图: {vname}")
        print(f"  显示 {len(visible_ids)} 个字段, 隐藏 {len(hidden_ids)} 个字段")

        # 创建或获取视图ID
        if vname in existing_views:
            view_id = existing_views[vname]
            print(f"  ⏭️  已存在 (view_id={view_id})，更新字段配置...")
        else:
            resp = api_post(
                f"/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/views",
                token, {"view_name": vname, "view_type": "grid"}
            )
            if resp.get("code") != 0:
                print(f"  ❌ 创建失败: {resp}")
                continue
            view_id = resp["data"]["view"]["view_id"]
            print(f"  ✅ 已创建 (view_id={view_id})")
            time.sleep(0.3)

        # 设置字段可见性：用 property.hidden_fields 隐藏不需要的字段
        patch_resp = api_patch(
            f"/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/views/{view_id}",
            token,
            {"property": {"hidden_fields": hidden_ids}}
        )
        if patch_resp.get("code") != 0:
            print(f"  ⚠️ 设置字段可见性失败: {patch_resp.get('msg', patch_resp)}")
        else:
            print(f"  ✅ 字段可见性已配置")
        time.sleep(0.3)

    print(f"\n{'='*40}")
    print("✅ 全部视图创建完成！去飞书产品表切换视图查看。")


if __name__ == "__main__":
    main()
