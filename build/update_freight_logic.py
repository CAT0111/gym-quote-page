import os

# ============== 1. 更新 transform.py ==============
with open('build/transform.py', 'r', encoding='utf-8') as f:
    tf_content = f.read()

# 替换字段映射
tf_content = tf_content.replace(
    '"①起运段费用": "module_1", "②海运费": "module_2", "③目的港杂费": "module_3", "④综合税率": "module_4", "⑤尾程费": "module_5", "⑥安全系数": "module_6"',
    '"①内陆运输": "module_1", "②起运港港杂": "module_2", "③海运费": "module_3", "④目的港杂费": "module_4", "⑤清关服务费": "module_5", "⑥综合税率": "module_6", "⑦尾程派送": "module_7", "⑧安全系数": "module_8"'
)

# 替换计算核心
old_tf_logic = """        m1, m2, m3, m4, m5, m6 = _num(logistics_for_market.get("module_1")), _num(logistics_for_market.get("module_2")), _num(logistics_for_market.get("module_3")), _num(logistics_for_market.get("module_4")), _num(logistics_for_market.get("module_5")), _num(logistics_for_market.get("module_6"), default=1.0)
        # DDP 6模块公式，这里用售价USD近似货值（用于税费计算）
        ddp_freight_usd = (m1 + m2 + m3 + (sell_total_usd + m2) * m4 + m5) * m6"""

new_tf_logic = """        m1, m2, m3, m4, m5, m6, m7, m8 = _num(logistics_for_market.get("module_1")), _num(logistics_for_market.get("module_2")), _num(logistics_for_market.get("module_3")), _num(logistics_for_market.get("module_4")), _num(logistics_for_market.get("module_5")), _num(logistics_for_market.get("module_6")), _num(logistics_for_market.get("module_7")), _num(logistics_for_market.get("module_8"), default=1.15)
        # DDP 8模块公式: CIF货值 = 机器总价RMB + 海运费
        cif_rmb = sell_total_rmb + m3
        tax_rmb = cif_rmb * m6
        ddp_freight_rmb = (m1 + m2 + m3 + m4 + m5 + tax_rmb + m7) * m8
        ddp_freight_usd = ddp_freight_rmb / USD_TO_CNY"""
tf_content = tf_content.replace(old_tf_logic, new_tf_logic)

# 替换给客户网页的地标展示字段
old_ports = 'MARKET_PORT = {"MY": {"port": "Kuala Lumpur", "port_zh": "吉隆坡", "port_ms": "Kuala Lumpur"}, "AU": {"port": "Sydney", "port_zh": "悉尼", "port_ms": "Sydney"}, "NZ": {"port": "Auckland", "port_zh": "奥克兰", "port_ms": "Auckland"}, "CA": {"port": "Vancouver", "port_zh": "温哥华", "port_ms": "Vancouver"}}'
new_ports = 'MARKET_PORT = {"MY": {"port": "Kuala Lumpur (near Twin Towers)", "port_zh": "吉隆坡（双子塔周边）", "port_ms": "Kuala Lumpur (berhampiran Menara Berkembar)"}, "AU": {"port": "Sydney CBD (near Opera House)", "port_zh": "悉尼市区（歌剧院周边）", "port_ms": "Sydney CBD"}, "NZ": {"port": "Auckland CBD (near Sky Tower)", "port_zh": "奥克兰市区（天空塔周边）", "port_ms": "Auckland CBD"}, "CA": {"port": "Toronto (near CN Tower)", "port_zh": "多伦多（CN塔周边）", "port_ms": "Toronto"}}'
tf_content = tf_content.replace(old_ports, new_ports)

with open('build/transform.py', 'w', encoding='utf-8') as f:
    f.write(tf_content)


# ============== 2. 更新 admin_server.py ==============
with open('build/admin_server.py', 'r', encoding='utf-8') as f:
    as_content = f.read()

# api_freight_rates 返回字段
as_content = as_content.replace(
    '"module_1": f.get("①起运段费用", ""),',
    '"module_1": f.get("①内陆运输", ""),\n                "module_2": f.get("②起运港港杂", ""),\n                "module_3": f.get("③海运费", ""),\n                "module_4": f.get("④目的港杂费", ""),\n                "module_5": f.get("⑤清关服务费", ""),\n                "module_6": f.get("⑥综合税率", ""),\n                "module_7": f.get("⑦尾程派送", ""),\n                "module_8": f.get("⑧安全系数", ""),')
