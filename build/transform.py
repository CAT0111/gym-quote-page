"""
transform.py — 飞书原始数据 → generator.py 所需的三大字典
输入: feishu_client.fetch_all() 返回的 4 张表原始记录
输出: PACKAGE, CATEGORIES, PRODUCTS（与 test_data.py 格式完全一致）
"""

# ================================================================
# 飞书中文字段名 → 代码内部 key 的映射
# ================================================================
FIELD_MAP_PRODUCT = {
    "我的SKU":       "sku",
    "分类":          "category",
    "英文名":        "name",
    "中文名":        "name_zh",
    "马来文名":      "name_ms",
    "售价FOB-USD":   "price_fob_usd",
    "采购价RMB":     "cost_rmb",
    "交期":          "lead_time",
    "产品主图":      "image_url",
    "默认视频":      "video_url",
    "尺寸mm":        "dim_mm",
    "占地面积m²":    "area_m2",
    "净重kg":        "net_weight_kg",
    "配重kg":        "weight_stack_kg",
    "主训练肌群":    "muscle_group",
    "准入市场认证":  "certifications",
    "澳洲专属卖点":  "selling_points_au",
    "马来专属卖点":  "selling_points_my",
}

FIELD_MAP_PACKAGE = {
    "方案ID":        "plan_id",
    "客户名":        "client_name",
    "包含器材列表":  "product_list",
    "适用面积m²":    "area_m2",
    "精准运费USD":   "override_freight_usd",
    "目标市场":      "market",
}

FIELD_MAP_QC = {
    "客户ID":        "client_id",
    "对应SKU":       "sku",
    "专属视频链接":  "video_url",
}

FIELD_MAP_LOGISTICS = {
    "国家":          "country",
    "柜型":          "container_type",
    "①起运段费用":   "module_1",
    "②海运费":       "module_2",
    "③目的港杂费":   "module_3",
    "④综合税率":     "module_4",
    "⑤尾程费":       "module_5",
    "⑥安全系数":     "module_6",
}

# ================================================================
# 分类代码 → 完整 category 字典（含多语言）
# 飞书 T_Product 的"分类"字段存的是这些代码
# ================================================================
CATEGORY_DEFS = {
    "SC": {
        "key": "sel",
        "label": "Pin-Loaded", "label_zh": "固定力量", "label_ms": "Beban Pin",
        "title": "Pin-Loaded Machines", "title_zh": "固定力量器械", "title_ms": "Mesin Beban Pin",
    },
    "PL": {
        "key": "pl",
        "label": "Plate Loaded", "label_zh": "挂片式", "label_ms": "Beban Plat",
        "title": "Plate-Loaded Machines", "title_zh": "挂片式器械", "title_ms": "Mesin Beban Plat",
    },
    "FM": {
        "key": "rf",
        "label": "Racks", "label_zh": "力量架", "label_ms": "Rak & Rangka",
        "title": "Racks & Frames", "title_zh": "力量架", "title_ms": "Rak & Rangka",
    },
    "BN": {
        "key": "bn",
        "label": "Benches", "label_zh": "训练凳", "label_ms": "Bangku",
        "title": "Benches", "title_zh": "训练凳", "title_ms": "Bangku Latihan",
    },
    "CA": {
        "key": "ca",
        "label": "Cardio", "label_zh": "有氧器械", "label_ms": "Kardio",
        "title": "Cardio Equipment", "title_zh": "有氧器械", "title_ms": "Peralatan Kardio",
    },
    "CB": {
        "key": "fw",
        "label": "Free Weights", "label_zh": "自由重量", "label_ms": "Berat Bebas",
        "title": "Free Weights", "title_zh": "自由重量", "title_ms": "Berat Bebas",
    },
    "FT": {
        "key": "ft",
        "label": "Functional", "label_zh": "功能训练", "label_ms": "Fungsional",
        "title": "Functional Training", "title_zh": "功能训练", "title_ms": "Latihan Fungsional",
    },
    "AB": {
        "key": "ac",
        "label": "Accessories", "label_zh": "辅助配件", "label_ms": "Aksesori",
        "title": "Accessories", "title_zh": "辅助配件", "title_ms": "Aksesori",
    },
}


# ================================================================
# 辅助函数
# ================================================================

def _map_fields(raw_fields, field_map):
    """把飞书中文字段名映射为英文 key"""
    mapped = {}
    for zh_name, en_key in field_map.items():
        if zh_name in raw_fields:
            mapped[en_key] = raw_fields[zh_name]
    return mapped


def _num(val, default=0):
    """安全地把飞书返回值转为 float，None/空字符串/非数字都返回 default"""
    if val is None or val == "":
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _extract_url(val):
    """飞书网址字段返回 {'link':'...','text':'...'} 或纯字符串，统一提取 URL"""
    if isinstance(val, dict):
        return val.get("link", "")
    if isinstance(val, str):
        return val
    return ""


