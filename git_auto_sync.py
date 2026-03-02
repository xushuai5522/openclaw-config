#!/usr/bin/env python3
"""
Git自动同步脚本
每天检测OpenClaw配置和项目文件是否有变更，有变更则自动提交
"""
import os
import sys
import subprocess
from datetime import datetime
import json

# 配置
WORKSPACE = "/Users/xs/.openclaw/workspace"
CONFIG_FILE = "/Users/xs/.openclaw/openclaw.json"
REPOS = {
    "openclaw-config": "/Users/xs/.openclaw/workspace",
    "openclaw-projects": "/Users/xs/.openclaw/workspace"
}

def run_cmd(cmd, cwd=None):
    """执行命令"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr

def check_git_changes(repo_path):
    """检查Git变更"""
    code, stdout, stderr = run_cmd("git status --porcelain", cwd=repo_path)
    return stdout.strip()

def commit_changes(repo_path, repo_name):
    """提交变更"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 获取变更文件列表
    changes = check_git_changes(repo_path)
    if not changes:
        return False, "无变更"
    
    # 添加所有变更
    run_cmd("git add -A", cwd=repo_path)
    
    # 提交
    commit_msg = f"{today}: 自动同步变更"
    code, stdout, stderr = run_cmd(f'git commit -m "{commit_msg}"', cwd=repo_path)
    
    if code == 0:
        return True, f"提交成功: {changes[:200]}"
    else:
        return False, f"提交失败: {stderr}"

def sync_to_github(repo_path, repo_name):
    """推送到GitHub"""
    # 先获取远程状态
    code, stdout, stderr = run_cmd("git remote -v", cwd=repo_path)
    
    # 检查是否需要设置远程
    if "origin" not in stdout:
        # 从仓库名推断GitHub地址
        github_url = f"https://github.com/xushuai5522/{repo_name}.git"
        run_cmd(f"git remote add origin {github_url}", cwd=repo_path)
    
    # 推送
    code, stdout, stderr = run_cmd("git push -u origin main", cwd=repo_path)
    
    if code == 0:
        return True, "推送成功"
    else:
        return False, f"推送失败: {stderr}"

def main():
    """主函数"""
    results = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    print(f"🔄 [{today}] 开始检测Git变更...")
    
    for repo_name, repo_path in REPOS.items():
        print(f"\n📂 检查仓库: {repo_name}")
        
        # 检查变更
        changes = check_git_changes(repo_path)
        if changes:
            print(f"  📝 发现变更: {len(changes.split())} 个文件")
            
            # 提交
            success, msg = commit_changes(repo_path, repo_name)
            print(f"  {msg}")
            
            if success:
                # 推送
                success, msg = sync_to_github(repo_path, repo_name)
                print(f"  🚀 {msg}")
                results.append(f"✅ {repo_name}: {msg}")
            else:
                results.append(f"❌ {repo_name}: {msg}")
        else:
            print(f"  ✅ 无变更")
    
    # 输出结果
    print(f"\n{'='*50}")
    print("📊 同步结果:")
    for r in results:
        print(f"  {r}")
    
    if not results:
        print("  ✅ 所有仓库已是最新状态")
    
    return results

if __name__ == "__main__":
    main()
