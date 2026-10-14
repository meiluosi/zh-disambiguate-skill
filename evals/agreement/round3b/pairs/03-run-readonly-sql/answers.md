（1）我当时的想法是行数超过约 500 万的表算大表，目前主要是 `events` 和 `order_items`。这两张表查询时必须带 `created_at` 的范围条件，并且 `LIMIT` 不超过 1000，小表可以不带。
（2）`WITH` 开头的查询和普通的 `EXPLAIN SELECT`，我当时没想过这一点。我明确想到的是 `EXPLAIN ANALYZE` 不允许，因为它会真实执行。
（3）超时后返回错误码 `QUERY_TIMEOUT`，不返回部分结果。30 秒是服务端 `statement_timeout`，模型应缩小范围后重试，不要原样重发。
