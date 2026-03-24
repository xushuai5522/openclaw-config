#!/usr/bin/env python3
"""
RRZ 原始素材审核员

输入：
- products/<product_key>/product_info.json
- products/<product_key>/raw/* 或商品根目录原始图

输出：
- raw_audit_result.json
- image_pipeline_request.json

目标：
- 在图片处理前做素材分诊
- 给 image pipeline 直接输出可消费参数，而不是只给口头建议
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

from PIL import Image, UnidentifiedImageError

TZ = timezone(timedelta(hours=8))
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_MAIN_COUNT = 5
DEFAULT_DESC_COUNT = 3
MIN_IMAGE_SIZE = 600


def now_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


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


def is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTS


def list_images(product_dir: Path) -> List[Path]:
    raw_dir = product_dir / "raw"
    if raw_dir.exists():
        imgs = [p for p in raw_dir.iterdir() if is_image(p)]
        if imgs:
            return sorted(imgs, key=lambda p: p.name.lower())
    return sorted([p for p in product_dir.iterdir() if is_image(p)], key=lambda p: p.name.lower())


def inspect_image(path: Path) -> Tuple[bool, Dict[str, Any]]:
    try:
        with Image.open(path) as img:
            width, height = img.width, img.height
            score = 0
            if width >= MIN_IMAGE_SIZE and height >= MIN_IMAGE_SIZE:
                score += 3
            if width >= height:
                score += 1
            if abs(width - height) <= max(width, height) * 0.2:
                score += 2
            if "official" in path.name.lower():
                score -= 2
            return True, {
                "file": path.name,
                "path": str(path),
                "width": width,
                "height": height,
                "format": img.format,
                "score": score,
                "near_square": abs(width - height) <= max(width, height) * 0.2,
            }
    except (UnidentifiedImageError, OSError) as e:
        return False, {
            "file": path.name,
            "path": str(path),
            "error": str(e),
            "score": -999,
        }


def choose_sets(valid_infos: List[Dict[str, Any]], main_count: int, desc_count: int) -> Tuple[List[str], List[str], List[str]]:
    notes: List[str] = []
    sorted_infos = sorted(valid_infos, key=lambda x: (-x["score"], x["file"]))
    preferred_infos = [x for x in sorted_infos if x["width"] >= MIN_IMAGE_SIZE and x["height"] >= MIN_IMAGE_SIZE]

    main_pool = preferred_infos or sorted_infos
    main = [x["file"] for x in main_pool[:main_count]]

    # 描述图优先使用高质量素材；不足时复用主图，而不是把低质图塞进 desc 推荐集
    desc = [x["file"] for x in preferred_infos if x["file"] not in main][:desc_count]

    if len(desc) < desc_count:
        refill = [x for x in main if x not in desc][: desc_count - len(desc)]
        desc.extend(refill)
        if refill:
            notes.append("描述图不足，已回退复用部分主图")

    return main, desc, notes


def load_manual_review(product_dir: Path) -> Dict[str, Any]:
    path = product_dir / "image_manual_review.json"
    return read_json(path) if path.exists() else {}


def build_request(product_dir: Path, product_info: Dict[str, Any], main: List[str], desc: List[str], invalid: List[str], low_quality: List[str], manual_drop: List[str]) -> Dict[str, Any]:
    return {
        "product_key": product_info.get("product_key") or product_dir.name,
        "main_images": main,
        "desc_images": desc,
        "drop_sources": sorted(set(invalid + low_quality + manual_drop)),
        "main_count": max(len(main), DEFAULT_MAIN_COUNT),
        "desc_count": max(len(desc), DEFAULT_DESC_COUNT),
        "main_size": 800,
        "desc_max_width": 1200,
        "background_mode": "white",
        "main_crop": "contain_center",
        "desc_strategy": "standardize_only",
        "reuse_main_images_as_desc": len(desc) < DEFAULT_DESC_COUNT,
        "generated_at": now_iso(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RRZ raw auditor")
    parser.add_argument("product", help="商品 key 或完整目录路径")
    parser.add_argument("--products-root", default="/Users/xs/.openclaw/workspace/products")
    args = parser.parse_args()

    product_dir = resolve_product_dir(args.product, args.products_root)
    product_info = read_json(product_dir / "product_info.json")
    manual_review = load_manual_review(product_dir)
    manual_drop = list(manual_review.get("drop_sources", []))
    manual_main_allow = list(manual_review.get("force_main_images", []))
    manual_desc_allow = list(manual_review.get("force_desc_images", []))
    images = list_images(product_dir)
    if not images:
        raise SystemExit("未发现原始图片")

    valid_infos: List[Dict[str, Any]] = []
    invalid_infos: List[Dict[str, Any]] = []
    issues: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    low_quality_files: List[str] = []

    for img in images:
        ok, info = inspect_image(img)
        if ok:
            valid_infos.append(info)
            if info["width"] < MIN_IMAGE_SIZE or info["height"] < MIN_IMAGE_SIZE:
                low_quality_files.append(info["file"])
                warnings.append({"level": "warning", "code": "RAW_IMAGE_SIZE_LT_MIN", "message": f"素材图尺寸低于 {MIN_IMAGE_SIZE}，将不进入推荐处理集", "extra": info})
        else:
            invalid_infos.append(info)
            warnings.append({"level": "warning", "code": "RAW_IMAGE_INVALID", "message": "素材图不可识别，将从处理链剔除", "extra": info})

    if not valid_infos:
        issues.append({"level": "block", "code": "RAW_NO_VALID_IMAGES", "message": "没有可用原始素材，禁止进入图片处理"})

    main_set, desc_set, notes = choose_sets(valid_infos, DEFAULT_MAIN_COUNT, DEFAULT_DESC_COUNT)

    if manual_main_allow:
        main_set = [x for x in manual_main_allow if x not in manual_drop][:DEFAULT_MAIN_COUNT]
        notes.append("使用人工指定的主图白名单")
    if manual_desc_allow:
        desc_set = [x for x in manual_desc_allow if x not in manual_drop][:DEFAULT_DESC_COUNT]
        notes.append("使用人工指定的详情图白名单")
    if len(valid_infos) < DEFAULT_MAIN_COUNT:
        warnings.append({"level": "warning", "code": "RAW_MAIN_LT_RECOMMENDED", "message": "可用素材图少于推荐主图数", "extra": {"count": len(valid_infos), "recommended": DEFAULT_MAIN_COUNT}})
    if len(desc_set) < DEFAULT_DESC_COUNT:
        warnings.append({"level": "warning", "code": "RAW_DESC_LT_RECOMMENDED", "message": "可分配的描述图少于推荐数量", "extra": {"count": len(desc_set), "recommended": DEFAULT_DESC_COUNT}})

    request = build_request(product_dir, product_info, main_set, desc_set, [x["file"] for x in invalid_infos], low_quality_files, manual_drop)
    raw_result = {
        "product_key": product_info.get("product_key") or product_dir.name,
        "status": "block" if issues else ("warning" if warnings or manual_drop else "pass"),
        "candidate_images": valid_infos,
        "invalid_images": invalid_infos,
        "recommended_main_images": main_set,
        "recommended_desc_images": desc_set,
        "issues": issues,
        "warnings": warnings,
        "manual_review": manual_review,
        "tool_params": {
            "image_pipeline_request": request
        },
        "notes": notes,
        "generated_at": now_iso(),
    }

    write_json(product_dir / "raw_audit_result.json", raw_result)
    write_json(product_dir / "image_pipeline_request.json", request)

    print(json.dumps({
        "product_key": product_dir.name,
        "status": raw_result["status"],
        "valid": len(valid_infos),
        "invalid": len(invalid_infos),
        "main": len(main_set),
        "desc": len(desc_set),
        "raw_audit_result": str(product_dir / "raw_audit_result.json"),
        "image_pipeline_request": str(product_dir / "image_pipeline_request.json"),
    }, ensure_ascii=False, indent=2))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
