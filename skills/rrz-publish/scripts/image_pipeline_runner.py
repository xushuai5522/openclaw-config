#!/usr/bin/env python3
"""
RRZ image pipeline runner

目标：把商品目录里的原始图片整理成可直接给人人租执行器消费的标准产物。

输入：
- products/<product_key>/product_info.json
- products/<product_key>/image_pipeline_request.json （可选）
- products/<product_key>/raw/* 或商品根目录中的图片

输出：
- products/<product_key>/processed/*
- products/<product_key>/main/*
- products/<product_key>/desc/*
- products/<product_key>/image_pipeline_result.json
"""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Iterable, List

from PIL import Image, ImageOps, UnidentifiedImageError

TZ = timezone(timedelta(hours=8))
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass
class PipelineConfig:
    product_dir: Path
    main_size: int = 800
    desc_max_width: int = 1200
    main_count: int = 5
    desc_count: int = 8
    overwrite: bool = True


def now_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def ensure_dirs(product_dir: Path) -> dict:
    dirs = {
        "raw": product_dir / "raw",
        "processed": product_dir / "processed",
        "main": product_dir / "main",
        "desc": product_dir / "desc",
        "logs": product_dir / "logs",
    }
    for p in dirs.values():
        p.mkdir(parents=True, exist_ok=True)
    return dirs


def is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTS


def list_images(paths: Iterable[Path]) -> List[Path]:
    return sorted([p for p in paths if is_image(p)], key=lambda p: p.name.lower())


def discover_source_images(product_dir: Path) -> List[Path]:
    raw_dir = product_dir / "raw"
    raw_images = list_images(raw_dir.iterdir()) if raw_dir.exists() else []
    if raw_images:
        return raw_images
    root_images = list_images(product_dir.iterdir())
    return [p for p in root_images if p.parent == product_dir]


def stage_to_raw(source_images: List[Path], raw_dir: Path, overwrite: bool) -> List[Path]:
    staged = []
    for src in source_images:
        target = raw_dir / src.name
        if src.resolve() != target.resolve():
            if overwrite or not target.exists():
                shutil.copy2(src, target)
        staged.append(target if target.exists() else src)
    return list_images(staged)


def is_readable_image(path: Path) -> bool:
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except (UnidentifiedImageError, OSError):
        return False


def load_request(product_dir: Path) -> dict:
    req_path = product_dir / "image_pipeline_request.json"
    return read_json(req_path) if req_path.exists() else {}


def normalize_orientation(img: Image.Image) -> Image.Image:
    return ImageOps.exif_transpose(img)


def open_rgb(path: Path) -> Image.Image:
    img = Image.open(path)
    img = normalize_orientation(img)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    return img


def white_bg_main(src: Path, dst: Path, size: int) -> dict:
    img = open_rgb(src)
    working = img.convert("RGBA") if img.mode == "RGBA" else img.convert("RGB")
    max_inner = int(size * 0.82)
    working.thumbnail((max_inner, max_inner), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    x = (size - working.width) // 2
    y = (size - working.height) // 2
    if working.mode == "RGBA":
        canvas.alpha_composite(working, (x, y))
    else:
        canvas.paste(working, (x, y))

    out = canvas.convert("RGB")
    out.save(dst, format="JPEG", quality=95, optimize=True)
    return {"path": str(dst), "width": out.width, "height": out.height, "source": str(src), "kind": "main"}


def standardize_desc(src: Path, dst: Path, max_width: int) -> dict:
    img = open_rgb(src).convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.Resampling.LANCZOS)
    img.save(dst, format="JPEG", quality=92, optimize=True)
    return {"path": str(dst), "width": img.width, "height": img.height, "source": str(src), "kind": "desc"}


def pick_images(staged_images: List[Path], request: dict, main_count: int, desc_count: int) -> tuple[list[Path], list[Path], list[str]]:
    notes: list[str] = []
    drop_sources = set(request.get("drop_sources", []))
    staged_images = [p for p in staged_images if p.name not in drop_sources]
    names = {p.name: p for p in staged_images}

    explicit_main = [names[n] for n in request.get("main_images", []) if n in names]
    explicit_desc = [names[n] for n in request.get("desc_images", []) if n in names]
    remaining = [p for p in staged_images if p not in explicit_main and p not in explicit_desc]

    if explicit_main:
        main_images = explicit_main[:main_count]
        notes.append("使用 image_pipeline_request.json 中指定的 main_images")
    else:
        main_images = remaining[:main_count]
        notes.append("未指定 main_images，按稳定排序自动选择主图")

    if explicit_desc:
        desc_images = explicit_desc[:desc_count]
        notes.append("使用 image_pipeline_request.json 中指定的 desc_images")
    else:
        pool = [p for p in staged_images if p not in main_images]
        desc_images = pool[:desc_count]
        notes.append("未指定 desc_images，按除主图外剩余图片自动选择描述图")

    # 显式 desc 若因 drop/坏图被削减，自动从剩余高质量池补足
    if len(desc_images) < desc_count:
        pool = [p for p in staged_images if p not in desc_images and p not in main_images]
        refill = pool[: desc_count - len(desc_images)]
        if refill:
            desc_images.extend(refill)
            notes.append("显式 desc 不足，已从剩余素材自动补足")

    if len(desc_images) < desc_count and request.get("reuse_main_images_as_desc"):
        refill = [p for p in main_images if p not in desc_images][: desc_count - len(desc_images)]
        if refill:
            desc_images.extend(refill)
            notes.append("按请求参数复用部分主图作为描述图")

    if len(desc_images) < desc_count and main_images:
        refill = [p for p in main_images if p not in desc_images][: desc_count - len(desc_images)]
        if refill:
            desc_images.extend(refill)
            notes.append("描述图不足，临时回退复用前几张主图")

    return main_images, desc_images[:desc_count], notes


