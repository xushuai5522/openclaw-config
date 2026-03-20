# 人人租Mac本地自动化方案

> 状态说明（2026-03-15）：这个目录保留为**当前主线联调入口**，适合本机图形界面下处理弹窗、导航、观察式开发和与大哥实时协同调试。

## 目标
解决"经营地址信息补充"弹窗问题，完成商品发布流程

## 环境要求
- Mac系统（有完整图形界面）
- Python 3.x
- Selenium
- ChromeDriver（位于 ~/bin/chromedriver）

## 安装依赖

```bash
pip3 install selenium
```

## 使用方法

```bash
cd /Users/xs/.openclaw/workspace/projects/rrz-mac-runner/
python3 rrz_mac_auto.py
```

## 功能特性

### 1. 智能弹窗关闭（核心功能）
- 自动检测并关闭"经营地址信息补充"弹窗
- 支持多种关闭方式：
  - 按钮文本匹配（跳过、确认、知道了等）
  - CSS选择器匹配（.el-dialog__close等）
  - JavaScript强制关闭
- 在登录后、导航时、操作前自动执行

### 2. 自动登录
- 自动填写手机号
- 自动点击"获取验证码"
- 等待用户手动输入验证码
- 登录成功后立即关闭弹窗

### 3. 商品列表导航
- 自动导航到商品管理 → 商品列表
- 每次导航后自动关闭弹窗
- 切换到iframe查看商品数据

### 4. 审核不通过商品查找
- 自动切换到iframe
- 查找所有"审核不通过"的商品
- 返回商品列表

### 5. 截图记录
- 关闭弹窗后截图
- 最终状态截图
- 保存到项目目录

## 弹窗关闭策略

### 方法1：按钮文本匹配
```python
popup_buttons = ['跳过', '确认', '知道了', '取消', '关闭', '×']
```

### 方法2：CSS选择器
```python
close_selectors = [
    '.el-dialog__close',
    '.el-message-box__close',
    '.el-notification__closeBtn'
]
```

### 方法3：JavaScript强制关闭
```javascript
// 隐藏所有弹窗
document.querySelectorAll('.el-dialog, .el-message-box').forEach(el => {
    el.style.display = 'none';
});

// 移除遮罩层
document.querySelectorAll('.el-dialog__wrapper').forEach(el => {
    el.remove();
});

// 恢复body滚动
document.body.style.overflow = 'auto';
```

## 执行流程

1. 启动浏览器（非headless模式）
2. 打开人人租后台登录页
3. 自动填写手机号并发送验证码
4. 等待用户手动输入验证码
5. 登录成功后立即关闭弹窗
6. 导航到商品列表（每步都关闭弹窗）
7. 切换到iframe查看商品
8. 查找审核不通过的商品
9. 截图保存
10. 保持浏览器30秒供查看

## 输出文件

- `product_list_after_close_popups.png` - 关闭弹窗后的截图
- `final_state.png` - 最终状态截图

## 预计耗时

约30分钟（包括手动输入验证码时间）

## 下一步扩展

- [ ] 自动修复审核不通过的商品
- [ ] 批量替换禁止词
- [ ] 自动提交审核
- [ ] 商品发布功能
