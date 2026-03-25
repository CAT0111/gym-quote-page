#!/usr/bin/env python3
import sys, json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
TEMPLATE_DIR = BUILD_DIR / "templates"
OUTPUT_DIR = PROJECT_ROOT

sys.path.insert(0, str(BUILD_DIR))
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
    pkg_dir = OUTPUT_DIR / "pkg"
    pkg_dir.mkdir(exist_ok=True)
    pkg_id = package["id"].lower().replace("-", "").replace("pkg", "")
    output_path = pkg_dir / (pkg_id + ".html")
    output_path.write_text(html, encoding="utf-8")
    print(f"  Generated: pkg/{pkg_id}.html")
    print(f"  Preview:   http://localhost:8080/pkg/{pkg_id}.html")


def generate_index_redirect():
    pkg_id = "400a"
    lines = [
        "<!DOCTYPE html>",
        "<html><head><meta charset=utf-8>",
        "<meta http-equiv=refresh content=0;url=/pkg/" + pkg_id + ".html>",
        "<title>ProvenLift</title></head>",
        "<body><p>Redirecting...</p></body></html>",
    ]
    (OUTPUT_DIR / "index.html").write_text("\n".join(lines), encoding="utf-8")
    print("  Generated: index.html")


def main():
    print("=" * 50)
    print("ProvenLift Quote Page Generator v1")
    print("=" * 50)
    print(f"  Package: {PACKAGE['id']} ({len(PRODUCTS)} machines)")
    print()
    generate_package_page(PACKAGE, CATEGORIES, PRODUCTS)
    generate_index_redirect()
    print()
    print("Done! -> http://localhost:8080/pkg/400a.html")


if __name__ == "__main__":
    main()
