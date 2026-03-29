#!/usr/bin/env python3
"""
一次性脚本：
1. 在套餐方案表新增「记录类型」单选字段（选项：模板 / 客户方案）
2. 将现有 PLAN001 记录标记为「模板」
"""
import sys, json, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from feishu_client import get_token, APP_TOKEN, TBL, fetch_all_records

BASE_URL = "https://open.feishu.cn/open-apis"
TABLE_ID = TBL["package"]

# ────── Step 1: 创建「记录类型」单选字段 ──────
print("=" * 50)
print("Step 1: 在套餐方案表创建「记录类型」单选字段")
print("=" * 50)

token = get_token()
url = f"{BASE_URL}/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields"

field_payload = {
    "field_name": "记录类型",
    "type": 3,  # 3 = Single option (单选)
    "property": {
        "options": [
            {"name": "模板", "color": 0},      # 蓝色
            {"name": "客户方案", "color": 1},   # 绿色
        ]
    }
}

body = json.dumps(field_payload).encode()
req = urllib.request.Request(url, data=body, method="POST",
      headers={"Authorization": f"Bearer {token}",
               "Content-Type": "application/json; charset=utf-8"})

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    if result.get("code") == 0:
        field_id = result["data"]["field"]["field_id"]
        print(f"  ✅ 字段创建成功！field_id = {field_id}")
    elif result.get("code") == 1254014:
        print(f"  ⚠️  字段「记录类型」已存在，跳过创建")
    else:
        print(f"  ❌ 创建失败: {result}")
        sys.exit(1)
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    print(f"  ❌ HTTP 错误 {e.code}: {error_body}")
    sys.exit(1)

# ────── Step 2: 找到 PLAN001 的 record_id 并标记为「模板」──────
print()
print("=" * 50)
print("Step 2: 将 PLAN001 标记为「模板」")
print("=" * 50)

records = fetch_all_records("package")
plan001_rid = None

for rec in records:
    plan_id = rec["fields"].get("方案ID", "")
    if plan_id == "PLAN001":
        plan001_rid = rec["record_id"]
        print(f"  找到 PLAN001, record_id = {plan001_rid}")
        break

if not plan001_rid:
    print("  ⚠️  未找到 PLAN001 记录，跳过标记")
    print("  （现有方案：", [r["fields"].get("方案ID","?") for r in records], "）")
else:
    # 更新记录
    update_url = (f"{BASE_URL}/bitable/v1/apps/{APP_TOKEN}"
                  f"/tables/{TABLE_ID}/records/{plan001_rid}")
    update_body = json.dumps({
        "fields": {
            "记录类型": "模板"
        }
    }).encode()
    req2 = urllib.request.Request(update_url, data=update_body, method="PUT",
           headers={"Authorization": f"Bearer {token}",
                    "Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req2) as resp2:
            result2 = json.loads(resp2.read())
        if result2.get("code") == 0:
            print(f"  ✅ PLAN001 已标记为「模板」")
        else:
            print(f"  ❌ 更新失败: {result2}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"  ❌ HTTP 错误 {e.code}: {error_body}")

print()
print("🎉 完成！请在飞书中确认套餐方案表已出现「记录类型」列")
