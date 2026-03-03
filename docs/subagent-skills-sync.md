# 子代理Skills配置指南

## 问题
子代理（cron任务、sessions_spawn）运行在独立环境，看不到主代理的skills目录。

## 解决方案
主代理维护 `skills-index.json` 和 `.skillsrc`，子代理启动时自动加载。

---

## 文件说明

### 1. skills-index.json
完整的技能索引（JSON格式），包含：
- 技能名称、路径、描述
- 核心技能列表
- workspace路径

### 2. .skillsrc
Shell环境变量配置，包含：
- SKILLS_DIR：技能目录路径
- SKILLS_INDEX：索引文件路径
- CORE_SKILLS：核心技能列表
- AVAILABLE_SKILLS：所有可用技能

### 3. scripts/sync_skills.py
自动扫描skills目录并更新索引文件

---

## 子代理使用方法

### Python子代理
```python
import json
from pathlib import Path

# 加载skills索引
workspace = Path("/Users/xs/.openclaw/workspace")
with open(workspace / "skills-index.json") as f:
    skills_index = json.load(f)

# 查找特定技能
rrz_skill = next(s for s in skills_index['skills'] if s['name'] == 'rrz')
skill_md_path = workspace / rrz_skill['skill_md']

# 读取SKILL.md
with open(skill_md_path) as f:
    skill_content = f.read()
```

### Shell子代理
```bash
# 加载环境变量
source ~/.openclaw/workspace/.skillsrc

# 使用
echo "Skills目录: $SKILLS_DIR"
echo "核心技能: $CORE_SKILLS"

# 读取特定技能
cat $SKILLS_DIR/rrz/SKILL.md
```

### 子代理启动模板
```python
# 在子代理开头添加
import json
from pathlib import Path

WORKSPACE = Path("/Users/xs/.openclaw/workspace")
SKILLS_INDEX = WORKSPACE / "skills-index.json"

def load_skill(skill_name):
    """加载指定技能的SKILL.md内容"""
    with open(SKILLS_INDEX) as f:
        index = json.load(f)
    
    skill = next((s for s in index['skills'] if s['name'] == skill_name), None)
    if not skill:
        return None
    
    skill_md = WORKSPACE / skill['skill_md']
    with open(skill_md) as f:
        return f.read()

# 使用示例
rrz_doc = load_skill('rrz')
if rrz_doc:
    print("已加载rrz技能文档")
```

---

## 主代理维护

### 手动更新索引
```bash
python3 scripts/sync_skills.py
```

### 自动更新（建议）
在HEARTBEAT.md或cron中添加：
```
每天检查一次skills变化，自动更新索引
```

---

## 集成到sessions_spawn

修改spawn调用，自动注入skills上下文：

```python
# 在task前添加skills加载指令
task_with_skills = f"""
首先加载skills配置：
- 读取 /Users/xs/.openclaw/workspace/skills-index.json
- 核心技能：rrz, rrz-publish, xhs-publish, image-generator

然后执行任务：
{original_task}
"""

sessions_spawn(task=task_with_skills, ...)
```

---

## 验证

测试子代理是否能访问skills：
```bash
# 创建测试子代理
openclaw cron add "测试skills访问" "cron 0 * * * *" "读取skills-index.json并列出所有技能名称"

# 查看执行结果
openclaw cron logs <job-id>
```
