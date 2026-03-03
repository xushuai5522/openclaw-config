---
name: github
description: "Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, and advanced queries."
---

# GitHub Skill

## 快速参考

- **触发词**: GitHub、PR、issue、CI、workflow
- **核心命令**: `gh pr`, `gh issue`, `gh run`, `gh api`
- **依赖工具**: gh CLI (GitHub官方命令行工具)

---

## 使用示例

### 示例1: 检查PR状态

**场景**: 查看PR #55的CI运行状态

```bash
# 检查PR的所有checks
gh pr checks 55 --repo owner/repo

# 输出示例:
# ✓ build       1m30s  https://github.com/...
# ✓ test        2m15s  https://github.com/...
# ✗ lint        45s    https://github.com/...

# 查看失败的check详情
gh run view <run-id> --repo owner/repo --log-failed
```

---

### 示例2: 创建和管理Issue

```bash
# 创建issue
gh issue create --repo owner/repo \
  --title "Bug: 登录失败" \
  --body "用户反馈登录时返回500错误" \
  --label bug \
  --assignee @me

# 列出所有open的issues
gh issue list --repo owner/repo --state open

# 列出分配给我的issues
gh issue list --repo owner/repo --assignee @me

# 查看issue详情
gh issue view 123 --repo owner/repo

# 关闭issue
gh issue close 123 --repo owner/repo --comment "已修复"

# 重新打开issue
gh issue reopen 123 --repo owner/repo
```

---

### 示例3: PR工作流

```bash
# 创建PR
gh pr create --repo owner/repo \
  --title "feat: 添加用户登录功能" \
  --body "实现了用户登录和注册功能" \
  --base main \
  --head feature/login

# 列出所有PR
gh pr list --repo owner/repo

# 查看PR详情
gh pr view 55 --repo owner/repo

# 查看PR的diff
gh pr diff 55 --repo owner/repo

# checkout PR到本地
gh pr checkout 55 --repo owner/repo

# 合并PR
gh pr merge 55 --repo owner/repo --squash

# 关闭PR（不合并）
gh pr close 55 --repo owner/repo
```

---

### 示例4: CI/CD工作流管理

```bash
# 列出最近的workflow runs
gh run list --repo owner/repo --limit 10

# 查看特定run的详情
gh run view 123456 --repo owner/repo

# 查看失败的步骤日志
gh run view 123456 --repo owner/repo --log-failed

# 重新运行失败的workflow
gh run rerun 123456 --repo owner/repo

# 取消正在运行的workflow
gh run cancel 123456 --repo owner/repo

# 查看workflow文件
gh workflow list --repo owner/repo
gh workflow view ci.yml --repo owner/repo
```

---

### 示例5: 使用API进行高级查询

```bash
# 获取PR的详细信息
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'

# 获取仓库的统计信息
gh api repos/owner/repo --jq '.stargazers_count, .forks_count, .open_issues_count'

# 列出所有collaborators
gh api repos/owner/repo/collaborators --jq '.[].login'

# 获取最近的commits
gh api repos/owner/repo/commits --jq '.[] | "\(.sha[0:7]) \(.commit.message)"'

# 搜索代码
gh api search/code?po:owner/repo+language:python+TODO --jq '.items[].path'
```

---

### 示例6: JSON输出和过滤

```bash
# 列出issues并格式化输出
gh issue list --repo owner/repo \
  --json number,title,state,labels \
  --jq '.[] | "\(.number): \(.title) [\(.state)]"'

# 列出PR并过滤特定作者
gh pr list --repo owner/repo \
  --json number,title,author \
  --jq '.[] | select(.author.login == "username") | "\(.number): \(.title)"'

# 获取最近关闭的issues
gh issue list --repo owner/repo \
  --state closed \
  --limit 5 \
  --json number,title,closedAt \
  --jq '.[] | "\(.number): \(.title) (closed: \(.closedAt))"'
```

---

## Pull Requests

Check CI status on a PR:
```bash
gh pr checks 55 --repo owner/repo
```

List recent workflow runs:
```bash
gh run list --repo owner/repo --limit 10
```

View a run and see which steps failed:
```bash
gh run view <run-id> --repo owner/repo
```

View logs for failed steps only:
```bash
gh run view <run-id> --repo owner/repo --log-failed
```

## API for Advanced Queries

The `gh api` command is useful for accessing data not available through other subcommands.

Get PR with specific fields:
```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```

## JSON Output

Most commands support `--json` for structured output. You can use `--jq` to filter:

```bash
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
```

---

## 常用场景

### 代码审查流程
```bash
# 1. 列出待审查的PR
gh pr list --repo owner/repo --label "needs-review"

# 2. checkout PR到本地
gh pr checkout 55

# 3. 查看代码变更
gh pr diff 55

# 4. 添加review评论
gh pr review 55 --comment --body "LGTM!"

# 5. 批准PR
gh pr review 55 --approve

# 6. 合并PR
gh pr merge 55 --squash
```

### Bug修复流程
```bash
# 1. 创建issue
gh issue create --title "Bug: xxx" --label bug

# 2. 创建分支修复
git checkout -b fix/issue-123

# 3. 提交代码后创建PR
gh pr create --title "fix: 修复issue #123"

# 4. 关联issue
gh pr edit 55 --add-label "fixes #123"

# 5. 合并后自动关闭issue
gh pr merge 55 --squash
```

---

## 配置说明

### 认证
```bash
# 登录GitHub
gh auth login

# 查看当前认证状态
gh auth status

# 切换账号
gh auth switch
```

### 默认仓库
```bash
# 在git仓库目录下，自动识别仓库
cd /path/to/repo
gh pr list  # 自动使用当前仓库

# 或者设置默认仓库
gh repo set-default owner/repo
```

---

## 依赖工具

- **gh CLI**: GitHub官方命令行工具
  - 安装: `brew install gh` (macOS)
  - 文档: https://cli.github.com/

---

## 常见问题

### 认证失败
```bash
# 重新登录
gh auth logout
gh auth login
```

### 找不到仓库
```bash
# 确保指定了正确的仓库
gh pr list --repo owner/repo

# 或者在仓库目录下执行
cd /path/to/repo
gh pr list
```

### API限流
```bash
# 查看API限流状态
gh api rate_limit

# 使用认证token可以提高限流上限
gh auth login
```
