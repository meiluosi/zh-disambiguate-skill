工具在只读副本上执行 SQL 查询。工具返回结果行。工具只允许 `SELECT` 语句。调用方提交其他语句时，工具直接报错。工具不允许 `EXPLAIN ANALYZE`，因为 `EXPLAIN ANALYZE` 会真实执行语句。查询运行超过 30 秒时，该查询会被终止。大表指行数超过约 500 万的表。目前的大表主要是 `events` 和 `order_items`。查询大表时，调用方必须在 SQL 中加上时间范围或 `LIMIT`。不加时间范围或 `LIMIT` 的大表查询基本跑不完。

保留未改：（1）以 `WITH` 开头的查询，以及不带 `ANALYZE` 的普通 `EXPLAIN`，算不算允许的 `SELECT` 语句？
