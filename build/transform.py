"""
transform.py — 飞书原始数据 → generator.py 所需的三大字典
"""
import json

FIELD_MAP_PRODUCT = {
    "我的SKU":       "sku", "分类":          "category", "英文名":        "name", "中文名":        "name_zh", "马来文名":      "name_ms",
    "采购价RMB":     "cost_rmb", "利润率":        "margin", "交期":          "lead_time", "产品主图":      "image_url",
    "默认视频":      "video_url", "英文视频":      "video_url_en", "马来文视频":    "video_url_ms",
    "器械尺寸mm":    "dim_mm", "尺寸mm":        "dim_mm",  # 兼容改名前后
    "占地面积m²":    "area_m2", "净重kg":        "net_weight_kg",
    "配重kg":        "weight_stack_kg", "主训练肌群":    "muscle_group", "准入市场认证":  "certifications",
    "澳洲专属卖点":  "selling_points_au", "马来专属卖点":  "selling_points_my",
    "毛重kg":        "gross_weight_kg", "包装尺寸mm":    "packing_mm", "详细参数JSON":  "extra_specs_json",
}

FIELD_MAP_PACKAGE = {
    "方案ID": "plan_id", "客户名": "client_name", "包含器材列表": "product_list", "适用面积m²": "area_m2",
    "精准运费USD": "override_freight_usd", "目标市场": "market", "记录类型": "record_type",
}

FIELD_MAP_QC = {"客户ID": "client_id", "对应SKU": "sku", "专属视频链接": "video_url"}
FIELD_MAP_LOGISTICS = {"国家": "country", "柜型": "container_type", "①起运段费用": "module_1", "②海运费": "module_2", "③目的港杂费": "module_3", "④综合税率": "module_4", "⑤尾程费": "module_5", "⑥安全系数": "module_6"}

MUSCLE_ZH_TO_EN = {"胸部": "Chest", "背部": "Back", "腿部": "Legs", "臂部": "Arms", "肩部": "Shoulders", "核心": "Core"}

CATEGORY_DEFS = {
    "SC": {"key": "sel", "label": "Pin-Loaded", "label_zh": "固定力量", "label_ms": "Beban Pin", "title": "Pin-Loaded Machines", "title_zh": "固定力量器械", "title_ms": "Mesin Beban Pin"},
    "固定力量": {"key": "sel", "label": "Pin-Loaded", "label_zh": "固定力量", "label_ms": "Beban Pin", "title": "Pin-Loaded Machines", "title_zh": "固定力量器械", "title_ms": "Mesin Beban Pin"},
    "PL": {"key": "pl", "label": "Plate Loaded", "label_zh": "挂片式", "label_ms": "Beban Plat", "title": "Plate-Loaded Machines", "title_zh": "挂片式器械", "title_ms": "Mesin Beban Plat"},
    "挂片式": {"key": "pl", "label": "Plate Loaded", "label_zh": "挂片式", "label_ms": "Beban Plat", "title": "Plate-Loaded Machines", "title_zh": "挂片式器械", "title_ms": "Mesin Beban Plat"},
    "FM": {"key": "rf", "label": "Racks", "label_zh": "力量架", "label_ms": "Rak & Rangka", "title": "Racks & Frames", "title_zh": "力量架", "title_ms": "Rak & Rangka"},
    "力量架": {"key": "rf", "label": "Racks", "label_zh": "力量架", "label_ms": "Rak & Rangka", "title": "Racks & Frames", "title_zh": "力量架", "title_ms": "Rak & Rangka"},
    "BN": {"key": "bn", "label": "Benches", "label_zh": "训练凳", "label_ms": "Bangku", "title": "Benches", "title_zh": "训练凳", "title_ms": "Bangku Latihan"},
    "训练凳": {"key": "bn", "label": "Benches", "label_zh": "训练凳", "label_ms": "Bangku", "title": "Benches", "title_zh": "训练凳", "title_ms": "Bangku Latihan"},
    "CA": {"key": "ca", "label": "Cardio", "label_zh": "有氧器械", "label_ms": "Kardio", "title": "Cardio Equipment", "title_zh": "有氧器械", "title_ms": "Peralatan Kardio"},
    "有氧器械": {"key": "ca", "label": "Cardio", "label_zh": "有氧器械", "label_ms": "Kardio", "title": "Cardio Equipment", "title_zh": "有氧器械", "title_ms": "Peralatan Kardio"},
    "CB": {"key": "fw", "label": "Free Weights", "label_zh": "自由重量", "label_ms": "Berat Bebas", "title": "Free Weights", "title_zh": "自由重量", "title_ms": "Berat Bebas"},
    "自由重量": {"key": "fw", "label": "Free Weights", "label_zh": "自由重量", "label_ms": "Berat Bebas", "title": "Free Weights", "title_zh": "自由重量", "title_ms": "Berat Bebas"},
    "FT": {"key": "ft", "label": "Functional", "label_zh": "功能训练", "label_ms": "Fungsional", "title": "Functional Training", "title_zh": "功能训练", "title_ms": "Latihan Fungsional"},
    "功能训练": {"key": "ft", "label": "Functional", "label_zh": "功能训练", "label_ms": "Fungsional", "title": "Functional Training", "title_zh": "功能训练", "title_ms": "Latihan Fungsional"},
    "AB": {"key": "ac", "label": "Accessories", "label_zh": "辅助配件", "label_ms": "Aksesori", "title": "Accessories", "title_zh": "辅助配件", "title_ms": "Aksesori"},
    "辅助配件": {"key": "ac", "label": "Accessories", "label_zh": "辅助配件", "label_ms": "Aksesori", "title": "Accessories", "title_zh": "辅助配件", "title_ms": "Aksesori"},
}

