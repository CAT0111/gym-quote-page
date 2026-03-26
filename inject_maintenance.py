#!/usr/bin/env python3
"""
Inject maintenance data into test_data.py PRODUCTS list.
Strategy: text-level insertion — find each product dict's closing "},"
and insert "maintenance": {...} before it. Work backwards to avoid offset drift.
"""
import sys, os, re, shutil, textwrap

# ── paths ──
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "build", "data", "test_data.py")
BACKUP = DATA_FILE + ".bak"

# ── import maintenance data ──
sys.path.insert(0, BASE)
from maintenance_data import MAINTENANCE

# ── read original file ──
with open(DATA_FILE, "r", encoding="utf-8") as f:
    src = f.read()

# ── find all SKU positions and their product-dict closing positions ──
# Each product dict starts with {"sku":"XXX" and we need to find its matching }
# We track brace nesting from the opening { of that dict.

sku_pattern = re.compile(r'\{"sku"\s*:\s*"([A-Z]{2}-\d{3})"')

# Collect (sku, insert_position) tuples
# insert_position = index of the closing } of the product dict
insertions = []

for m in sku_pattern.finditer(src):
    sku = m.group(1)
    if sku not in MAINTENANCE:
        print(f"  SKIP: {sku} — no maintenance data")
        continue

    # Find the matching closing brace for this product dict
    start = m.start()  # position of the opening {
    depth = 0
    i = start
    while i < len(src):
        ch = src[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                # i is the position of the closing } of this product dict
                insertions.append((sku, i))
                break
        elif ch == '"':
            # skip over string contents to avoid counting { } inside strings
            i += 1
            while i < len(src) and src[i] != '"':
                if src[i] == '\\':
                    i += 1  # skip escaped char
                i += 1
        i += 1

print(f"Found {len(insertions)} products to inject (out of {len(MAINTENANCE)} maintenance entries)")

if not insertions:
    print("ERROR: No insertion points found!")
    sys.exit(1)

# ── helper: serialize a maintenance dict as Python source text ──
def py_repr_value(obj, indent=2):
    """Serialize a Python object to valid Python source code string."""
    sp = "    "
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = []
        for k, v in obj.items():
            items.append(f"{sp * indent}{py_repr_value(k)}: {py_repr_value(v, indent + 1)}")
        return "{\n" + ",\n".join(items) + f",\n{sp * (indent - 1)}}}"
    elif isinstance(obj, list):
        if not obj:
            return "[]"
        items = []
        for item in obj:
            items.append(f"{sp * indent}{py_repr_value(item, indent + 1)}")
        return "[\n" + ",\n".join(items) + f",\n{sp * (indent - 1)}]"
    elif isinstance(obj, str):
        # Use repr() for proper escaping of quotes and special chars
        return repr(obj)
    elif isinstance(obj, bool):
        return "True" if obj else "False"
    elif obj is None:
        return "None"
    elif isinstance(obj, (int, float)):
        return repr(obj)
    else:
        return repr(obj)

# ── backup original ──
shutil.copy2(DATA_FILE, BACKUP)
print(f"Backup saved: {BACKUP}")

# ── perform insertions (from back to front to preserve offsets) ──
insertions.sort(key=lambda x: x[1], reverse=True)

result = src
injected = 0

for sku, close_pos in insertions:
    maint_data = MAINTENANCE[sku]
    # Determine the indentation of the current product dict
    # Look backwards from close_pos to find the line start for context
    # The product dict fields use 5-space indent ("     " after the 4-space dict start)
    # We'll use a consistent 5-space indent for the maintenance field
    maint_text = py_repr_value(maint_data, indent=2)
    # Insert:  ,\n     "maintenance": { ... }
    insertion = f',\n     "maintenance": {maint_text}'
    # Insert just before the closing }
    result = result[:close_pos] + insertion + result[close_pos:]
    injected += 1

# ── write back ──
with open(DATA_FILE, "w", encoding="utf-8") as f:
    f.write(result)

print(f"\nInjected maintenance into {injected} products.")
print(f"Written updated {DATA_FILE}")
print("\nVerify with:")
print("  python3 -c \"import sys; sys.path.insert(0,'build/data'); import test_data as td; total=len(td.PRODUCTS); has_m=sum(1 for p in td.PRODUCTS if 'maintenance' in p); print(f'{has_m}/{total} products have maintenance')\"")
print("\nThen run:  python3 build/generator.py")