as_content = as_content.replace('                "module_2": f.get("②海运费", ""),\n', '')
as_content = as_content.replace('                "module_3": f.get("③目的港杂费", ""),\n', '')
as_content = as_content.replace('                "module_4": f.get("④综合税率", ""),\n', '')
as_content = as_content.replace('                "module_5": f.get("⑤尾程费", ""),\n', '')
as_content = as_content.replace('                "module_6": f.get("⑥安全系数", ""),\n', '')

# api_freight_update 写字段
old_update = """            "①起运段费用": float(data.get("module_1", 0)),
            "②海运费": float(data.get("module_2", 0)),
            "③目的港杂费": float(data.get("module_3", 0)),
            "④综合税率": float(data.get("module_4", 0)),
            "⑤尾程费": float(data.get("module_5", 0)),
            "⑥安全系数": float(data.get("module_6", 1.15)),"""
new_update = """            "①内陆运输": float(data.get("module_1", 0)),
            "②起运港港杂": float(data.get("module_2", 0)),
            "③海运费": float(data.get("module_3", 0)),
            "④目的港杂费": float(data.get("module_4", 0)),
            "⑤清关服务费": float(data.get("module_5", 0)),
            "⑥综合税率": float(data.get("module_6", 0)),
            "⑦尾程派送": float(data.get("module_7", 0)),
            "⑧安全系数": float(data.get("module_8", 1.15)),"""
as_content = as_content.replace(old_update, new_update)

# api_freight_calculate 计算逻辑
old_calc = """        m1 = _num(logistics_fields.get("①起运段费用"))
        m2 = _num(logistics_fields.get("②海运费"))
        m3 = _num(logistics_fields.get("③目的港杂费"))
        m4 = _num(logistics_fields.get("④综合税率"))
        m5 = _num(logistics_fields.get("⑤尾程费"))
        m6 = _num(logistics_fields.get("⑥安全系数"), default=1.0)

        # 检查精准运费覆盖
        override_freight_rmb = _num(pkg.get("精准运费USD"), default=None)
        if override_freight_rmb:
            ddp_freight_usd = override_freight_rmb / USD_TO_CNY
            is_override = True
        else:
            subtotal = m1 + m2 + m3 + (sell_total_usd + m2) * m4 + m5
            ddp_freight_usd = subtotal * m6
            is_override = False"""

new_calc = """        m1 = _num(logistics_fields.get("①内陆运输"))
        m2 = _num(logistics_fields.get("②起运港港杂"))
        m3 = _num(logistics_fields.get("③海运费"))
        m4 = _num(logistics_fields.get("④目的港杂费"))
        m5 = _num(logistics_fields.get("⑤清关服务费"))
        m6 = _num(logistics_fields.get("⑥综合税率"))
        m7 = _num(logistics_fields.get("⑦尾程派送"))
        m8 = _num(logistics_fields.get("⑧安全系数"), default=1.15)

        # 检查精准运费覆盖
        override_freight_rmb = _num(pkg.get("精准运费USD"), default=None)
        if override_freight_rmb:
            ddp_freight_usd = override_freight_rmb / USD_TO_CNY
            is_override = True
        else:
            cif_rmb = sell_total_rmb + m3
            tax_rmb = cif_rmb * m6
            ddp_freight_rmb = (m1 + m2 + m3 + m4 + m5 + tax_rmb + m7) * m8
            ddp_freight_usd = ddp_freight_rmb / USD_TO_CNY
            is_override = False"""
as_content = as_content.replace(old_calc, new_calc)

old_ret = '                "m1": m1, "m2": m2, "m3": m3, "m4": m4, "m5": m5, "m6": m6,'
new_ret = '                "m1": m1, "m2": m2, "m3": m3, "m4": m4, "m5": m5, "m6": m6, "m7": m7, "m8": m8'
as_content = as_content.replace(old_ret, new_ret)

with open('build/admin_server.py', 'w', encoding='utf-8') as f:
    f.write(as_content)

print("✅ 后端路由与计算公式升级完成！")