def _map_fields(raw_fields, field_map):
    return {en_key: raw_fields[zh_name] for zh_name, en_key in field_map.items() if zh_name in raw_fields}

def _num(val, default=0):
    if val is None or val == "": return default
    try: return float(val)
    except (TypeError, ValueError): return default

def _extract_url(val):
    if isinstance(val, dict): return val.get("link", "")
    if isinstance(val, str): return val
    return ""

def _extract_link_record_ids(val):
    ids = []
    if isinstance(val, list):
        for item in val:
            if isinstance(item, dict) and "record_ids" in item: ids.extend(item["record_ids"])
            elif isinstance(item, str): ids.append(item)
    return ids

def _parse_extra_specs(raw_json_str):
    """解析详细参数JSON字段，返回 dict"""
    if not raw_json_str or not isinstance(raw_json_str, str):
        return {}
    try:
        return json.loads(raw_json_str)
    except (json.JSONDecodeError, TypeError):
        return {}

def _calc_sell_rmb(cost_rmb, margin_raw):
    """采购价RMB × (1+利润率) = 售价RMB"""
    cost = _num(cost_rmb)
    if cost <= 0:
        return 0
    if margin_raw is not None and margin_raw != "":
        margin = _num(margin_raw, default=0.4)
    else:
        margin = 0.4
    return round(cost * (1 + margin), 2)

