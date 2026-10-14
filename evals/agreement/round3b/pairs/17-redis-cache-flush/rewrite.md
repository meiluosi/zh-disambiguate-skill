缓存数据脏了、需要清理时，不得执行 `FLUSHALL`。`FLUSHALL` 会同时删除 session，所有用户都要重新登录。

按以下步骤清理：

1. 执行 `redis-cli --scan --pattern 'product:*'`，找出要删除的 key。`product:*` 只是示例，你必须把 pattern 改成实际受影响的 key 前缀。pattern 不得匹配 session 的前缀 `sess:*`。
2. 分批 `UNLINK` 这些 key，每批约 500 个。每两批之间执行 `sleep 1`。
3. 删除完成后，观察数据库 CPU。数据库 CPU 指主库监控面板上的 CPU，不是 Redis 的 CPU。清理缓存后，请求会穿透到数据库。
4. 如果数据库 CPU 持续 1 分钟超过 70%，暂停删除。数据库 CPU 回到 50% 以下后，再继续删除。

保留未改：（1）观察数据库 CPU 是在每批 `UNLINK` 之后，还是全部删完之后？（2）「回到 50% 以下」是否含 50%？
