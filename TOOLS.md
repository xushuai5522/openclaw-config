# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

## 鼠标控制

### 原生方案（推荐）
- 编译好的程序：`/Users/xs/bin/mouse_click`
- 用法：`mouse_click x y`（移动到坐标并点击）
- 编译命令：
  ```bash
  gcc mouse_click.c -o mouse_click -framework CoreGraphics -framework CoreFoundation
  ```

### 备选方案
- `cliclick`（需通过 osascript 调用，权限有限）
- 路径：`/usr/local/Homebrew/bin/cliclick`

---

## 电商主图生成技能

### 技能位置
- 路径：`/Users/xs/.openclaw/workspace/skills/image-generator/SKILL.md`
- 功能：生成符合电商平台要求的商品主图

### 提示词模板
```
【电商商品主图生成】
产品：{product_name}

【处理步骤】
1. 背景移除：删除原图背景、所有文字，水印、logo
2. 商品优化：边缘锐利、材质清晰，光影自然、颜色准确
3. 背景设置：纯白色 #FFFFFF，居中布局
4. 输出规格：800×800px，PNG/JPG

【生成视角】
- 正面：商品正面完整展示
- 侧面45度：展示立体感和细节
- 背面：背面全貌和特征

【质量标准】
- 商品占比：70-80%
- 边缘：平滑无瑕疵
- 清晰度：高清锐利
- 光影：自然柔和

【风格】：干净专业、电商主图风格
```

### 火山引擎API
- 地址：https://ark.cn-beijing.volces.com/api/v3/images/generations
- Key：675362ca-6313-43e5-a705-3046f668e2b1
- 模型：doubao-seedream-4-0-250828

---

## NAS 连接

### 基础信息
- 品牌：飞牛NAS (FeiNiu fnOS)
- 型号：FAT-NIU
- IP地址：192.168.1.80
- Web管理：http://192.168.1.80:5666/
- 用户名：temp
- 密码：xs552200

### 服务配置
- SMB服务：已开启，端口445
- SSH服务：已开启，端口22
- WebDAV：支持（可作为备选）

### SMB共享设置
- 我的文件、他人共享：全部允许
- 团队文件：全部允许
- temp用户文件：Photos文件夹

### 连接方式

**方式1：Finder手动挂载（推荐）**
```bash
# 按 Cmd+K，输入：
smb://192.168.1.80

# 然后输入用户名temp和密码xs552200
# 查看实际的共享文件夹名称
```

**方式2：WebDAV（备选）**
```bash
# 如果SMB有问题，可以用WebDAV
# 具体地址需要在NAS后台查看
```

### 待解决问题
- 飞牛NAS的SMB共享名未确认（不是常见的temp/home/homes）
- 需要手动用Finder连接一次确认实际共享名
- 或通过SSH登录查看 /etc/samba/smb.conf 配置

---

Add whatever helps you do your job. This is your cheat sheet.
