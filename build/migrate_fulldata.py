#!/usr/bin/env python3
"""
migrate_fulldata.py — 将 test_data.py 完整产品数据迁移到飞书
用法:
  python3 build/migrate_fulldata.py          # dry-run 只打印不写入
  python3 build/migrate_fulldata.py --commit # 真正写入飞书
"""
import sys, os, json, re, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from feishu_client import fetch_all_records, update_record, add_field
from data.test_data import PRODUCTS

COMMIT = "--commit" in sys.argv

# ── 分类映射 ──
CAT_MAP = {
    "sel": "固定力量", "pl": "挂片式", "rf": "力量架", "bn": "训练凳",
    "ac": "有氧器械", "fw": "自由重量", "ft": "功能训练", "ca": "辅助配件",
}

# ── 需新增的 11 个字段 ──
NEW_FIELDS = [
    # (字段名, 飞书类型编号, property_config)
    ("维保徽章", 3, {"options": [
        {"name": "full-kit"}, {"name": "long-life"}, {"name": "consumable"}
    ]}),
    ("维保承诺(自定义)", 1, None),
    ("耐用性说明", 1, None),
    ("耐用性说明中文", 1, None),
    ("耐用性说明马来文", 1, None),
    ("保养计划JSON", 1, None),
    ("备件清单JSON", 1, None),
    ("产品特点", 1, None),
    ("产品备注", 1, None),
    ("主要材质", 1, None),
    ("最大承重kg", 2, None),
]


def safe_num(text):
    """从文本提取数字: '268 kg' → 268.0, '<4 tons' → 4.0"""
    if not text:
        return None
    m = re.search(r"[\d,.]+", str(text))
    if m:
        try:
            return float(m.group().replace(",", ""))
        except ValueError:
            return None
    return None


def build_fields(p):
    """将一条 test_data 产品转换为飞书字段 dict"""
    specs = p.get("specs", {})
    maint = p.get("maintenance", {})
    f = {}

    # ── A. 直接映射（已有字段）──
    f["英文名"] = p.get("name", "")
    f["中文名"] = p.get("name_zh", "")
    f["马来文名"] = p.get("name_ms", "")

    if p.get("image_url"):
        f["产品主图"] = {"link": p["image_url"], "text": p["image_url"]}
    if p.get("video_url"):
        f["默认视频"] = {"link": p["video_url"], "text": p["video_url"]}

    cat = CAT_MAP.get(p.get("category_key", ""))
    if cat:
        f["分类"] = cat

    # ── B. specs → 已有独立字段 ──
    if specs.get("Dimensions"):
        f["器械尺寸mm"] = specs["Dimensions"]
    if specs.get("Packing"):
        f["包装尺寸mm"] = specs["Packing"]

    for src, dst in [("Net Weight", "净重kg"), ("Gross Weight", "毛重kg"),
                     ("Weight Stack", "配重kg")]:
        v = safe_num(specs.get(src))
        if v is not None:
            f[dst] = v

    # ── C. specs → 新增独立字段 ──
    if specs.get("Feature"):
        f["产品特点"] = specs["Feature"]
    if specs.get("Note"):
        f["产品备注"] = specs["Note"]
    if specs.get("Material"):
        f["主要材质"] = specs["Material"]
    v = safe_num(specs.get("Max Load"))
    if v is not None:
        f["最大承重kg"] = v

    # ── D. 完整 specs JSON 兜底 ──
    f["详细参数JSON"] = json.dumps(specs, ensure_ascii=False)

    # ── E. maintenance 拆字段 ──
    if maint.get("badge"):
        f["维保徽章"] = maint["badge"]
    # 维保承诺(自定义) 初始迁移留空（用默认值）

    if maint.get("durability_note"):
        f["耐用性说明"] = maint["durability_note"]
    if maint.get("durability_note_zh"):
        f["耐用性说明中文"] = maint["durability_note_zh"]
    if maint.get("durability_note_ms"):
        f["耐用性说明马来文"] = maint["durability_note_ms"]

    if maint.get("schedule"):
        f["保养计划JSON"] = json.dumps(maint["schedule"], ensure_ascii=False)
    if maint.get("spare_parts"):
        f["备件清单JSON"] = json.dumps(maint["spare_parts"], ensure_ascii=False)

    return f


