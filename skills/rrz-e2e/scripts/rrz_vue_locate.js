/**
 * rrz_vue_locate.js
 *
 * 目标：按特征动态定位人人租编辑页里的关键 Vue 数据节点，
 * 禁止依赖固定 uid / 某次页面树结构。
 *
 * 支持：
 * - Vue 3（当前真实页面）优先：从 #app.__vue_app__ 组件树动态扫描
 * - Vue 2 / __vue__ 作为兜底
 *
 * 用法：在 iframe[name=rrzuji] 内 evaluate 注入后执行：
 *   const state = window.rrzLocateVueState();
 */
(function () {
  function isObj(v) {
    return !!v && typeof v === 'object';
  }

  function clone(v) {
    try { return JSON.parse(JSON.stringify(v)); } catch { return null; }
  }

  function nameOf(type) {
    if (!type) return null;
    if (typeof type === 'string') return type;
    return type.name || type.__name || type.__file || null;
  }

  function summarizeModel(model) {
    if (!isObj(model)) return null;
    return {
      keys: Object.keys(model).slice(0, 40),
      imagesLength: Array.isArray(model.images) ? model.images.length : null,
      imagesJsonTwoLength: Array.isArray(model.imagesJsonTwo) ? model.imagesJsonTwo.length : null,
      hasDetails: typeof model.details === 'string',
      title: typeof model.name === 'string' ? model.name : (typeof model.title === 'string' ? model.title : null)
    };
  }

  function summarizeRows(rows) {
    const first = Array.isArray(rows) && rows[0] ? rows[0] : null;
    return {
      rowCount: Array.isArray(rows) ? rows.length : null,
      firstRowKeys: first ? Object.keys(first).slice(0, 30) : null,
      firstRowDeposit: first && 'deposit' in first ? first.deposit : null,
      firstRowBuyoutPrice: first && 'buyoutPrice' in first ? first.buyoutPrice : null
    };
  }

  function getVue3RootInstance() {
    const appEl = document.querySelector('#app');
    const app = appEl && appEl.__vue_app__;
    return app && app._container && app._container._vnode && app._container._vnode.component
      ? app._container._vnode.component
      : null;
  }

  function locateByVue3Tree() {
    const root = getVue3RootInstance();
    const app = document.querySelector('#app')?.__vue_app__;
    if (!root && !app) return null;

    let bestForm = null;
    let bestPricing = null;
    const seen = new WeakSet();
    const queue = [
      { path: 'rootComponent', value: root },
      { path: 'app', value: app },
      { path: 'routeInstance', value: app?.config?.globalProperties?.$route?.matched?.[0]?.instances?.default?._ }
    ].filter(x => x.value && typeof x.value === 'object');

    function scoreForm(candidate) {
      if (!isObj(candidate)) return -1;
      let score = 0;
      if (Array.isArray(candidate.images)) score += 3;
      if (Array.isArray(candidate.imagesJsonTwo)) score += 3;
      if (typeof candidate.details === 'string') score += 2;
      if (typeof candidate.name === 'string' || typeof candidate.title === 'string') score += 1;
      if (Array.isArray(candidate.images) && Array.isArray(candidate.imagesJsonTwo)) score += 2;
      return score;
    }

    function scorePricing(rows) {
      if (!Array.isArray(rows)) return -1;
      let score = rows.length > 0 ? 3 : 1;
      const first = isObj(rows[0]) ? rows[0] : null;
      if (!first) return rows.length ? score : -1;
      if ('deposit' in first) score += 2;
      if ('buyoutPrice' in first) score += 2;
      if ('oneMonth' in first || 'threeMonth' in first || 'sixMonth' in first || 'oneYear' in first) score += 2;
      return score;
    }

    while (queue.length) {
      const current = queue.shift();
      const value = current.value;
      if (!isObj(value) || seen.has(value)) continue;
      seen.add(value);

      const formScore = scoreForm(value);
      if (formScore >= 6 && (!bestForm || formScore > bestForm.score)) {
        bestForm = { path: current.path, score: formScore, model: value };
      }

      const pricingScore = scorePricing(value);
      if (pricingScore >= 6 && (!bestPricing || pricingScore > bestPricing.score)) {
        bestPricing = { path: current.path, score: pricingScore, sellTableData: value };
      }

      let keys = [];
      try { keys = Reflect.ownKeys(value).filter(k => typeof k === 'string'); } catch { continue; }
      for (const key of keys.slice(0, 160)) {
        let child;
        try { child = value[key]; } catch { continue; }
        if (isObj(child)) queue.push({ path: `${current.path}.${key}`, value: child });
      }
    }

    return {
      formModel: bestForm ? bestForm.model : null,
      sellTableData: bestPricing ? bestPricing.sellTableData : null,
      meta: {
        formPath: bestForm ? bestForm.path : null,
        formOwner: bestForm ? 'graph-search' : null,
        pricingPath: bestPricing ? bestPricing.path : null,
        pricingOwner: bestPricing ? 'graph-search' : null
      }
    };
  }

  function locateByVue2Fallback() {
    function walk(node, visit, depth = 0, maxDepth = 12) {
      if (!node || depth > maxDepth) return;
      visit(node, depth);
      const children = node.children || [];
      for (const child of children) walk(child, visit, depth + 1, maxDepth);
    }

    let formVm = null;
    let pricingVm = null;

    walk(document.body, (el) => {
      const vm = el.__vue__;
      if (!vm) return;
      const props = vm.$props || {};
      const data = vm.$data || {};

      if (!formVm) {
        const model = props.model || data.formData || data.model;
        if (isObj(model) && ('images' in model || 'imagesJsonTwo' in model || 'details' in model)) {
          formVm = vm;
        }
      }

      if (!pricingVm) {
        const sellTableData = data.sellTableData || props.sellTableData;
        if (Array.isArray(sellTableData) && sellTableData.length > 0) {
          pricingVm = vm;
        }
      }
    });

    return {
      formModel: formVm ? (formVm.$props?.model || formVm.$data?.formData || formVm.$data?.model || null) : null,
      sellTableData: pricingVm ? (pricingVm.$data?.sellTableData || pricingVm.$props?.sellTableData || null) : null,
      meta: {
        formPath: formVm ? 'vue2-form' : null,
        formOwner: formVm ? (formVm.$options?.name || formVm.$options?._componentTag || null) : null,
        pricingPath: pricingVm ? 'vue2-pricing' : null,
        pricingOwner: pricingVm ? (pricingVm.$options?.name || formVm?.$options?._componentTag || null) : null
      }
    };
  }

  window.rrzLocateVueState = function () {
    const vue3 = locateByVue3Tree();
    const fallback = (!vue3 || (!vue3.formModel && !vue3.sellTableData)) ? locateByVue2Fallback() : null;
    const picked = (vue3 && (vue3.formModel || vue3.sellTableData)) ? vue3 : (fallback || { formModel: null, sellTableData: null, meta: {} });

    return {
      ok: !!(picked.formModel || picked.sellTableData),
      vueVersion: document.querySelector('#app')?.__vue_app__ ? 3 : 2,
      formFound: !!picked.formModel,
      pricingFound: !!picked.sellTableData,
      formModel: picked.formModel || null,
      sellTableData: picked.sellTableData || null,
      meta: picked.meta || {},
      summary: {
        formModel: summarizeModel(picked.formModel),
        pricing: summarizeRows(picked.sellTableData)
      }
    };
  };

  console.log('✅ rrzLocateVueState 已注入');
})();
