主库挂了时，按以下步骤处理：

1. 在跳板机上 `ping` `pg-primary`，确认故障不是网络抖动。
2. 如果 `ping` 连续丢包，继续第 3 步。
3. 在 `pg-replica-1` 上执行 `pg_ctl promote`。
4. 等 `pg-replica-1` 起来。
5. 把 `/etc/pgbouncer/pgbouncer.ini` 里的 `host` 改成新主库 `pg-replica-1` 的地址。
6. reload pgbouncer。
7. DBA 确认数据没有分叉之前，不得拉起老主库。

保留未改：「连续丢包」「等它起来」和 reload 的方式保留原写法，因为原文没有给出判定标准和具体命令。（1）`ping` 多少次、连续丢几个包，算「连续丢包」？（2）`ping` 没有连续丢包时，下一步做什么？（3）用什么方法判断 `pg-replica-1` 已经起来、可以作为新主库？（4）`pgbouncer.ini` 在哪台机器上？reload 用哪条命令？（5）执行人要不要主动通知 DBA 检查数据是否分叉？
