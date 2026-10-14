`access_token` 已过期。
调用方用 `refresh_token` 调用 `POST /oauth/refresh`，换取新的 `access_token`。刷新方式不是让用户重新登录，也不是重启会话。
刷新返回 `invalid_grant` 时，`refresh_token` 也已过期。这时调用方停止重试，并告诉用户需要重新授权。
刷新成功后，调用方把刚才失败的那一个请求原样重发一次。调用方只重试一次。
失败的请求是写操作（POST、PUT、DELETE）时，按以下规则处理：
1. 请求带了 `Idempotency-Key` 时，调用方可以原样重发。
2. 请求没带 `Idempotency-Key` 时，调用方先确认上一次请求有没有生效。
保留未改：本次请求是否完全没有执行？
