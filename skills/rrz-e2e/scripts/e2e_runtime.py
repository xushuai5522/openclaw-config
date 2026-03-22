#!/usr/bin/env python3
"""rrz-e2e 运行时支撑：商品锁、幂等状态、熔断、告警去重、原子写。"""

import sys, os, json, time, hashlib, fcntl, argparse
from pathlib import Path
from typing import Optional

LOCK_DIR = Path("/tmp")
STATE_DIR = Path("/tmp")
LOCK_TIMEOUT = 1800  # 30 min
BREAKER_THRESHOLD = 3  # 连续失败步数触发熔断
ALERT_DEDUP_SEC = 300  # 同类告警去重窗口

# ── 原子写 ──────────────────────────────────────────────

def atomic_write(path: Path, data: dict):
    """tmp -> rename，带版本号和哈希。"""
    data["_version"] = data.get("_version", 0) + 1
    raw = json.dumps(data, ensure_ascii=False, indent=2)
    data["_hash"] = hashlib.sha256(raw.encode()).hexdigest()[:16]
    raw = json.dumps(data, ensure_ascii=False, indent=2)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(raw, encoding="utf-8")
    tmp.rename(path)

def safe_read(path: Path) -> Optional[dict]:
    """读取状态文件，校验哈希。"""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        stored_hash = data.pop("_hash", None)
        raw = json.dumps(data, ensure_ascii=False, indent=2)
        expected = hashlib.sha256(raw.encode()).hexdigest()[:16]
        if stored_hash and stored_hash != expected:
            print(f"⚠️ 状态文件哈希不匹配，可能损坏: {path}", file=sys.stderr)
            return None
        return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"⚠️ 状态文件读取失败: {e}", file=sys.stderr)
        return None

# ── 商品锁 ──────────────────────────────────────────────

def lock_path(product_id: str) -> Path:
    return LOCK_DIR / f"rrz_lock_{product_id}.lock"

def state_path(product_id: str) -> Path:
    return STATE_DIR / f"rrz_state_{product_id}.json"

def alert_path() -> Path:
    return STATE_DIR / "rrz_alerts.json"


def gate_path(product_id: str) -> Path:
    return STATE_DIR / f"rrz_gate_{product_id}.json"

