#!/usr/bin/env python3
"""
migrate_testdata_to_feishu.py
把 test_data.py 的 63 台产品一次性灌入飞书产品主表
用法: python3 build/migrate_testdata_to_feishu.py
"""
import sys, re
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BUILD_DIR))
sys.path.insert(0, str(BUILD_DIR / "data"))

from feishu_client import fetch_all, batch_create_records, batch_delete_records
from test_data import PRODUCTS

# ========== 映射表 ==========

# category_key → 中文分类
CAT_MAP = {
    "sel": "固定力量",
    "pl":  "挂片式",
    "rf":  "力量架",
    "bn":  "训练凳",
    "ca":  "有氧器械",
    "fw":  "自由重量",
    "ft":  "功能训练",
    "ac":  "辅助配件",
}

# 英文Target → 中文肌群多选（每个target映射到1~3个中文标签）
TARGET_MAP = {
    "Rear Delt / Chest":                          ["胸部", "肩部"],
    "Front / Middle Deltoid":                      ["肩部"],
    "Lats / Rhomboids / Biceps":                   ["背部", "臂部"],
    "Biceps":                                      ["臂部"],
    "俯卧曲腿":                                     ["腿部"],
    "Hamstrings":                                  ["腿部"],
    "Quadriceps":                                  ["腿部"],
    "Inner / Outer Thigh":                         ["腿部"],
    "Full body multi-joint":                       ["全身"],
    "Chest / Back / Shoulders multi-function":     ["综合多功能"],
    "Middle Deltoid":                              ["肩部"],
    "Lats / Teres Major":                          ["背部"],
    "Deltoid / Triceps":                           ["肩部", "臂部"],
    "Lats / Rhomboids":                            ["背部"],
    "Upper Chest / Front Deltoid":                 ["胸部", "肩部"],
    "Outer Chest / Serratus Anterior":             ["胸部"],
    "Triceps / Lats":                              ["臂部", "背部"],
    "Lower Chest":                                 ["胸部"],
    "Mid Chest":                                   ["胸部"],
    "Chest / Front Deltoid / Triceps":             ["胸部", "肩部", "臂部"],
    "Quads / Glutes":                              ["腿部"],
    "Quads / Glutes / Hamstrings":                 ["腿部"],
    "Full body (lat pull / low row / pec fly / legs etc.)": ["全身"],
    "Full body (squat / bench press / row / shrug etc.)":   ["全身"],
    "Squat / Deadlift / Bench Press / Pull-up":    ["全身"],
    "Erector Spinae / Glutes":                     ["背部", "核心"],
    "Bicep curl / Triceps":                        ["臂部"],
    "Shoulders / Arms / Glutes / Legs":            ["有氧"],
    "Full body (upper + lower limbs linked)":      ["有氧"],
    "Full body (core focused)":                    ["核心"],
    "Full body explosive power / Core / Glutes & Legs": ["全身", "核心", "腿部"],
    "Lats / Biceps / Core":                        ["背部", "臂部", "核心"],
}


def make_link_field(url):
    """构造飞书链接字段格式"""
    if not url:
        return None
    return {"link": url, "text": url}


def extract_number(text):
    """从文本中提取数字（如 '150 kg' -> '150'）"""
    if not text:
        return ""
    m = re.search(r'[\d.]+', str(text))
    return m.group() if m else text


def convert_product(p):
    """把 test_data 的一个产品转成飞书 fields 字典"""
    specs = p.get("specs", {})
    target = specs.get("Target", "")
    
    fields = {
        "我的SKU":     p["sku"],
        "英文名":       p["name"],
        "中文名":       p["name_zh"],
        "马来文名":     p["name_ms"],
        "分类":         CAT_MAP.get(p.get("category_key", ""), ""),
        "售价FOB-USD":  p.get("price_fob_usd", 0),
    }

    # 链接字段
    img = make_link_field(p.get("image_url", ""))
    if img:
        fields["产品主图"] = img
    vid = make_link_field(p.get("video_url", ""))
    if vid:
        fields["默认视频"] = vid

    # 规格字段
    dim = specs.get("Dimensions", "") or specs.get("Size", "") or specs.get("Unit Size", "")
    if dim:
        fields["尺寸mm"] = dim

    # 净重：优先 Net Weight，其次 Gross Weight，其次 Weight / Total Net Weight
    nw = specs.get("Net Weight", "") or specs.get("Gross Weight", "") or specs.get("Weight", "") or specs.get("Total Net Weight", "")
    if nw:
        val = extract_number(nw)
        try:
            fields["净重kg"] = float(val)
        except (ValueError, TypeError):
            pass

    # 配重
    ws = specs.get("Weight Stack", "")
    if ws and any(c.isdigit() for c in str(ws)):
        val = extract_number(ws)
        try:
            fields["配重kg"] = float(val)
        except (ValueError, TypeError):
            pass

    # 肌群多选
    if target and target in TARGET_MAP:
        fields["主训练肌群"] = TARGET_MAP[target]

    return fields


def main():
    # Step 1: 拉取现有数据，删除测试记录
    print("=" * 50)
    print("  飞书产品主表数据迁移")
    print("=" * 50)
    
    raw = fetch_all()
    existing = raw["product"]
    
    if existing:
        old_ids = [r["record_id"] for r in existing]
        old_skus = [r["fields"].get("我的SKU", "?") for r in existing]
        print(f"\n  🗑️  即将删除 {len(old_ids)} 条旧数据: {old_skus}")
        batch_delete_records("product", old_ids)
    
    # Step 2: 转换 63 条产品
    records = []
    for p in PRODUCTS:
        fields = convert_product(p)
        records.append({"fields": fields})
    
    print(f"\n  📝 准备写入 {len(records)} 条产品...")
    
    # Step 3: 批量写入
    created_ids = batch_create_records("product", records)
    
    print(f"\n  ✅ 完成! 成功写入 {len(created_ids)} 条产品到飞书产品主表")
    print("=" * 50)


if __name__ == "__main__":
    main()
