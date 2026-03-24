#!/usr/bin/env python3
"""
把 image pipeline + audit reviewer 的文件产物，编译成给 rrzSubmitAtomic 使用的 payload。

输入：
- product_info.json
- upload_data.json
- image_pipeline_result.json
- audit_result.json

输出：
- submit_payload.json

用途：
- 让“文件协议链”直接接到“页面执行链”
- 页面侧不再手工挑图，直接消费 image_pipeline_result.json
- submit 行为受 audit_result.json 控制
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def resolve_product_dir(product: str, products_root: str) -> Path:
    candidate = Path(product)
    if candidate.exists():
        return candidate.resolve()
    return (Path(products_root) / product).resolve()


def normalize_rrz_image_items(items: List[Any]) -> List[Dict[str, Any]]:
    out = []
    for idx, item in enumerate(items, 1):
        if isinstance(item, str):
            out.append({"url": item, "src": item, "name": f"rrz_{idx}.jpg", "path": item})
        elif isinstance(item, dict):
            url = item.get("url") or item.get("path") or item.get("src")
            if url:
                out.append({
                    "url": url,
                    "src": item.get("src") or url,
                    "name": item.get("name") or Path(url).name or f"rrz_{idx}.jpg",
                    "path": item.get("path") or url,
                })
    return out


def build_sell_table_data(upload_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    plans = upload_data.get("pricing", {}).get("plans", [])
    deposit = upload_data.get("pricing", {}).get("deposit")
    rows = []
    for p in plans:
        row = {
            "name": p.get("name"),
            "deposit": deposit,
        }
        duration = str(p.get("duration") or "")
        price = p.get("price")
        if duration in ("1周", "7天"):
            row["sevenDay"] = price
        elif duration in ("1个月", "30天"):
            row["oneMonth"] = price
        elif duration in ("3个月", "90天"):
            row["threeMonth"] = price
        elif duration in ("6个月", "180天"):
            row["sixMonth"] = price
        elif duration in ("1年", "365天"):
            row["oneYear"] = price
        else:
            row["price"] = price
        rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Build RRZ submit payload")
    parser.add_argument("product", help="商品 key 或目录")
    parser.add_argument("--products-root", default="/Users/xs/.openclaw/workspace/products")
    parser.add_argument("--submit", action="store_true", help="标记为提交审核")
    parser.add_argument("--save-draft", action="store_true", help="标记为保存草稿")
    parser.add_argument("--block-on-warning", action="store_true", help="warning 也阻止 submit")
    args = parser.parse_args()

    product_dir = resolve_product_dir(args.product, args.products_root)
    product_info = read_json(product_dir / "product_info.json")
    upload_data = read_json(product_dir / "upload_data.json")
    image_result = read_json(product_dir / "image_pipeline_result.json")
    audit_result = read_json(product_dir / "audit_result.json")

    payload = {
        "productKey": product_dir.name,
        "title": upload_data.get("title") or product_info.get("title"),
        "brand": upload_data.get("brand") or product_info.get("brand"),
        "model": upload_data.get("model") or product_info.get("model"),
        "details": upload_data.get("description") or product_info.get("description") or "",
        "mainImages": normalize_rrz_image_items(image_result.get("main_images", [])),
        "descImages": normalize_rrz_image_items(image_result.get("desc_images", [])),
        "sellTableData": build_sell_table_data(upload_data),
        "auditStatus": audit_result.get("status"),
        "auditResult": audit_result,
        "requireAuditBeforeSubmit": True,
        "allowSubmitOnWarning": not args.block_on_warning,
        "submitReview": bool(args.submit),
        "saveDraft": bool(args.save_draft),
        "sourceArtifacts": {
            "product_info": str(product_dir / "product_info.json"),
            "upload_data": str(product_dir / "upload_data.json"),
            "image_pipeline_result": str(product_dir / "image_pipeline_result.json"),
            "audit_result": str(product_dir / "audit_result.json"),
        }
    }

    out = product_dir / "submit_payload.json"
    write_json(out, payload)
    print(json.dumps({
        "product_key": product_dir.name,
        "audit_status": payload["auditStatus"],
        "main_images": len(payload["mainImages"]),
        "desc_images": len(payload["descImages"]),
        "sell_rows": len(payload["sellTableData"]),
        "submitReview": payload["submitReview"],
        "saveDraft": payload["saveDraft"],
        "result": str(out),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
