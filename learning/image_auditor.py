#!/usr/bin/env python3
"""
图片AI审核系统
用于电商上架前的图片质量检测与筛选
支持AI智能分析和传统规则匹配
"""

import os
import base64
import json
import requests
from PIL import Image
import numpy as np
from pathlib import Path

# ==================== API 配置 ====================
GEMINI_API_CONFIG = {
    "api_url": "https://mydamoxing.cn/v1/chat/completions",
    "api_key": "sk-3SlcsWRMEgZd9FgjBnSDA1SIE7hVk0u8b0PztwX5YTRyCW5E",
    "model": "gemini-3-pro-preview"  # 可用
}

# 人人租平台图片要求
RENT_PLATFORM_REQUIREMENTS = """
平台图片要求：
- 尺寸：600x600px以上
- 背景：白底/纯色底
- 内容：仅商品主体照片，不能有文字/水印
- 质量：清晰无模糊
- 禁止：品牌Logo(除商品本身)、二维码、联系方式
"""

import os
from PIL import Image
import numpy as np
from pathlib import Path

class ImageAuditor:
    """图片审核器"""
    
    def __init__(self, min_size=600, min_kb=50):
        self.min_size = min_size
        self.min_kb = min_kb
    
    def audit(self, image_path: str) -> dict:
        """审核单张图片"""
        result = {
            'path': image_path,
            'grade': 'A',
            'issues': [],
            'details': {}
        }
        
        # 1. 基础质量检查
        quality = self._check_quality(image_path)
        result['details']['quality'] = quality
        
        if not quality['passed']:
            result['grade'] = 'C'
            result['issues'].append(quality['reason'])
            return result
        
        # 2. 背景检测
        background = self._check_background(image_path)
        result['details']['background'] = background
        
        # 3. 水印检测
        watermark = self._check_watermark(image_path)
        result['details']['watermark'] = watermark
        
        if watermark['detected']:
            result['grade'] = 'B'
            result['issues'].append(f"检测到水印: {watermark['type']}")
        
        # 4. 版权风险检测
        copyright = self._check_copyright(image_path)
        result['details']['copyright'] = copyright
        
        if copyright['detected']:
            result['grade'] = 'C'
            result['issues'].append(f"版权风险: {copyright['type']}")
        
        return result
    
    def _check_quality(self, image_path: str) -> dict:
        """检查基础质量"""
        try:
            img = Image.open(image_path)
            width, height = img.size
            file_size = os.path.getsize(image_path) / 1024  # KB
            
            # 检查分辨率
            if width < self.min_size or height < self.min_size:
                return {
                    'passed': False,
                    'reason': f"分辨率不足 {self.min_size}x{self.min_size}"
                }
            
            # 检查文件大小
            if file_size < self.min_kb:
                return {
                    'passed': False,
                    'reason': f"文件太小 ({file_size:.1f}KB)"
                }
            
            return {
                'passed': True,
                'resolution': f"{width}x{height}",
                'size_kb': f"{file_size:.1f}KB"
            }
        except Exception as e:
            return {
                'passed': False,
                'reason': f"无法读取图片: {e}"
            }
    
    def _check_background(self, image_path: str) -> dict:
        """检查背景是否为白底"""
        try:
            img = Image.open(image_path).convert('RGB')
            img = img.resize((100, 100))  # 缩小以便快速分析
            pixels = np.array(img)
            
            # 检查四个角和边缘的颜色
            corners = [
                pixels[0, 0],      # 左上
                pixels[0, -1],     # 右上
                pixels[-1, 0],    # 左下
                pixels[-1, -1],    # 右下
                pixels[50, 0],    # 左中
                pixels[50, -1],    # 右中
                pixels[0, 50],    # 上中
                pixels[-1, 50],   # 下中
            ]
            
            # 计算接近白色的像素比例
            white_count = sum(1 for p in corners if all(v > 200 for v in p))
            white_ratio = white_count / len(corners)
            
            if white_ratio >= 0.75:
                return {'detected': False, 'type': '白底', 'ratio': white_ratio}
            elif white_ratio >= 0.5:
                return {'detected': False, 'type': '浅色底', 'ratio': white_ratio}
            else:
                return {'detected': True, 'type': '非白底', 'ratio': white_ratio}
                
        except Exception as e:
            return {'detected': False, 'error': str(e)}
    
    def _check_text(self, image_path: str) -> dict:
        """检测图片中是否有文字"""
        # 简化版：检测文字特征（实际可用OCR）
        # 文字区域通常有高对比度边缘
        try:
            img = Image.open(image_path).convert('L')  # 转灰度
            img = img.resize((100, 100))
  # 转            pixels = np.array(img)
            
            # 计算边缘（梯度）
            dx = np.abs(np.diff(pixels, axis=1))
            dy = np.abs(np.diff(pixels, axis=0))
            
            # 高梯度区域可能表示有文字/图案
            edge_density = np.mean(dx > 20) + np.mean(dy > 20)
            
            # 如果边缘过于密集，可能有文字
            if edge_density > 0.3:
                return {'detected': True, 'type': '可能有文字', 'density': float(edge_density)}
            
            return {'detected': False, 'density': float(edge_density)}
        except Exception as e:
            return {'detected': False, 'error': str(e)}
    
    def _check_watermark(self, image_path: str) -> dict:
        """检测水印"""
        try:
            img = Image.open(image_path).convert('RGB')
            img = img.resize((100, 100))
            pixels = np.array(img)
            
            # 检查右下角区域（水印常见位置）
            bottom_right = pixels[70:, 70:]
            
            # 检测文字/图案特征
            gray = np.mean(bottom_right, axis=2)
            variance = np.var(gray)
            
            # 高方差可能表示有文字/图案
            if variance > 500:
                return {'detected': True, 'type': '右下角可能有水印', 'variance': float(variance)}
            
            return {'detected': False, 'variance': float(variance)}
            
        except Exception as e:
            return {'detected': False, 'error': str(e)}
    
    def _check_copyright(self, image_path: str) -> dict:
        """检测版权风险"""
        # 简化版：检测品牌色
        # 实际可用OCR或品牌识别API
        return {'detected': False, 'note': '需要更复杂的模型检测'}
    
    # ==================== AI 智能审核 ====================
    
    def _encode_image_to_base64(self, image_path: str, max_size: int = 1024) -> str:
        """将图片编码为base64（自动压缩）"""
        from PIL import Image
        import io
        
        img = Image.open(image_path)
        
        # 压缩大图
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        # 转RGB（去透明度）
        if img.mode in ('RGBA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # 保存为JPEG
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def _call_gemini_api(self, image_path: str) -> dict:
        """调用Gemini API进行图片分析"""
        try:
            # 编码图片
            base64_image = self._encode_image_to_base64(image_path)
            
            # 构建请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GEMINI_API_CONFIG['api_key']}"
            }
            
            prompt = f"""你是一个电商图片审核专家。请分析这张商品图片是否符合以下要求：

{RENT_PLATFORM_REQUIREMENTS}

请以JSON格式返回审核结果：
{{
    "passed": true/false,
    "grade": "A/B/C",
    "issues": ["问题1", "问题2"],
    "reason": "总体评价",
    "details": {{
        "background": "白底/浅色底/非白底",
        "has_watermark": true/false,
        "has_text": true/false,
        "has_brand_logo": true/false,
        "clarity": "清晰/一般/模糊",
        "suggestion": "修改建议"
    }}
}}

只返回JSON，不要其他内容。"""
            
            payload = {
                "model": GEMINI_API_CONFIG['model'],
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 2000
            }
            
            response = requests.post(
                GEMINI_API_CONFIG['api_url'],
                headers=headers,
                json=payload,
                timeout=120  # 增加到120秒
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # 解析JSON
                try:
                    # 尝试提取JSON
                    if '```json' in content:
                        content = content.split('```json')[1].split('```')[0]
                    elif '```' in content:
                        content = content.split('```')[1].split('```')[0]
                    
                    return json.loads(content)
                except:
                    return {"error": "解析失败", "raw": content[:200]}
            else:
                return {"error": f"API错误: {response.status_code}", "detail": response.text[:200]}
                
        except Exception as e:
            return {"error": str(e)}
    
    def ai_audit(self, image_path: str) -> dict:
        """AI智能审核单张图片"""
        print(f"\n🤖 正在AI分析: {os.path.basename(image_path)}")
        
        result = self._call_gemini_api(image_path)
        
        if "error" in result:
            print(f"   ❌ API调用失败: {result['error']}")
            # 降级到规则匹配
            print(f"   🔄 降级到规则匹配...")
            return self.audit(image_path)
        
        print(f"   ✅ 审核完成: {result.get('grade', 'N/A')}级")
        if result.get('issues'):
            print(f"   ⚠️ 问题: {', '.join(result['issues'])}")
        
        # 合并结果
        final_result = {
            'path': image_path,
            'grade': result.get('grade', 'B'),
            'issues': result.get('issues', []),
            'details': {
                'ai_analysis': result.get('details', {}),
                'reason': result.get('reason', ''),
                'ai_model': GEMINI_API_CONFIG['model']
            },
            'is_ai': True
        }
        
        return final_result
    
    def smart_audit(self, image_path: str, use_ai: bool = True) -> dict:
        """智能审核：AI优先，失败则降级到规则匹配"""
        if use_ai:
            return self.ai_audit(image_path)
        else:
            return self.audit(image_path)
    
    # ==================== 图片修改功能 ====================
    
    def auto_fix_image(self, image_path: str, output_path: str = None) -> dict:
        """自动修复图片问题
        
        检测问题并尝试修复：
        - 非白底背景 → 去除背景/转白底
        - 水印 → 尝试去除
        - 模糊 → 锐化
        """
        import io
        from PIL import Image, ImageEnhance, ImageFilter
        
        print(f"\n🔧 正在自动修复: {os.path.basename(image_path)}")
        
        if output_path is None:
            # 生成输出路径
            name, ext = os.path.splitext(image_path)
            output_path = f"{name}_fixed{ext}"
        
        try:
            img = Image.open(image_path)
            original_mode = img.mode
            
            # 转为RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            issues_fixed = []
            
            # 1. 背景处理 - 转白底
            img_array = np.array(img)
            
            # 获取图片四个角的颜色
            corners = [
                img_array[0, 0],
                img_array[0, -1],
                img_array[-1, 0],
                img_array[-1, -1]
            ]
            
            # 检查背景是否接近白色
            corner_brightness = np.mean(corners)
            
            if corner_brightness < 240:  # 不够白
                # 尝试去背景 - 简单的白底替换
                # 找到商品主体（假设中间区域是商品）
                h, w = img_array.shape[:2]
                center_region = img_array[h//4:3*h//4, w//4:3*w//4]
                center_color = np.mean(center_region, axis=(0, 1))
                
                # 创建白底
                background = np.ones_like(img_array) * 255
                
                # 简单的阈值分割 - 把接近中心颜色的保留
                diff_from_center = np.abs(img_array.astype(float) - center_color)
                mask = np.mean(diff_from_center, axis=2) < 60  # 阈值
                
                # 混合
                result = img_array.copy()
                result[~mask] = 255  # 背景变白
                
                img = Image.fromarray(result.astype(np.uint8))
                issues_fixed.append("背景转白底")
            
            # 2. 增强清晰度
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.3)
            issues_fixed.append("增强清晰度")
            
            # 3. 保存
            img.save(output_path, 'JPEG', quality=95, optimize=True)
            
            print(f"   ✅ 修复完成: {os.path.basename(output_path)}")
            print(f"   📝 修复项: {', '.join(issues_fixed)}")
            
            return {
                'success': True,
                'output_path': output_path,
                'fixed': issues_fixed
            }
            
        except Exception as e:
            print(f"   ❌ 修复失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def audit_and_fix(self, image_path: str, use_ai: bool = True) -> dict:
        """审核 + 自动修复流程
        
        1. 先审核
        2. 如果不通过，自动尝试修复
        3. 再次审核修复后的图片
        """
        print(f"\n{'='*60}")
        print(f"🔄 审核 + 自动修复流程")
        print(f"{'='*60}")
        
        # 第一轮审核
        print(f"\n📋 第一轮审核...")
        result = self.smart_audit(image_path, use_ai=use_ai)
        
        if result['grade'] in ['A', 'B']:
            print(f"   ✅ 审核通过 ({result['grade']}级)，无需修复")
            result['fix_attempted'] = False
            return result
        
        # 审核不通过，尝试修复
        print(f"   ⚠️ 审核不通过 ({result['grade']}级)，开始自动修复...")
        print(f"   📝 问题: {', '.join(result['issues'])}")
        
        fix_result = self.auto_fix_image(image_path)
        
        result['fix_attempted'] = True
        result['fix_result'] = fix_result
        
        if fix_result['success']:
            # 修复后再次审核
            print(f"\n📋 第二轮审核（修复后）...")
            result2 = self.smart_audit(fix_result['output_path'], use_ai=use_ai)
            result['after_fix'] = result2
            result['fixed'] = fix_result['fixed']
            
            if result2['grade'] in ['A', 'B']:
                print(f"   ✅ 修复成功！审核通过 ({result2['grade']}级)")
            else:
                print(f"   ⚠️ 修复后仍未完全通过 ({result2['grade']}级)")
        
        return result
    
    def batch_audit(self, folder: str, use_ai: bool = False) -> list:
        """批量审核文件夹中的图片
        
        Args:
            folder: 图片文件夹路径
            use_ai: 是否使用AI审核（默认False，使用规则匹配）
        """
        results = []
        folder_path = Path(folder)
        
        # 支持 jpg, jpeg, png
        extensions = ['*.jpg', '*.jpeg', '*.png']
        
        for ext in extensions:
            for img_path in folder_path.glob(ext):
                if use_ai:
                    result = self.ai_audit(str(img_path))
                else:
                    result = self.audit(str(img_path))
                results.append(result)
        
        return results
    
    def batch_ai_audit(self, folder: str) -> list:
        """批量AI智能审核"""
        return self.batch_audit(folder, use_ai=True)
    
    def print_report(self, results: list):
        """打印审核报告"""
        print("\n" + "="*60)
        print("图片审核报告")
        print("="*60)
        
        a_count = sum(1 for r in results if r['grade'] == 'A')
        b_count = sum(1 for r in results if r['grade'] == 'B')
        c_count = sum(1 for r in results if r['grade'] == 'C')
        
        print(f"\n总计: {len(results)} 张")
        print(f"✅ A级: {a_count} 张")
        print(f"⚠️ B级: {b_count} 张")
        print(f"❌ C级: {c_count} 张")
        
        print("\n详细结果:")
        for r in results:
            status = "✅" if r['grade'] == 'A' else "⚠️" if r['grade'] == 'B' else "❌"
            print(f"\n{status} {os.path.basename(r['path'])} ({r['grade']}级)")
            if r['issues']:
                for issue in r['issues']:
                    print(f"   - {issue}")


if __name__ == "__main__":
    import sys
    
    # 解析命令行参数
    use_ai = False
    auto_fix = False
    folder = "/Users/xs/.openclaw/workspace/product_images"
    
    for arg in sys.argv[1:]:
        if arg == "--ai" or arg == "-a":
            use_ai = True
        elif arg == "--fix" or arg == "-f":
            auto_fix = True
        elif arg == "--help" or arg == "-h":
            print("""
图片审核系统使用说明：

用法: python image_auditor.py [选项] [文件或文件夹路径]

选项:
  -a, --ai      使用AI智能审核（默认使用规则匹配）
  -f, --fix     审核失败后自动修复
  -h, --help   显示帮助信息

示例:
  python image_auditor.py                           # 审核默认文件夹（规则匹配）
  python image_auditor.py --ai                      # AI智能审核默认文件夹
  python image_auditor.py --ai --fix                # AI审核 + 自动修复
  python image_auditor.py /path/to/images           # 审核指定文件夹
  python image_auditor.py --ai /path/to/images      # AI审核指定文件夹
  python image_auditor.py --ai --fix image.jpg     # AI审核 + 修复单张图片
""")
            sys.exit(0)
        else:
            # 判断是文件还是文件夹
            if os.path.isfile(arg):
                # 单个文件
                print("="*60)
                if use_ai:
                    print("🤖 图片AI智能审核系统")
                    print(f"📡 API: {GEMINI_API_CONFIG['api_url']}")
                    print(f"🤖 模型: {GEMINI_API_CONFIG['model']}")
                else:
                    print("📐 图片规则审核系统")
                print(f"📄 文件: {arg}")
                if auto_fix:
                    print("🔧 模式: 审核 + 自动修复")
                print("="*60)
                
                auditor = ImageAuditor()
                
                if auto_fix:
                    result = auditor.audit_and_fix(arg, use_ai=use_ai)
                elif use_ai:
                    result = auditor.ai_audit(arg)
                else:
                    result = auditor.audit(arg)
                
                auditor.print_report([result])
                sys.exit(0)
            else:
                folder = arg
    
    print("="*60)
    if use_ai:
        print("🤖 图片AI智能审核系统")
        print(f"📡 API: {GEMINI_API_CONFIG['api_url']}")
        print(f"🤖 模型: {GEMINI_API_CONFIG['model']}")
    else:
        print("📐 图片规则审核系统")
    if auto_fix:
        print("🔧 模式: 审核 + 自动修复")
    print(f"📁 目录: {folder}")
    print("="*60)
    
    auditor = ImageAuditor()
    
    if auto_fix:
        # 批量审核+修复
        results = []
        folder_path = Path(folder)
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            for img_path in folder_path.glob(ext):
                result = auditor.audit_and_fix(str(img_path), use_ai=use_ai)
                results.append(result)
    elif use_ai:
        results = auditor.batch_ai_audit(folder)
    else:
        results = auditor.batch_audit(folder)
    
    auditor.print_report(results)
