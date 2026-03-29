"""
admin_server.py — 业务员 Web 管理后台 v2
功能：套餐模板浏览 / 客户方案创建与编辑 / 产品总库筛选 / 页面生成
"""
import sys, json, subprocess, traceback, time
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
def index():
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

            # 计算 FOB 总价
            fob_total = 0
            for rid in linked_rids:
                prec = _cache["rid_to_product"].get(rid)
                if prec:
                    fob_total += _num(prec["fields"].get("售价FOB-USD", 0))

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
                "record_type": record_type,
                "fob_total_usd": round(fob_total),
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
            results.append({
                "record_id": rec["record_id"],
                "sku": sku,
                "name": name,
                "name_zh": name_zh,
                "name_ms": name_ms,
                "category": category,
                "category_zh": cat_def.get("label_zh", category),
                "muscles": muscles,
                "price_fob_usd": price,
                "image_url": image_url,
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
    入参: { "template_record_id": "recXXX", "client_name": "客户名" }
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

        # 生成客户方案 ID（中文可读）和 URL slug（英文干净）
        market = tpl_fields.get("目标市场", "")
        market_zh_map = {"MY": "马来西亚", "AU": "澳洲", "NZ": "新西兰", "CA": "加拿大"}
        market_zh = market_zh_map.get(market, market)
        area = tpl_fields.get("适用面积m²", "")
        area_str = f"{int(float(area))}m²" if area else ""
        plan_id = f"{market_zh}-{client_name}-{area_str}" if area_str else f"{market_zh}-{client_name}"

        # 构建新记录的 fields
        # 关联字段写入格式: 直接传 record_id 数组
        linked_rids = _extract_link_record_ids(tpl_fields.get("包含器材列表", []))

        new_fields = {
            "方案ID": plan_id,
            "客户名": client_name,
            "包含器材列表": linked_rids,
            "记录类型": "客户方案",
        }
        # 复制可选字段（数字字段必须转 float，飞书读出来可能是字符串）
        if tpl_fields.get("适用面积m²"):
            try:
                new_fields["适用面积m²"] = float(tpl_fields["适用面积m²"])
            except (TypeError, ValueError):
                pass
        if tpl_fields.get("目标市场"):
            new_fields["目标市场"] = tpl_fields["目标市场"]
        if tpl_fields.get("精准运费USD"):
            try:
                new_fields["精准运费USD"] = float(tpl_fields["精准运费USD"])
            except (TypeError, ValueError):
                pass

        new_rid = create_record("package", new_fields)

        # 局部更新缓存（不重新拉飞书）
        if _cache["raw"]:
            new_rec = {
                "record_id": new_rid,
                "fields": {
                    "方案ID": plan_id,
                    "客户名": client_name,
                    "包含器材列表": tpl_fields.get("包含器材列表", []),
                    "记录类型": "客户方案",
                    "目标市场": tpl_fields.get("目标市场", ""),
                    "适用面积m²": tpl_fields.get("适用面积m²", ""),
                }
            }
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

            products.append({
                "record_id": rid,
                "sku": sku,
                "name": pf.get("英文名", ""),
                "name_zh": pf.get("中文名", ""),
                "category": category,
                "category_zh": label_zh,
                "price_fob_usd": price,
                "image_url": _extract_url(pf.get("产品主图", "")),
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
            "fob_total_usd": round(fob_total),
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
if __name__ == "__main__":
    print("=" * 50)
    print("  ProvenLift 业务员管理后台 v2")
    print("  http://localhost:5050")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5050, debug=True)
