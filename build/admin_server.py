"""
admin_server.py — 业务员 Web 管理后台 v2
功能：套餐模板浏览 / 客户方案创建与编辑 / 产品总库筛选 / 页面生成
"""
import sys, json, subprocess, traceback, time, urllib.request
from pathlib import Path
from flask import Flask, render_template, jsonify, request

BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent

sys.path.insert(0, str(BUILD_DIR))
from feishu_client import (
    fetch_all, fetch_all_records, get_token,
    update_record, create_record,
    APP_TOKEN, TBL, BASE_URL
)
from transform import (
    build_data, _map_fields, _extract_link_record_ids, _extract_url, _num,
    FIELD_MAP_PACKAGE, FIELD_MAP_PRODUCT, CATEGORY_DEFS, MUSCLE_ZH_TO_EN
)

app = Flask(__name__,
            template_folder=str(BUILD_DIR / "admin_templates"),
            static_folder=str(PROJECT_ROOT / "static"))

# ============================================================
#  内存缓存：避免每次接口都拉飞书（可手动刷新）
# ============================================================
_cache = {
    "raw": None,
    "ts": 0,
    "rid_to_sku": {},
    "sku_to_rid": {},
    "rid_to_product": {},
}
CACHE_TTL = 120  # 秒

# 汇率缓存（以 CNY 为基准）
_fx_cache = {
    "rates": {
        "MYR": 0.5786, "AUD": 0.2101, "NZD": 0.2521,
        "CAD": 0.2002, "USD": 0.1445,
    },
    "ts": 0,
}
FX_TTL = 3600  # 汇率缓存 1 小时

# 市场代码 → 货币代码
MARKET_TO_CURRENCY = {
    "MY": "MYR", "AU": "AUD", "NZ": "NZD", "CA": "CAD", "": "USD",
}
CURRENCY_SYMBOLS = {
    "MYR": "RM", "AUD": "A$", "NZD": "NZ$", "CAD": "C$", "USD": "$",
}