def clean_output_dir(path: Path) -> None:
    for child in path.iterdir():
        if child.is_file():
            child.unlink()


def run_pipeline(config: PipelineConfig) -> dict:
    product_dir = config.product_dir
    product_info_path = product_dir / "product_info.json"
    if not product_info_path.exists():
        raise FileNotFoundError(f"缺少 product_info.json: {product_info_path}")

    product_info = read_json(product_info_path)
    request = load_request(product_dir)
    dirs = ensure_dirs(product_dir)

    source_images = discover_source_images(product_dir)
    if not source_images:
        raise RuntimeError("未发现原始图片；请放到商品目录或 raw/ 目录")

    staged_images = stage_to_raw(source_images, dirs["raw"], config.overwrite)
    invalid_images = [str(p) for p in staged_images if not is_readable_image(p)]
    staged_images = [p for p in staged_images if is_readable_image(p)]
    if not staged_images:
        raise RuntimeError("发现原始图片，但全部不可读；请检查文件是否损坏")

    if config.overwrite:
        clean_output_dir(dirs["processed"])
        clean_output_dir(dirs["main"])
        clean_output_dir(dirs["desc"])

    main_inputs, desc_inputs, notes = pick_images(
        staged_images,
        request,
        main_count=request.get("main_count", config.main_count),
        desc_count=request.get("desc_count", config.desc_count),
    )

    processed_records, main_records, desc_records = [], [], []
    product_key = request.get("product_key") or product_info.get("product_key") or product_dir.name

    for idx, src in enumerate(main_inputs, 1):
        processed_path = dirs["processed"] / f"main_{idx:02d}.jpg"
        main_path = dirs["main"] / f"main_{idx:02d}.jpg"
        rec = white_bg_main(src, processed_path, size=request.get("main_size", config.main_size))
        shutil.copy2(processed_path, main_path)
        processed_records.append(rec)
        main_records.append({**rec, "path": str(main_path)})

    for idx, src in enumerate(desc_inputs, 1):
        processed_path = dirs["processed"] / f"desc_{idx:02d}.jpg"
        desc_path = dirs["desc"] / f"desc_{idx:02d}.jpg"
        rec = standardize_desc(src, processed_path, max_width=request.get("desc_max_width", config.desc_max_width))
        shutil.copy2(processed_path, desc_path)
        processed_records.append(rec)
        desc_records.append({**rec, "path": str(desc_path)})

    result = {
        "product_key": product_key,
        "status": "ok" if main_records and desc_records else "failed",
        "main_images": main_records,
        "desc_images": desc_records,
        "upload_payload": {
            "title": product_info.get("title"),
            "main_images": [x["path"] for x in main_records],
            "desc_images": [x["path"] for x in desc_records],
        },
        "request_used": request,
        "raw_images": [str(p) for p in staged_images],
        "invalid_images": invalid_images,
        "processed_images": processed_records,
        "generated_at": now_iso(),
        "notes": notes + ([f"跳过不可读图片 {len(invalid_images)} 张"] if invalid_images else []),
    }

    write_json(product_dir / "image_pipeline_result.json", result)
    return result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="RRZ image pipeline runner")
    p.add_argument("product", help="商品 key 或完整目录路径")
    p.add_argument("--products-root", default="/Users/xs/.openclaw/workspace/products", help="商品根目录")
    p.add_argument("--main-size", type=int, default=800)
    p.add_argument("--desc-max-width", type=int, default=1200)
    p.add_argument("--main-count", type=int, default=5)
    p.add_argument("--desc-count", type=int, default=8)
    p.add_argument("--no-overwrite", action="store_true")
    return p


def resolve_product_dir(product: str, products_root: str) -> Path:
    candidate = Path(product)
    if candidate.exists():
        return candidate.resolve()
    return (Path(products_root) / product).resolve()


def main() -> int:
    args = build_parser().parse_args()
    product_dir = resolve_product_dir(args.product, args.products_root)
    config = PipelineConfig(
        product_dir=product_dir,
        main_size=args.main_size,
        desc_max_width=args.desc_max_width,
        main_count=args.main_count,
        desc_count=args.desc_count,
        overwrite=not args.no_overwrite,
    )
    result = run_pipeline(config)
    print(json.dumps({
        "product_key": result["product_key"],
        "status": result["status"],
        "main_count": len(result["main_images"]),
        "desc_count": len(result["desc_images"]),
        "result": str(product_dir / "image_pipeline_result.json"),
    }, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