# ═══════════════════════════════════════
#  Phase 1: 创建新字段
# ═══════════════════════════════════════
def phase1_create_fields():
    print("\n╔══ Phase 1: 创建飞书新字段 ══╗")
    # 先拉已有字段名，避免重复创建
    existing = fetch_all_records("product")
    existing_field_names = set()
    if existing:
        existing_field_names = set(existing[0].get("fields", {}).keys())

    created = 0
    skipped = 0
    for name, ftype, prop in NEW_FIELDS:
        if name in existing_field_names:
            print(f"  ⏭️  {name} — 已存在，跳过")
            skipped += 1
            continue
        if COMMIT:
            try:
                add_field("product", name, ftype, prop)
                print(f"  ✅ {name} — 已创建")
                created += 1
                time.sleep(0.3)
            except Exception as e:
                print(f"  ❌ {name} — 创建失败: {e}")
        else:
            print(f"  🔵 {name} (type={ftype}) — dry-run，未创建")
            created += 1

    print(f"  小结: 新建 {created}, 跳过 {skipped}")
    return True


# ═══════════════════════════════════════
#  Phase 2: 匹配 SKU → record_id
# ═══════════════════════════════════════
def phase2_match_sku():
    print("\n╔══ Phase 2: 匹配 SKU ══╗")
    records = fetch_all_records("product")
    sku_to_rec = {}
    for r in records:
        sku = r.get("fields", {}).get("我的SKU", "")
        if sku:
            sku_to_rec[sku] = r["record_id"]

    td_skus = {p["sku"] for p in PRODUCTS}
    matched = td_skus & set(sku_to_rec.keys())
    missing_in_feishu = td_skus - set(sku_to_rec.keys())
    extra_in_feishu = set(sku_to_rec.keys()) - td_skus

    print(f"  test_data: {len(td_skus)} 个 SKU")
    print(f"  飞书:      {len(sku_to_rec)} 条记录")
    print(f"  ✅ 匹配:   {len(matched)}")
    if missing_in_feishu:
        print(f"  ⚠️  test_data 有但飞书没有: {sorted(missing_in_feishu)}")
    if extra_in_feishu:
        print(f"  ℹ️  飞书有但 test_data 没有: {sorted(extra_in_feishu)}")

    return sku_to_rec


# ═══════════════════════════════════════
#  Phase 3: 写入数据
# ═══════════════════════════════════════
def phase3_write(sku_to_rec):
    print("\n╔══ Phase 3: 写入产品数据 ══╗")
    success = 0
    fail = 0
    skip = 0

    for i, p in enumerate(PRODUCTS):
        sku = p["sku"]
        rec_id = sku_to_rec.get(sku)

        if not rec_id:
            print(f"  [{i+1:2d}/63] {sku} — ⚠️ 飞书无此 SKU，跳过")
            skip += 1
            continue

        fields = build_fields(p)
        field_count = len(fields)

        if COMMIT:
            try:
                update_record("product", rec_id, fields)
                print(f"  [{i+1:2d}/63] {sku} — ✅ 已更新 {field_count} 个字段")
                success += 1
                time.sleep(0.35)  # 飞书限流保护
            except Exception as e:
                print(f"  [{i+1:2d}/63] {sku} — ❌ 失败: {e}")
                fail += 1
        else:
            print(f"  [{i+1:2d}/63] {sku} — 🔵 dry-run | {field_count} 个字段待写入")
            # 打印前3条的字段清单作为抽样
            if i < 3:
                for k, v in fields.items():
                    val_preview = str(v)[:60]
                    print(f"           {k}: {val_preview}")
            success += 1

    print(f"\n  小结: 成功 {success}, 失败 {fail}, 跳过 {skip}")


# ═══════════════════════════════════════
#  主流程
# ═══════════════════════════════════════
if __name__ == "__main__":
    mode = "🔴 正式写入" if COMMIT else "🔵 DRY-RUN（预览模式）"
    print(f"\n{'='*50}")
    print(f"  ProvenLift 全量数据迁移  |  {mode}")
    print(f"  数据源: test_data.py ({len(PRODUCTS)} 条产品)")
    print(f"{'='*50}")

    phase1_create_fields()
    sku_map = phase2_match_sku()
    phase3_write(sku_map)

    print(f"\n{'='*50}")
    if not COMMIT:
        print("  以上为预览，确认无误后执行:")
        print("  python3 build/migrate_fulldata.py --commit")
    else:
        print("  ✅ 迁移完成！")
        print("  建议验证: 飞书打开产品表，抽查 3-5 条记录")
        print("  然后重新生成一个客户方案页面，检查维保面板是否正常显示")
    print(f"{'='*50}\n")
