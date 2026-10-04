`access_token` 已过期。按以下步骤处理：

1. 用 `refresh_token` 调用 `POST /oauth/refresh`，获取新的 `access_token`。刷新不是让用户重新登录，也不是重启会话。
2. 如果刷新返回 `invalid_grant`，说明 `refresh_token` 也已过期。停止重试，告诉用户需要重新授权。
3. 如果刷新成功，用新的 `access_token` 把刚才失败的那一个请求原样重发。只重发 1 次。

如果失败的请求是写操作（POST、PUT、DELETE），第 3 步按以下规则执行：

- 请求带有 `Idempotency-Key`：可以直接重发。
- 请求没有带 `Idempotency-Key`：先确认上一次请求是否已经生效，再决定是否重发。
