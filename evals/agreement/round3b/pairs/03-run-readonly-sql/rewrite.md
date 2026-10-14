工具在只读副本上执行 SQL 查询，并返回结果行。
工具只接受 `SELECT` 语句。其他语句会直接报错。
工具不接受 `EXPLAIN ANALYZE`，因为 `EXPLAIN ANALYZE` 会真的运行这个查询。
查询运行超过 30 秒时，服务端按 `statement_timeout` 终止这个查询。
服务端终止查询时，工具返回错误码 `QUERY_TIMEOUT`，不返回部分结果。
收到 `QUERY_TIMEOUT` 后，调用方必须缩小查询范围，再重试。调用方不得原样重发同一个查询。
行数超过约 500 万的表是大表。目前的大表主要是 `events` 和 `order_items`。
查询大表时，调用方必须带上时间范围或者 `LIMIT`。否则查询基本无法在 30 秒内完成。
查询 `events` 或 `order_items` 时，调用方必须满足以下全部条件：
1. 带上 `created_at` 的范围条件。
2. 带上 `LIMIT`，并且 `LIMIT` 不超过 1000。
查询小表时，调用方不必带时间范围，也不必带 `LIMIT`。

保留未改：「只接受 `SELECT` 语句」：工具是否接受以 `WITH` 开头的查询？工具是否接受普通的 `EXPLAIN SELECT`？
