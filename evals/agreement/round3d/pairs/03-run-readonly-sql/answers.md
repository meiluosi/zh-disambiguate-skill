（1）我当时的想法是行数超过约 500 万的表算大表，目前主要是 `events` 和 `order_items`。这两张表查询时必须带 `created_at` 的范围条件，并且 `LIMIT` 不超过 1000，小表可以不带。
（2）我当时的想法是超时后返回错误码 `QUERY_TIMEOUT`，模型应缩小范围后重试，不要原样重发。是否会带回已取到的部分行，我当时没想过这一点。
（3）我当时的想法是别的语句包括 `INSERT`、`UPDATE`、`DELETE`、`DROP`，也包括 `EXPLAIN ANALYZE`，因为它会真实执行。以 `WITH` 开头的查询、不带 `ANALYZE` 的 `EXPLAIN`，以及能否一次提交多条语句，我当时没想过这几点。
