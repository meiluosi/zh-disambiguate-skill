（1）我当时的想法是：「大表」指行数超过约 500 万的表，目前主要是 `events` 和 `order_items`。
（2）`EXPLAIN ANALYZE` 不算允许的，因为它会真实执行。以 `WITH` 开头的查询，以及不带 `ANALYZE` 的普通 `EXPLAIN`，我当时没想过这一点。
