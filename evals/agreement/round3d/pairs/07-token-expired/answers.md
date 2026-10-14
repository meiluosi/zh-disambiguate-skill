（1）我当时的想法是用 `refresh_token` 调 `POST /oauth/refresh` 换新的 `access_token`，不是让用户重新登录，也不是重启会话。如果刷新本身返回 `invalid_grant`，说明 `refresh_token` 也过期了，就停止重试，告诉用户需要重新授权。
（2）本次请求是否完全没有执行，我当时没想过这一点。关于重试，我当时的想法是把刚才失败的那一个请求原样重发一次，只重试一次；写操作（POST/PUT/DELETE）带了 `Idempotency-Key` 才可以安全重发，没带的先确认上一次有没有生效。
