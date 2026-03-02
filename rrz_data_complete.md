# 人人租后台完整功能数据

## 已掌握页面数据

### 1. 首页 (/site/index)
- 今日数据：待发货 0、待归还 1、待结算 6
- 累计成交：30单、¥31,480、租出49
- 在租设备：8台

### 2. 我的商品 (/spu-view/my-list)
- Xiaomi Pad 5 11英寸 80新
- Xiaomi Pad 6S Pro 12.4英寸 90新

### 3. 订单列表 (/order/v4-order-index)
- 侧边栏菜单：
  - 订单列表-v4
  - 发货工作台
  - 售后工作台
  - 企销售后
  - 检测单
  - 凭证审核列表
  - 逾期订单列表 46
  - 购买申请
  - 设备管控申请
  - 预授权到期列表
  - 接单高级设置
  - 法务助手
  - 物流管理
  - 用户投诉

### 4. 资金账户 (/account/asset-index)
- 侧边栏菜单：
  - 资金账户
  - 报销管理
  - 提现记录
  - 申请提现
  - 对账管理
  - 发票管理
- 当前余额显示区域

### 5. 工单中心 (/user-wo/my-handle-index)
- 侧边栏菜单：
  - 客诉工单
  - 进行中的工单
  - 已完成的工单
  - 客诉工单总览
  - 商家工单
  - 服务工单
  - 店铺违规

### 6. 店铺诊断 (/shuzhi/shop-diag)
- 侧边栏菜单：
  - 数据查询
  - 店铺诊断
  - 经营情况查询
  - 发货数据查询
  - 经营月报详情
  - 配置中心

### 7. 营销中心 (/commodity-promote-v2/index)
- 侧边栏菜单：
  - 商家服务
  - 推广活动2.0
  - 服务市场
  - 我的服务
  - 租用订单预约回收
  - 平台项目
  - 返佣中心
  - 应用中心
  - 营销工具
  - 权益中心

### 8. 发布商品 (/spu-view/create)
- iframe中的表单
- 字段：
  - 商品关键词搜索
  - 一级类目
  - 二级类目
  - 品牌
  - 型号
- 按钮：搜索、确认下一步
- ⚠️ 需要风控验证

---

## 页面访问方式

### 可直接访问的页面
1. 首页: https://admin.rrzu.com/site/index
2. 我的商品: https://admin.rrzu.com/spu-view/my-list
3. 发布商品: https://admin.rrzu.com/spu-view/create
4. 订单列表: https://admin.rrzu.com/order/v4-order-index
5. 资金账户: https://admin.rrzu.com/account/asset-index
6. 工单中心: https://admin.rrzu.com/user-wo/my-handle-index
7. 代发设备: https://admin.rrzu.com/warehouse/all-device-index
8. 回收订单: https://admin.rrzu.com/recycle-batch-order/index
9. 店铺诊断: https://admin.rrzu.com/shuzhi/shop-diag
10. 营销中心: https://admin.rrzu.com/commodity-promote-v2/index

### 页面特点
- 主页面是外壳，侧边栏菜单需要点击才展开
- 内容在iframe中加载
- 部分页面需要登录态验证

---
最后更新: 2026-02-19
