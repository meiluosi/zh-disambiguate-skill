工具在只读副本上执行 SQL 查询，并返回结果行。
工具只接受 `SELECT` 语句。其他语句会直接报错。
会报错的语句包括 `INSERT`、`UPDATE`、`DELETE`、`DROP` 和 `EXPLAIN ANALYZE`。`EXPLAIN ANALYZE` 会真实执行语句，所以也会报错。
查询运行超过 30 秒时，工具终止查询，并返回错误码 `QUERY_TIMEOUT`。
调用方收到 `QUERY_TIMEOUT` 后，缩小查询范围再重试。不要原样重发同一个查询。
行数超过约 500 万的表是大表。目前的大表主要是 `events` 和 `order_items`。
查询大表时，调用方必须至少带上以下一项：时间范围、`LIMIT`。不带的查询基本跑不完。
查询 `events` 或 `order_items` 时，调用方必须同时满足以下两条：
1. 带上 `created_at` 的范围条件。
2. 带上 `LIMIT`，并且 `LIMIT` 的值不超过 1000。
查询行数不超过约 500 万的小表时，调用方可以不带时间范围和 `LIMIT`。
保留未改：（1）查询被终止时，工具除了返回 `QUERY_TIMEOUT`，会不会带回已取到的部分行？（2）以 `WITH` 开头的查询、不带 `ANALYZE` 的 `EXPLAIN` 是否允许？一次能不能提交多条语句？
