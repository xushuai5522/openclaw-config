#!/usr/bin/env python3
"""
RRZ V2 审核员：规则审核 + 修复建议 + 工具参数

输入：
- products/<product_key>/product_info.json
- products/<product_key>/upload_data.json
- products/<product_key>/image_pipeline_result.json
- products/<product_key>/raw_audit_result.json （可选）

输出：
- products/<product_key>/audit_result.json
- products/<product_key>/audit_advice.json
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

from PIL import Image, UnidentifiedImageError

TZ = timezone(timedelta(hours=8))
FORBIDDEN_WORDS = ["租赁", "出租", "免押", "免息", "分期"]
WARNING_WORDS = ["测试", "最"]
PACKAGE_ALLOWED = ["租完归还", "可归还", "到期可归还/续租", "到期可归还", "随租随还", "到期须归还"]
TITLE_REQUIRED_KEYS = ["brand", "model"]
MIN_MAIN_IMAGES = 1
MIN_DESC_IMAGES = 1
RECOMMENDED_DESC_IMAGES = 3
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


def normalize_text(v: Any) -> str:
    return re.sub(r"\s+", " ", str(v or "")).strip()


def strip_spaces_upper(v: Any) -> str:
    return normalize_text(v).replace(" ", "").upper()


def push_issue(issues: List[dict], level: str, code: str, message: str, extra: Any = None) -> None:
    issues.append({"level": level, "code": code, "message": message, "extra": extra})


def resolve_product_dir(product: str, products_root: str) -> Path:
    candidate = Path(product)
    if candidate.exists():
        return candidate.resolve()
    return (Path(products_root) / product).resolve()


def contains_any(text: str, words: List[str]) -> List[str]:
    return [w for w in words if w in text]


def image_info(path: Path) -> Tuple[bool, Dict[str, Any]]:
    try:
        with Image.open(path) as img:
            return True, {"path": str(path), "width": img.width, "height": img.height, "format": img.format}
    except (UnidentifiedImageError, OSError) as e:
        return False, {"path": str(path), "error": str(e)}


def validate_image_set(items: List[Dict[str, Any]], issues: List[dict], kind: str, minimum: int) -> List[Dict[str, Any]]:
    infos = []
    if len(items) < minimum:
        push_issue(issues, "block", f"{kind.upper()}_COUNT_LT_MIN", f"{kind} 数量不足，至少需要 {minimum} 张", {"count": len(items), "minimum": minimum})
    for idx, item in enumerate(items, 1):
        path = Path(item.get("path", ""))
        if not path.exists():
            push_issue(issues, "block", f"{kind.upper()}_MISSING_FILE", f"{kind} 第 {idx} 张文件不存在", {"path": str(path)})
            continue
        ok, info = image_info(path)
        info["index"] = idx
        if not ok:
            push_issue(issues, "block", f"{kind.upper()}_UNREADABLE", f"{kind} 第 {idx} 张图片不可读", info)
            infos.append(info)
            continue
        if info["width"] < MIN_IMAGE_SIZE or info["height"] < MIN_IMAGE_SIZE:
            push_issue(issues, "block", f"{kind.upper()}_SIZE_LT_MIN", f"{kind} 第 {idx} 张尺寸低于 {MIN_IMAGE_SIZE}x{MIN_IMAGE_SIZE}", info)
        infos.append(info)
    return infos


def title_has_scene(title: str, brand: str, model: str) -> bool:
    t = normalize_text(title)
    if not t:
        return False
    for token in [brand, model]:
        if token:
            t = t.replace(token, " ")
    t = re.sub(r"\b[0-9]+成新\b", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return len(t) >= 4


def extract_package_names(upload_data: Dict[str, Any]) -> List[str]:
    names = []
    for p in upload_data.get("pricing", {}).get("plans", []):
        name = normalize_text(p.get("name"))
        if name:
            names.append(name)
    return names


def build_advice(product_dir: Path, audit_result: Dict[str, Any], raw_audit_result: Dict[str, Any] | None) -> Dict[str, Any]:
    warnings = audit_result.get("warnings", [])
    blocking = audit_result.get("blocking_issues", [])
    raw_request = (raw_audit_result or {}).get("tool_params", {}).get("image_pipeline_request", {})

    fix_actions: List[Dict[str, Any]] = []
    desc_target = max(RECOMMENDED_DESC_IMAGES, audit_result.get("checks", {}).get("desc_image_count", 0))
    invalid_source_files: List[str] = []

    for item in warnings + blocking:
        code = item.get("code")
        extra = item.get("extra") or {}
        if code == "DESC_IMAGES_LT_RECOMMENDED":
            fix_actions.append({
                "type": "expand_desc_images",
                "target": "image_pipeline",
                "reason": item.get("message"),
                "params": {"desc_count": RECOMMENDED_DESC_IMAGES, "reuse_main_images_as_desc": True, "desc_max_width": 1200}
            })
        if code == "INVALID_SOURCE_IMAGES":
            invalid_source_files.extend([Path(x).name for x in extra.get("invalid_images", [])])
        if code == "WARNING_WORDS_HIT":
            fix_actions.append({
                "type": "rewrite_copy",
                "target": "title_or_description",
                "reason": item.get("message"),
                "params": {"replace_words": extra.get("words", []), "max_length": 60}
            })
        if code == "FORBIDDEN_WORDS_HIT":
            fix_actions.append({
                "type": "rewrite_copy",
                "target": "title_and_description",
                "reason": item.get("message"),
                "params": {"forbidden_words": extra.get("words", []), "must_remove": True, "max_length": 60}
            })

    if invalid_source_files:
        fix_actions.insert(0, {
            "type": "drop_invalid_source",
            "target": "raw",
            "reason": "存在不可读原始素材，需从处理链剔除",
            "params": {"drop_sources": invalid_source_files}
        })

    image_request = {
        "product_key": product_dir.name,
        "main_images": raw_request.get("main_images", []),
        "desc_images": raw_request.get("desc_images", []),
        "drop_sources": sorted(set(raw_request.get("drop_sources", []) + invalid_source_files)),
        "main_count": max(raw_request.get("main_count", 5), audit_result.get("checks", {}).get("main_image_count", 0), 5),
        "desc_count": max(raw_request.get("desc_count", 3), desc_target, 3),
        "main_size": raw_request.get("main_size", 800),
        "desc_max_width": raw_request.get("desc_max_width", 1200),
        "background_mode": raw_request.get("background_mode", "white"),
        "main_crop": raw_request.get("main_crop", "contain_center"),
        "desc_strategy": raw_request.get("desc_strategy", "standardize_only"),
        "reuse_main_images_as_desc": True if audit_result.get("checks", {}).get("desc_image_count", 0) < RECOMMENDED_DESC_IMAGES else raw_request.get("reuse_main_images_as_desc", False),
    }

    advice = {
        "product_key": product_dir.name,
        "status": audit_result.get("status"),
        "summary": "允许提审" if audit_result.get("status") == "pass" else ("存在告警，建议先修再提审" if audit_result.get("status") == "warning" else "存在阻断项，禁止提审"),
        "decisions": {
            "can_submit": audit_result.get("status") != "block",
            "need_manual_review": audit_result.get("status") == "block",
            "should_regenerate_images": any(x["type"] in {"expand_desc_images", "drop_invalid_source"} for x in fix_actions),
            "should_rewrite_copy": any(x["type"] == "rewrite_copy" for x in fix_actions),
        },
        "fix_actions": fix_actions,
        "tool_params": {
            "image_pipeline_request": image_request,
            "submit_policy": {
                "allow_submit": audit_result.get("status") != "block",
                "allow_submit_on_warning": True,
                "require_manual_review": audit_result.get("status") == "block",
            }
        },
        "generated_at": now_iso(),
    }
    return advice


def evaluate(product_dir: Path) -> tuple[Dict[str, Any], Dict[str, Any]]:
    product_info = read_json(product_dir / "product_info.json")
    upload_data = read_json(product_dir / "upload_data.json")
    image_result = read_json(product_dir / "image_pipeline_result.json")
    raw_audit_result = read_json(product_dir / "raw_audit_result.json") if (product_dir / "raw_audit_result.json").exists() else None

    issues: List[dict] = []
    warnings: List[dict] = []

    title = normalize_text(upload_data.get("title") or product_info.get("title"))
    brand = normalize_text(upload_data.get("brand") or product_info.get("brand"))
    model = normalize_text(upload_data.get("model") or product_info.get("model"))
    description = normalize_text(upload_data.get("description"))

    if not title:
        push_issue(issues, "block", "TITLE_EMPTY", "标题为空")
    else:
        missing = [k for k in TITLE_REQUIRED_KEYS if not normalize_text(product_info.get(k))]
        if missing:
            push_issue(warnings, "warning", "PRODUCT_INFO_INCOMPLETE", "product_info 关键字段不完整", {"missing": missing})
        if brand and brand not in title:
            push_issue(issues, "block", "BRAND_NOT_IN_TITLE", "标题未包含品牌", {"brand": brand, "title": title})
        if model and strip_spaces_upper(model) not in strip_spaces_upper(title):
            push_issue(issues, "block", "MODEL_NOT_IN_TITLE", "标题未包含型号", {"model": model, "title": title})
        if not title_has_scene(title, brand, model):
            push_issue(warnings, "warning", "TITLE_SCENE_WEAK", "标题里的使用场景不够明显", {"title": title})
        forbidden = contains_any(title + "\n" + description, FORBIDDEN_WORDS)
        if forbidden:
            push_issue(issues, "block", "FORBIDDEN_WORDS_HIT", "命中禁词", {"words": forbidden})
        warn_words = contains_any(title + "\n" + description, WARNING_WORDS)
        if warn_words:
            push_issue(warnings, "warning", "WARNING_WORDS_HIT", "命中风险词，建议改写", {"words": warn_words})

    package_names = extract_package_names(upload_data)
    if not package_names:
        push_issue(issues, "block", "PACKAGE_EMPTY", "未发现套餐方案")
    else:
        invalid_packages = [name for name in package_names if not any(k in name for k in PACKAGE_ALLOWED)]
        if invalid_packages:
            push_issue(issues, "block", "PACKAGE_TEMPLATE_INVALID", "存在不符合模板的套餐名", {"invalid": invalid_packages})
        if len(package_names) < 2:
            push_issue(warnings, "warning", "PACKAGE_COUNT_LT_2", "套餐方案少于 2 个，建议补足可审核的多规格形态", {"count": len(package_names)})

    pricing = upload_data.get("pricing", {})
    deposit = pricing.get("deposit")
    device_value = pricing.get("device_value") or product_info.get("pricing", {}).get("device_value")
    if deposit is None:
        push_issue(issues, "block", "DEPOSIT_EMPTY", "押金为空")
    elif device_value is not None:
        try:
            if float(deposit) > float(device_value):
                push_issue(issues, "block", "DEPOSIT_GT_DEVICE_VALUE", "押金高于设备价值", {"deposit": deposit, "device_value": device_value})
        except Exception:
            push_issue(warnings, "warning", "PRICING_PARSE_FAILED", "定价字段解析失败", {"deposit": deposit, "device_value": device_value})

    main_images = image_result.get("main_images", [])
    desc_images = image_result.get("desc_images", [])
    invalid_images = image_result.get("invalid_images", [])
    main_infos = validate_image_set(main_images, issues, "main_images", MIN_MAIN_IMAGES)
    desc_infos = validate_image_set(desc_images, issues, "desc_images", MIN_DESC_IMAGES)

    if len(desc_images) < RECOMMENDED_DESC_IMAGES:
        push_issue(warnings, "warning", "DESC_IMAGES_LT_RECOMMENDED", f"描述图少于推荐值 {RECOMMENDED_DESC_IMAGES} 张", {"count": len(desc_images)})
    if invalid_images:
        push_issue(warnings, "warning", "INVALID_SOURCE_IMAGES", "存在不可读原始素材，已被 image pipeline 跳过", {"invalid_images": invalid_images})
    if not description:
        push_issue(warnings, "warning", "DESCRIPTION_EMPTY", "描述为空或过短，虽然不一定阻断，但建议补充")

    blocking = [x for x in issues if x["level"] == "block"]
    warn_only = warnings + [x for x in issues if x["level"] == "warning"]
    score = max(0, 100 - len(blocking) * 15 - len(warn_only) * 4)
    status = "block" if blocking else ("warning" if warn_only else "pass")

    result = {
        "product_key": product_dir.name,
        "status": status,
        "pass": status == "pass",
        "score": score,
        "blocking_issues": blocking,
        "warnings": warn_only,
        "checks": {
            "title_present": bool(title),
            "brand_in_title": bool(brand and brand in title),
            "model_in_title": bool(model and strip_spaces_upper(model) in strip_spaces_upper(title)),
            "package_count": len(package_names),
            "main_image_count": len(main_images),
            "desc_image_count": len(desc_images),
            "invalid_source_count": len(invalid_images),
            "description_present": bool(description),
        },
        "artifacts": {
            "product_info": str(product_dir / "product_info.json"),
            "upload_data": str(product_dir / "upload_data.json"),
            "image_pipeline_result": str(product_dir / "image_pipeline_result.json"),
            "raw_audit_result": str(product_dir / "raw_audit_result.json") if raw_audit_result else None,
            "main_images": main_infos,
            "desc_images": desc_infos,
        },
        "generated_at": now_iso(),
    }
    advice = build_advice(product_dir, result, raw_audit_result)
    return result, advice


def main() -> int:
    parser = argparse.ArgumentParser(description="RRZ V2 audit reviewer")
    parser.add_argument("product", help="商品 key 或完整目录路径")
    parser.add_argument("--products-root", default="/Users/xs/.openclaw/workspace/products")
    args = parser.parse_args()

    product_dir = resolve_product_dir(args.product, args.products_root)
    result, advice = evaluate(product_dir)
    result_path = product_dir / "audit_result.json"
    advice_path = product_dir / "audit_advice.json"
    write_json(result_path, result)
    write_json(advice_path, advice)
    print(json.dumps({
        "product_key": product_dir.name,
        "status": result["status"],
        "score": result["score"],
        "blocking": len(result["blocking_issues"]),
        "warnings": len(result["warnings"]),
        "audit_result": str(result_path),
        "audit_advice": str(advice_path),
    }, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "block" else 0


if __name__ == "__main__":
    raise SystemExit(main())