def build_data(raw, plan_id=None, client_id=None):
    # 汇率（后续可接实时API，此处硬编码兜底）
    USD_TO_CNY, USD_TO_MYR = 7.25, 4.45

    rid_to_product, sku_to_product = {}, {}
    for rec in raw["product"]:
        p = _map_fields(rec["fields"], FIELD_MAP_PRODUCT)
        p["_record_id"] = rec["record_id"]
        p["image_url"] = _extract_url(p.get("image_url", ""))
        p["video_url"] = _extract_url(p.get("video_url", ""))
        p["video_url_en"] = _extract_url(p.get("video_url_en", ""))
        p["video_url_ms"] = _extract_url(p.get("video_url_ms", ""))
        if not isinstance(p.get("muscle_group"), list): p["muscle_group"] = []
        if not isinstance(p.get("certifications"), list): p["certifications"] = []
        # 计算售价
        p["sell_rmb"] = _calc_sell_rmb(p.get("cost_rmb"), p.get("margin"))
        p["sell_usd"] = round(p["sell_rmb"] / USD_TO_CNY, 2) if p["sell_rmb"] else 0
        p["sell_myr"] = round(p["sell_rmb"] / USD_TO_CNY * USD_TO_MYR, 2) if p["sell_rmb"] else 0
        rid_to_product[rec["record_id"]] = p
        if p.get("sku"): sku_to_product[p["sku"]] = p

    target_pkg = None
    for rec in raw["package"]:
        pkg = _map_fields(rec["fields"], FIELD_MAP_PACKAGE)
        if plan_id and pkg.get("plan_id") == plan_id:
            target_pkg = pkg
            break
    if target_pkg is None and raw["package"]: target_pkg = _map_fields(raw["package"][0]["fields"], FIELD_MAP_PACKAGE)
    if target_pkg is None: raise ValueError("飞书中没有找到任何套餐方案")

    linked_rids = _extract_link_record_ids(target_pkg.get("product_list", []))
    pkg_products_raw = [rid_to_product[rid] for rid in linked_rids if rid in rid_to_product]

    if client_id:
        qc_map = { _map_fields(rec["fields"], FIELD_MAP_QC).get("sku"): _extract_url(_map_fields(rec["fields"], FIELD_MAP_QC).get("video_url", "")) for rec in raw["qc_media"] if _map_fields(rec["fields"], FIELD_MAP_QC).get("client_id") == client_id and _map_fields(rec["fields"], FIELD_MAP_QC).get("sku") }
        for p in pkg_products_raw:
            if p.get("sku") in qc_map:
                p["video_url"] = qc_map[p["sku"]]
                p["_qc_override"] = True

    market = target_pkg.get("market", "MY")
    logistics_for_market = next((_map_fields(rec["fields"], FIELD_MAP_LOGISTICS) for rec in raw["logistics"] if _map_fields(rec["fields"], FIELD_MAP_LOGISTICS).get("country") == market), None)

    # 售价总计（RMB 为基准）
    sell_total_rmb = sum(p.get("sell_rmb", 0) for p in pkg_products_raw)
    sell_total_usd = round(sell_total_rmb / USD_TO_CNY)
    sell_total_myr = round(sell_total_rmb / USD_TO_CNY * USD_TO_MYR)

    # DDP 物流计算（以 USD 为单位，与售价独立）
    override_freight_rmb = _num(target_pkg.get("override_freight_usd"), default=None)

    if override_freight_rmb:
        ddp_freight_usd = override_freight_rmb / USD_TO_CNY
        ddp_is_estimate = False
    elif logistics_for_market:
        m1, m2, m3, m4, m5, m6 = _num(logistics_for_market.get("module_1")), _num(logistics_for_market.get("module_2")), _num(logistics_for_market.get("module_3")), _num(logistics_for_market.get("module_4")), _num(logistics_for_market.get("module_5")), _num(logistics_for_market.get("module_6"), default=1.0)
        # DDP 6模块公式，这里用售价USD近似货值（用于税费计算）
        ddp_freight_usd = (m1 + m2 + m3 + (sell_total_usd + m2) * m4 + m5) * m6
        ddp_is_estimate = True
    else:
        ddp_freight_usd = 0
        ddp_is_estimate = True

    ddp_freight_cny = round(ddp_freight_usd * USD_TO_CNY)
    ddp_freight_myr = round(ddp_freight_usd * USD_TO_MYR)
    ddp_total_usd = sell_total_usd + round(ddp_freight_usd)
    ddp_total_cny = round(sell_total_rmb + ddp_freight_cny)
    ddp_total_myr = sell_total_myr + ddp_freight_myr

    area = int(_num(target_pkg.get("area_m2")))
    n_machines = len(pkg_products_raw)
    MARKET_PORT = {"MY": {"port": "Kuala Lumpur", "port_zh": "吉隆坡", "port_ms": "Kuala Lumpur"}, "AU": {"port": "Sydney", "port_zh": "悉尼", "port_ms": "Sydney"}, "NZ": {"port": "Auckland", "port_zh": "奥克兰", "port_ms": "Auckland"}, "CA": {"port": "Vancouver", "port_zh": "温哥华", "port_ms": "Vancouver"}}
    port_info = MARKET_PORT.get(market, MARKET_PORT["MY"])

    PACKAGE = {
        "id": target_pkg.get("plan_id", "PKG-001"),
        "name": f"{area}m² Commercial Gym · {n_machines} Machines", "name_zh": f"{area}㎡ 商用健身房 · {n_machines}台器械", "name_ms": f"Pakej Gim Komersial {area}m² · {n_machines} Mesin",
        "area_sqm": area, "total_machines": n_machines,
        "sell_total_rmb": round(sell_total_rmb), "sell_total_usd": sell_total_usd, "sell_total_myr": sell_total_myr,
        "fob_location": "Ningjin",
        "ddp_freight_usd": round(ddp_freight_usd), "ddp_freight_cny": ddp_freight_cny, "ddp_freight_myr": ddp_freight_myr,
        "ddp_port": port_info["port"], "ddp_port_zh": port_info["port_zh"], "ddp_port_ms": port_info["port_ms"],
        "ddp_quote_date_en": "Mar 2026", "ddp_quote_date_zh": "2026年3月", "ddp_quote_date_ms": "Mac 2026",
        "ddp_total_usd": ddp_total_usd, "ddp_total_cny": ddp_total_cny, "ddp_total_myr": ddp_total_myr,
        "ddp_is_estimate": ddp_is_estimate, "whatsapp_number": "8613800000000", "client_name": target_pkg.get("client_name", ""), "market": market,
    }

    seen_cats = []
    seen_keys = set()
    for p in pkg_products_raw:
        cat_code = p.get("category", "")
        if cat_code in CATEGORY_DEFS and cat_code not in seen_keys:
            seen_keys.add(cat_code)
            seen_cats.append(CATEGORY_DEFS[cat_code])
    CATEGORIES = seen_cats if seen_cats else list(CATEGORY_DEFS.values())

    PRODUCTS = []
    for p in pkg_products_raw:
        cat_code = p.get("category", "")
        cat_def = CATEGORY_DEFS.get(cat_code, CATEGORY_DEFS["固定力量"])

        # 组装 specs：先放飞书独立字段，再 merge 详细参数JSON
        specs = {}
        if p.get("dim_mm"): specs["Dimensions"] = p["dim_mm"]
        if p.get("packing_mm"): specs["Packing"] = p["packing_mm"]
        if p.get("lead_time"): specs["Lead Time"] = p["lead_time"]
        if _num(p.get("weight_stack_kg")) > 0: specs["Weight Stack"] = f"{_num(p.get('weight_stack_kg')):.0f} kg"
        if _num(p.get("net_weight_kg")) > 0: specs["Net Weight"] = f"{_num(p.get('net_weight_kg')):.0f} kg"
        if _num(p.get("gross_weight_kg")) > 0: specs["Gross Weight"] = f"{_num(p.get('gross_weight_kg')):.0f} kg"
        if _num(p.get("area_m2")) > 0: specs["Floor Area"] = f"{_num(p.get('area_m2'))} m²"
        if p.get("muscle_group"):
            specs["Target"] = " / ".join([MUSCLE_ZH_TO_EN.get(m, m) for m in p["muscle_group"]])

        # merge 详细参数JSON（不覆盖已有键）
        extra = _parse_extra_specs(p.get("extra_specs_json"))
        for k, v in extra.items():
            if k not in specs:
                specs[k] = v

        product = {
            "sku": p.get("sku", ""), "name": p.get("name", ""), "name_zh": p.get("name_zh", ""), "name_ms": p.get("name_ms", ""),
            "category_key": cat_def.get("key", "sel"),
            "sell_rmb": p.get("sell_rmb", 0), "sell_usd": p.get("sell_usd", 0), "sell_myr": p.get("sell_myr", 0),
            "qty": 1, "zone": "",
            "thumb_url": p.get("image_url", ""), "image_url": p.get("image_url", ""),
            "video_url": p.get("video_url", ""),
            "video_url_en": p.get("video_url_en", ""),
            "video_url_ms": p.get("video_url_ms", ""),
            "specs": specs,
        }
        if p.get("_qc_override"): product["qc_override"] = True
        PRODUCTS.append(product)

    return PACKAGE, CATEGORIES, PRODUCTS
