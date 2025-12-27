# Bug Reports - 博客系统


## BUG-SEC-001：CSRF保护未生效 - 创建文章
- 来源用例：TC-SEC-001
- 严重级别：高（安全风险）
- 优先级：P0
- 状态：Verified（已修复并回归通过）

### 复现环境
- 浏览器：Chrome
- 账号：otheruser（已登录）

### 前置条件
- 用户处于已登录状态（Cookie中有有效 session）

### 复现步骤
1. 构造请求：POST `/blog/create`
2. 表单数据：`title=aaa`，`body=bbb`
3. 不携带 `csrf_token` 参数（仅携带登录 Cookie）
4. 发送请求

### 实际结果
- 请求未被拒绝，返回 `HTTP 200 OK`
- 页面不显示 CSRF 校验错误提示

### 回归结果
- 修复后回归：缺失 csrf_token 的 POST `/blog/create` 被拒绝（HTTP 400），文章不会被创建

### 预期结果
- 服务端应拒绝缺失/无效 CSRF token 的 POST 请求（建议 400/403），并提示 CSRF 校验失败

### 修复建议
- 在所有修改数据的接口（create/edit/delete）统一启用并强制校验 CSRF token，缺失/无效直接拒绝。

### 回归点
- 携带有效 token 创建文章成功
- 缺失/无效 token 创建文章失败（400/403），且不产生新文章

### 证据
- 截图：`screenshots/BUG-SEC-001.png`

---

## BUG-SEC-002：CSRF保护未生效 - 删除文章
- 来源用例：TC-SEC-002
- 严重级别：高（安全风险）
- 优先级：P0
- 状态：Verified（已修复并回归通过）

### 复现环境
- 浏览器：Chrome
- 账号：testuser（已登录，且为文章作者）

### 前置条件
- 存在文章：ID=5

### 复现步骤
1. 构造请求：POST `/blog/post/5/delete`
2. 不携带 `csrf_token` 参数（仅携带登录 Cookie）
3. 发送请求
4. 再次访问文章详情页确认文章是否存在

### 实际结果
- 删除请求未被拒绝，返回 `HTTP 302` 重定向到 `/`
- 文章被成功删除（再次访问详情页显示不存在/404）

### 回归结果
- 修复后回归：缺失 csrf_token 的 POST `/blog/post/5/delete` 被拒绝（HTTP 400），文章不会被删除

### 预期结果
- 服务端应拒绝缺失/无效 CSRF token 的删除请求（建议 400/403），文章不应被删除

### 修复建议
- 删除接口强制校验 CSRF token，缺失/无效直接拒绝请求。

### 回归点
- 携带有效 token 删除成功
- 缺失/无效 token 删除失败（400/403），文章仍存在

### 证据
- 截图：`screenshots/BUG-SEC-002.png`

---

## BUG-UX-001：登录后未按 next 参数跳转回原目标页面
- 来源用例：TC-UX-006
- 严重级别：中
- 优先级：P1
- 状态：Verified（已修复并回归通过）

### 复现环境
- 浏览器：Chrome
- 账号：testuser

### 前置条件
- 用户未登录（清空 Cookie / 无会话）

### 复现步骤
1. 未登录访问受保护页面：`/blog/create`
2. 页面跳转到登录页，并携带 `next` 参数
3. 输入正确账号密码登录

### 实际结果
- 登录成功后跳转到首页（`/`）
- 未跳转回 `next` 指定页面（如 `/blog/create`）

### 回归结果
- 修复后回归：登录页携带 next 参数时，登录成功后按 next 重定向回原目标页面（如 `/blog/create`）

### 预期结果
- 登录成功后应按 `next` 参数返回原目标页面（同时需校验 next 合法性，避免开放重定向）

### 修复建议
- 登录表单提交需保留 URL 上的 next 参数（避免 POST 丢失 querystring）；登录成功后校验并按 next 跳转。

### 回归点
- next 指向 `/blog/create` 时，登录成功后返回 `/blog/create`
- next 缺失/非法时，登录成功后跳转默认首页

### 备注
- 创建/编辑/删除后的跳转逻辑均正常，问题集中在登录后的 next 参数处理

### 证据
- 截图：`screenshots/BUG-UX-001.png`

