#!/usr/bin/env python3
import json, re, time, urllib.request
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

ADMIN_LIST = "https://admin.rrzu.com/spu-view/list"
LOGIN_URL = "https://www.rrzu.com/auth/server-login"
USER = "15162152584"
PWD = "152584"

BAN_MAP = {
    "租赁": "租用",
    "出租": "提供使用",
    "免押": "",
    "免息": "",
    "分期": "",
    "最便宜": "",
    "最低价": "",
}


def get_ws():
    data = urllib.request.urlopen("http://127.0.0.1:18800/json/version", timeout=5).read().decode()
    return json.loads(data)["webSocketDebuggerUrl"]


def pick_rrz_frame(page):
    for f in page.frames:
        if "admin-vue.rrzu.com" in (f.url or "") or f.name == "rrzuji":
            return f
    return None


def close_popups(page):
    for txt in ["跳过", "确认", "我知道了", "暂不", "关闭", "×"]:
        try:
            page.get_by_text(txt, exact=False).first.click(timeout=500)
        except Exception:
            pass


def ensure_login(page):
    page.goto(ADMIN_LIST, wait_until="domcontentloaded")
    time.sleep(2)
    if "server-login" in page.url or "auth" in page.url or "login" in page.url:
        page.goto(LOGIN_URL, wait_until="domcontentloaded")
        time.sleep(1)
        # 密码登录
        for t in ["密码登录", "账号密码登录"]:
            try:
                page.get_by_text(t).click(timeout=1000)
                break
            except Exception:
                pass
        # 填写账号密码
        filled = False
        for sel in ["input[placeholder*='手机号']", "input[type='text']"]:
            try:
                page.locator(sel).first.fill(USER, timeout=1000)
                filled = True
                break
            except Exception:
                pass
        for sel in ["input[placeholder*='密码']", "input[type='password']"]:
            try:
                page.locator(sel).first.fill(PWD, timeout=1000)
                break
            except Exception:
                pass
        # 协议勾选
        try:
            page.locator("input[type='checkbox']").first.check(timeout=1000)
        except Exception:
            pass
        # 登录
        clicked = False
        try:
            page.evaluate("""() => {
              const btn = [...document.querySelectorAll('button')].find(b => /登录|登 录/.test(b.innerText||''));
              if (btn) btn.click();
            }""")
            clicked = True
        except Exception:
            pass
        if not clicked:
            for t in ["登录", "登 录"]:
                try:
                    page.get_by_role("button", name=re.compile(t)).click(timeout=1000)
                    break
                except Exception:
                    pass
        time.sleep(4)
        page.goto(ADMIN_LIST, wait_until="domcontentloaded")
        time.sleep(2)


def extract_failed(frame):
    js = r'''() => {
      const rows = [...document.querySelectorAll('tr')];
      const products = [];
      let current = null;
      for (const row of rows) {
        const text = (row.innerText || '').trim();
        const idMatch = text.match(/ID:(\d+)/);
        if (idMatch) {
          current = {id: idMatch[1], name: '', status: '', reason: ''};
          const nameEl = row.querySelector('a, .el-link, .goods-name, .title');
          if (nameEl) current.name = (nameEl.innerText || '').trim();
          if (text.includes('审核不通过')) current.status = '审核不通过';
          products.push(current);
        }
        if (current && /不通过原因/.test(text)) {
          current.reason = text.replace(/不再提示[\s\S]*$/, '').trim();
        }
      }
      return products.filter(p => p.status === '审核不通过' || p.reason);
    }'''
    return frame.evaluate(js)


def click_edit_for(frame, pid):
    # 通过包含ID的行找“修改商品”按钮
    js = f'''() => {{
      const rows = [...document.querySelectorAll('tr')];
      for (const row of rows) {{
        const txt = row.innerText || '';
        if (txt.includes('ID:{pid}')) {{
          const btn = [...row.querySelectorAll('button, a, span')].find(el => /修改商品|修改/.test(el.innerText||''));
          if (btn) {{ btn.click(); return 'clicked'; }}
        }}
      }}
      const all = [...document.querySelectorAll('button, a, span')].filter(el => /修改商品/.test(el.innerText||''));
      if (all.length) {{ all[0].click(); return 'fallback'; }}
      return 'not_found';
    }}'''
    return frame.evaluate(js)


