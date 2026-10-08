主库挂了时，按以下步骤操作：

1. 确认故障不是网络抖动。满足以下任一条件时，判定为连续丢包：
   - 在跳板机上执行 `ping -c 20 pg-primary`，丢包率超过 50%。
   - `pg_isready` 连续 3 次失败，每次间隔 10 秒。
2. 只有判定为连续丢包时，才继续第 3 步。偶尔丢一两个包不算连续丢包。这时继续观察，而不是切换。
3. 在 `pg-replica-1` 上执行 `pg_ctl promote`。
4. 等 `pg-replica-1` 起来。`pg_is_in_recovery()` 返回 `false` 时，`pg-replica-1` 就算起来了。通常在 10 秒内起来。
5. 把 `/etc/pgbouncer/pgbouncer.ini` 里的 `host` 改成 `pg-replica-1` 的地址。
6. 执行 pgbouncer 的 `RELOAD;` 命令，而不是重启 pgbouncer 进程。重启进程会断掉现有连接。
7. DBA 明确回复数据没有分叉之前，你不得对老主库做以下任何一项：
   - 拉起老主库。
   - 执行 `systemctl start postgresql`。
   - 把老主库重新挂成从库。

保留未改：（1）`pgbouncer.ini` 在哪台机器上？（2）由谁联系 DBA：执行者主动通知 DBA，还是等 DBA 自己确认？
