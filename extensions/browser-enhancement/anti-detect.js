// OpenClaw 浏览器反检测增强脚本
// 基于 2026-03-04 技术方案

(function() {
  'use strict';

  // 1. 隐藏 WebDriver 特征
  Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
  });

  // 2. Chrome 特征伪装
  window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {}
  };

  // 3. Permissions API 伪装
  const originalQuery = window.navigator.permissions.query;
  window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
      Promise.resolve({ state: Notification.permission }) :
      originalQuery(parameters)
  );

  // 4. Plugins 伪装
  Object.defineProperty(navigator, 'plugins', {
    get: () => [
      {
        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
        description: "Portable Document Format",
        filename: "internal-pdf-viewer",
        length: 1,
        name: "Chrome PDF Plugin"
      },
      {
        0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
        description: "Portable Document Format", 
        filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
        length: 1,
        name: "Chrome PDF Viewer"
      }
    ]
  });

  // 5. Languages 伪装
  Object.defineProperty(navigator, 'languages', {
    get: () => ['zh-CN', 'zh', 'en-US', 'en']
  });

  // 6. Canvas 指纹混淆
  const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
  HTMLCanvasElement.prototype.toDataURL = function(type) {
    const context = this.getContext('2d');
    const imageData = context.getImageData(0, 0, this.width, this.height);
    // 添加微小噪点（人眼不可见）
    for (let i = 0; i < imageData.data.length; i += 4) {
      imageData.data[i] += Math.floor(Math.random() * 3) - 1;
    }
    context.putImageData(imageData, 0, 0);
    return originalToDataURL.apply(this, arguments);
  };

  // 7. WebGL 指纹伪装
  const getParameter = WebGLRenderingContext.prototype.getParameter;
  WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
      return 'Intel Inc.';
    }
    if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
      return 'Intel Iris OpenGL Engine';
    }
    return getParameter.apply(this, arguments);
  };

  // 8. 硬件并发数伪装
  Object.defineProperty(navigator, 'hardwareConcurrency', {
    get: () => 8
  });

  // 9. 设备内存伪装
  Object.defineProperty(navigator, 'deviceMemory', {
    get: () => 8
  });

  // 10. Battery API 伪装
  if (navigator.getBattery) {
    const originalGetBattery = navigator.getBattery;
    navigator.getBattery = function() {
      return originalGetBattery.apply(this, arguments).then(battery => {
        Object.defineProperty(battery, 'charging', { get: () => true });
        Object.defineProperty(battery, 'chargingTime', { get: () => 0 });
        Object.defineProperty(battery, 'dischargingTime', { get: () => Infinity });
        Object.defineProperty(battery, 'level', { get: () => 1 });
        return battery;
      });
    };
  }

  console.log('[OpenClaw] 反检测脚本已注入');
})();
