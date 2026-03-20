#!/usr/bin/env python3
"""
人人租API猎手 - 实战抓包工具
通过CDP连接浏览器，监听所有网络请求，记录真实API调用
"""
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from pathlib import Path

CDP_URL = "http://127.0.0.1:18800"
OUTPUT_DIR = Path("/Users/xs/.openclaw/workspace/projects/rrz-api-hunter/captured")

class ApiHunter:
    def __init__(self):
        self.captured = []
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def start_capture(self):
        """开始抓包"""
        print("🎯 人人租API猎手启动")
        print("=" * 60)
        
        pw = sync_playwright().start()
        try:
            browser = pw.chromium.connect_over_cdp(CDP_URL)
            ctx = browser.contexts[0]
            
            # 找到人人租后台页面
            page = None
            for p in ctx.pages:
                if 'admin.rrzu.com' in p.url or 'rrzu' in p.url.lower():
                    page = p
                    break
            
            if not page:
                print("❌ 未找到人人租后台页面")
                print("请先在浏览器中打开: https://admin.rrzu.com")
                print("并登录账号: 15162152584 / 152584")
                return
            
            print(f"✅ 已连接到页面: {page.url}")
            print("\n📡 开始监听网络请求...")
            print("请在浏览器中执行以下操作：")
            print("  1. 刷新页面（获取登录态）")
            print("  2. 点击商品列表（获取列表API）")
            print("  3. 点击'发布商品'（获取创建API）")
            print("  4. 上传一张图片（获取上传API）")
            print("  5. 填写表单并提交（获取提交API）")
            print("\n按 Ctrl+C 停止监听并保存结果\n")
            
            # 监听请求
            def handle_request(request):
                url = request.url
                # 过滤：只记录人人租相关的API
                if any(domain in url for domain in ['rrzu.com', 'rrzuji.cn']):
                    req_data = {
                        'timestamp': datetime.now().isoformat(),
                        'method': request.method,
                        'url': url,
                        'headers': dict(request.headers),
                        'post_data': None
                    }
                    
                    # 尝试获取POST数据
                    if request.method in ['POST', 'PUT', 'PATCH']:
                        try:
                            post_data = request.post_data
                            if post_data:
                                # 尝试解析JSON
                                try:
                                    req_data['post_data'] = json.loads(post_data)
                                except:
                                    req_data['post_data'] = post_data[:1000]  # 限制长度
                        except:
                            pass
                    
                    self.captured.append(req_data)
                    print(f"📥 [{request.method}] {url}")
            
            # 监听响应
            def handle_response(response):
                url = response.url
                if any(domain in url for domain in ['rrzu.com', 'rrzuji.cn']):
                    try:
                        # 查找对应的请求
                        for req in reversed(self.captured):
                            if req['url'] == url and 'response' not in req:
                                body = response.body()
                                
                                # 尝试解析JSON响应
                                try:
                                    body_json = json.loads(body.decode('utf-8'))
                                    req['response'] = {
                                        'status': response.status,
                                        'headers': dict(response.headers),
                                        'body': body_json
                                    }
                                except:
                                    req['response'] = {
                                        'status': response.status,
                                        'headers': dict(response.headers),
                                        'body': body.decode('utf-8', errors='ignore')[:2000]
                                    }
                                
                                print(f"📤 [{response.status}] {url}")
                                break
                    except Exception as e:
                        pass
            
            page.on('request', handle_request)
            page.on('response', handle_response)
            
            # 保持监听
            try:
                while True:
                    time.sleep(0.5)
            except KeyboardInterrupt:
                print("\n\n⏹️  停止监听")
                
        finally:
            self.save_results()
            pw.stop()
    
    def save_results(self):
        """保存抓包结果"""
        if not self.captured:
            print("❌ 没有捕获到任何请求")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存完整数据
        full_file = self.output_dir / f"full_{timestamp}.json"
        with open(full_file, 'w', encoding='utf-8') as f:
            json.dump(self.captured, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 已保存 {len(self.captured)} 条请求")
        print(f"📁 完整数据: {full_file}")
        
        # 生成分析报告
        self.generate_report(timestamp)
    
    def generate_report(self, timestamp):
        """生成API分析报告"""
        report_file = self.output_dir / f"report_{timestamp}.md"
        
        # 按URL分组
        api_groups = {}
        for req in self.captured:
            url = req['url']
            # 提取路径（去除query参数）
            path = url.split('?')[0]
            if path not in api_groups:
                api_groups[path] = []
            api_groups[path].append(req)
        
        # 生成报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 人人租API分析报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"捕获请求数: {len(self.captured)}\n")
            f.write(f"API端点数: {len(api_groups)}\n\n")
            
            f.write("## API端点清单\n\n")
            for path, reqs in sorted(api_groups.items()):
                methods = set(r['method'] for r in reqs)
                f.write(f"### {path}\n")
                f.write(f"- 方法: {', '.join(methods)}\n")
                f.write(f"- 调用次数: {len(reqs)}\n")
                
                # 显示第一个请求的详细信息
                first_req = reqs[0]
                
                # 关键请求头
                important_headers = ['authorization', 'go-token', 'token', 'cookie', 'content-type']
                f.write("- 关键请求头:\n")
                for key, value in first_req['headers'].items():
                    if key.lower() in important_headers:
                        # 脱敏处理
                        if 'token' in key.lower() or 'authorization' in key.lower():
                            value = value[:20] + "..." if len(value) > 20 else value
                        f.write(f"  - `{key}`: `{value}`\n")
                
                # POST数据示例
                if first_req.get('post_data'):
                    f.write("- POST数据示例:\n")
                    f.write("```json\n")
                    if isinstance(first_req['post_data'], dict):
                        f.write(json.dumps(first_req['post_data'], ensure_ascii=False, indent=2))
                    else:
                        f.write(str(first_req['post_data'])[:500])
                    f.write("\n```\n")
                
                # 响应示例
                if 'response' in first_req:
                    f.write("- 响应示例:\n")
                    f.write(f"  - 状态码: {first_req['response']['status']}\n")
                    f.write("```json\n")
                    if isinstance(first_req['response']['body'], dict):
                        f.write(json.dumps(first_req['response']['body'], ensure_ascii=False, indent=2)[:1000])
                    else:
                        f.write(str(first_req['response']['body'])[:500])
                    f.write("\n```\n")
                
                f.write("\n")
        
        print(f"📊 分析报告: {report_file}")


if __name__ == '__main__':
    hunter = ApiHunter()
    hunter.start_capture()
