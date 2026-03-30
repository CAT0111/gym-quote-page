import os

with open('build/admin_server.py', 'r', encoding='utf-8') as f:
    as_content = f.read()

# 1. 列表接口补充读取
old_rate = '"module_8": f.get("⑧安全系数", ""),\n                "updated_at": f.get("更新时间", ""), '
new_rate = '"module_8": f.get("⑧安全系数", ""),\n                "valid_days": f.get("有效天数", 7),\n                "updated_at": f.get("更新时间", ""),'
if '"valid_days": f.get("有效天数"' not in as_content:
    as_content = as_content.replace(old_rate, new_rate)

# 2. 写入接口补充保存
old_update = '"⑧安全系数": float(data.get("module_8", 1.15)),\n            "更新时间": now_str,'
new_update = '"⑧安全系数": float(data.get("module_8", 1.15)),\n            "有效天数": int(data.get("valid_days", 7)),\n            "更新时间": now_str,'
if '"有效天数": int(data.get("valid_days"' not in as_content:
    as_content = as_content.replace(old_update, new_update)

# 3. 测算接口补充动态过期判断
old_calc = """        if updated_at:
            try:
                from datetime import datetime, timedelta
                dt = datetime.strptime(updated_at, "%Y-%m-%d %H:%M")
                is_expired = (datetime.now() - dt).days > 7
            except:"""
new_calc = """        if updated_at:
            try:
                from datetime import datetime, timedelta
                dt = datetime.strptime(updated_at, "%Y-%m-%d %H:%M")
                valid_days = int(_num(logistics_fields.get("有效天数"), default=7))
                is_expired = (datetime.now() - dt).days > valid_days
            except:"""
if 'valid_days = int(_num(logistics_fields' not in as_content:
    as_content = as_content.replace(old_calc, new_calc)

with open('build/admin_server.py', 'w', encoding='utf-8') as f:
    f.write(as_content)

print("✅ 后端『有效天数』逻辑已挂载！")
