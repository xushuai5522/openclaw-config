#!/usr/bin/env python3
"""
人人租租金计算器
根据购入成本自动计算押金、租金、买断价
"""

def calculate_rent(buy_cost: float) -> dict:
    """
    计算租赁价格
    
    参数:
        buy_cost: 购入成本 (元)
    
    返回:
        dict: 包含押金、租金、买断价等
    """
    # 押金 = 购入成本 × 80%
    deposit = buy_cost * 0.8
    
    # 买断价 = 购入成本 × 138%
    buyout_price = buy_cost * 1.38
    
    # 归还方案租金 (最长1年)
    # 1个月: 10% × 1
    # 3个月: 10% × 3 × 98%
    # 6个月: 10% × 6 × 96%
    # 12个月: 10% × 12 × 92%
    
    return_plan = {
        "1个月": buy_cost * 0.10 * 1,
        "3个月": buy_cost * 0.10 * 3 * 0.98,
        "6个月": buy_cost * 0.10 * 6 * 0.96,
        "12个月": buy_cost * 0.10 * 12 * 0.92,
    }
    
    # 续租方案 (最长3年，但不超过买断价)
    # 第一年与归还方案一致
    renew_plan = {
        "1年": min(return_plan["12个月"], buyout_price),
    }
    
    # 第2年、第3年（如果有的话）
    # 2年: 10% × 24 × 90%
    # 3年: 10% × 36 × 88%
    renew_plan["2年"] = min(buy_cost * 0.10 * 24 * 0.90, buyout_price)
    renew_plan["3年"] = min(buy_cost * 0.10 * 36 * 0.88, buyout_price)
    
    return {
        "购入成本": buy_cost,
        "押金": deposit,
        "买断价": buyout_price,
        "归还方案": return_plan,
        "续租方案": renew_plan,
    }


def format_result(result: dict) -> str:
    """格式化输出"""
    lines = [
        f"购入成本: ¥{result['购入成本']:,.0f}",
        f"押金: ¥{result['押金']:,.0f}",
        f"买断价: ¥{result['买断价']:,.0f}",
        "",
        "归还方案租金:",
    ]
    
    for term, price in result["归还方案"].items():
        lines.append(f"  {term}: ¥{price:,.0f}")
    
    lines.append("")
    lines.append("续租方案租金:")
    
    for term, price in result["续租方案"].items():
        lines.append(f"  {term}: ¥{price:,.0f}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cost = float(sys.argv[1])
    else:
        # 默认示例
        cost = 10000
    
    result = calculate_rent(cost)
    print(format_result(result))
