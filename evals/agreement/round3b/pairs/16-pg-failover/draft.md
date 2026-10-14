主库故障时，按以下步骤操作：

1. 在跳板机上 `ping` `pg-primary`，确认故障不是网络抖动。
2. 如果 `ping` 连续丢包，继续第 3 步。
3. 在 `pg-replica-1` 上执行 `pg_ctl promote`。
4. 等待 `pg-replica-1` 启动完成。
5. 把 `/etc/pgbouncer/pgbouncer.ini` 里的 `host` 改成 `pg-replica-1` 的地址。
6. reload pgbouncer。

DBA 确认数据没有分叉之前，不得启动老主库。

保留未改：（1）`ping` 时发多少个包、丢几个包算「连续丢包」？没有连续丢包时，下一步做什么？（2）`/etc/pgbouncer/pgbouncer.ini` 在哪台机器上？reload 用什么命令？（3）谁负责通知 DBA 检查数据是否分叉？（4）原文写「等 DBA 确认数据没分叉再说」：DBA 确认后，老主库直接启动，还是等进一步指示？
