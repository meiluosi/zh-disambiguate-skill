403：当前账号没有 `project:deploy` 权限，不能操作 `prod-gateway`。

请按以下步骤处理：

1. 联系项目管理员。
2. 请项目管理员在「成员管理」中给当前账号添加角色。角色必须是 `Maintainer` 或更高（含 `Maintainer`），例如 `Maintainer` 或 `Owner`。`Developer` 和 `Reporter` 角色不满足要求。
3. 添加角色后，重新登录。
4. 重试操作。

保留未改：「不能操作 `prod-gateway`」包括只读操作吗？账号缺少 `project:deploy` 权限时，对 `prod-gateway` 的只读操作也不能执行吗？
