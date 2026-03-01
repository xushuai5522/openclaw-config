#!/usr/bin/env python3
"""
每日总结生成脚本
根据前一天对话记录生成总结、反思、优化文档
"""
import os
from datetime import datetime, timedelta

# 日期（前一天）
today = datetime.now()
yesterday = today - timedelta(days=1)
date_str = yesterday.strftime("%Y-%m-%d")
date_dir = yesterday.strftime("%Y/%m/%d")

# 路径
base_dir = "/Users/xs/.openclaw/workspace/chat-history"
output_dir = f"{base_dir}/{date_dir}"
history_file = f"{output_dir}/001-流水线搭建.md"  # 假设的主文件

# 创建输出文件
summary_file = f"{output_dir}/999-每日总结.md"

# 检查是否有对话记录
if not os.path.exists(output_dir):
    print(f"目录不存在: {output_dir}")
    exit(0)

# 获取当天所有文件
files = sorted([f for f in os.listdir(output_dir) if f.endswith('.md')])

# 读取对话内容
content = ""
for f in files:
    with open(f"{output_dir}/{f}", 'r') as fp:
        content += f"\n\n=== {f} ===\n\n"
        content += fp.read()

# 生成总结文档
summary = f"""# {date_str} 每日总结

## 📋 总结

[根据当日对话内容自动生成]

## 🤔 反思

1. 哪些地方可以做得更好？
2. 遇到的问题及解决方案
3. 需要改进的流程

## 🚀 优化

1. 下一步可以改进的方向
2. 需要固化的新技能
3. 需要优化的流程

---

*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

# 写入文件
os.makedirs(output_dir, exist_ok=True)
with open(summary_file, 'w') as f:
    f.write(summary)

print(f"每日总结已生成: {summary_file}")
