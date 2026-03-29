"""
project_map.py — 项目结构快照生成器
用途：每次新会话前跑一次，生成 PROJECT_MAP.md 粘贴给 AI
扫描：本地文件结构 + 飞书表字段定义
"""
import os
import sys
import json
import urllib.request
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ── 复用 feishu_client 的认证 ──────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))
from feishu_client import get_token, APP_TOKEN, TBL, BASE_URL

# ── 配置 ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "PROJECT_MAP.md"

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", "backups",
    ".cloudflared", "venv", ".venv", "env", ".wrangler",
}
SKIP_FILES = {".DS_Store", "Thumbs.db"}
BINARY_EXTENSIONS = {
    ".glb", ".gz", ".tar", ".zip", ".png", ".jpg", ".jpeg",
    ".gif", ".mp4", ".webm", ".ico", ".woff", ".woff2",
}

# 当一个目录下同类文件超过此数量时，合并显示
COLLAPSE_THRESHOLD = 5

ROUTE_FILES = {"admin_server.py"}


# ── 本地扫描 ──────────────────────────────────────────
def scan_local():
    tree_lines = []
    key_files = {}

    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in sorted(dirs) if d not in SKIP_DIRS]
        rel_root = Path(root).relative_to(PROJECT_ROOT)
        depth = len(rel_root.parts)

        if depth > 0:
            tree_lines.append(f"{'  ' * (depth - 1)}{rel_root.name}/")

        # 按扩展名分组，决定是否合并
        by_ext = defaultdict(list)
        for fname in sorted(files):
            if fname in SKIP_FILES:
                continue
            by_ext[Path(fname).suffix.lower()].append(fname)

        indent = "  " * depth
        shown_files = set()

        for ext, fnames in by_ext.items():
            # 同一目录下同一扩展名文件过多 → 合并成一行
            if len(fnames) >= COLLAPSE_THRESHOLD and ext in (".html", ".jpg", ".jpeg", ".png", ".json"):
                # 取最早和最晚修改时间
                mtimes = []
                total_size = 0
                for fn in fnames:
                    fp = Path(root) / fn
                    try:
                        s = fp.stat()
                        mtimes.append(s.st_mtime)
                        total_size += s.st_size
                    except OSError:
                        pass
                latest = datetime.fromtimestamp(max(mtimes)).strftime("%m-%d %H:%M") if mtimes else "?"
                if ext in BINARY_EXTENSIONS:
                    size_str = f"共{total_size / 1024 / 1024:.1f}MB" if total_size > 1024*1024 else f"共{total_size / 1024:.0f}KB"
                    tree_lines.append(f"{indent}({len(fnames)}个 {ext} 文件, {size_str}, 最新:{latest})")
                else:
                    tree_lines.append(f"{indent}({len(fnames)}个 {ext} 文件, 最新:{latest})")
                shown_files.update(fnames)
                continue

        # 逐一显示未被合并的文件
        for fname in sorted(files):
            if fname in SKIP_FILES or fname in shown_files:
                continue
            fpath = Path(root) / fname
            suffix = fpath.suffix.lower()
            try:
                stat = fpath.stat()
                size = stat.st_size
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%m-%d %H:%M")
            except OSError:
                size = 0
                mtime = "?"

            if suffix in BINARY_EXTENSIONS:
                sz = f"{size / 1024 / 1024:.1f}MB" if size > 1024*1024 else f"{size / 1024:.0f}KB"
                tree_lines.append(f"{indent}{fname}  ({sz}, {mtime})")
            else:
                try:
                    lc = len(fpath.read_text(encoding="utf-8", errors="ignore").splitlines())
                except Exception:
                    lc = 0
                tree_lines.append(f"{indent}{fname}  ({lc}行, {mtime})")

            if fname in ROUTE_FILES:
                key_files[str(fpath.relative_to(PROJECT_ROOT))] = _extract_routes(fpath)

    return tree_lines, key_files


def _extract_routes(fpath):
    routes = []
    try:
        for line in fpath.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("@app.route(") or line.startswith("@app.get(") or line.startswith("@app.post("):
                routes.append(line)
    except Exception:
        pass
    return routes


# ── 飞书字段扫描 ─────────────────────────────────────
FIELD_TYPE_NAMES = {
    1: "Text", 2: "Number", 3: "SingleSelect", 4: "MultiSelect",
    5: "DateTime", 7: "Checkbox", 11: "Person", 13: "Phone",
    15: "Url", 17: "Attachment", 18: "Link", 19: "Lookup",
    20: "Formula", 21: "DuplexLink", 22: "Location",
    23: "GroupChat", 1001: "CreatedTime", 1002: "ModifiedTime",
    1003: "CreatedBy", 1004: "ModifiedBy", 1005: "AutoNumber",
}


def fetch_table_fields(table_key):
    token = get_token()
    table_id = TBL[table_key]
    url = (f"{BASE_URL}/bitable/v1/apps/{APP_TOKEN}"
           f"/tables/{table_id}/fields?page_size=100")
    req = urllib.request.Request(url,
          headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
        if result.get("code") != 0:
            return None, f"API错误: {result.get('msg', 'unknown')}"
        return result["data"].get("items", []), None
    except Exception as e:
        return None, str(e)


def format_field_info(field):
    name = field.get("field_name", "?")
    ftype = field.get("type", 0)
    type_name = FIELD_TYPE_NAMES.get(ftype, f"Type_{ftype}")
    options_str = ""
    prop = field.get("property", {})
    if prop and isinstance(prop, dict):
        options = prop.get("options", [])
        if options:
            names = [o.get("name", "?") for o in options[:15]]
            if len(options) > 15:
                names.append(f"...共{len(options)}项")
            options_str = f" [{', '.join(names)}]"
    return f"  {name:<20s} {type_name}{options_str}"


def scan_feishu():
    sections = []
    for table_key, table_id in TBL.items():
        fields, err = fetch_table_fields(table_key)
        if err:
            sections.append(f"\n### {table_key} ({table_id}) — ⚠️ 拉取失败: {err}")
            continue
        # 统计记录数
        try:
            from feishu_client import fetch_all_records
            count = len(fetch_all_records(table_key))
        except Exception:
            count = "?"
        sections.append(f"\n### {table_key} ({table_id}) — {len(fields)}个字段, {count}条记录")
        for f in fields:
            sections.append(format_field_info(f))
    return sections


# ── 输出 ──────────────────────────────────────────────
def generate():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"# 项目结构快照 (自动生成于 {now})", ""]

    print("📂 扫描本地文件...")
    tree, key_files = scan_local()
    lines.append("## 本地文件结构")
    lines.append("```")
    lines.extend(tree)
    lines.append("```")
    lines.append("")

    if key_files:
        lines.append("## 关键文件摘要")
        for fpath, routes in key_files.items():
            lines.append(f"\n### {fpath} — {len(routes)}条路由")
            for r in routes:
                lines.append(f"  {r}")
        lines.append("")

    print("📡 扫描飞书表字段...")
    feishu_sections = scan_feishu()
    lines.append("## 飞书表结构 (实时拉取)")
    lines.extend(feishu_sections)
    lines.append("")

    content = "\n".join(lines)
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"\n✅ 已生成 {OUTPUT_FILE}")
    print(f"   共 {len(content)} 字符, {len(lines)} 行")
    print(f"\n💡 使用方法: cat {OUTPUT_FILE} | pbcopy")
    print("   然后粘贴到新会话中，配合基准提示词使用")


if __name__ == "__main__":
    generate()
