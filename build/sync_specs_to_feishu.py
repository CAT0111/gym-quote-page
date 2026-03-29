"""
sync_specs_to_feishu.py
1) 把「尺寸mm」改名为「器械尺寸mm」
2) 新增 4 个字段（毛重kg、包装尺寸mm、详细参数JSON、英文视频、马来文视频）
3) 从 test_data.py 读取 specs，按 SKU 匹配回写到飞书
"""
import sys, json, os, re
sys.path.insert(0, os.path.dirname(__file__))
from feishu_client import (fetch_all_records, add_field, update_record,
                           get_token, TBL, BASE_URL)
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data'))
from test_data import PRODUCTS as LOCAL_PRODUCTS

APP_TOKEN = os.environ["FEISHU_APP_TOKEN"]

# ---- Step 1: 把「尺寸mm」改名为「器械尺寸mm」----
print("=" * 50)
print("Step 1: 重命名「尺寸mm」→「器械尺寸mm」")
print("=" * 50)

token = get_token()
table_id = TBL["product"]
field_id_dim = "fldTSGxzJE"  # 尺寸mm 的字段ID

url = f"{BASE_URL}/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/fields/{field_id_dim}"
body = json.dumps({"field_name": "器械尺寸mm"}).encode()
req = urllib.request.Request(url, data=body, method="PUT",
      headers={"Authorization": f"Bearer {token}",
               "Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    if result.get("code") == 0:
        print("  ✅ 已改名为「器械尺寸mm」")
    else:
        print(f"  ⚠️  改名返回: {result}")
except Exception as e:
    print(f"  ❌ 改名失败: {e}")

# ---- Step 2: 查询现有字段，新增缺失字段 ----
print("\n" + "=" * 50)
print("Step 2: 新增字段")
print("=" * 50)

def get_existing_fields():
    token = get_token()
    url = f"{BASE_URL}/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/fields?page_size=100"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    if result.get("code") != 0:
        raise RuntimeError(f"获取字段列表失败: {result}")
    return {f["field_name"] for f in result["data"]["items"]}

existing = get_existing_fields()
print(f"  现有字段: {sorted(existing)}\n")

NEW_FIELDS = [
    ("毛重kg",       2,  None),   # 数字
    ("包装尺寸mm",   1,  None),   # 文本
    ("详细参数JSON", 1,  None),   # 文本
    ("英文视频",     15, None),   # 超链接
    ("马来文视频",   15, None),   # 超链接
]

for name, ftype, prop in NEW_FIELDS:
    if name in existing:
        print(f"  ⏭️  「{name}」已存在，跳过")
    else:
        add_field("product", name, ftype, prop)

# ---- Step 3: 构建 SKU → 本地数据映射 ----
print("\n" + "=" * 50)
print("Step 3: 回写数据到飞书")
print("=" * 50)

# 这些键已有飞书独立字段，不进 JSON
SKIP_KEYS = {"Dimensions", "Net Weight", "Weight Stack", "Target",
             "Gross Weight", "Packing"}

def parse_kg(val):
    if not val:
        return None
    v = val.strip().lower()
    if "ton" in v:
        m = re.search(r'[\d.]+', v)
        return float(m.group()) * 1000 if m else None
    m = re.search(r'[\d.]+', v)
    return float(m.group()) if m else None

sku_data = {}
for p in LOCAL_PRODUCTS:
    sku = p.get("sku", "")
    if not sku:
        continue
    specs = p.get("specs", {})

    gross = parse_kg(specs.get("Gross Weight"))
    packing = specs.get("Packing", "")

    json_specs = {}
    for k, v in specs.items():
        if k in SKIP_KEYS:
            continue
        json_specs[k] = v

    sku_data[sku] = {"gross": gross, "packing": packing, "json": json_specs}

print(f"  本地有 specs 的 SKU: {len(sku_data)} 个\n")

# ---- 拉取飞书记录，按 SKU 匹配更新 ----
records = fetch_all_records("product")
print(f"  飞书产品表: {len(records)} 条\n")

updated = 0
skipped = 0
no_match = 0

for rec in records:
    sku = rec["fields"].get("我的SKU", "")
    if not sku or sku not in sku_data:
        no_match += 1
        continue

    local = sku_data[sku]
    upd = {}

    if local["gross"] is not None:
        upd["毛重kg"] = local["gross"]
    if local["packing"]:
        upd["包装尺寸mm"] = local["packing"]
    if local["json"]:
        upd["详细参数JSON"] = json.dumps(local["json"], ensure_ascii=False)

    if not upd:
        skipped += 1
        continue

    try:
        update_record("product", rec["record_id"], upd)
        updated += 1
    except Exception as e:
        print(f"  ❌ {sku} 失败: {e}")

print(f"\n{'='*50}")
print(f"✅ 更新: {updated} | ⏭️ 无需更新: {skipped} | ❓ 无本地数据: {no_match}")
print(f"\n⚠️  注意: transform.py 中的 FIELD_MAP_PRODUCT 需要把")
print(f"   '尺寸mm' 改为 '器械尺寸mm'，下一步处理。")
