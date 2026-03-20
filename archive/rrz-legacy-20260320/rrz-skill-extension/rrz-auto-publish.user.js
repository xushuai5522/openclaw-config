// ==UserScript==
// @name         人人租商品发布助手
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  自动填充商品信息、批量上传图片、一键发布
// @author       电子牛马
// @match        https://merchant.renrenzu.com/*
// @match        https://*.renrenzu.com/merchant/*
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_registerMenuCommand
// @grant        GM_addStyle
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    // ==================== 配置管理 ====================
    const CONFIG_KEY = 'rrz_publish_config';
    
    // 默认配置模板
    const DEFAULT_CONFIG = {
        templates: [
            {
                name: '默认模板',
                data: {
                    title: '',
                    category: '',
                    brand: '',
                    model: '',
                    deposit: '',
                    dailyRent: '',
                    description: '',
                    images: []
                }
            }
        ],
        currentTemplate: 0
    };

    // 加载配置
    function loadConfig() {
        const saved = GM_getValue(CONFIG_KEY);
        return saved ? JSON.parse(saved) : DEFAULT_CONFIG;
    }

    // 保存配置
    function saveConfig(config) {
        GM_setValue(CONFIG_KEY, JSON.stringify(config));
    }

    // ==================== Vue实例访问 ====================
    
    // 获取Vue实例（多种方式兼容）
    function getVueInstance(element) {
        if (!element) return null;
        
        // 方式1: __vue__ (Vue 2)
        if (element.__vue__) return element.__vue__;
        
        // 方式2: __vueParentComponent (Vue 3)
        if (element.__vueParentComponent) return element.__vueParentComponent;
        
        // 方式3: _vnode
        if (element._vnode && element._vnode.context) return element._vnode.context;
        
        // 方式4: 递归查找父元素
        if (element.parentElement) return getVueInstance(element.parentElement);
        
        return null;
    }

    // 查找根Vue实例
    function findRootVue() {
        const app = document.querySelector('#app') || document.querySelector('[data-v-app]');
        return getVueInstance(app);
    }

    // ==================== 表单填充 ====================
    
    // 智能填充输入框
    function fillInput(selector, value) {
        const input = document.querySelector(selector);
        if (!input) {
            console.warn(`未找到元素: ${selector}`);
            return false;
        }

        // 设置值
        input.value = value;
        
        // 触发Vue的input事件
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        
        // 触发Vue的v-model更新
        const vueInstance = getVueInstance(input);
        if (vueInstance && vueInstance.$forceUpdate) {
            vueInstance.$forceUpdate();
        }
        
        return true;
    }

    // 选择下拉框
    function selectOption(selector, value) {
        const select = document.querySelector(selector);
        if (!select) {
            console.warn(`未找到下拉框: ${selector}`);
            return false;
        }

        // 查找匹配的option
        const options = Array.from(select.options);
        const option = options.find(opt => 
            opt.value === value || 
            opt.text === value ||
            opt.text.includes(value)
        );

        if (option) {
            select.value = option.value;
            select.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        }

        console.warn(`未找到选项: ${value}`);
        return false;
    }

    // 填充富文本编辑器
    function fillRichText(selector, content) {
        const editor = document.querySelector(selector);
        if (!editor) {
            console.warn(`未找到富文本编辑器: ${selector}`);
            return false;
        }

        // 尝试多种富文本编辑器
        // 1. TinyMCE
        if (window.tinymce) {
            const ed = tinymce.get(editor.id);
            if (ed) {
                ed.setContent(content);
                return true;
            }
        }

        // 2. Quill
        if (editor.__quill) {
            editor.__quill.root.innerHTML = content;
            return true;
        }

        // 3. 直接设置innerHTML
        const contentDiv = editor.querySelector('.ql-editor') || 
                          editor.querySelector('[contenteditable]') ||
                          editor;
        contentDiv.innerHTML = content;
        contentDiv.dispatchEvent(new Event('input', { bubbles: true }));
        
        return true;
    }

    // ==================== 图片上传 ====================
    
    // 批量上传图片
    async function uploadImages(imageUrls) {
        console.log('开始上传图片:', imageUrls);
        
        // 查找上传按钮或输入框
        const uploadInput = document.querySelector('input[type="file"][accept*="image"]');
        if (!uploadInput) {
            console.error('未找到图片上传输入框');
            return false;
        }

        // 下载图片并转换为File对象
        const files = [];
        for (const url of imageUrls) {
            try {
                const response = await fetch(url);
                const blob = await response.blob();
                const filename = url.split('/').pop() || `image_${Date.now()}.jpg`;
                const file = new File([blob], filename, { type: blob.type });
                files.push(file);
            } catch (error) {
                console.error(`下载图片失败: ${url}`, error);
            }
        }

        if (files.length === 0) {
            console.error('没有成功下载任何图片');
            return false;
        }

        // 创建DataTransfer对象（模拟文件选择）
        const dataTransfer = new DataTransfer();
        files.forEach(file => dataTransfer.items.add(file));
        uploadInput.files = dataTransfer.files;

        // 触发change事件
        uploadInput.dispatchEvent(new Event('change', { bubbles: true }));
        
        console.log(`成功上传 ${files.length} 张图片`);
        return true;
    }

    // ==================== 自动填充主流程 ====================
    
    async function autoFillForm(config) {
        console.log('开始自动填充表单:', config);
        
        const data = config.data;
        let success = true;

        // 1. 填充基本信息
        if (data.title) {
            success &= fillInput('input[placeholder*="商品名称"]', data.title);
        }

        if (data.category) {
            success &= selectOption('select[placeholder*="分类"]', data.category);
        }

        if (data.brand) {
            success &= fillInput('input[placeholder*="品牌"]', data.brand);
        }

        if (data.model) {
            success &= fillInput('input[placeholder*="型号"]', data.model);
        }

        // 2. 填充价格信息
        if (data.deposit) {
            success &= fillInput('input[placeholder*="押金"]', data.deposit);
        }

        if (data.dailyRent) {
            success &= fillInput('input[placeholder*="日租金"]', data.dailyRent);
        }

        // 3. 填充商品描述
        if (data.description) {
            success &= fillRichText('.rich-text-editor', data.description);
        }

        // 4. 上传图片
        if (data.images && data.images.length > 0) {
            await uploadImages(data.images);
        }

        if (success) {
            showNotification('✅ 表单填充完成！', 'success');
        } else {
            showNotification('⚠️ 部分字段填充失败，请检查', 'warning');
        }

        return success;
    }

    // ==================== UI界面 ====================
    
    // 添加样式
    GM_addStyle(`
        #rrz-auto-panel {
            position: fixed;
            top: 50%;
            right: 20px;
            transform: translateY(-50%);
            z-index: 99999;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            padding: 16px;
            min-width: 280px;
            max-width: 400px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        #rrz-auto-panel.collapsed {
            width: 60px;
            min-width: 60px;
            padding: 12px;
        }

        #rrz-auto-panel.collapsed .panel-content {
            display: none;
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid #eee;
        }

        .panel-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }

        .panel-toggle {
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            padding: 4px;
            line-height: 1;
        }

        .panel-content {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .config-selector {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }

        .btn {
            padding: 10px 16px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-primary {
            background: #1890ff;
            color: white;
        }

        .btn-primary:hover {
            background: #40a9ff;
        }

        .btn-success {
            background: #52c41a;
            color: white;
        }

        .btn-success:hover {
            background: #73d13d;
        }

        .btn-secondary {
            background: #f0f0f0;
            color: #666;
        }

        .btn-secondary:hover {
            background: #e0e0e0;
        }

        .config-input {
            width: 100%;
            min-height: 120px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-family: monospace;
            font-size: 12px;
            resize: vertical;
        }

        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.15);
            z-index: 100000;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        .notification.success {
            background: #f6ffed;
            border: 1px solid #b7eb8f;
            color: #52c41a;
        }

        .notification.warning {
            background: #fffbe6;
            border: 1px solid #ffe58f;
            color: #faad14;
        }

        .notification.error {
            background: #fff2f0;
            border: 1px solid #ffccc7;
            color: #ff4d4f;
        }
    `);

    // 显示通知
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // 创建UI面板
    function createPanel() {
        const config = loadConfig();
        
        const panel = document.createElement('div');
        panel.id = 'rrz-auto-panel';
        panel.innerHTML = `
            <div class="panel-header">
                <span class="panel-title">🐂 发布助手</span>
                <button class="panel-toggle" id="panel-toggle">−</button>
            </div>
            <div class="panel-content">
                <select class="config-selector" id="template-selector">
                    ${config.templates.map((t, i) => 
                        `<option value="${i}" ${i === config.currentTemplate ? 'selected' : ''}>${t.name}</option>`
                    ).join('')}
                </select>
                
                <button class="btn btn-primary" id="btn-fill">📝 自动填充</button>
                <button class="btn btn-success" id="btn-submit">🚀 一键提交</button>
                <button class="btn btn-secondary" id="btn-config">⚙️ 配置管理</button>
            </div>
        `;

        document.body.appendChild(panel);

        // 绑定事件
        document.getElementById('panel-toggle').addEventListener('click', () => {
            panel.classList.toggle('collapsed');
            const btn = document.getElementById('panel-toggle');
            btn.textContent = panel.classList.contains('collapsed') ? '+' : '−';
        });

        document.getElementById('btn-fill').addEventListener('click', async () => {
            const selectedIndex = document.getElementById('template-selector').value;
            const template = config.templates[selectedIndex];
            await autoFillForm(template);
        });

        document.getElementById('btn-submit').addEventListener('click', async () => {
            const selectedIndex = document.getElementById('template-selector').value;
            const template = config.templates[selectedIndex];
            await autoFillForm(template);
            
            // 等待填充完成后点击提交按钮
            setTimeout(() => {
                const submitBtn = document.querySelector('button[type="submit"]') ||
                                 document.querySelector('.submit-btn') ||
                                 document.querySelector('button:contains("提交")');
                if (submitBtn) {
                    submitBtn.click();
                    showNotification('✅ 已提交！', 'success');
                } else {
                    showNotification('⚠️ 未找到提交按钮，请手动提交', 'warning');
                }
            }, 1000);
        });

        document.getElementById('btn-config').addEventListener('click', () => {
            showConfigDialog(config);
        });
    }

    // 配置管理对话框
    function showConfigDialog(config) {
        const dialog = document.createElement('div');
        dialog.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 100000;
        `;

        dialog.innerHTML = `
            <div style="background: white; padding: 24px; border-radius: 12px; max-width: 600px; width: 90%;">
                <h3 style="margin: 0 0 16px 0;">配置管理</h3>
                <textarea class="config-input" id="config-json">${JSON.stringify(config, null, 2)}</textarea>
                <div style="display: flex; gap: 12px; margin-top: 16px;">
                    <button class="btn btn-primary" id="save-config">💾 保存</button>
                    <button class="btn btn-secondary" id="cancel-config">取消</button>
                </div>
            </div>
        `;

        document.body.appendChild(dialog);

        document.getElementById('save-config').addEventListener('click', () => {
            try {
                const newConfig = JSON.parse(document.getElementById('config-json').value);
                saveConfig(newConfig);
                showNotification('✅ 配置已保存！', 'success');
                dialog.remove();
                location.reload();
            } catch (error) {
                showNotification('❌ JSON格式错误！', 'error');
            }
        });

        document.getElementById('cancel-config').addEventListener('click', () => {
            dialog.remove();
        });

        dialog.addEventListener('click', (e) => {
            if (e.target === dialog) dialog.remove();
        });
    }

    // ==================== 初始化 ====================
    
    function init() {
        // 检查是否在商品发布页面
        if (window.location.href.includes('/publish') || 
            window.location.href.includes('/product/add') ||
            document.querySelector('.product-form')) {
            
            console.log('人人租发布助手已加载');
            createPanel();
            
            // 注册菜单命令
            GM_registerMenuCommand('📝 打开配置', () => {
                const config = loadConfig();
                showConfigDialog(config);
            });
        }
    }

    // 等待页面加载完成
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