def apply_fixes_in_frame(frame):
    js = '''() => {
      const banMap = {
        '租赁': '租用', '出租': '提供使用', '免押': '', '免息': '', '分期': '', '最便宜': '', '最低价': ''
      };
      const out = {replaced:0, titleBefore:'', titleAfter:'', packageRenamed:0, specHeaderFixed:0};
      const fields = [...document.querySelectorAll('input, textarea, [contenteditable="true"]')];
      function getv(el){ return el.value !== undefined ? el.value : (el.innerText || ''); }
      function setv(el, v){
        if (el.value !== undefined) {
          el.value = v;
          el.dispatchEvent(new Event('input', {bubbles:true}));
          el.dispatchEvent(new Event('change', {bubbles:true}));
        } else {
          el.innerText = v;
          el.dispatchEvent(new Event('input', {bubbles:true}));
        }
      }
      for (const el of fields) {
        let v = getv(el);
        if (!v) continue;
        let nv = v;
        for (const [k, r] of Object.entries(banMap)) nv = nv.split(k).join(r);
        if (nv !== v) { setv(el, nv); out.replaced++; }
      }

      const titleEl = fields.find(el => /标题/.test((el.placeholder||'') + ' ' + (el.getAttribute('aria-label')||''))) || fields[0];
      if (titleEl) {
        let t = getv(titleEl) || '';
        out.titleBefore = t;
        if (!/^90新/.test(t)) t = '90新 ' + t;
        // 去禁止词
        for (const [k, r] of Object.entries(banMap)) t = t.split(k).join(r);
        // 型号兜底
        if (!/[A-Za-z]\d|\d[A-Za-z]|\d{2,}/.test(t)) t += ' 型号版';
        t = t.replace(/\s+/g, ' ').trim();
        setv(titleEl, t);
        out.titleAfter = t;
      }

      for (const el of fields) {
        let v = getv(el) || '';
        if (/套餐\d*|租赁/.test(v) && v.length <= 12) {
          setv(el, v.replace(/套餐\d*/g,'租完归还').replace(/租赁/g,'租用'));
          out.packageRenamed++;
        }
        if (v === '套餐') { setv(el, '型号'); out.specHeaderFixed++; }
      }
      return out;
    }'''
    return frame.evaluate(js)


def submit_review(page, frame):
    # 先在iframe找提交
    for target in (frame, page.main_frame):
        try:
            ok = target.evaluate('''() => {
              const btn = [...document.querySelectorAll('button, span')].find(el => /提交审核/.test(el.innerText||''));
              if (btn) { btn.click(); return true; }
              return false;
            }''')
            if ok:
                time.sleep(1)
                break
        except Exception:
            pass
    # 确认弹窗
    for target in (frame, page.main_frame):
        try:
            target.evaluate('''() => {
              const btn = [...document.querySelectorAll('button, span')].find(el => /确认|确定|提交/.test(el.innerText||''));
              if (btn) btn.click();
            }''')
        except Exception:
            pass
    time.sleep(2)


def run():
    ws = get_ws()
    result = {"cdp": "ok", "ws": ws, "failed": [], "processed": []}
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws)
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = None
        for pg in ctx.pages:
            if 'rrzu.com' in pg.url:
                page = pg
                break
        if page is None:
            page = ctx.new_page()

        ensure_login(page)
        close_popups(page)
        page.goto(ADMIN_LIST, wait_until="domcontentloaded")
        time.sleep(2)

        frame = pick_rrz_frame(page)
        if not frame:
            result["error"] = "未找到rrzuji iframe"
            print(json.dumps(result, ensure_ascii=False, indent=2)); return

        failed = extract_failed(frame)
        result["failed"] = failed

        for item in failed:
            pid = item.get("id")
            rec = {"id": pid, "name": item.get("name"), "reason": item.get("reason"), "status": "start"}
            try:
                before_pages = set(ctx.pages)
                click_ret = click_edit_for(frame, pid)
                rec["click"] = click_ret
                new_page = None
                try:
                    # 等待新标签
                    t0 = time.time()
                    while time.time() - t0 < 8:
                        now = set(ctx.pages)
                        diff = [p for p in now if p not in before_pages]
                        if diff:
                            new_page = diff[0]
                            break
                        time.sleep(0.2)
                except Exception:
                    pass
                if not new_page:
                    # 可能在当前页跳转
                    for p2 in ctx.pages:
                        if '/spu-view/create' in p2.url:
                            new_page = p2; break
                if not new_page:
                    rec["status"] = "failed_open_edit"
                    result["processed"].append(rec)
                    continue

                new_page.bring_to_front()
                time.sleep(2)
                edit_frame = pick_rrz_frame(new_page) or new_page.main_frame
                rec["fix"] = apply_fixes_in_frame(edit_frame)
                submit_review(new_page, edit_frame)
                rec["status"] = "submitted"
                # 关闭编辑页
                if new_page != page:
                    try: new_page.close()
                    except Exception: pass
                page.bring_to_front()
                time.sleep(1)
            except Exception as e:
                rec["status"] = "error"
                rec["error"] = str(e)
            result["processed"].append(rec)

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print(json.dumps({"cdp":"error", "error": str(e)}, ensure_ascii=False, indent=2))
