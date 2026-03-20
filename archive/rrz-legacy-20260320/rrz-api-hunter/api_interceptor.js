// 人人租API拦截器 - 在浏览器控制台运行
// 使用方法：
// 1. 打开 https://admin.rrzu.com
// 2. 按F12打开控制台
// 3. 粘贴此代码并回车
// 4. 操作页面（点击商品列表、发布商品等）
// 5. 查看控制台输出的API调用记录

(function() {
    console.log('🎯 人人租API拦截器已启动');
    console.log('开始记录所有API请求...\n');
    
    const apiLog = [];
    
    // 拦截 fetch
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const [url, options = {}] = args;
        
        console.log('📡 [FETCH]', options.method || 'GET', url);
        
        const logEntry = {
            type: 'fetch',
            timestamp: new Date().toISOString(),
            method: options.method || 'GET',
            url: url,
            headers: options.headers || {},
            body: options.body
        };
        
        // 尝试解析body
        if (options.body) {
            try {
                logEntry.bodyParsed = JSON.parse(options.body);
            } catch(e) {
                logEntry.bodyParsed = options.body;
            }
        }
        
        apiLog.push(logEntry);
        
        return originalFetch.apply(this, args).then(response => {
            // 克隆响应以便读取
            const clonedResponse = response.clone();
            
            clonedResponse.json().then(data => {
                console.log('📥 [RESPONSE]', response.status, url);
                console.log('   数据:', data);
                
                logEntry.response = {
                    status: response.status,
                    data: data
                };
            }).catch(() => {
                // 非JSON响应
            });
            
            return response;
        });
    };
    
    // 拦截 XMLHttpRequest
    const originalOpen = XMLHttpRequest.prototype.open;
    const originalSend = XMLHttpRequest.prototype.send;
    
    XMLHttpRequest.prototype.open = function(method, url, ...rest) {
        this._method = method;
        this._url = url;
        return originalOpen.apply(this, [method, url, ...rest]);
    };
    
    XMLHttpRequest.prototype.send = function(body) {
        console.log('📡 [XHR]', this._method, this._url);
        
        const logEntry = {
            type: 'xhr',
            timestamp: new Date().toISOString(),
            method: this._method,
            url: this._url,
            body: body
        };
        
        // 尝试解析body
        if (body) {
            try {
                logEntry.bodyParsed = JSON.parse(body);
            } catch(e) {
                logEntry.bodyParsed = body;
            }
        }
        
        apiLog.push(logEntry);
        
        // 监听响应
        this.addEventListener('load', function() {
            console.log('📥 [RESPONSE]', this.status, this._url);
            try {
                const data = JSON.parse(this.responseText);
                console.log('   数据:', data);
                
                logEntry.response = {
                    status: this.status,
                    data: data
                };
            } catch(e) {
                console.log('   响应:', this.responseText.substring(0, 200));
            }
        });
        
        return originalSend.apply(this, arguments);
    };
    
    // 导出日志的函数
    window.exportApiLog = function() {
        console.log('\n📊 API调用记录汇总:');
        console.log('总计:', apiLog.length, '个请求\n');
        
        // 按URL分组
        const grouped = {};
        apiLog.forEach(log => {
            const key = `${log.method} ${log.url}`;
            if (!grouped[key]) {
                grouped[key] = [];
            }
            grouped[key].push(log);
        });
        
        console.log('API端点清单:');
        Object.keys(grouped).forEach(key => {
            console.log(`  ${key} (${grouped[key].length}次)`);
        });
        
        // 下载JSON文件
        const dataStr = JSON.stringify(apiLog, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'rrz_api_log_' + Date.now() + '.json';
        link.click();
        
        console.log('\n✅ API日志已下载!');
        
        return apiLog;
    };
    
    console.log('\n使用说明:');
    console.log('1. 在页面中操作（点击商品列表、发布商品等）');
    console.log('2. 控制台会实时显示API调用');
    console.log('3. 操作完成后，运行: exportApiLog()');
    console.log('4. 会自动下载完整的API日志JSON文件\n');
})();
