#!/usr/bin/env python3
"""Open Interpreter 启动脚本 - 使用中转API连接Claude"""

from interpreter import interpreter

# 中转API配置
interpreter.llm.api_key = "sk-5e5rZgZ17IiakvNWPDFCKfdSzhlvQ1AlZtv5zfnPcE9FUuYk"
interpreter.llm.api_base = "https://www.zhongzhuan.win/v1"
interpreter.llm.model = "openai/aws.amazon/claude-opus-4-5:once"

# 基础设置
interpreter.auto_run = False  # 安全起见，执行代码前确认
interpreter.llm.supports_functions = True
interpreter.llm.supports_vision = True

# 启动交互式会话
interpreter.chat()
