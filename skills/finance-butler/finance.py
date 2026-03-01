#!/usr/bin/env python3
"""家庭理财小管家 - 记账核心模块"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

LEDGER_PATH = Path(__file__).parent.parent.parent / "data" / "finance" / "ledger.json"

CATEGORIES = {
    "餐饮": {"emoji": "🍜", "keywords": ["吃饭", "午餐", "早餐", "晚餐", "外卖", "饮品", "咖啡", "奶茶", "火锅", "烧烤", "零食", "水果", "买菜", "食堂", "餐厅", "小吃", "夜宵", "饮料"]},
    "居住": {"emoji": "🏠", "keywords": ["房租", "水电", "物业", "维修", "燃气", "宽带", "网费"]},
    "交通": {"emoji": "🚗", "keywords": ["打车", "地铁", "公交", "加油", "停车", "高铁", "机票", "火车", "滴滴", "出租车", "骑车"]},
    "购物": {"emoji": "🛒", "keywords": ["淘宝", "京东", "拼多多", "衣服", "鞋", "日用品", "超市", "电子", "数码", "手机", "电脑"]},
    "娱乐": {"emoji": "🎮", "keywords": ["游戏", "电影", "订阅", "会员", "KTV", "旅游", "门票", "演出"]},
    "医疗": {"emoji": "💊", "keywords": ["看病", "药", "医院", "体检", "保险", "挂号"]},
    "教育": {"emoji": "📚", "keywords": ["课程", "书", "培训", "学费", "考试"]},
    "工作": {"emoji": "💼", "keywords": ["办公", "服务器", "域名", "工具", "软件", "云服务"]},
    "人情": {"emoji": "🎁", "keywords": ["红包", "礼物", "请客", "份子钱", "转账"]},
    "其他": {"emoji": "📦", "keywords": []},
}

def load_ledger():
    if LEDGER_PATH.exists():
        with open(LEDGER_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "1.0", "settings": {"currency": "CNY", "monthly_budget": 0, "category_budgets": {}, "auto_record": False}, "records": [], "income": []}

def save_ledger(data):
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def guess_category(desc):
    desc_lower = desc.lower()
    for cat, info in CATEGORIES.items():
        for kw in info["keywords"]:
            if kw in desc_lower:
                return cat
    return "其他"

def add_record(desc, amount, category=None, record_type="支出", date=None):
    ledger = load_ledger()
    if category is None:
        category = guess_category(desc)
    record = {
        "id": len(ledger["records"]) + 1,
        "date": date or datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "type": record_type,
        "category": category,
        "amount": float(amount),
        "desc": desc,
        "source": "manual"
    }
    if record_type == "收入":
        ledger["income"].append(record)
    else:
        ledger["records"].append(record)
    save_ledger(ledger)
    emoji = CATEGORIES.get(category, {}).get("emoji", "📦")
    return f"✅ 已记账：{emoji} {desc} ¥{amount} [{category}]"

def get_summary(period="month"):
    ledger = load_ledger()
    now = datetime.now()
    records = ledger["records"]
    
    if period == "month":
        prefix = now.strftime("%Y-%m")
        title = f"{now.year}年{now.month}月"
    elif period == "week":
        week_start = now - timedelta(days=now.weekday())
        prefix = None
        title = f"本周（{week_start.strftime('%m/%d')}起）"
    elif period == "today":
        prefix = now.strftime("%Y-%m-%d")
        title = "今日"
    else:
        prefix = period
        title = period

    filtered = []
    for r in records:
        if period == "week":
            rd = datetime.strptime(r["date"], "%Y-%m-%d")
            week_start = now - timedelta(days=now.weekday())
            if rd >= week_start.replace(hour=0, minute=0, second=0):
                filtered.append(r)
        elif r["date"].startswith(prefix):
            filtered.append(r)

    if not filtered:
        return f"📊 {title}暂无支出记录"

    total = sum(r["amount"] for r in filtered)
    by_cat = {}
    for r in filtered:
        cat = r["category"]
        by_cat[cat] = by_cat.get(cat, 0) + r["amount"]

    lines = [f"📊 {title}支出报告", f"💰 总支出：¥{total:.2f}", ""]
    sorted_cats = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
    for cat, amt in sorted_cats:
        emoji = CATEGORIES.get(cat, {}).get("emoji", "📦")
        pct = amt / total * 100
        lines.append(f"{emoji} {cat}：¥{amt:.2f}（{pct:.0f}%）")

    lines.append(f"\n📝 共 {len(filtered)} 笔记录")
    
    # Budget check
    settings = ledger.get("settings", {})
    budget = settings.get("monthly_budget", 0)
    if budget > 0 and period == "month":
        remaining = budget - total
        pct_used = total / budget * 100
        lines.append(f"\n💳 预算：¥{budget:.2f} | 已用 {pct_used:.0f}% | 剩余 ¥{remaining:.2f}")
        if pct_used >= 100:
            lines.append("⚠️ 已超支！")
        elif pct_used >= 80:
            lines.append("⚠️ 预算即将用完！")

    return "\n".join(lines)

def get_recent(n=10):
    ledger = load_ledger()
    records = ledger["records"][-n:]
    if not records:
        return "📝 暂无记录"
    lines = [f"📝 最近 {len(records)} 笔记录：", ""]
    for r in reversed(records):
        emoji = CATEGORIES.get(r["category"], {}).get("emoji", "📦")
        lines.append(f"{r['date']} {emoji} {r['desc']} ¥{r['amount']:.2f}")
    return "\n".join(lines)

def set_budget(amount, category=None):
    ledger = load_ledger()
    if category:
        ledger["settings"]["category_budgets"][category] = float(amount)
        save_ledger(ledger)
        return f"✅ 已设置 {category} 月预算：¥{amount}"
    else:
        ledger["settings"]["monthly_budget"] = float(amount)
        save_ledger(ledger)
        return f"✅ 已设置月度总预算：¥{amount}"

def delete_last():
    ledger = load_ledger()
    if not ledger["records"]:
        return "❌ 没有可删除的记录"
    removed = ledger["records"].pop()
    save_ledger(ledger)
    emoji = CATEGORIES.get(removed["category"], {}).get("emoji", "📦")
    return f"🗑️ 已删除：{emoji} {removed['desc']} ¥{removed['amount']:.2f}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: finance.py <command> [args]")
        print("  add <描述> <金额> [分类]")
        print("  income <描述> <金额>")
        print("  summary [month|week|today]")
        print("  recent [n]")
        print("  budget <金额> [分类]")
        print("  delete_last")
        print("  categories")
        sys.exit(1)

    cmd = sys.argv[1]
    
    if cmd == "add":
        desc = sys.argv[2] if len(sys.argv) > 2 else "未知"
        amount = sys.argv[3] if len(sys.argv) > 3 else "0"
        cat = sys.argv[4] if len(sys.argv) > 4 else None
        print(add_record(desc, amount, cat))
    elif cmd == "income":
        desc = sys.argv[2] if len(sys.argv) > 2 else "未知"
        amount = sys.argv[3] if len(sys.argv) > 3 else "0"
        print(add_record(desc, amount, record_type="收入"))
    elif cmd == "summary":
        period = sys.argv[2] if len(sys.argv) > 2 else "month"
        print(get_summary(period))
    elif cmd == "recent":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print(get_recent(n))
    elif cmd == "budget":
        amount = sys.argv[2] if len(sys.argv) > 2 else "0"
        cat = sys.argv[3] if len(sys.argv) > 3 else None
        print(set_budget(amount, cat))
    elif cmd == "delete_last":
        print(delete_last())
    elif cmd == "categories":
        for cat, info in CATEGORIES.items():
            print(f"{info['emoji']} {cat}")
    else:
        print(f"未知命令: {cmd}")
