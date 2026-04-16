# 页面设计说明（桌面优先）

## 全局设计规范（两页共用）
### Layout
- 桌面优先：内容容器 `max-width: 1200px` 居中；左右留白随屏幕增大而增加。
- 使用 CSS Grid + Flex 混合：
  - 主内容区卡片列表使用 Grid（桌面 2 列；<= 992px 变 1 列）。
  - 卡片内部标题区、工具区（按钮/分页）使用 Flex 对齐。

### Meta Information
- Title：沿用现有标题（Dashboard：`我的后台 - 教材交易区块链系统`；Status：`区块链状态 - 教材交易区块链系统`）。
- Description：补充一句页面用途（可写在 `<meta name="description">`）。
- Open Graph：可选（若暂不做外链分享，可不加）。

### Global Styles（Design Tokens）
- 背景：`--bg: #f5f5f5`
- 卡片：`--card: #ffffff`，圆角 10px，阴影 `0 6px 18px rgba(16,24,40,.08)`
- 主色（延续现有绿）：`--primary: #4CAF50`，hover `#45a049`
- 文本：主文本 `#111827`，次级 `#6B7280`，分隔线 `#E5E7EB`
- 字体：中文优先 `ui-sans-serif, system-ui, -apple-system, "Segoe UI", Arial`；等宽 `ui-monospace, SFMono-Regular, Menlo, Consolas`
- 按钮：
  - Primary：绿色底白字
  - Secondary：深灰底白字
  - Danger：红色底白字
  - Hover/Focus：增加轻微上浮（translateY(-1px)）与更深阴影
- 链接：默认与主色一致；hover 下划线

### Vue 渐进式“岛屿”交互规范
- Vue 只挂载到指定容器（`#dashboard-app` / `#blockchain-status-app`），不接管整个 `<body>`。
- 首屏无闪烁：Jinja 可先输出简化骨架或旧内容；Vue 挂载后替换为组件化 UI。
- 轻提示：复制成功/失败、提交确认前提示等统一用顶部 Toast（如不引入库，可用自研轻量组件）。

---

## 页面 1：我的后台（/dashboard）
### Page Structure
- 顶部：Header（站点标题 + 当前用户信息）
- 第二层：Nav（与现有链接一致）
- 内容区：
  1) “我的账号”卡片（单列）
  2) 下方网格区（桌面 2 列）：左列“我发布的教材”，右列“待确认交易”；下一行“我发起的交易（买家）”可跨两列（更利于阅读长列表）

### Sections & Components
1. Header
- 左：站点名“教材交易区块链系统”
- 右/副标题：`我的后台（{user_name or user_id}）`
- 背景用主色，文字白色；高度更紧凑（桌面 64–80px）。

2. Nav（可抽成复用组件）
- 水平导航，当前页高亮；hover 反白或底部主色下划线。
- 小屏：折叠为“更多”下拉（可选；若不做折叠，则允许换行）。

3. 我的账号卡片（AccountCard）
- 信息行：`用户ID` 等宽展示；右侧“复制”按钮。
- 复制交互：点击后 Toast 提示“复制成功/失败”（替代 alert）。

4. 我发布的教材（TextbookListCard）
- 顶部工具区：标题 + “发布新教材”按钮。
- 列表项（TextbookItem）：
  - 主要信息（教材ID、创建时间）置顶
  - 次要信息（位置、描述）以浅色文本展示
  - 图片区域：若多图，使用横向可滚动缩略图条（不改变数据，只改变排布）
  - 操作：保持“查看详情”链接按钮
- 空状态：展示简短引导“暂无发布记录”。

5. 待确认交易（PendingTxCard）
- 顶部：标题 + 辅助说明“只显示你作为卖家、状态为 pending 的交易”。
- 列表项：交易ID突出显示；买家信息、报价、状态分组展示。
- 操作区：
  - 保持现有两个 `<form method="POST">` 提交逻辑不变
  - UI 上改为并排按钮，并加“确认前二次确认弹层”（可选；若不加，至少做 hover 与禁用态）

6. 我发起的交易（BuyerTxCard）
- 列表项信息密度适中：交易ID、教材、报价、状态、时间；卖家信息（若存在）放在次要区域。
- 操作：保留“查看教材详情”。

### Responsive Behavior
- >= 992px：网格 2 列；买家交易卡跨两列。
- < 992px：所有卡片单列堆叠；按钮宽度自适应，图片缩略图保持可滚动。

---

## 页面 2：区块链状态（/blockchain/status）
### Page Structure
- 顶部 Header + Nav（与 Dashboard 视觉一致，形成统一品牌）
- 内容区单列：
  1) 链状态概览卡（区块数量 + 有效性标签）
  2) 分页条（上方一次 + 下方一次，沿用现有结构）
  3) 区块列表（BlockList）

### Sections & Components
1. 链状态概览（ChainSummary）
- 指标卡样式：
  - “区块数量”以大号数字突出
  - “有效/无效”用状态徽标（绿/红）替代纯文本

2. 分页条（Pager）
- 左：上一页按钮；中：`第 page / total_pages 页`；右：下一页按钮。
- 禁用态：灰度 + 禁止点击（与现有 `.disabled` 一致，但视觉更明显）。
- 保持链接跳转：href 仍为 `/blockchain/status?page=...`。

3. 区块卡片（BlockItem）
- 标题：`区块 #index`
- 信息区：timestamp、previous_hash、hash、交易数量
  - hash 使用等宽字体 + 可复制按钮（可选；若实现，仍不改后端）
- 交易列表（TransactionList）：
  - 每笔交易为子卡片（TransactionItem）
  - 字段保持“存在才展示”的规则（与当前模板一致）

4. 返回入口
- 保留“← 返回首页”链接，样式统一为次要链接按钮。

### Responsive Behavior
- 桌面：区块卡片内信息区可用两列 definition list（DL）布局。
- 小屏：信息区改为单列，hash 自动换行并提供复制。