def _extract_link_record_ids(val):
    """
    飞书关联字段返回格式:
    [{'record_ids': ['recXXX', 'recYYY'], 'table_id': 'tblZZZ', 'text': '...'}]
    提取所有 record_id
    """
    ids = []
    if isinstance(val, list):
        for item in val:
            if isinstance(item, dict) and "record_ids" in item:
                ids.extend(item["record_ids"])
            elif isinstance(item, str):
                ids.append(item)
    return ids


# ================================================================
# 核心构建函数
# ================================================================

def build_data(raw, plan_id=None, client_id=None):
    """
    主入口：把 feishu_client.fetch_all() 的原始数据转换为三大字典。

    参数:
        raw: feishu_client.fetch_all() 返回值
        plan_id: 指定套餐方案 ID（如 "PLAN001"），None 则取第一个
        client_id: 客户 ID（用于 QC 视频覆盖）

    返回: (PACKAGE, CATEGORIES, PRODUCTS)
    """

    # ------ 1. 构建 record_id → product 映射 ------
    rid_to_product = {}  # record_id → mapped product dict
    sku_to_product = {}  # sku → mapped product dict

    for rec in raw["product"]:
        p = _map_fields(rec["fields"], FIELD_MAP_PRODUCT)
        p["_record_id"] = rec["record_id"]

        # 处理网址字段
        p["image_url"] = _extract_url(p.get("image_url", ""))
        p["video_url"] = _extract_url(p.get("video_url", ""))

        # 多选字段已经是 list，兜底处理
        if not isinstance(p.get("muscle_group"), list):
            p["muscle_group"] = []
        if not isinstance(p.get("certifications"), list):
            p["certifications"] = []

        rid_to_product[rec["record_id"]] = p
        if p.get("sku"):
            sku_to_product[p["sku"]] = p

    # ------ 2. 找到目标套餐 ------
    target_pkg = None
    for rec in raw["package"]:
        pkg = _map_fields(rec["fields"], FIELD_MAP_PACKAGE)
        if plan_id and pkg.get("plan_id") == plan_id:
            target_pkg = pkg
            break
    if target_pkg is None and raw["package"]:
        target_pkg = _map_fields(raw["package"][0]["fields"], FIELD_MAP_PACKAGE)

    if target_pkg is None:
        raise ValueError("飞书中没有找到任何套餐方案")

    # ------ 3. 解析套餐包含的产品 ------
    link_val = target_pkg.get("product_list", [])
    linked_rids = _extract_link_record_ids(link_val)

    pkg_products_raw = []
    for rid in linked_rids:
        if rid in rid_to_product:
            pkg_products_raw.append(rid_to_product[rid])

    # ------ 4. QC 视频覆盖 ------
    if client_id:
        qc_map = {}  # sku → video_url
        for rec in raw["qc_media"]:
            qc = _map_fields(rec["fields"], FIELD_MAP_QC)
            if qc.get("client_id") == client_id and qc.get("sku"):
                qc_map[qc["sku"]] = _extract_url(qc.get("video_url", ""))
        for p in pkg_products_raw:
            if p.get("sku") in qc_map:
                p["video_url"] = qc_map[p["sku"]]
                p["_qc_override"] = True

    # ------ 5. 物流费率 ------
    market = target_pkg.get("market", "MY")
    logistics_for_market = None
    for rec in raw["logistics"]:
        lr = _map_fields(rec["fields"], FIELD_MAP_LOGISTICS)
        if lr.get("country") == market:
            logistics_for_market = lr
            break

    # ------ 6. 计算 DDP ------
    fob_total = sum(_num(p.get("price_fob_usd")) for p in pkg_products_raw)
    override_freight = _num(target_pkg.get("override_freight_usd"), default=None)

    if override_freight:
        ddp_freight = override_freight
        ddp_is_estimate = False
    elif logistics_for_market:
        m1 = _num(logistics_for_market.get("module_1"))
        m2 = _num(logistics_for_market.get("module_2"))
        m3 = _num(logistics_for_market.get("module_3"))
        m4 = _num(logistics_for_market.get("module_4"))
        m5 = _num(logistics_for_market.get("module_5"))
        m6 = _num(logistics_for_market.get("module_6"), default=1.0)
        tax = (fob_total + m2) * m4
        ddp_freight = (m1 + m2 + m3 + tax + m5) * m6
        ddp_is_estimate = True
    else:
        ddp_freight = 0
        ddp_is_estimate = True

    ddp_total = fob_total + ddp_freight

    # ------ 7. 组装 PACKAGE 字典 ------
    area = int(_num(target_pkg.get("area_m2")))
    n_machines = len(pkg_products_raw)

    MARKET_PORT = {
        "MY": {"port": "Kuala Lumpur", "port_zh": "吉隆坡", "port_ms": "Kuala Lumpur"},
        "AU": {"port": "Sydney",       "port_zh": "悉尼",   "port_ms": "Sydney"},
        "NZ": {"port": "Auckland",     "port_zh": "奥克兰", "port_ms": "Auckland"},
        "CA": {"port": "Vancouver",    "port_zh": "温哥华", "port_ms": "Vancouver"},
    }
    port_info = MARKET_PORT.get(market, MARKET_PORT["MY"])

    # 汇率（粗略，后续可从飞书拉取实时汇率）
    USD_TO_CNY = 7.25
    USD_TO_MYR = 4.45

    PACKAGE = {
        "id": target_pkg.get("plan_id", "PKG-001"),
        "name": f"{area}m² Commercial Gym · {n_machines} Machines",
        "name_zh": f"{area}㎡ 商用健身房 · {n_machines}台器械",
        "name_ms": f"Pakej Gim Komersial {area}m² · {n_machines} Mesin",
        "area_sqm": area,
        "total_machines": n_machines,
        "fob_total_usd": round(fob_total),
        "fob_total_cny": round(fob_total * USD_TO_CNY),
        "fob_total_myr": round(fob_total * USD_TO_MYR),
        "cif_port_klang_usd": None,
        "fob_location": "Ningjin",
        "ddp_freight_usd": round(ddp_freight),
        "ddp_freight_cny": round(ddp_freight * USD_TO_CNY),
        "ddp_freight_myr": round(ddp_freight * USD_TO_MYR),
        "ddp_port": port_info["port"],
        "ddp_port_zh": port_info["port_zh"],
        "ddp_port_ms": port_info["port_ms"],
        "ddp_quote_date_en": "Mar 2026",
        "ddp_quote_date_zh": "2026年3月",
        "ddp_quote_date_ms": "Mac 2026",
        "ddp_total_usd": round(ddp_total),
        "ddp_total_cny": round(ddp_total * USD_TO_CNY),
        "ddp_total_myr": round(ddp_total * USD_TO_MYR),
        "ddp_is_estimate": ddp_is_estimate,
        "whatsapp_number": "8613800000000",
        "client_name": target_pkg.get("client_name", ""),
        "market": market,
    }

    # ------ 8. 组装 CATEGORIES（只保留本套餐实际用到的分类）------
    seen_cats = []
    seen_keys = set()
    for p in pkg_products_raw:
        cat_code = p.get("category", "")
        if cat_code in CATEGORY_DEFS and cat_code not in seen_keys:
            seen_keys.add(cat_code)
            seen_cats.append(CATEGORY_DEFS[cat_code])

    CATEGORIES = seen_cats if seen_cats else list(CATEGORY_DEFS.values())

    # ------ 9. 组装 PRODUCTS（与 test_data.py 格式对齐）------
    PRODUCTS = []
    for p in pkg_products_raw:
        cat_code = p.get("category", "")
        cat_def = CATEGORY_DEFS.get(cat_code, {})

        # 构建 specs 字典
        specs = {}
        if p.get("dim_mm"):
            specs["Dimensions"] = p["dim_mm"]
        if p.get("weight_stack_kg"):
            specs["Weight Stack"] = f"{p['weight_stack_kg']} kg"
        if p.get("net_weight_kg"):
            specs["Net Weight"] = f"{p['net_weight_kg']} kg"
        if p.get("area_m2"):
            specs["Floor Area"] = f"{p['area_m2']} m²"
        if p.get("muscle_group"):
            specs["Target"] = " / ".join(p["muscle_group"])

        product = {
            "sku": p.get("sku", ""),
            "name": p.get("name", ""),
            "name_zh": p.get("name_zh", ""),
            "name_ms": p.get("name_ms", ""),
            "category_key": cat_def.get("key", "sel"),
            "price_fob_usd": _num(p.get("price_fob_usd")),
            "qty": 1,
            "zone": "",
            "thumb_url": p.get("image_url", ""),
            "image_url": p.get("image_url", ""),
            "video_url": p.get("video_url", ""),
            "specs": specs,
        }

        # QC 视频标记
        if p.get("_qc_override"):
            product["qc_override"] = True

        PRODUCTS.append(product)

    return PACKAGE, CATEGORIES, PRODUCTS


# ====== 单独运行时做格式验证 ======
if __name__ == "__main__":
    from feishu_client import fetch_all
    import json

    raw = fetch_all()
    PACKAGE, CATEGORIES, PRODUCTS = build_data(raw, plan_id="PLAN001", client_id="CLIENT001")

    print("=" * 50)
    print("PACKAGE:")
    print(json.dumps(PACKAGE, indent=2, ensure_ascii=False))
    print()
    print(f"CATEGORIES: {len(CATEGORIES)} 个")
    for c in CATEGORIES:
        print(f"  {c['key']}: {c['label']} / {c['label_zh']}")
    print()
    print(f"PRODUCTS: {len(PRODUCTS)} 个")
    for p in PRODUCTS:
        qc = " 🎬QC" if p.get("qc_override") else ""
        print(f"  {p['sku']}: {p['name']} (${p['price_fob_usd']}){qc}")
        print(f"    specs: {p['specs']}")
