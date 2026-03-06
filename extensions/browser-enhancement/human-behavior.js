// OpenClaw 人类行为模拟脚本
// 贝塞尔曲线鼠标轨迹 + 自然输入节奏

(function() {
  'use strict';

  // 贝塞尔曲线生成器（三次贝塞尔）
  function bezierCurve(start, end, controlPoint1, controlPoint2, steps) {
    const points = [];
    for (let t = 0; t <= 1; t += 1 / steps) {
      const x = Math.pow(1 - t, 3) * start.x +
                3 * Math.pow(1 - t, 2) * t * controlPoint1.x +
                3 * (1 - t) * Math.pow(t, 2) * controlPoint2.x +
                Math.pow(t, 3) * end.x;
      const y = Math.pow(1 - t, 3) * start.y +
                3 * Math.pow(1 - t, 2) * t * controlPoint1.y +
                3 * (1 - t) * Math.pow(t, 2) * controlPoint2.y +
                Math.pow(t, 3) * end.y;
      points.push({ x: Math.round(x), y: Math.round(y) });
    }
    return points;
  }

  // 生成自然鼠标轨迹
  window.humanMouseMove = function(targetElement) {
    const rect = targetElement.getBoundingClientRect();
    const start = { x: window.lastMouseX || 0, y: window.lastMouseY || 0 };
    const end = { 
      x: rect.left + rect.width / 2, 
      y: rect.top + rect.height / 2 
    };
    
    // 随机控制点（模拟手臂弧线）
    const cp1 = {
      x: start.x + (end.x - start.x) * 0.3 + (Math.random() - 0.5) * 100,
      y: start.y + (end.y - start.y) * 0.3 + (Math.random() - 0.5) * 100
    };
    const cp2 = {
      x: start.x + (end.x - start.x) * 0.7 + (Math.random() - 0.5) * 100,
      y: start.y + (end.y - start.y) * 0.7 + (Math.random() - 0.5) * 100
    };
    
    const steps = Math.max(20, Math.floor(Math.hypot(end.x - start.x, end.y - start.y) / 10));
    const points = bezierCurve(start, end, cp1, cp2, steps);
    
    // 模拟鼠标移动事件
    let i = 0;
    const interval = setInterval(() => {
      if (i >= points.length) {
        clearInterval(interval);
        targetElement.click();
        return;
      }
      const point = points[i];
      window.lastMouseX = point.x;
      window.lastMouseY = point.y;
      
      const event = new MouseEvent('mousemove', {
        clientX: point.x,
        clientY: point.y,
        bubbles: true
      });
      document.dispatchEvent(event);
      i++;
    }, 5 + Math.random() * 5); // 5-10ms间隔
  };

  // 自然输入模拟
  window.humanType = async function(element, text) {
    element.focus();
    
    for (let i = 0; i < text.length; i++) {
      const char = text[i];
      
      // 随机打字错误（5%概率）
      if (Math.random() < 0.05 && i > 0) {
        const wrongChar = String.fromCharCode(char.charCodeAt(0) + (Math.random() > 0.5 ? 1 : -1));
        element.value += wrongChar;
        element.dispatchEvent(new Event('input', { bubbles: true }));
        await sleep(50 + Math.random() * 100);
        
        // 退格修正
        element.value = element.value.slice(0, -1);
        element.dispatchEvent(new Event('input', { bubbles: true }));
        await sleep(50 + Math.random() * 100);
      }
      
      // 正常输入
      element.value += char;
      element.dispatchEvent(new Event('input', { bubbles: true }));
      
      // 自然延迟（50-300ms）
      const delay = 50 + Math.random() * 250;
      await sleep(delay);
    }
    
    element.dispatchEvent(new Event('change', { bubbles: true }));
  };

  // 自然滚动模拟
  window.humanScroll = async function(targetY) {
    const start = window.scrollY;
    const distance = targetY - start;
    const segments = Math.floor(Math.abs(distance) / 100) + 1;
    
    for (let i = 0; i < segments; i++) {
      const progress = (i + 1) / segments;
      const easeProgress = 1 - Math.pow(1 - progress, 3); // 缓动函数
      const currentY = start + distance * easeProgress;
      
      window.scrollTo(0, currentY);
      
      // 随机暂停（模拟阅读）
      if (Math.random() < 0.3) {
        await sleep(200 + Math.random() * 500);
      }
      
      // 偶尔回弹
      if (Math.random() < 0.1) {
        window.scrollTo(0, currentY - 20);
        await sleep(100);
        window.scrollTo(0, currentY);
      }
      
      await sleep(50 + Math.random() * 100);
    }
  };

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  console.log('[OpenClaw] 人类行为模拟脚本已注入');
})();
