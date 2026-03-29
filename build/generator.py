#!/usr/bin/env python3
import sys, json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
TEMPLATE_DIR = BUILD_DIR / "templates"
OUTPUT_DIR = PROJECT_ROOT

sys.path.insert(0, str(BUILD_DIR))

# ====== Phase 1: 飞书直连（替换 test_data.py）======
try:
    from feishu_client import fetch_all
    from transform import build_data
    _USE_FEISHU = True
except Exception as e:
    print(f"  ⚠️  飞书连接失败，回退到本地测试数据: {e}")
    _USE_FEISHU = False

if _USE_FEISHU:
    # 可通过命令行指定: python3 generator.py PLAN002 CLIENT002
    _plan_id = sys.argv[1] if len(sys.argv) > 1 else None
    _client_id = sys.argv[2] if len(sys.argv) > 2 else None
    raw = fetch_all()
    PACKAGE, CATEGORIES, PRODUCTS = build_data(raw, plan_id=_plan_id, client_id=_client_id)
else:
    from data.test_data import PACKAGE, CATEGORIES, PRODUCTS


def group_products_by_category(products, categories):
    grouped = {}
    for cat in categories:
        grouped[cat["key"]] = [p for p in products if p["category_key"] == cat["key"]]
    return grouped


def generate_package_page(package, categories, products):
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)
    env.filters["tojson"] = lambda x: json.dumps(x, ensure_ascii=False)
    template = env.get_template("base.html")
    grouped = group_products_by_category(products, categories)
    html = template.render(package=package, categories=categories, grouped_products=grouped)

    # 生成 URL-safe 的目录名：中文方案ID → 英文slug
    import re, unicodedata
    raw_id = package["id"]
    # 市场中文→英文代码
    _mkt = {"马来西亚":"my","澳洲":"au","新西兰":"nz","加拿大":"ca"}
    slug = raw_id.lower()
    for zh, en in _mkt.items():
        slug = slug.replace(zh, en)
    # 去掉 m²/㎡ 符号，保留数字
    slug = slug.replace("m²", "m").replace("㎡", "m")
    # 只保留字母数字和连字符
    slug = re.sub(r"[^a-z0-9\-]", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    pkg_id = slug if slug else raw_id.lower().replace("-", "").replace("pkg", "")
    plan_dir = OUTPUT_DIR / "pkg" / pkg_id
    plan_dir.mkdir(parents=True, exist_ok=True)

    # 自动递增版本号：扫描已有 v* 目录
    existing_versions = [
        int(d.name[1:]) for d in plan_dir.iterdir()
        if d.is_dir() and d.name.startswith("v") and d.name[1:].isdigit()
    ]
    next_ver = max(existing_versions, default=0) + 1

    # 写入版本目录
    ver_dir = plan_dir / f"v{next_ver}"
    ver_dir.mkdir(exist_ok=True)
    (ver_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"  Generated: pkg/{pkg_id}/v{next_ver}/index.html")

    # 写入 latest.html（客户固定链接，每次覆盖）
    (plan_dir / "latest.html").write_text(html, encoding="utf-8")
    print(f"  Updated:   pkg/{pkg_id}/latest.html")

    # 同时保留旧格式兼容（覆盖 pkg/{id}.html）
    compat_path = OUTPUT_DIR / "pkg" / (pkg_id + ".html")
    compat_path.write_text(html, encoding="utf-8")

    print(f"  Preview:   /pkg/{pkg_id}/latest.html")
    print(f"  Version:   v{next_ver}")


def generate_index_redirect():
    import re
    _mkt2 = {"马来西亚":"my","澳洲":"au","新西兰":"nz","加拿大":"ca"}
    _slug = PACKAGE["id"].lower()
    for zh, en in _mkt2.items():
        _slug = _slug.replace(zh, en)
    _slug = _slug.replace("m²", "m").replace("㎡", "m")
    _slug = re.sub(r"[^a-z0-9\-]", "-", _slug)
    _slug = re.sub(r"-+", "-", _slug).strip("-")
    pkg_id = _slug if _slug else PACKAGE["id"].lower().replace("-", "").replace("pkg", "")
    lines = [
        "<!DOCTYPE html>",
        "<html><head><meta charset=utf-8>",
        "<meta http-equiv=refresh content=0;url=/pkg/" + pkg_id + "/latest.html>",
        "<title>ProvenLift</title></head>",
        "<body><p>Redirecting...</p></body></html>",
    ]
    (OUTPUT_DIR / "index.html").write_text("\n".join(lines), encoding="utf-8")
    print("  Generated: index.html")


def main():
    print("=" * 50)
    print("ProvenLift Quote Page Generator v2 (Feishu)")
    print("=" * 50)
    print(f"  Package: {PACKAGE['id']} ({len(PRODUCTS)} machines)")
    if PACKAGE.get('client_name'):
        print(f"  Client:  {PACKAGE['client_name']}")
    print(f"  Market:  {PACKAGE.get('market', 'N/A')}")
    print(f"  Source:  {'飞书 API' if _USE_FEISHU else '本地 test_data.py'}")
    print()
    generate_package_page(PACKAGE, CATEGORIES, PRODUCTS)
    generate_index_redirect()
    print()
    print(f"Done! -> https://www.provenlift.com/pkg/{PACKAGE['id'].lower().replace('-','').replace('pkg','')}.html")


if __name__ == "__main__":
    main()