def _get_fx_rates():
    """获取实时汇率（CNY为基准），失败则用缓存"""
    now = time.time()
    if _fx_cache["ts"] and (now - _fx_cache["ts"] < FX_TTL):
        return _fx_cache["rates"]
    try:
        req = urllib.request.Request(
            "https://open.er-api.com/v6/latest/CNY",
            headers={"User-Agent": "ProvenLift/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        if data.get("result") == "success":
            rates = data["rates"]
            _fx_cache["rates"] = {
                "MYR": rates.get("MYR", 0.5786),
                "AUD": rates.get("AUD", 0.2101),
                "NZD": rates.get("NZD", 0.2521),
                "CAD": rates.get("CAD", 0.2002),
                "USD": rates.get("USD", 0.1445),
            }
            _fx_cache["ts"] = now
            print(f"  💱 汇率已更新: {_fx_cache['rates']}")
    except Exception as e:
        print(f"  ⚠️ 汇率获取失败，使用缓存: {e}")
    return _fx_cache["rates"]

def _ensure_cache(force=False):
    """确保缓存有效，超时或强制时重新拉取"""
    now = time.time()
    if not force and _cache["raw"] and (now - _cache["ts"] < CACHE_TTL):
        return _cache["raw"]
    print("  🔄 刷新飞书数据缓存 ...")
    raw = fetch_all()
    _cache["raw"] = raw
    _cache["ts"] = now
    # 构建 record_id ↔ sku 双向映射
    rid_to_sku = {}
    sku_to_rid = {}
    rid_to_product = {}
    for rec in raw["product"]:
        sku = rec["fields"].get("我的SKU", "")
        rid = rec["record_id"]
        rid_to_sku[rid] = sku
        if sku:
            sku_to_rid[sku] = rid
        rid_to_product[rid] = rec
    _cache["rid_to_sku"] = rid_to_sku
    _cache["sku_to_rid"] = sku_to_rid
    _cache["rid_to_product"] = rid_to_product
    return raw


# ============================================================
#  页面路由
# ============================================================
@app.route("/")
def portal():
    return render_template("portal.html")


@app.route("/admin")
def admin_page():
    return render_template("admin.html")


# ============================================================
#  API: 方案列表（区分模板/客户方案）
# ============================================================
@app.route("/api/plans")
def api_plans():
    """拉取所有方案，按 record_type 区分"""
    try:
        raw = _ensure_cache()
        rid_to_sku = _cache["rid_to_sku"]
        templates = []
        client_plans = []

        for rec in raw["package"]:
            f = rec["fields"]
            pkg = _map_fields(f, FIELD_MAP_PACKAGE)
            record_type = f.get("记录类型", "")
            # 解析关联的产品 SKU
            link_val = pkg.get("product_list", [])
            linked_rids = _extract_link_record_ids(link_val)
            skus = [rid_to_sku.get(rid, rid) for rid in linked_rids]

            # 计算总价
            fob_total = 0
            sell_total_rmb = 0
            for rid in linked_rids:
                prec = _cache["rid_to_product"].get(rid)
                if prec:
                    fob_total += _num(prec["fields"].get("售价FOB-USD", 0))
                    c = _num(prec["fields"].get("采购价RMB", 0))
                    m = _num(prec["fields"].get("利润率", 0)) or 0.4
                    sell_total_rmb += round(c * (1 + m), 2) if c else 0

            # 按分类统计
            cat_counts = {}
            for rid in linked_rids:
                prec = _cache["rid_to_product"].get(rid)
                if prec:
                    cat_code = prec["fields"].get("分类", "")
                    cat_def = CATEGORY_DEFS.get(cat_code, {})
                    label = cat_def.get("label_zh", cat_code)
                    cat_counts[label] = cat_counts.get(label, 0) + 1

            item = {
                "record_id": rec["record_id"],
                "plan_id": pkg.get("plan_id", ""),
                "client_name": pkg.get("client_name", ""),
                "market": pkg.get("market", ""),
                "area_m2": pkg.get("area_m2", ""),
                "n_products": len(skus),
                "skus": skus,
                "linked_rids": linked_rids,
                "has_override_freight": bool(pkg.get("override_freight_usd")),
            "override_freight_usd": _num(pkg.get("override_freight_usd", 0)),
                "record_type": record_type,
                "fob_total_usd": round(fob_total),
                "sell_total_rmb": round(sell_total_rmb),
                "cat_counts": cat_counts,
            }
            if record_type == "客户方案":
                client_plans.append(item)
            else:
                templates.append(item)

        return jsonify({"ok": True, "templates": templates, "client_plans": client_plans})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  API: 产品总库（支持筛选）
# ============================================================
@app.route("/api/products")
def api_products():
    """
    产品全量列表，支持筛选参数：
      ?category=SC       按分类代码
      ?muscle=背部        按肌群（中文）
      ?keyword=深蹲       按中文名/SKU 模糊匹配
    """
    try:
        raw = _ensure_cache()
        cat_filter = request.args.get("category", "").strip()
        muscle_filter = request.args.get("muscle", "").strip()
        keyword = request.args.get("keyword", "").strip().lower()

        results = []
        for rec in raw["product"]:
            f = rec["fields"]
            sku = f.get("我的SKU", "")
            category = f.get("分类", "")
            name = f.get("英文名", "")
            name_zh = f.get("中文名", "")
            name_ms = f.get("马来文名", "")
            muscles = f.get("主训练肌群", [])
            if not isinstance(muscles, list):
                muscles = []
            price = _num(f.get("售价FOB-USD", 0))
            image_url = _extract_url(f.get("产品主图", ""))

            # 分类筛选
            if cat_filter and category != cat_filter:
                continue
            # 肌群筛选
            if muscle_filter and muscle_filter not in muscles:
                continue
            # 关键词（匹配中文名 + SKU）
            if keyword:
                search_text = (sku + " " + name_zh + " " + name).lower()
                if keyword not in search_text:
                    continue

            cat_def = CATEGORY_DEFS.get(category, {})
            cost_rmb = _num(f.get("采购价RMB", 0))
            margin = _num(f.get("利润率", 0)) or 0.4
            sell_rmb = round(cost_rmb * (1 + margin), 2) if cost_rmb else 0
            video_url = _extract_url(f.get("默认视频", ""))
            dimensions = f.get("尺寸mm", "")
            net_weight = _num(f.get("净重kg", 0))
            weight_stack = _num(f.get("配重kg", 0))
            area = _num(f.get("占地面积m²", 0))
            results.append({
                "record_id": rec["record_id"],
                "sku": sku,
                "name": name,
                "name_zh": name_zh,
                "name_ms": name_ms,
                "category": category,
                "category_zh": cat_def.get("label_zh", category),
                "muscles": muscles,
                "cost_rmb": cost_rmb,
                "margin": margin,
                "sell_rmb": sell_rmb,
                "price_fob_usd": price,
                "image_url": image_url,
                "video_url": video_url,
                "dimensions": dimensions,
                "net_weight": net_weight,
                "weight_stack": weight_stack,
                "area_m2": area,
            })

        return jsonify({"ok": True, "products": results, "total": len(results)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  API: 获取可用的筛选选项
# ============================================================
@app.route("/api/filter-options")
def api_filter_options():
    """返回所有分类和肌群选项，供前端构建筛选 UI"""
    try:
        raw = _ensure_cache()
        categories = set()
        muscles = set()
        for rec in raw["product"]:
            f = rec["fields"]
            cat = f.get("分类", "")
            if cat:
                categories.add(cat)
            mg = f.get("主训练肌群", [])
            if isinstance(mg, list):
                for m in mg:
                    muscles.add(m)

        cat_list = []
        for code in sorted(categories):
            cat_def = CATEGORY_DEFS.get(code, {})
            cat_list.append({
                "code": code,
                "label": cat_def.get("label", code),
                "label_zh": cat_def.get("label_zh", code),
            })

        return jsonify({
            "ok": True,
            "categories": cat_list,
            "muscles": sorted(muscles),
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  API: 从模板创建客户方案
# ============================================================
@app.route("/api/client-plan/create", methods=["POST"])
def api_create_client_plan():
    """
    从模板复制创建客户方案
    入参: {
        "template_record_id": "recXXX",
        "client_name": "客户名",
        "market": "MY",          # 可选，优先使用；不传则继承模板
        "area_m2": 400           # 可选，优先使用；不传则继承模板
    }
    """
    try:
        data = request.get_json()
        tpl_rid = data.get("template_record_id", "")
        client_name = data.get("client_name", "").strip()
        if not tpl_rid or not client_name:
            return jsonify({"ok": False, "error": "缺少 template_record_id 或 client_name"})

        raw = _ensure_cache()

        # 找到模板记录
        tpl_rec = None
        for rec in raw["package"]:
            if rec["record_id"] == tpl_rid:
                tpl_rec = rec
                break
        if not tpl_rec:
            return jsonify({"ok": False, "error": f"找不到模板 {tpl_rid}"})

        tpl_fields = tpl_rec["fields"]

        # ── 目标市场：优先前端传入，否则继承模板 ──
        market = data.get("market", "").strip()
        if not market:
            market = tpl_fields.get("目标市场", "")

        # ── 适用面积：优先前端传入，否则继承模板 ──
        area_raw = data.get("area_m2")
        if area_raw is not None and str(area_raw).strip():
            try:
                area = float(area_raw)
            except (TypeError, ValueError):
                area = None
        else:
            try:
                area = float(tpl_fields.get("适用面积m²", 0)) or None
            except (TypeError, ValueError):
                area = None

        # ── 生成方案 ID ──
        market_zh_map = {"MY": "马来西亚", "AU": "澳洲", "NZ": "新西兰", "CA": "加拿大"}
        market_zh = market_zh_map.get(market, market)
        area_str = f"{int(area)}m²" if area else ""
        plan_id = f"{market_zh}-{client_name}-{area_str}" if area_str else f"{market_zh}-{client_name}"

        # ── 构建新记录 fields ──
        linked_rids = _extract_link_record_ids(tpl_fields.get("包含器材列表", []))

        new_fields = {
            "方案ID": plan_id,
            "客户名": client_name,
            "包含器材列表": linked_rids,
            "记录类型": "客户方案",
        }
        if market:
            new_fields["目标市场"] = market
        if area:
            new_fields["适用面积m²"] = area
        # 精准运费从模板继承
        if tpl_fields.get("精准运费USD"):
            try:
                new_fields["精准运费USD"] = float(tpl_fields["精准运费USD"])
            except (TypeError, ValueError):
                pass

        new_rid = create_record("package", new_fields)

        # ── 局部更新缓存 ──
        if _cache["raw"]:
            new_rec = {
                "record_id": new_rid,
                "fields": {
                    "方案ID": plan_id,
                    "客户名": client_name,
                    "包含器材列表": tpl_fields.get("包含器材列表", []),
                    "记录类型": "客户方案",
                    "目标市场": market,
                    "适用面积m²": area or "",
                }
            }
            if tpl_fields.get("精准运费USD"):
                new_rec["fields"]["精准运费USD"] = tpl_fields.get("精准运费USD")
            _cache["raw"]["package"].append(new_rec)

        return jsonify({
            "ok": True,
            "record_id": new_rid,
            "plan_id": plan_id,
            "client_name": client_name,
            "n_products": len(linked_rids),
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  API: 更新客户方案基础信息（市场/面积/运费）
# ============================================================
@app.route("/api/client-plan/<record_id>/update-info", methods=["POST"])
def api_update_plan_info(record_id):
    """
    更新方案的基础信息字段
    入参: {
        "market": "AU",               # 可选
        "area_m2": 350,               # 可选
        "override_freight_usd": 5800  # 可选
    }
    任何字段传了就更新，不传则不动
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"ok": False, "error": "空请求"})

        raw = _ensure_cache()

        # 找到方案记录
        target = None
        for rec in raw["package"]:
            if rec["record_id"] == record_id:
                target = rec
                break
        if not target:
            return jsonify({"ok": False, "error": f"找不到方案 {record_id}"})

        update_fields = {}
        cache_updates = {}

        # 目标市场
        if "market" in data:
            val = data["market"].strip() if data["market"] else ""
            update_fields["目标市场"] = val
            cache_updates["目标市场"] = val

        # 适用面积
        if "area_m2" in data:
            try:
                val = float(data["area_m2"]) if data["area_m2"] else 0
                update_fields["适用面积m²"] = val
                cache_updates["适用面积m²"] = val
            except (TypeError, ValueError):
                return jsonify({"ok": False, "error": "面积必须为数字"})

        # 精准运费
        if "override_freight_usd" in data:
            raw_val = data["override_freight_usd"]
            if raw_val is None or str(raw_val).strip() == "":
                update_fields["精准运费USD"] = None
                cache_updates["精准运费USD"] = ""
            else:
                try:
                    val = float(raw_val)
                    update_fields["精准运费USD"] = val
                    cache_updates["精准运费USD"] = val
                except (TypeError, ValueError):
                    return jsonify({"ok": False, "error": "运费必须为数字"})

        if not update_fields:
            return jsonify({"ok": True, "msg": "无需更新"})

        # ── 如果市场或面积变了，重新生成方案 ID ──
        old_fields = target["fields"]
        new_market = cache_updates.get("目标市场", old_fields.get("目标市场", ""))
        new_area = cache_updates.get("适用面积m²", old_fields.get("适用面积m²", ""))
        client_name = old_fields.get("客户名", "")

        if "目标市场" in update_fields or "适用面积m²" in update_fields:
            market_zh_map = {"MY": "马来西亚", "AU": "澳洲", "NZ": "新西兰", "CA": "加拿大"}
            market_zh = market_zh_map.get(new_market, new_market)
            try:
                area_str = f"{int(float(new_area))}m²" if new_area else ""
            except (TypeError, ValueError):
                area_str = ""
            new_plan_id = f"{market_zh}-{client_name}-{area_str}" if area_str else f"{market_zh}-{client_name}"
            update_fields["方案ID"] = new_plan_id
            cache_updates["方案ID"] = new_plan_id

        # ── 写飞书 ──
        update_record("package", record_id, update_fields)

        # ── 局部更新缓存 ──
        if _cache["raw"]:
            for rec in _cache["raw"]["package"]:
                if rec["record_id"] == record_id:
                    rec["fields"].update(cache_updates)
                    break

        return jsonify({
            "ok": True,
            "msg": "已更新",
            "updated_fields": list(update_fields.keys()),
            "plan_id": update_fields.get("方案ID", old_fields.get("方案ID", "")),
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  API: 获取单个方案详情
# ============================================================
# ============================================================
#  API: 获取单个方案详情
# ============================================================
@app.route("/api/client-plan/<record_id>")
def api_client_plan_detail(record_id):
    """获取单个方案的完整信息，包括每个产品的详细数据"""
    try:
        raw = _ensure_cache()
        rid_to_sku = _cache["rid_to_sku"]

        # 找到方案记录
        target = None
        for rec in raw["package"]:
            if rec["record_id"] == record_id:
                target = rec
                break
        if not target:
            return jsonify({"ok": False, "error": f"找不到方案 {record_id}"})

        f = target["fields"]
        pkg = _map_fields(f, FIELD_MAP_PACKAGE)
        linked_rids = _extract_link_record_ids(pkg.get("product_list", []))

        # 获取每个产品的详细信息
        products = []
        fob_total = 0
        sell_total_rmb = 0
        cat_counts = {}
        for rid in linked_rids:
            prec = _cache["rid_to_product"].get(rid)
            if not prec:
                continue
            pf = prec["fields"]
            sku = pf.get("我的SKU", "")
            category = pf.get("分类", "")
            cat_def = CATEGORY_DEFS.get(category, {})
            price = _num(pf.get("售价FOB-USD", 0))
            fob_total += price

            label_zh = cat_def.get("label_zh", category)
            cat_counts[label_zh] = cat_counts.get(label_zh, 0) + 1

            cost_rmb = _num(pf.get("采购价RMB", 0))
            margin = _num(pf.get("利润率", 0)) or 0.4
            sell_rmb = round(cost_rmb * (1 + margin), 2) if cost_rmb else 0
            sell_total_rmb += sell_rmb
            products.append({
                "record_id": rid,
                "sku": sku,
                "name": pf.get("英文名", ""),
                "name_zh": pf.get("中文名", ""),
                "category": category,
                "category_zh": label_zh,
                "cost_rmb": cost_rmb,
                "margin": margin,
                "sell_rmb": sell_rmb,
                "price_fob_usd": price,
                "image_url": _extract_url(pf.get("产品主图", "")),
                "video_url": _extract_url(pf.get("默认视频", "")),
                "dimensions": pf.get("尺寸mm", ""),
                "net_weight": _num(pf.get("净重kg", 0)),
                "weight_stack": _num(pf.get("配重kg", 0)),
                "area_m2": _num(pf.get("占地面积m²", 0)),
                "muscles": pf.get("主训练肌群", []) if isinstance(pf.get("主训练肌群"), list) else [],
            })

        return jsonify({
            "ok": True,
            "record_id": record_id,
            "plan_id": pkg.get("plan_id", ""),
            "client_name": pkg.get("client_name", ""),
            "market": pkg.get("market", ""),
            "area_m2": pkg.get("area_m2", ""),
            "record_type": f.get("记录类型", ""),
            "has_override_freight": bool(pkg.get("override_freight_usd")),
            "override_freight_usd": _num(pkg.get("override_freight_usd", 0)),
            "fob_total_usd": round(fob_total),
            "sell_total_rmb": round(sell_total_rmb),
            "cat_counts": cat_counts,
            "n_products": len(products),
            "products": products,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  API: 方案添加 SKU
# ============================================================
@app.route("/api/client-plan/<record_id>/add-sku", methods=["POST"])
def api_add_sku(record_id):
    """
    向方案添加一个产品
    入参: { "product_record_id": "recXXX" }
    """
    try:
        data = request.get_json()
        product_rid = data.get("product_record_id", "")
        if not product_rid:
            return jsonify({"ok": False, "error": "缺少 product_record_id"})

        raw = _ensure_cache()

        # 找到方案记录，获取当前关联列表
        target = None
        for rec in raw["package"]:
            if rec["record_id"] == record_id:
                target = rec
                break
        if not target:
            return jsonify({"ok": False, "error": f"找不到方案 {record_id}"})

        current_rids = _extract_link_record_ids(
            target["fields"].get("包含器材列表", [])
        )

        # 防重复添加
        if product_rid in current_rids:
            sku = _cache["rid_to_sku"].get(product_rid, product_rid)
            return jsonify({"ok": True, "msg": f"{sku} 已在方案中", "skipped": True})

        # 追加并写回飞书
        new_rids = current_rids + [product_rid]
        update_record("package", record_id, {
            "包含器材列表": new_rids
        })

        # 局部更新缓存（把新的关联列表写回内存中的 package 记录）
        if _cache["raw"]:
            for rec in _cache["raw"]["package"]:
                if rec["record_id"] == record_id:
                    # 重建关联字段的读取格式
                    rec["fields"]["包含器材列表"] = [{
                        "record_ids": new_rids,
                        "table_id": TBL["product"],
                    }]
                    break

        sku = _cache["rid_to_sku"].get(product_rid, product_rid)
        return jsonify({
            "ok": True,
            "msg": f"已添加 {sku}",
            "n_products": len(new_rids),
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  API: 方案移除 SKU
# ============================================================
@app.route("/api/client-plan/<record_id>/remove-sku", methods=["POST"])
def api_remove_sku(record_id):
    """
    从方案移除一个产品
    入参: { "product_record_id": "recXXX" }
    """
    try:
        data = request.get_json()
        product_rid = data.get("product_record_id", "")
        if not product_rid:
            return jsonify({"ok": False, "error": "缺少 product_record_id"})

        raw = _ensure_cache()

        target = None
        for rec in raw["package"]:
            if rec["record_id"] == record_id:
                target = rec
                break
        if not target:
            return jsonify({"ok": False, "error": f"找不到方案 {record_id}"})

        current_rids = _extract_link_record_ids(
            target["fields"].get("包含器材列表", [])
        )

        if product_rid not in current_rids:
            sku = _cache["rid_to_sku"].get(product_rid, product_rid)
            return jsonify({"ok": True, "msg": f"{sku} 不在方案中", "skipped": True})

        new_rids = [r for r in current_rids if r != product_rid]
        update_record("package", record_id, {
            "包含器材列表": new_rids
        })

        # 局部更新缓存
        if _cache["raw"]:
            for rec in _cache["raw"]["package"]:
                if rec["record_id"] == record_id:
                    rec["fields"]["包含器材列表"] = [{
                        "record_ids": new_rids,
                        "table_id": TBL["product"],
                    }]
                    break

        sku = _cache["rid_to_sku"].get(product_rid, product_rid)
        return jsonify({
            "ok": True,
            "msg": f"已移除 {sku}",
            "n_products": len(new_rids),
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  API: 实时汇率
# ============================================================
@app.route("/api/exchange-rates")
def api_exchange_rates():
    """返回 CNY 为基准的汇率"""
    try:
        rates = _get_fx_rates()
        return jsonify({
            "ok": True,
            "base": "CNY",
            "rates": rates,
            "symbols": CURRENCY_SYMBOLS,
            "market_currency": MARKET_TO_CURRENCY,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  API: 刷新缓存
# ============================================================
@app.route("/api/refresh-cache", methods=["POST"])
def api_refresh_cache():
    """手动强制刷新飞书数据缓存"""
    try:
        _ensure_cache(force=True)
        return jsonify({"ok": True, "msg": "缓存已刷新"})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  API: 生成客户页面（保留原逻辑）
# ============================================================
@app.route("/api/generate", methods=["POST"])
def api_generate():
    """执行 generator.py 生成页面"""
    try:
        data = request.get_json()
        plan_id = data.get("plan_id", "")
        client_id = data.get("client_id", "")

        cmd = [sys.executable, str(BUILD_DIR / "generator.py")]
        if plan_id:
            cmd.append(plan_id)
        if client_id:
            cmd.append(client_id)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            return jsonify({"ok": False, "error": result.stderr or result.stdout})

        output = result.stdout
        preview_url = ""
        pkg_file = ""
        version = ""
        for line in output.splitlines():
            if "Preview:" in line:
                preview_url = line.split("Preview:")[-1].strip()
            elif "Generated: pkg/" in line:
                pkg_file = line.split("Generated:")[-1].strip()
            elif "Version:" in line:
                version = line.split("Version:")[-1].strip()

        return jsonify({
            "ok": True,
            "output": output,
            "preview_url": preview_url,
            "pkg_file": pkg_file,
            "version": version,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": traceback.format_exc()})


# ============================================================
#  API: QC 客户列表（保留原逻辑）
# ============================================================
@app.route("/api/qc_clients")
def api_qc_clients():
    """拉取所有有 QC 视频的客户 ID 列表"""
    try:
        raw = _ensure_cache()
        clients = set()
        for rec in raw["qc_media"]:
            cid = rec["fields"].get("客户ID", "")
            if cid:
                clients.add(cid)
        return jsonify({"ok": True, "clients": sorted(clients)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  启动
# ============================================================

# ============================================================
#  素材任务管理页面
# ============================================================
@app.route("/shoot")
def shoot_page():
    return render_template("shoot.html")


# ============================================================
#  API: 素材任务 — 创建任务批次
# ============================================================
@app.route("/api/shoot/create-batch", methods=["POST"])
def api_shoot_create_batch():
    """
    创建一批拍摄任务
    入参: {
        "batch_name": "2026-03-29-济南工厂",
        "product_record_ids": ["recXXX", "recYYY", ...],
        "media_type": "产品主图",        // 产品主图|试机视频|细节特写|场景图
        "write_target": "产品主图"       // 产品主图|默认视频
    }
    """
    try:
        data = request.get_json()
        batch_name = (data.get("batch_name") or "").strip()
        product_rids = data.get("product_record_ids", [])
        # 兼容旧版单选和新版多选
        media_types = data.get("media_types", [])
        if not media_types:
            single = data.get("media_type", "")
            if single:
                media_types = [single]
        write_target_single = data.get("write_target", "")

        if not batch_name:
            return jsonify({"ok": False, "error": "请输入任务批次名称"})
        if not product_rids:
            return jsonify({"ok": False, "error": "请选择至少一个产品"})
        if not media_types:
            return jsonify({"ok": False, "error": "请选择至少一种素材类型"})

        # 素材类型 → 回写目标 自动映射
        TYPE_TO_TARGET = {
            "产品主图": "产品主图",
            "场景图": "产品主图",
            "试机视频": "默认视频",
            "细节特写": "默认视频",
        }

        raw = _ensure_cache()
        rid_to_sku = _cache["rid_to_sku"]

        created = []
        for rid in product_rids:
            for mtype in media_types:
                wt = write_target_single or TYPE_TO_TARGET.get(mtype, "产品主图")
                fields = {
                    "任务批次": batch_name,
                    "关联SKU": [rid],
                    "素材类型": mtype,
                    "状态": "待拍",
                    "回写目标": wt,
                }
                new_rid = create_record("media_task", fields)
                sku = rid_to_sku.get(rid, rid)
                created.append({"record_id": new_rid, "sku": sku, "type": mtype})

        return jsonify({
            "ok": True,
            "msg": f"已创建 {len(created)} 条任务（{len(product_rids)} 产品 × {len(media_types)} 类型）",
            "batch_name": batch_name,
            "tasks": created,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  API: 素材任务 — 获取任务列表
# ============================================================
@app.route("/api/shoot/tasks")
def api_shoot_tasks():
    """
    获取素材任务列表
    可选参数:
      ?batch=批次名       按批次筛选
      ?status=待拍        按状态筛选
      ?view=shoot|edit|review|all  按视图筛选（快捷方式）
    """
    try:
        raw = _ensure_cache()
        rid_to_sku = _cache["rid_to_sku"]
        rid_to_product = _cache["rid_to_product"]

        # 拉取素材任务表
        from feishu_client import fetch_all_records
        task_records = fetch_all_records("media_task")

        batch_filter = request.args.get("batch", "").strip()
        status_filter = request.args.get("status", "").strip()
        view_filter = request.args.get("view", "").strip()

        # 视图快捷映射
        VIEW_STATUS_MAP = {
            "shoot": ["待拍", "需补拍"],
            "edit": ["已拍", "剪辑中"],
            "review": ["待审核"],
            "all": [],
        }
        allowed_statuses = VIEW_STATUS_MAP.get(view_filter, [])

        tasks = []
        batches = set()
        status_counts = {}

        for rec in task_records:
            f = rec["fields"]
            batch = f.get("任务批次", "")
            status = f.get("状态", "待拍")
            media_type = f.get("素材类型", "")
            shooter = f.get("拍摄人", "")
            note = f.get("拍摄备注", "")
            editor = f.get("剪辑师", "")
            write_target = f.get("回写目标", "")

            # 成品链接（超链接字段）
            result_link_raw = f.get("成品链接", "")
            result_link = _extract_url(result_link_raw)

            # 完成时间
            done_time = f.get("完成时间", "")

            # 关联SKU解析
            linked_rids = _extract_link_record_ids(f.get("关联SKU", []))
            sku = ""
            product_name = ""
            product_name_zh = ""
            product_image = ""
            product_rid = ""
            if linked_rids:
                product_rid = linked_rids[0]
                sku = rid_to_sku.get(product_rid, "")
                prec = rid_to_product.get(product_rid)
                if prec:
                    product_name = prec["fields"].get("英文名", "")
                    product_name_zh = prec["fields"].get("中文名", "")
                    product_image = _extract_url(prec["fields"].get("产品主图", ""))

            if batch:
                batches.add(batch)
            status_counts[status] = status_counts.get(status, 0) + 1

            # 筛选
            if batch_filter and batch != batch_filter:
                continue
            if status_filter and status != status_filter:
                continue
            if allowed_statuses and status not in allowed_statuses:
                continue

            tasks.append({
                "record_id": rec["record_id"],
                "batch": batch,
                "sku": sku,
                "product_rid": product_rid,
                "product_name": product_name,
                "product_name_zh": product_name_zh,
                "product_image": product_image,
                "media_type": media_type,
                "status": status,
                "shooter": shooter,
                "note": note,
                "editor": editor,
                "result_link": result_link,
                "write_target": write_target,
                "done_time": done_time,
            })

        # 按批次分组排序（最新批次在前），同批次内按SKU排序
        tasks.sort(key=lambda t: (t["batch"], t["sku"]))

        return jsonify({
            "ok": True,
            "tasks": tasks,
            "total": len(tasks),
            "batches": sorted(batches, reverse=True),
            "status_counts": status_counts,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  API: 素材任务 — 更新单条任务状态/字段
# ============================================================
@app.route("/api/shoot/task/<record_id>/update", methods=["POST"])
def api_shoot_task_update(record_id):
    """
    更新任务的字段
    入参（全部可选，传哪个更新哪个）: {
        "status": "已拍",
        "shooter": "小王",
        "note": "灯光需补拍",
        "editor": "张三",
        "result_link": "https://cdn.provenlift.com/xxx.mp4"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"ok": False, "error": "空请求"})

        update_fields = {}

        if "status" in data:
            update_fields["状态"] = data["status"]
            # 如果标记为已完成，自动记录完成时间
            if data["status"] == "已完成":
                import time as _time
                update_fields["完成时间"] = int(_time.time()) * 1000  # 飞书日期字段用毫秒时间戳

        if "shooter" in data:
            update_fields["拍摄人"] = data["shooter"]

        if "note" in data:
            update_fields["拍摄备注"] = data["note"]

        if "editor" in data:
            update_fields["剪辑师"] = data["editor"]

        if "result_link" in data:
            link = data["result_link"].strip()
            if link:
                update_fields["成品链接"] = {"link": link, "text": link}
            else:
                update_fields["成品链接"] = None

        if not update_fields:
            return jsonify({"ok": True, "msg": "无需更新"})

        update_record("media_task", record_id, update_fields)

        return jsonify({
            "ok": True,
            "msg": "已更新",
            "updated_fields": list(update_fields.keys()),
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  API: 素材任务 — 审核通过并回写产品主表
# ============================================================
@app.route("/api/shoot/task/<record_id>/approve", methods=["POST"])
def api_shoot_task_approve(record_id):
    """
    审核通过：将成品链接回写到产品主表对应字段，并将任务标记为已完成
    """
    try:
        from feishu_client import fetch_all_records

        # 拉取该任务记录
        task_records = fetch_all_records("media_task")
        target = None
        for rec in task_records:
            if rec["record_id"] == record_id:
                target = rec
                break
        if not target:
            return jsonify({"ok": False, "error": f"找不到任务 {record_id}"})

        f = target["fields"]
        result_link = _extract_url(f.get("成品链接", ""))
        write_target = f.get("回写目标", "")
        linked_rids = _extract_link_record_ids(f.get("关联SKU", []))

        if not result_link:
            return jsonify({"ok": False, "error": "该任务还没有成品链接"})
        if not linked_rids:
            return jsonify({"ok": False, "error": "该任务没有关联SKU"})
        if not write_target:
            return jsonify({"ok": False, "error": "该任务没有指定回写目标"})

        product_rid = linked_rids[0]

        # 映射回写目标 → 飞书字段名
        TARGET_FIELD_MAP = {
            "产品主图": "产品主图",
            "默认视频": "默认视频",
        }
        feishu_field = TARGET_FIELD_MAP.get(write_target)
        if not feishu_field:
            return jsonify({"ok": False, "error": f"未知的回写目标: {write_target}"})

        # 回写产品主表（网址字段格式）
        update_record("product", product_rid, {
            feishu_field: {"link": result_link, "text": result_link}
        })

        # 更新任务状态为已完成
        import time as _time
        update_record("media_task", record_id, {
            "状态": "已完成",
            "完成时间": int(_time.time()) * 1000,
        })

        # 刷新产品缓存中的对应字段
        if _cache["rid_to_product"].get(product_rid):
            _cache["rid_to_product"][product_rid]["fields"][feishu_field] = {
                "link": result_link, "text": result_link
            }

        sku = _cache["rid_to_sku"].get(product_rid, product_rid)
        return jsonify({
            "ok": True,
            "msg": f"已将 {result_link} 回写到 {sku} 的「{write_target}」字段，任务已完成",
            "sku": sku,
            "field": write_target,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})


# ============================================================
#  API: 素材任务 — 批量更新状态
# ============================================================
@app.route("/api/shoot/batch-update-status", methods=["POST"])
def api_shoot_batch_update():
    """
    批量更新任务状态
    入参: {
        "record_ids": ["recXXX", "recYYY"],
        "status": "已拍"
    }
    """
    try:
        data = request.get_json()
        record_ids = data.get("record_ids", [])
        status = data.get("status", "")
        if not record_ids or not status:
            return jsonify({"ok": False, "error": "缺少参数"})

        success = 0
        for rid in record_ids:
            try:
                fields = {"状态": status}
                if status == "已完成":
                    import time as _time
                    fields["完成时间"] = int(_time.time()) * 1000
                update_record("media_task", rid, fields)
                success += 1
            except Exception:
                traceback.print_exc()

        return jsonify({
            "ok": True,
            "msg": f"已更新 {success}/{len(record_ids)} 条",
            "success": success,
            "total": len(record_ids),
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)})

if __name__ == "__main__":
    print("=" * 50)
    print("  ProvenLift 业务员管理后台 v2")
    print("  http://localhost:5050")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5050, debug=True)
