主库挂了时，按以下步骤处理：

1. 在跳板机上 `ping` `pg-primary`，确认故障不是网络抖动。
2. 满足以下任一条件时，算连续丢包，继续第 4 步：
   - `ping -c 20` 的丢包率超过 50%。
   - `pg_isready` 连续 3 次失败，每次间隔 10 秒。
3. 偶尔丢一两个包，不算连续丢包。这时继续观察，不切换主库。
4. 在 `pg-replica-1` 上执行 `pg_ctl promote`。
5. 等 `pg-replica-1` 起来。`pg_is_in_recovery()` 返回 `false` 时，`pg-replica-1` 已经起来。通常 10 秒内起来。
6. 把 `/etc/pgbouncer/pgbouncer.ini` 里的 `host` 改成新主库 `pg-replica-1` 的地址。
7. 在 pgbouncer 里执行 `RELOAD;` 命令。不得重启 pgbouncer 进程。重启进程会断掉现有连接。
8. DBA 明确回复数据没有分叉之前，不得拉起老主库。具体包括：
   - 不得对老主库执行 `systemctl start postgresql`。
   - 不得把老主库重新挂成从库。

保留未改：（1）`pgbouncer.ini` 在哪台机器上？（2）执行人要不要主动通知 DBA 检查数据是否分叉？
