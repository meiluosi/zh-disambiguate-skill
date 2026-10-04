在只读副本上执行 SQL 查询，返回结果行。

本工具只执行 `SELECT` 语句。工具对其他语句直接返回错误。其他语句包括：

- `INSERT`、`UPDATE`、`DELETE`、`DROP`
- `EXPLAIN ANALYZE`（`EXPLAIN ANALYZE` 会真实执行查询）

服务端的 `statement_timeout` 为 30 秒。查询执行超过 30 秒时，服务端终止查询，工具返回错误码 `QUERY_TIMEOUT`。

大表指行数超过约 500 万的表，目前主要是 `events` 和 `order_items`。查询大表时，SQL 必须同时满足以下 2 个条件：

1. 包含 `created_at` 的范围条件。
2. 包含 `LIMIT`，值不超过 1000。

大表查询不满足这 2 个条件时，查询基本上会超过 30 秒。查询小表时，SQL 可以不包含这 2 项。

收到 `QUERY_TIMEOUT` 后，如果调用方要重试，必须先缩小查询范围。调用方不得原样重发同一条 SQL。

保留未改：「目前主要是」——作者没有列出 `events` 和 `order_items` 以外的大表，也没有说明这些表是否都有 `created_at` 列。
