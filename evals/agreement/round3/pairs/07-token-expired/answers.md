（1）我当时的想法是用 `refresh_token` 调 `POST /oauth/refresh` 换新的 `access_token`，不是让用户重新登录，也不是重启会话。
（2）如果刷新本身返回 `invalid_grant`，说明 `refresh_token` 也过期了，就停止重试，告诉用户需要重新授权。
