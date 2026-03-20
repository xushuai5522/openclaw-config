# 人人租商品发布助手 - 使用文档

## 📦 安装方法

### 前置条件
1. 安装浏览器扩展管理器（任选其一）：
   - **Tampermonkey**（推荐）：[Chrome商店](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo) | [Firefox](https://addons.mozilla.org/firefox/addon/tampermonkey/)
   - **Violentmonkey**：[Chrome商店](https://chrome.google.com/webstore/detail/violentmonkey/jinjaccalgkegednnccohejagnlnfdag)

### 安装脚本
1. 点击 `rrz-auto-publish.user.js` 文件
2. 复制全部内容
3. 打开 Tampermonkey 管理面板
4. 点击「添加新脚本」
5. 粘贴代码，保存（Ctrl+S / Cmd+S）

## 🚀 使用方法

### 1. 打开人人租商家后台
访问商品发布页面：
- `https://merchant.renrenzu.com/publish`
- 或任何包含商品表单的页面

### 2. 界面说明
右侧会出现悬浮面板「🐂 发布助手」：

```
┌─────────────────────┐
│ 🐂 发布助手      [−]│
├─────────────────────┤
│ [选择模板 ▼]        │
│                     │
│ [📝 自动填充]       │
│ [🚀 一键提交]       │
│ [⚙️ 配置管理]       │
└─────────────────────┘
```

### 3. 核心功能

#### 📝 自动填充
- 根据选中的模板自动填充所有表单字段
- 包括：商品名称、分类、品牌、型号、押金、日租金、描述、图片

#### 🚀 一键提交
- 自动填充 + 自动点击提交按钮
- 适合批量发布相似商品

#### ⚙️ 配置管理
- 管理多个商品模板
- JSON格式配置，支持导入导出

### 4. 配置模板

点击「⚙️ 配置管理」，编辑JSON配置：

```json
{
  "templates": [
    {
      "name": "iPhone 14 Pro",
      "data": {
        "title": "iPhone 14 Pro 256GB 深空黑",
        "category": "手机数码",
        "brand": "Apple",
        "model": "iPhone 14 Pro",
        "deposit": "5000",
        "dailyRent": "50",
        "description": "<p>全新iPhone 14 Pro，支持灵动岛</p>",
        "images": [
          "https://example.com/image1.jpg",
          "https://example.com/image2.jpg"
        ]
      }
    },
    {
      "name": "MacBook Pro",
      "data": {
        "title": "MacBook Pro 14寸 M3 Pro",
        "category": "电脑办公",
        "brand": "Apple",
        "model": "MacBook Pro 14",
        "deposit": "12000",
        "dailyRent": "120",
        "description": "<p>M3 Pro芯片，18GB内存，512GB存储</p>",
        "images": [
          "https://example.com/mac1.jpg"
        ]
      }
    }
  ],
  "currentTemplate": 0
}
```

### 5. 图片上传说明

**支持两种方式：**

1. **URL方式**（推荐）：
   ```json
   "images": [
     "https://example.com/image1.jpg",
     "https://example.com/image2.jpg"
   ]
   ```
   脚本会自动下载并上传到人人租

2. **本地文件**：
   手动上传后，脚本会保留已上传的图片

## ⚙️ 高级功能

### 快捷键（可自定义）
- 打开配置：右键菜单 → 「📝 打开配置」

### 折叠面板
- 点击面板右上角「−」按钮可折叠/展开
- 折叠后只显示图标，不占用屏幕空间

### 批量操作
1. 准备多个模板
2. 切换模板 → 点击「🚀 一键提交」
3. 等待提交完成后，切换下一个模板
4. 重复操作

## 🔧 故障排查

### 问题1：脚本没有加载
**解决方法：**
- 检查 Tampermonkey 是否启用
- 检查脚本是否启用（绿色开关）
- 刷新页面（Ctrl+R / Cmd+R）

### 问题2：自动填充失败
**可能原因：**
- 人人租后台更新了页面结构
- 字段选择器不匹配

**解决方法：**
1. 打开浏览器控制台（F12）
2. 查看错误信息
3. 手动调整选择器：
   ```javascript
   // 在脚本中找到对应的选择器并修改
   fillInput('input[placeholder*="商品名称"]', data.title);
   // 改为实际的选择器
   fillInput('input[name="productName"]', data.title);
   ```

### 问题3：图片上传失败
**解决方法：**
- 确保图片URL可访问（不需要登录）
- 检查图片格式（支持jpg/png/webp）
- 图片大小不超过5MB
- 如果URL上传失败，改用手动上传

### 问题4：提交按钮找不到
**解决方法：**
- 检查提交按钮的实际选择器
- 修改脚本中的提交按钮查找逻辑：
   ```javascript
   const submitBtn = document.querySelector('button.your-submit-class');
   ```

## 🛡️ 安全说明

### 数据存储
- 所有配置存储在浏览器本地（GM_setValue）
- 不会上传到任何服务器
- 卸载脚本后数据会被清除

### 权限说明
- `@match`：只在人人租域名下运行
- `@grant GM_setValue/GM_getValue`：存储配置
- `@grant GM_registerMenuCommand`：注册右键菜单

### 兼容性
- 不会修改人人租后台的原始代码
- 不会影响后台正常使用
- 可以随时禁用/卸载脚本

## 📝 更新日志

### v1.0.0 (2026-03-04)
- ✅ 初始版本
- ✅ 支持自动填充表单
- ✅ 支持批量上传图片
- ✅ 支持多模板管理
- ✅ 支持一键提交
- ✅ 悬浮UI面板

## 🔮 后续计划

- [ ] 支持从Excel/CSV导入商品数据
- [ ] 支持定时发布
- [ ] 支持商品复制/克隆
- [ ] 支持批量修改价格
- [ ] 支持数据统计和导出

## 💡 使用技巧

### 技巧1：快速切换模板
- 为常用商品创建多个模板
- 使用快捷键快速切换

### 技巧2：图片复用
- 将常用图片上传到图床
- 在模板中使用图床URL
- 避免重复上传

### 技巧3：描述模板化
- 准备多个描述模板
- 使用HTML格式（支持富文本）
- 包含常用的租赁条款

### 技巧4：批量发布
```javascript
// 准备10个模板
// 使用循环自动发布
for (let i = 0; i < 10; i++) {
  // 切换模板
  // 点击一键提交
  // 等待3秒
}
```

## 🤝 反馈与支持

遇到问题或有建议？
- 查看浏览器控制台错误信息
- 检查人人租后台是否更新
- 联系开发者更新脚本

---

**开发者：电子牛马 🐂🐴**  
**版本：v1.0.0**  
**最后更新：2026-03-04**
