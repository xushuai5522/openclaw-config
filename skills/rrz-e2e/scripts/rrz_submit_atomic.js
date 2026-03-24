/**
 * rrz_submit_atomic.js
 *
 * 目标：在同一脚本内完成“定位 → 可选上传 → 写值 → 保存草稿/提交审核”的原子提交流程。
 *
 * 依赖：
 * - 先注入 rrz_vue_locate.js
 * - submit 前建议注入 rrz_gate.js
 * - 如需上传图片，再注入 rrz_upload.js
 */
(function () {
  function ensure(condition, msg) {
    if (!condition) throw new Error(msg);
  }

  function clone(v) {
    return JSON.parse(JSON.stringify(v));
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function normalizeImages(items) {
    if (!Array.isArray(items)) return [];
    return items.map((item, idx) => {
      if (typeof item === 'string') {
        return { url: item, name: `rrz_${idx + 1}.jpg` };
      }
      if (item && typeof item === 'object') {
        if (item.url) return item;
        if (item.picUrl) return { ...item, url: item.picUrl };
      }
      return item;
    }).filter(Boolean);
  }

  async function uploadIfNeeded(uploadItems) {
    if (!Array.isArray(uploadItems) || !uploadItems.length) return [];
    const base64Items = uploadItems.filter(x => x && x.base64);
    if (!base64Items.length) return normalizeImages(uploadItems);
    ensure(window.rrzUpload, '存在 base64 图片，但 rrzUpload 未注入');

    const result = [];
    for (const item of uploadItems) {
      if (item && item.url) {
        result.push(item);
        continue;
      }
      if (!item || !item.base64) continue;
      const suffix = item.suffix || 'jpg';
      const uploaded = await window.rrzUploadOne(item.base64, suffix);
      ensure(uploaded && uploaded.done && uploaded.url, '图片上传失败');
      result.push({
        url: uploaded.url,
        name: item.name || `rrz_${result.length + 1}.${suffix}`,
        path: uploaded.path || ''
      });
    }
    return normalizeImages(result);
  }

  function patchTitle(formModel, payload) {
    if (!payload.title) return;
    const nextTitle = payload.autoTruncateTitle && payload.title.length > 60
      ? payload.title.slice(0, 60)
      : payload.title;
    let patched = false;
    if ('name' in formModel) {
      formModel.name = nextTitle;
      patched = true;
    }
    if ('title' in formModel) {
      formModel.title = nextTitle;
      patched = true;
    }
    if ('goodsName' in formModel) {
      formModel.goodsName = nextTitle;
      patched = true;
    }
    if (!patched) {
      const input = document.querySelector('input[placeholder*="30个字"]') || document.querySelector('input[maxlength="30"]');
      if (input) {
        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
        if (setter) setter.call(input, nextTitle);
        else input.value = nextTitle;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: 'End' }));
      }
    }
  }

  function patchDetails(formModel, payload) {
    if (typeof payload.details !== 'string') return;
    formModel.details = payload.details;
  }

  function patchImages(formModel, mainImages, descImages) {
    if (mainImages && mainImages.length) {
      formModel.images = clone(mainImages);
      if ('picList' in formModel) formModel.picList = clone(mainImages);
      if ('imageLength' in formModel) formModel.imageLength = mainImages.length;
    }
    if (descImages && descImages.length) {
      formModel.imagesJsonTwo = clone(descImages);
      if ('descPicList' in formModel) formModel.descPicList = clone(descImages);
    }
  }

  function patchRows(rows, payloadRows) {
    if (!Array.isArray(payloadRows) || !payloadRows.length) return;
    ensure(Array.isArray(rows), 'sellTableData 不是数组');
    ensure(payloadRows.length <= rows.length, 'sellTableData 行数不匹配');
    payloadRows.forEach((patch, idx) => Object.assign(rows[idx], patch));
  }

  function findButton(label) {
    const nodes = Array.from(document.querySelectorAll('button, .ant-btn, .el-button, [role="button"]'));
    return nodes.find(el => new RegExp(label).test((el.innerText || el.textContent || '').trim()));
  }

  function toastTexts() {
    const selectors = ['.ant-message-notice-content', '.el-message__content', '.ant-notification-notice', '.el-notification__content'];
    const texts = [];
    for (const sel of selectors) {
      for (const el of document.querySelectorAll(sel)) {
        const text = (el.innerText || el.textContent || '').trim();
        if (text) texts.push(text);
      }
    }
    return texts.slice(0, 20);
  }

  async function clickAction(kind) {
    const label = kind === 'submitReview' ? '提交审核' : '保存草稿';
    const btn = findButton(label);
    if (!btn) return { clicked: false, reason: `${kind}-button-not-found` };
    btn.click();
    await sleep(1500);
    const confirm = findButton('确 定|确定');
    if (confirm) {
      confirm.click();
      await sleep(1200);
    }
    return { clicked: true, kind, toasts: toastTexts() };
  }

  function buildSnapshot(formModel, rows) {
    return {
      title: formModel.name || formModel.title || null,
      detailsLength: typeof formModel.details === 'string' ? formModel.details.length : null,
      imagesLength: Array.isArray(formModel.images) ? formModel.images.length : 0,
      imagesJsonTwoLength: Array.isArray(formModel.imagesJsonTwo) ? formModel.imagesJsonTwo.length : 0,
      firstRow: rows && rows[0] ? clone(rows[0]) : null,
      secondRow: rows && rows[1] ? clone(rows[1]) : null
    };
  }

  function normalizeAuditStatus(status) {
    return String(status || '').trim().toLowerCase();
  }

  function evaluateAuditBlock(payload) {
    const audit = payload.auditResult || null;
    const status = normalizeAuditStatus(payload.auditStatus || audit?.status);
    const blockingIssues = Array.isArray(audit?.blocking_issues) ? audit.blocking_issues : [];
    const allowSubmitOnWarning = payload.allowSubmitOnWarning !== false;

    if (!audit && payload.requireAuditBeforeSubmit) {
      return {
        blocked: true,
        reason: 'audit-required-but-missing',
        status: 'missing'
      };
    }
    if (status === 'block' || status === 'blocked' || blockingIssues.length > 0) {
      return {
        blocked: true,
        reason: 'audit-blocked-submit',
        status: status || 'block',
        blockCount: blockingIssues.length,
        audit
      };
    }
    if ((status === 'warning' || status === 'pass_with_warning') && !allowSubmitOnWarning) {
      return {
        blocked: true,
        reason: 'audit-warning-blocked-by-policy',
        status,
        warningCount: Array.isArray(audit?.warnings) ? audit.warnings.length : null,
        audit
      };
    }
    return {
      blocked: false,
      reason: 'audit-passed',
      status: status || (audit ? 'pass' : 'missing'),
      audit
    };
  }

  window.rrzSubmitAtomic = async function (payload) {
    ensure(window.rrzLocateVueState, 'rrzLocateVueState 未注入');
    const located = window.rrzLocateVueState();
    ensure(located.formFound, '未找到商品信息表单 model');
    ensure(located.pricingFound, '未找到销售规格 sellTableData');

    const formModel = located.formModel;
    const rows = located.sellTableData;

    const mainImages = await uploadIfNeeded(payload.mainImages || []);
    const descImages = await uploadIfNeeded(payload.descImages || []);

    patchTitle(formModel, payload);
    patchDetails(formModel, payload);
    patchImages(formModel, mainImages, descImages);
    patchRows(rows, payload.sellTableData);

    await sleep(300);
    const afterPatch = window.rrzLocateVueState();
    const gatePayload = {
      ...payload,
      mainImages: mainImages.length ? mainImages : (payload.mainImages || []),
      descImages: descImages.length ? descImages : (payload.descImages || [])
    };
    const gateReport = window.rrzRunGate ? window.rrzRunGate(gatePayload) : null;
    const auditDecision = evaluateAuditBlock(payload);

    let action = { clicked: false, reason: 'skipped' };
    if (payload.submitReview) {
      if (auditDecision.blocked) {
        action = {
          clicked: false,
          blocked: true,
          reason: auditDecision.reason,
          auditStatus: auditDecision.status,
          auditBlockCount: auditDecision.blockCount || 0,
          auditWarningCount: auditDecision.warningCount || 0
        };
      } else if (gateReport && !gateReport.ok) {
        action = {
          clicked: false,
          blocked: true,
          reason: 'gate-blocked-submit',
          gateStatus: gateReport.status,
          blockCount: gateReport.summary?.blockCount || 0
        };
      } else {
        action = await clickAction('submitReview');
      }
    } else if (payload.saveDraft) {
      action = await clickAction('saveDraft');
    }
    await sleep(800);

    return {
      ok: !action.blocked,
      meta: located.meta,
      snapshot: buildSnapshot(afterPatch.formModel || formModel, afterPatch.sellTableData || rows),
      audit: auditDecision,
      gate: gateReport,
      action,
      toastTexts: toastTexts()
    };
  };

  console.log('✅ rrzSubmitAtomic 已注入');
})();