def do_lock(product_id: str):
    lp = lock_path(product_id)
    # 检查过期锁
    if lp.exists():
        age = time.time() - lp.stat().st_mtime
        if age > LOCK_TIMEOUT:
            lp.unlink()
            print(f"🔓 过期锁已清理 ({int(age)}s)")
    fd = os.open(str(lp), os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        print(f"❌ 商品 {product_id} 已被锁定，等待或稍后重试")
        sys.exit(1)
    # 写 PID 方便排查
    os.write(fd, f"{os.getpid()}\n".encode())
    # 不关 fd，保持锁（进程退出自动释放）
    print(f"🔒 商品 {product_id} 已锁定 (pid={os.getpid()})")

def do_unlock(product_id: str):
    lp = lock_path(product_id)
    if lp.exists():
        lp.unlink()
    print(f"🔓 商品 {product_id} 已解锁")

# ── 幂等状态 ────────────────────────────────────────────

STEPS = ["pricing", "images", "info", "gate", "draft", "submit", "verify"]

def do_init(product_id: str, resume: bool):
    sp = state_path(product_id)
    existing = safe_read(sp) if resume else None
    if existing and resume:
        done = [s for s in STEPS if existing.get(f"step_{s}")]
        print(f"📋 恢复状态，已完成: {done or '无'}")
        print(json.dumps(existing, ensure_ascii=False, indent=2))
        return
    state = {
        "product_id": product_id,
        "created": time.time(),
        "_version": 0,
        "breaker_count": 0,
        "breaker_tripped": False,
    }
    for s in STEPS:
        state[f"step_{s}"] = None  # None=未完成, timestamp=完成时间
    atomic_write(sp, state)
    print(f"📋 初始化状态: {product_id}")

def do_done(product_id: str, step: str):
    if step not in STEPS:
        print(f"❌ 未知步骤: {step}，可选: {STEPS}")
        sys.exit(1)
    sp = state_path(product_id)
    state = safe_read(sp)
    if not state:
        print(f"❌ 无状态文件，先运行 init")
        sys.exit(1)
    if state.get(f"step_{step}"):
        print(f"⏭️ 步骤 {step} 已完成，跳过")
        return
    state[f"step_{step}"] = time.time()
    state["breaker_count"] = 0  # 成功重置熔断计数
    atomic_write(sp, state)
    print(f"✅ 步骤 {step} 完成")

# ── 熔断 ────────────────────────────────────────────────

def do_fail(product_id: str, step: str, reason: str = ""):
    sp = state_path(product_id)
    state = safe_read(sp)
    if not state:
        print("❌ 无状态文件"); sys.exit(1)
    state["breaker_count"] = state.get("breaker_count", 0) + 1
    state[f"last_fail_{step}"] = {"time": time.time(), "reason": reason}
    if state["breaker_count"] >= BREAKER_THRESHOLD:
        state["breaker_tripped"] = True
        atomic_write(sp, state)
        print(f"🔴 熔断触发！连续 {state['breaker_count']} 步失败，流程暂停")
        print("   运行 reset-breaker 恢复")
        sys.exit(2)
    atomic_write(sp, state)
    print(f"⚠️ 步骤 {step} 失败 ({state['breaker_count']}/{BREAKER_THRESHOLD})")

def do_reset_breaker(product_id: str):
    sp = state_path(product_id)
    state = safe_read(sp)
    if not state:
        print("❌ 无状态文件"); sys.exit(1)
    state["breaker_count"] = 0
    state["breaker_tripped"] = False
    atomic_write(sp, state)
    print(f"🟢 熔断已重置: {product_id}")

def do_check(product_id: str):
    """检查当前状态，返回下一步。"""
    sp = state_path(product_id)
    state = safe_read(sp)
    if not state:
        print("❌ 无状态文件"); sys.exit(1)
    if state.get("breaker_tripped"):
        print("🔴 熔断中，需 reset-breaker"); sys.exit(2)
    for s in STEPS:
        if not state.get(f"step_{s}"):
            print(f"➡️ 下一步: {s}")
            return
    print("🎉 全部完成")


def do_gate_report(product_id: str, report_path: str = ""):
    sp = state_path(product_id)
    state = safe_read(sp)
    if not state:
        print("❌ 无状态文件，先运行 init")
        sys.exit(1)

    gp = gate_path(product_id)
    if report_path:
        src = Path(report_path)
        if not src.exists():
            print(f"❌ gate 报告不存在: {src}")
            sys.exit(1)
        try:
            report = json.loads(src.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"❌ gate 报告不是有效 JSON: {src} ({e})")
            sys.exit(1)
    else:
        report = safe_read(gp)
        if not report:
            print(f"❌ gate 报告不存在: {gp}")
            sys.exit(1)

    stored = {
        "product_id": product_id,
        "updated": time.time(),
        "report": report,
        "status": report.get("status"),
        "ok": bool(report.get("ok")),
        "block_count": report.get("summary", {}).get("blockCount", 0),
        "warning_count": report.get("summary", {}).get("warningCount", 0),
        "_version": 0,
    }
    atomic_write(gp, stored)

    state["gate_status"] = stored["status"]
    state["gate_ok"] = stored["ok"]
    state["gate_report_path"] = str(gp)
    state["gate_summary"] = {
        "block_count": stored["block_count"],
        "warning_count": stored["warning_count"],
    }
    if stored["ok"]:
        state["step_gate"] = state.get("step_gate") or time.time()
    else:
        state["step_gate"] = None
        state["submit_blocked"] = True
    atomic_write(sp, state)
    print(json.dumps(stored, ensure_ascii=False, indent=2))


def do_can_submit(product_id: str):
    sp = state_path(product_id)
    state = safe_read(sp)
    if not state:
        print("❌ 无状态文件"); sys.exit(1)
    if not state.get("step_gate") or state.get("gate_ok") is False:
        print("🚫 gate 未通过，不允许 submit")
        sys.exit(2)
    print("✅ gate 已通过，可以 submit")

# ── 告警去重 ────────────────────────────────────────────

def do_alert(category: str, message: str):
    ap = alert_path()
    alerts = safe_read(ap) or {"alerts": {}, "_version": 0}
    now = time.time()
    key = category
    last = alerts["alerts"].get(key, {})
    if last and (now - last.get("time", 0)) < ALERT_DEDUP_SEC:
        last["count"] = last.get("count", 1) + 1
        alerts["alerts"][key] = last
        atomic_write(ap, alerts)
        print(f"🔕 告警已聚合 ({last['count']}次): {category}")
        return False  # 被去重
    alerts["alerts"][key] = {"time": now, "count": 1, "msg": message}
    atomic_write(ap, alerts)
    print(f"🔔 {message}")
    return True  # 需要播报

# ── CLI ─────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="rrz-e2e 运行时")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("lock").add_argument("product_id")
    sub.add_parser("unlock").add_argument("product_id")

    init_p = sub.add_parser("init")
    init_p.add_argument("product_id")
    init_p.add_argument("resume", nargs="?", default="")

    done_p = sub.add_parser("done")
    done_p.add_argument("product_id")
    done_p.add_argument("step")

    fail_p = sub.add_parser("fail")
    fail_p.add_argument("product_id")
    fail_p.add_argument("step")
    fail_p.add_argument("reason", nargs="?", default="")

    sub.add_parser("reset-breaker").add_argument("product_id")
    sub.add_parser("check").add_argument("product_id")

    gate_p = sub.add_parser("gate-report")
    gate_p.add_argument("product_id")
    gate_p.add_argument("report_path", nargs="?", default="")

    sub.add_parser("can-submit").add_argument("product_id")

    alert_p = sub.add_parser("alert")
    alert_p.add_argument("category")
    alert_p.add_argument("message")

    args = p.parse_args()
    if not args.cmd:
        p.print_help(); sys.exit(1)

    dispatch = {
        "lock": lambda: do_lock(args.product_id),
        "unlock": lambda: do_unlock(args.product_id),
        "init": lambda: do_init(args.product_id, args.resume == "resume"),
        "done": lambda: do_done(args.product_id, args.step),
        "fail": lambda: do_fail(args.product_id, args.step, args.reason),
        "reset-breaker": lambda: do_reset_breaker(args.product_id),
        "check": lambda: do_check(args.product_id),
        "gate-report": lambda: do_gate_report(args.product_id, args.report_path),
        "can-submit": lambda: do_can_submit(args.product_id),
        "alert": lambda: do_alert(args.category, args.message),
    }
    dispatch[args.cmd]()

if __name__ == "__main__":
    main()
