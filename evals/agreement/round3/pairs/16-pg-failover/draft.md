主库挂了时，按以下步骤操作：

1. 确认故障不是网络抖动：在跳板机上 `ping` `pg-primary`。
2. 只有连续丢包时，才继续第 3 步。
3. 在 `pg-replica-1` 上执行 `pg_ctl promote`。
4. 等 `pg-replica-1` 起来。
5. 把 `/etc/pgbouncer/pgbouncer.ini` 里的 `host` 改成 `pg-replica-1` 的地址。
6. reload pgbouncer。
7. DBA 确认数据没有分叉之前，不得拉起老主库。

保留未改：（1）「连续丢包」指连续丢几个包，或者持续多久？没有连续丢包时，下一步做什么？（2）怎样判断 `pg-replica-1` 已经「起来」？（3）`pgbouncer.ini` 在哪台机器上？用什么命令 reload？（4）由谁联系 DBA：执行者主动通知 DBA，还是等 DBA 自己确认？
