"""
setup_media_task_table.py — 一次性脚本：在飞书多维表格中创建「素材任务表」
用法: python3 build/setup_media_task_table.py

执行后会输出新表的 table_id，需要手动添加到 build/.env 中：
  FEISHU_TBL_MEDIA_TASK=tblXXXXXX
"""
import json, urllib.request, sys
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BUILD_DIR))
from feishu_client import get_token, APP_TOKEN, BASE_URL, TBL

def create_table(name, fields):
    """
    在多维表格中新建一张数据表
    name: 表名
    fields: [{"field_name": "xxx", "type": 1, ...}, ...]
    返回: table_id
    """
    token = get_token()
    url = f"{BASE_URL}/bitable/v1/apps/{APP_TOKEN}/tables"
    payload = {
        "table": {
            "name": name,
            "default_view_name": "全部任务",
            "fields": fields,
        }
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method="POST",
          headers={"Authorization": f"Bearer {token}",
                   "Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    if result.get("code") != 0:
        raise RuntimeError(f"建表失败: {result}")
    table_id = result["data"]["table_id"]
    return table_id

def main():
    print("=" * 50)
    print("  创建飞书「素材任务表 T_Media_Task」")
    print("=" * 50)

    # 飞书字段类型编号:
    # 1=多行文本, 2=数字, 3=单选, 4=多选, 7=复选框, 5=日期, 15=超链接, 21=关联
    # 单选 type=3 需要 property.options
    # 关联 type=21 需要 property.table_id

    fields = [
        {
            "field_name": "任务批次",
            "type": 1,  # 文本
        },
        {
            "field_name": "关联SKU",
            "type": 21,  # 关联
            "property": {
                "table_id": TBL["product"],
                "multiple": False,
            }
        },
        {
            "field_name": "素材类型",
            "type": 3,  # 单选
            "property": {
                "options": [
                    {"name": "产品主图"},
                    {"name": "试机视频"},
                    {"name": "细节特写"},
                    {"name": "场景图"},
                ]
            }
        },
        {
            "field_name": "状态",
            "type": 3,  # 单选
            "property": {
                "options": [
                    {"name": "待拍", "color": 0},
                    {"name": "已拍", "color": 1},
                    {"name": "剪辑中", "color": 2},
                    {"name": "待审核", "color": 3},
                    {"name": "已完成", "color": 4},
                    {"name": "需补拍", "color": 5},
                ]
            }
        },
        {
            "field_name": "拍摄人",
            "type": 1,  # 文本
        },
        {
            "field_name": "拍摄备注",
            "type": 1,  # 文本
        },
        {
            "field_name": "剪辑师",
            "type": 1,  # 文本
        },
        {
            "field_name": "成品链接",
            "type": 15,  # 超链接
        },
        {
            "field_name": "回写目标",
            "type": 3,  # 单选
            "property": {
                "options": [
                    {"name": "产品主图"},
                    {"name": "默认视频"},
                ]
            }
        },
        {
            "field_name": "完成时间",
            "type": 5,  # 日期
        },
    ]

    table_id = create_table("素材任务表", fields)

    print(f"\n  ✅ 建表成功！")
    print(f"  table_id: {table_id}")
    print(f"\n  👉 请将以下内容添加到 build/.env 文件末尾：")
    print(f"  FEISHU_TBL_MEDIA_TASK={table_id}")
    print(f"\n  👉 然后在 feishu_client.py 的 TBL 字典中添加：")
    print(f'  "media_task": os.environ["FEISHU_TBL_MEDIA_TASK"],')

if __name__ == "__main__":
    main()
