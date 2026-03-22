/**
 * rrz_capture_state.js
 *
 * 目标：失败时统一抓取人人租编辑页关键状态，减少“知道没成但证据不全”。
 * 用法：在 iframe[name=rrzuji] 内注入后执行
 *   window.rrzCaptureState({ lastAction: 'saveDraft' })
 */
(function () {
  function safeClone(v) {
    try { return JSON.parse(JSON.stringify(v)); } catch { return null; }
  }

  function textOf(selector) {
    return Array.from(document.querySelectorAll(selector))
      .map(el => (el.innerText || el.textContent || '').trim())
      .filter(Boolean)
      .slice(0, 20);
  }

  function gatherButtons() {
    return Array.from(document.querySelectorAll('button, .ant-btn, .el-button, [role="button"]'))
      .map(el => (el.innerText || el.textContent || '').trim())
      .filter(Boolean)
      .slice(0, 50);
  }

  window.rrzCaptureState = function (extra) {
    const located = window.rrzLocateVueState ? window.rrzLocateVueState() : null;
    const text = (document.body && document.body.innerText) ? document.body.innerText.slice(0, 5000) : '';
    const formModel = located && located.formModel ? safeClone(located.formModel) : null;
    const sellTableData = located && located.sellTableData ? safeClone(located.sellTableData) : null;

    return {
      href: location.href,
      title: document.title,
      time: new Date().toISOString(),
      buttons: gatherButtons(),
      gateReport: window.__RRZ_GATE_LAST_REPORT__ || null,
      toastTexts: [
        ...textOf('.ant-message-notice-content'),
        ...textOf('.el-message__content'),
        ...textOf('.ant-notification-notice'),
        ...textOf('.el-notification__content')
      ].slice(0, 20),
      located: located ? {
        formFound: located.formFound,
        pricingFound: located.pricingFound,
        meta: located.meta,
        summary: located.summary
      } : null,
      formModel,
      sellTableData,
      bodyText: text,
      extra: extra || null
    };
  };

  console.log('✅ rrzCaptureState 已注入');
})();
