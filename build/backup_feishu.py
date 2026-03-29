"""
backup_feishu.py — 飞书多维表格全量备份
用法: python3 build/backup_feishu.py
输出: backups/feishu/YYYY-MM-DD_HHMMSS.json（4张表全量数据）

可配合 cron 每天自动执行:
  crontab -e
  0 9 * * * cd /Users/你的用户名/Projects/gym-quote-page && /usr/bin/python3 build/backup_feishu.py >> backups/feishu/cron.log 2>&1
"""
import json, sys
from pathlib import Path
from datetime import datetime

BUILD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BUILD_DIR.parent
BACKUP_DIR = PROJECT_ROOT / "backups" / "feishu"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BUILD_DIR))
from feishu_client import fetch_all

def main():
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    print(f"[{ts}] 开始飞书全量备份 ...")

    raw = fetch_all()

    # 统计
    summary = {}
    for key, records in raw.items():
        summary[key] = len(records)

    # 保存
    out_path = BACKUP_DIR / f"{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "backup_time": ts,
            "summary": summary,
            "data": raw,
        }, f, ensure_ascii=False, indent=1)

    size_kb = out_path.stat().st_size / 1024
    print(f"  ✅ 备份完成: {out_path.name} ({size_kb:.0f} KB)")
    for k, v in summary.items():
        print(f"     {k}: {v} 条")

    # 自动清理：保留最近 60 个备份文件
    all_backups = sorted(BACKUP_DIR.glob("*.json"), key=lambda p: p.name)
    if len(all_backups) > 60:
        to_delete = all_backups[:-60]
        for f in to_delete:
            f.unlink()
            print(f"  🗑️  清理旧备份: {f.name}")

    print(f"  当前备份总数: {len(list(BACKUP_DIR.glob('*.json')))} 个")

if __name__ == "__main__":
    main()
