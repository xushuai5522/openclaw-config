#!/usr/bin/env python3
"""
Skills同步工具 - 为子代理生成skills配置
主代理定期运行此脚本，更新 .skillsrc 和 skills-index.json
"""
import os
import json
from pathlib import Path

WORKSPACE = Path("/Users/xs/.openclaw/workspace")
SKILLS_DIR = WORKSPACE / "skills"
OUTPUT_JSON = WORKSPACE / "skills-index.json"
OUTPUT_RC = WORKSPACE / ".skillsrc"

def scan_skills():
    """扫描skills目录，生成索引"""
    skills = []
    
    if not SKILLS_DIR.exists():
        return skills
    
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        
        # 读取SKILL.md前几行提取描述
        description = ""
        with open(skill_md, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[:10]:
                if line.startswith('description:'):
                    description = line.replace('description:', '').strip()
                    break
        
        skills.append({
            "name": skill_dir.name,
            "path": f"skills/{skill_dir.name}",
            "skill_md": f"skills/{skill_dir.name}/SKILL.md",
            "description": description
        })
    
    return skills

def generate_json(skills):
    """生成JSON索引"""
    data = {
        "workspace": str(WORKSPACE),
        "skills_dir": str(SKILLS_DIR),
        "total": len(skills),
        "skills": skills,
        "core_skills": [
            "rrz", "rrz-publish", "xhs-publish", 
            "image-generator", "finance-butler"
        ]
    }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 生成 {OUTPUT_JSON}")

def generate_shellrc(skills):
    """生成shell配置文件"""
    skills_list = ' '.join([s['name'] for s in skills])
    lines = [
        "# Skills配置文件 - 供子代理读取",
        "# 主代理自动生成，请勿手动编辑",
        "",
        f"export SKILLS_DIR={SKILLS_DIR}",
        f"export SKILLS_INDEX={OUTPUT_JSON}",
        "",
        "# 核心技能列表",
        "export CORE_SKILLS='rrz rrz-publish xhs-publish image-generator finance-butler'",
        "",
        "# 所有可用技能",
        f"export AVAILABLE_SKILLS='{skills_list}'",
        "",
        "# 使用方法：",
        "# source ~/.openclaw/workspace/.skillsrc",
        "# echo \\$SKILLS_DIR",
        "# cat \\$SKILLS_INDEX | jq '.skills[] | select(.name==\\\"rrz\\\")'",
    ]
    
    with open(OUTPUT_RC, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ 生成 {OUTPUT_RC}")

def main():
    print("🔍 扫描skills目录...")
    skills = scan_skills()
    print(f"📦 找到 {len(skills)} 个技能")
    
    generate_json(skills)
    generate_shellrc(skills)
    
    print("\n✅ Skills索引已更新")
    print(f"   JSON: {OUTPUT_JSON}")
    print(f"   Shell: {OUTPUT_RC}")
    print("\n子代理使用方法：")
    print("  1. Python: json.load(open('skills-index.json'))")
    print("  2. Shell: source .skillsrc && echo $SKILLS_DIR")

if __name__ == '__main__':
    main()
