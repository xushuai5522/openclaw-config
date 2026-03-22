/**
 * rrz_gate.js
 *
 * 目标：为人人租提审前增加最小可用规则 gate。
 * 结果分三类：pass / warning / block
 * - block：允许保存草稿，不允许 submit
 * - warning：提示但不阻塞 submit
 * - pass：可进入 submit
 *
 * 依赖：建议先注入 rrz_vue_locate.js
 */
(function () {
  const TITLE_MAX = 60;
  const PACKAGE_ALLOWED = [
    '租完归还',
    '可归还',
    '到期可归还/续租',
    '到期可归还',
    '续租',
    '随租随还'
  ];
  const FORBIDDEN_WORDS = ['租赁', '出租', '免押', '免息', '分期'];
  const WARNING_WORDS = ['测试', '最'];

  function isObj(v) {
    return !!v && typeof v === 'object';
  }

  function clone(v) {
    try { return JSON.parse(JSON.stringify(v)); } catch { return null; }
  }

  function pushIssue(list, level, code, message, extra) {
    list.push({ level, code, message, extra: extra || null });
  }

  function normalizeText(v) {
    return String(v || '').replace(/\s+/g, ' ').trim();
  }

  function stripSpaces(v) {
    return normalizeText(v).replace(/\s+/g, '').toUpperCase();
  }

  function titleText(formModel, payload) {
    return normalizeText(payload?.title || formModel?.name || formModel?.title || '');
  }

  function detailsHtml(formModel, payload) {
    return String(payload?.details ?? formModel?.details ?? '');
  }

  function mainImages(formModel, payload) {
    const items = payload?.mainImages || formModel?.images || formModel?.picList || [];
    return Array.isArray(items) ? items.filter(Boolean) : [];
  }

  function descImages(formModel, payload) {
    const items = payload?.descImages || formModel?.imagesJsonTwo || formModel?.descPicList || [];
    return Array.isArray(items) ? items.filter(Boolean) : [];
  }

  function extractModelCandidates(payload, formModel, rows) {
    const values = [];
    const fromPayload = [
      payload?.model,
      payload?.productModel,
      payload?.actualModel,
      payload?.expectedModel
    ];
    const fromForm = [
      formModel?.model,
      formModel?.goodsModel,
      formModel?.specModel,
      formModel?.subTitle
    ];
    const fromRows = Array.isArray(rows)
      ? rows.flatMap(r => [r?.name, r?.model, r?.specValue, r?.spec, r?.configName])
      : [];

    for (const item of [...fromPayload, ...fromForm, ...fromRows]) {
      const text = normalizeText(item);
      if (text && !values.includes(text)) values.push(text);
    }
    return values;
  }

  function hasModelInTitle(title, candidates) {
    const normalizedTitle = stripSpaces(title);
    return candidates.some(c => {
      const token = stripSpaces(c);
      return token && normalizedTitle.includes(token);
    });
  }

  function hasModelInDetails(details, candidates) {
    const normalized = stripSpaces(details.replace(/<[^>]+>/g, ' '));
    return candidates.some(c => {
      const token = stripSpaces(c);
      return token && normalized.includes(token);
    });
  }

  function descriptionContainsImage(details, descImagesList) {
    if (/<img\b/i.test(details)) return true;
    if (Array.isArray(descImagesList) && descImagesList.length > 0) return true;
    return false;
  }

  function packageNames(rows) {
    if (!Array.isArray(rows)) return [];
    const keys = ['name', 'specValue', 'configName', 'packageName', 'title'];
    return rows.map((row) => {
      for (const key of keys) {
        const text = normalizeText(row?.[key]);
        if (text) return text;
      }
      return '';
    }).filter(Boolean);
  }

  function headerLooksInvalid(formModel, payload) {
    const headers = [];
    const fromPayload = payload?.specHeaders;
    const fromForm = formModel?.sellTableTitle || formModel?.specTitle || formModel?.tableHeader || formModel?.skuHeader;
    if (Array.isArray(fromPayload)) headers.push(...fromPayload.map(normalizeText));
    else if (typeof fromPayload === 'string') headers.push(normalizeText(fromPayload));
    if (Array.isArray(fromForm)) headers.push(...fromForm.map(normalizeText));
    else if (typeof fromForm === 'string') headers.push(normalizeText(fromForm));
    return headers.some(h => h === '套餐' || /^套餐[名称规格]?$/i.test(h));
  }

  function priceFieldSummary(rows) {
    const requiredKeys = ['deposit', 'buyoutPrice'];
    const optionalRentKeys = ['oneMonth', 'threeMonth', 'sixMonth', 'oneYear', 'monthPrice', 'price'];
    const missing = [];
    if (!Array.isArray(rows) || !rows.length) {
      return { rowCount: 0, missing: ['sellTableData'], rows: [] };
    }
    const rowSummary = rows.map((row, idx) => {
      const rowMissing = [];
      for (const key of requiredKeys) {
        const value = row?.[key];
        if (value === '' || value === null || value === undefined) rowMissing.push(key);
      }
      const hasAnyRent = optionalRentKeys.some(key => row?.[key] !== '' && row?.[key] !== null && row?.[key] !== undefined);
      if (!hasAnyRent) rowMissing.push('rentPrice');
      if (rowMissing.length) missing.push({ row: idx, fields: rowMissing });
      return {
        row: idx,
        name: normalizeText(row?.name || row?.specValue || row?.configName || ''),
        deposit: row?.deposit ?? null,
        buyoutPrice: row?.buyoutPrice ?? null,
        hasRentPrice: hasAnyRent
      };
    });
    return { rowCount: rows.length, missing, rows: rowSummary };
  }

  function truncateTitle(title, max) {
    if (title.length <= max) return { changed: false, title };
    return { changed: true, title: title.slice(0, max) };
  }

  window.rrzRunGate = function (payload) {
    const located = window.rrzLocateVueState ? window.rrzLocateVueState() : { formModel: null, sellTableData: null, formFound: false, pricingFound: false, meta: {} };
    const formModel = located.formModel || {};
    const rows = located.sellTableData || [];
    const issues = [];

    const title = titleText(formModel, payload);
    const details = detailsHtml(formModel, payload);
    const main = mainImages(formModel, payload);
    const desc = descImages(formModel, payload);
    const modelCandidates = extractModelCandidates(payload, formModel, rows);
    const pkgNames = packageNames(rows);
    const priceSummary = priceFieldSummary(rows);
    const titleTrim = truncateTitle(title, TITLE_MAX);
    const titleForCheck = titleTrim.title;

    if (!title) {
      pushIssue(issues, 'block', 'TITLE_EMPTY', '标题为空');
    } else {
      if (titleTrim.changed) {
        pushIssue(issues, 'warning', 'TITLE_TRUNCATED', `标题超过 ${TITLE_MAX} 字，建议截断`, { originalLength: title.length, truncated: titleTrim.title });
      }
      if (!modelCandidates.length) {
        pushIssue(issues, 'warning', 'MODEL_CANDIDATE_EMPTY', '未提取到可靠型号候选，无法做强一致校验');
      } else {
        if (!hasModelInTitle(titleForCheck, modelCandidates)) {
          pushIssue(issues, 'block', 'MODEL_NOT_IN_TITLE', '标题未包含可识别型号', { modelCandidates });
        }
        if (!hasModelInDetails(details, modelCandidates)) {
          pushIssue(issues, 'warning', 'MODEL_NOT_IN_DETAILS', '描述中未识别到型号，建议补齐型号文本', { modelCandidates });
        }
      }
    }

    for (const word of FORBIDDEN_WORDS) {
      if (title.includes(word) || details.includes(word) || pkgNames.some(name => name.includes(word))) {
        pushIssue(issues, 'block', 'FORBIDDEN_WORD', `存在禁表述：${word}`, { word });
      }
    }
    for (const word of WARNING_WORDS) {
      if (title.includes(word) || details.includes(word) || pkgNames.some(name => name.includes(word))) {
        pushIssue(issues, 'warning', 'RISKY_WORD', `存在高风险词：${word}，建议改写`, { word });
      }
    }

    if (!main.length) pushIssue(issues, 'block', 'MAIN_IMAGES_MISSING', '主图缺失');
    if (!desc.length) pushIssue(issues, 'block', 'DESC_IMAGES_MISSING', '描述图缺失');
    if (!descriptionContainsImage(details, desc)) pushIssue(issues, 'block', 'DETAILS_NO_IMAGE', '商品描述未包含图片');

    if (!pkgNames.length) {
      pushIssue(issues, 'block', 'PACKAGE_NAME_MISSING', '未识别到套餐名称');
    } else {
      const invalidNames = pkgNames.filter(name => !PACKAGE_ALLOWED.some(allowed => name.includes(allowed)));
      if (invalidNames.length) {
        pushIssue(issues, 'block', 'PACKAGE_NAME_INVALID', '存在不符合模板的套餐命名', { invalidNames, allowed: PACKAGE_ALLOWED });
      }
    }

    if (headerLooksInvalid(formModel, payload)) {
      pushIssue(issues, 'block', 'SPEC_HEADER_INVALID', '销售规格表头仍含“套餐”');
    }

    if (!located.pricingFound) {
      pushIssue(issues, 'block', 'PRICING_NOT_FOUND', '未定位到销售规格 sellTableData');
    }
    if (priceSummary.rowCount === 0) {
      pushIssue(issues, 'block', 'PRICE_ROWS_EMPTY', '销售规格为空');
    } else if (priceSummary.missing.length) {
      pushIssue(issues, 'block', 'PRICE_FIELDS_MISSING', '关键价格字段不完整', { missing: priceSummary.missing });
    }

    const blocked = issues.filter(x => x.level === 'block');
    const warnings = issues.filter(x => x.level === 'warning');
    const report = {
      ok: blocked.length === 0,
      status: blocked.length ? 'blocked' : (warnings.length ? 'pass_with_warning' : 'passed'),
      summary: {
        pass: blocked.length === 0,
        blockCount: blocked.length,
        warningCount: warnings.length,
        title: titleForCheck,
        titleOriginal: title || null,
        titleLength: title.length,
        titleTruncated: titleTrim.changed ? titleTrim.title : null,
        modelCandidates,
        mainImageCount: main.length,
        descImageCount: desc.length,
        packageNames: pkgNames,
        priceSummary,
        locateMeta: located.meta || {}
      },
      issues,
      snapshot: {
        formFound: !!located.formFound,
        pricingFound: !!located.pricingFound,
        formModel: clone({
          title: formModel?.name || formModel?.title || null,
          model: formModel?.model || formModel?.goodsModel || null,
          imagesLength: Array.isArray(formModel?.images) ? formModel.images.length : 0,
          imagesJsonTwoLength: Array.isArray(formModel?.imagesJsonTwo) ? formModel.imagesJsonTwo.length : 0,
          detailsLength: typeof formModel?.details === 'string' ? formModel.details.length : 0
        }),
        firstRows: clone(Array.isArray(rows) ? rows.slice(0, 2) : [])
      }
    };

    window.__RRZ_GATE_LAST_REPORT__ = report;
    return report;
  };

  console.log('✅ rrzRunGate 已注入');
})();