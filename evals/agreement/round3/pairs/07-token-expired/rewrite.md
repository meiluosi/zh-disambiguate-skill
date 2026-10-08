`access_token` 已过期。
调用方用 `refresh_token` 调用 `POST /oauth/refresh`，换取新的 `access_token`。然后调用方重试原请求。
刷新 `access_token` 的方式不是让用户重新登录，也不是重启会话。
`POST /oauth/refresh` 返回 `invalid_grant` 时，`refresh_token` 也已经过期。
这时调用方停止重试。调用方告诉用户需要重新授权。
