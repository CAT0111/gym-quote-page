"""
feishu_client.py — 飞书多维表格 API 客户端
职责：获取 token、拉取任意表全量记录（自动分页）
"""
import urllib.request
import json
import os
from pathlib import Path


def _load_env():
    """从 build/.env 读取配置，注入 os.environ"""
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        raise FileNotFoundError(f"找不到 {env_path}，请先创建 .env 文件")
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip())


_load_env()

BASE_URL = "https://open.feishu.cn/open-apis"
APP_ID = os.environ["FEISHU_APP_ID"]
APP_SECRET = os.environ["FEISHU_APP_SECRET"]
APP_TOKEN = os.environ["FEISHU_APP_TOKEN"]

TBL = {
    "product":   os.environ["FEISHU_TBL_PRODUCT"],
    "package":   os.environ["FEISHU_TBL_PACKAGE"],
    "qc_media":  os.environ["FEISHU_TBL_QC_MEDIA"],
    "logistics": os.environ["FEISHU_TBL_LOGISTICS"],
}

_token_cache = {"token": None}


def get_token():
    """获取 tenant_access_token（带简单缓存）"""
    if _token_cache["token"]:
        return _token_cache["token"]
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    body = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
    req = urllib.request.Request(url, data=body,
          headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    if result.get("code") != 0:
        raise RuntimeError(f"飞书 token 获取失败: {result}")
    _token_cache["token"] = result["tenant_access_token"]
    return _token_cache["token"]


def fetch_all_records(table_key):
    """
    拉取指定表的全量记录（自动分页，每页 500 条）
    table_key: "product" | "package" | "qc_media" | "logistics"
    返回: [{"record_id": "recXXX", "fields": {...}}, ...]
    """
    token = get_token()
    table_id = TBL[table_key]
    all_records = []
    page_token = None

    while True:
        url = (f"{BASE_URL}/bitable/v1/apps/{APP_TOKEN}"
               f"/tables/{table_id}/records?page_size=500")
        if page_token:
            url += f"&page_token={page_token}"

        req = urllib.request.Request(url,
              headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())

        if result.get("code") != 0:
            raise RuntimeError(f"飞书拉取 {table_key} 失败: {result}")

        items = result["data"].get("items", [])
        all_records.extend(items)

        if not result["data"].get("has_more", False):
            break
        page_token = result["data"].get("page_token")

    return all_records


def fetch_all():
    """一次性拉取 4 张表，返回字典"""
    print("  📡 正在连接飞书 ...")
    data = {}
    for key in TBL:
        records = fetch_all_records(key)
        data[key] = records
        print(f"     ✅ {key}: {len(records)} 条")
    print()
    return data




def batch_create_records(table_key, records, batch_size=500):
    """
    批量创建记录
    table_key: "product" | "package" | "qc_media" | "logistics"
    records: [{"fields": {...}}, ...]
    返回: 创建成功的 record_id 列表
    """
    token = get_token()
    table_id = TBL[table_key]
    created_ids = []

    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        url = (f"{BASE_URL}/bitable/v1/apps/{APP_TOKEN}"
               f"/tables/{table_id}/records/batch_create")
        body = json.dumps({"records": batch}).encode()
        req = urllib.request.Request(url, data=body, method="POST",
              headers={"Authorization": f"Bearer {token}",
                       "Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
        if result.get("code") != 0:
            raise RuntimeError(f"飞书批量创建失败: {result}")
        for r in result["data"].get("records", []):
            created_ids.append(r["record_id"])
        print(f"     ✅ 批次 {i//batch_size+1}: 写入 {len(batch)} 条")

    return created_ids


def batch_delete_records(table_key, record_ids):
    """
    批量删除记录
    table_key: "product" | "package" | "qc_media" | "logistics"
    record_ids: ["recXXX", ...]
    """
    token = get_token()
    table_id = TBL[table_key]
    url = (f"{BASE_URL}/bitable/v1/apps/{APP_TOKEN}"
           f"/tables/{table_id}/records/batch_delete")
    body = json.dumps({"records": record_ids}).encode()
    req = urllib.request.Request(url, data=body, method="POST",
          headers={"Authorization": f"Bearer {token}",
                   "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    if result.get("code") != 0:
        raise RuntimeError(f"飞书批量删除失败: {result}")
    print(f"     🗑️  已删除 {len(record_ids)} 条记录")


# ====== 单独运行时做连通性测试 ======
if __name__ == "__main__":
    data = fetch_all()
    for key, records in data.items():
        print(f"\n{'='*40}")
        print(f"  {key} — {len(records)} 条")
        if records:
            print(f"  首条字段: {list(records[0]['fields'].keys())}")
