#!/usr/bin/env python3
"""
图片处理工作流 - 优化版
区分AI初筛和AI审核
"""
import os, sys, cv2, numpy as np, time
sys.path.insert(0, '/Users/xs/.openclaw/workspace')
from api_stability import call_api_with_retry

API_KEY = "675362ca-6313-43e5-a705-3046f668e2b1"

def ai_filter(url):
    """AI初筛：判断是否商品主体 + 型号匹配
    规则：
    1. 必须是完整的实体商品图片（不能是局部特写、细节图）
    2. 背景必须是纯白底（商品周围不能有其他颜色背景，包括黑底）
    3. 不能是宣传图/海报/素材图（必须是从某个角度拍的商品实物图）
    4. 商品必须在画面居中或偏中位置，不能偏边角
    5. 必须能看出产品型号（通过logo、铭刻、型号标识等）
    """
    result = call_api_with_retry(
        "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "doubao-seed-1-6-vision-250815",
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": """你是一个专业的电商图片审核员。判断是否为合格的商品主图。

审核标准（必须全部满足）：
1. 必须是完整的实体商品（不能是局部特写、配件、线材等）
2. 背景必须是纯白底（商品周围除了白色不能有其他颜色，包括黑底、灰底、有色背景都不行）
3. 必须是商品实物图（不能是宣传海报、渲染图、示意图）
4. 商品必须在画面中央或偏中央位置（不能偏边角）
5. 图片必须清晰展示商品全貌，且能看出产品型号/品牌/名称

输出格式：只有"是"或"否"，不要其他内容。"""},
                {"type": "image_url", "image_url": {"url": url}}
            ]}],
            "max_tokens": 50},
        timeout=180
    )
    if result:
        return "是" in result.get('choices',[{}])[0].get('message',{}).get('content','')
    return False

def ai_audit(url):
    """AI审核：底色/尺寸/文字/成色/完整性/型号识别
    规则：
    1. 底色：必须是纯白底，商品周围一圈都是白色，不能有黑边/灰边/其他颜色边
    2. 尺寸：必须 >= 600x600px
    3. 文字：主图不能有后期添加的文字（商品自身铭刻如品牌logo除外）
    4. 成色：判断商品新旧程度（全新/95新/9成新等）
    5. 完整性：必须是商品整体，不能是局部特写
    6. 型号识别：必须能识别出具体的产品型号
    """
    result = call_api_with_retry(
        "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "doubao-seed-1-6-vision-250815",
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": """你是一个严格的电商图片审核员。对图片进行详细审核。

必须检查的6个维度：
1. 底色：背景是否为纯白底（商品周围一圈都是白色，不能有黑边/灰边/其他颜色边）- 通过/不通过
2. 尺寸：图片是否足够大，商品占比是否合理 - 通过/不通过
3. 文字：主图是否有后期添加的文字（通过/不通过；商品自身铭刻如品牌logo不算）
4. 成色：商品新旧程度（全新/95新/9成新/8成新等）
5. 完整性：是否为商品整体展示，非局部特写 - 通过/不通过
6. 型号：图片中能否识别出具体的产品型号/名称 - 通过/不通过

最后给出结论：6个维度全部通过才输出"通过"，否则输出"不通过"

输出格式示例：
底色:通过 尺寸:通过 文字:通过 成色:95新 完整性:通过 型号:通过 结论:通过"""},
                {"type": "image_url", "image_url": {"url": url}}
            ]}],
            "max_tokens": 300},
        timeout=180
    )
    if result:
        content = result.get('choices',[{}])[0].get('message',{}).get('content','')
        return "结论:通过" in content or "结论：通过" in content
    return False

def process_workflow(image_urls, target_model=None):
    """图片处理工作流
    Args:
        image_urls: [(name, url), ...]
        target_model: 目标产品型号，如"Mac Studio M4 Max"，用于验证一致性
    """
    # AI初筛
    print("=== AI初筛 ===")
    valid = []
    for name, url in image_urls:
        if ai_filter(url):
            valid.append((name, url))
            print(f"  {name}: ✅")
        else:
            print(f"  {name}: ❌ 过滤")
    
    print(f"\n初筛结果: {len(valid)} 张")
    
    if len(valid) < 3:
        print("⚠️ 有效图片不足3张")
        return False
    
    # AI审核 + 型号提取
    print("\n=== AI审核 ===")
    passed = []
    model_detected = None
    for name, url in valid:
        result = ai_audit(url)
        if result:
            passed.append((name, url))
            print(f"  {name}: ✅")
        else:
            print(f"  {name}: ❌")
    
    print(f"\n审核结果: {len(passed)} 张通过")
    
    # 型号一致性检查
    if target_model and len(passed) >= 3:
        print(f"\n=== 型号一致性检查 ===")
        print(f"目标型号: {target_model}")
        
        # 提取每张图片的型号
        for name, url in passed:
            detected = extract_model_from_image(url)
            print(f"  {name}: {detected}")
            
            if model_detected is None:
                model_detected = detected
            elif detected and model_detected:
                # 检查是否匹配
                if not is_model_match(model_detected, detected):
                    print(f"  ⚠️ 型号不一致: {model_detected} vs {detected}")
        
        # 检查是否所有图片都是同一型号
        print(f"\n最终使用型号: {model_detected}")
    
    return len(passed) >= 3

def extract_model_from_image(url):
    """从图片中提取产品型号"""
    result = call_api_with_retry(
        "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "doubao-seed-1-6-vision-250815",
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": "仔细看这张图片，识别出商品的具体型号/名称。只输出型号名称，不要其他内容。例如：Mac Studio M4 Max"},
                {"type": "image_url", "image_url": {"url": url}}
            ]}],
            "max_tokens": 100},
        timeout=180
    )
    if result:
        return result.get('choices',[{}])[0].get('message',{}).get('content','').strip()
    return None

def is_model_match(model1, model2):
    """检查两个型号是否匹配（模糊匹配）"""
    if not model1 or not model2:
        return False
    m1 = model1.lower().replace(" ", "")
    m2 = model2.lower().replace(" ", "")
    # 包含关系或关键词匹配
    return m1 in m2 or m2 in m1 or any(k in m1 and k in m2 for k in ["mac", "studio", "max", "m4"])
