`access_token` 已过期。
请调用方用 `refresh_token` 调用 `POST /oauth/refresh`，换取新的 `access_token`。然后重试这次请求。
调用方不必让用户重新登录，也不必重启会话。
如果 `POST /oauth/refresh` 返回 `invalid_grant`，说明 `refresh_token` 也已过期。
这时调用方停止重试，并告诉用户需要重新授权。
