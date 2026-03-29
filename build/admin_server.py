"""
admin_server.py — 业务员 Web 管理后台
功能：选择套餐方案 → 一键生成客户专属网页 → 复制链接
"""
import sys, json, subprocess, traceback
from pathlib import Path
from flask import Flask, render_template, jsonify, request

BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent

sys.path.insert(0, str(BUILD_DIR))
from feishu_client import fetch_all, TBL
from transform import build_data, _map_fields, _extract_link_record_ids, FIELD_MAP_PACKAGE

app = Flask(__name__,
            template_folder=str(BUILD_DIR / "admin_templates"),
            static_folder=str(PROJECT_ROOT / "static"))


@app.route("/")
def index():
    return render_template("admin.html")


@app.route("/api/plans")
def api_plans():
    """拉取所有套餐方案，返回给前端下拉菜单"""
    try:
        raw = fetch_all()
        plans = []
        # 构建 record_id → sku 映射
        rid_to_sku = {}
        for rec in raw["product"]:
            sku = rec["fields"].get("我的SKU", "")
            rid_to_sku[rec["record_id"]] = sku

        for rec in raw["package"]:
            pkg = _map_fields(rec["fields"], FIELD_MAP_PACKAGE)
            # 解析关联的产品 SKU
            link_val = pkg.get("product_list", [])
            linked_rids = _extract_link_record_ids(link_val)
            skus = [rid_to_sku.get(rid, rid) for rid in linked_rids]

            plans.append({
                "plan_id": pkg.get("plan_id", ""),
                "client_name": pkg.get("client_name", ""),
                "market": pkg.get("market", ""),
                "area_m2": pkg.get("area_m2", ""),
                "n_products": len(skus),
                "skus": skus,
                "has_override_freight": bool(pkg.get("override_freight_usd")),
            })
        return jsonify({"ok": True, "plans": plans})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


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

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            return jsonify({"ok": False, "error": result.stderr or result.stdout})

        # 从输出中提取生成的文件路径
        output = result.stdout
        preview_url = ""
        for line in output.splitlines():
            if "Preview:" in line:
                preview_url = line.split("Preview:")[-1].strip()
            elif "Generated: pkg/" in line:
                pkg_file = line.split("Generated:")[-1].strip()

        return jsonify({
            "ok": True,
            "output": output,
            "preview_url": preview_url,
            "pkg_file": pkg_file if 'pkg_file' in dir() else "",
        })
    except Exception as e:
        return jsonify({"ok": False, "error": traceback.format_exc()})


@app.route("/api/qc_clients")
def api_qc_clients():
    """拉取所有有 QC 视频的客户 ID 列表"""
    try:
        raw_qc = fetch_all()
        clients = set()
        for rec in raw_qc["qc_media"]:
            cid = rec["fields"].get("客户ID", "")
            if cid:
                clients.add(cid)
        return jsonify({"ok": True, "clients": sorted(clients)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


if __name__ == "__main__":
    print("=" * 50)
    print("  ProvenLift 业务员管理后台")
    print("  http://localhost:5050")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5050, debug=True)
