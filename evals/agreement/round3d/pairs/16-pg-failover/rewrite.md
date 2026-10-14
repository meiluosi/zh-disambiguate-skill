主库挂了时，按以下步骤处理：

1. 在跳板机上检查 `pg-primary`，确认故障不是网络抖动。满足以下任一条件时，算连续丢包：
   1. `ping -c 20 pg-primary` 的丢包率超过 50%。
   2. `pg_isready` 连续 3 次失败，每次间隔 10 秒。
   偶尔丢一两个包，不算连续丢包。
2. 如果没有连续丢包，继续观察。不切换主库。
3. 如果连续丢包，继续第 4 步。
4. 在 `pg-replica-1` 上执行 `pg_ctl promote`。
5. 等待 `pg-replica-1` 起来。`pg_is_in_recovery()` 返回 `false` 时，算 `pg-replica-1` 已经起来。`pg-replica-1` 通常在 10 秒内起来。
6. 把 `/etc/pgbouncer/pgbouncer.ini` 里的 `host` 改成新主库地址。
7. 在 pgbouncer 中执行 `RELOAD;` 命令，让配置生效。用 `RELOAD;`，不用重启 pgbouncer 进程的方式。重启 pgbouncer 进程会断掉现有连接。
8. DBA 明确回复数据没有分叉之前，你对老主库不得做以下任何一项：
   1. 执行 `systemctl start postgresql`。
   2. 把老主库重新挂成从库。

保留未改：（1）最多等待 `pg-replica-1` 起来多久？超时后做什么？（2）「新主库地址」填 `pg-replica-1` 的 IP 还是主机名？（3）修改 `pgbouncer.ini` 和执行 `RELOAD;` 在哪台机器上？（4）谁负责联系 DBA，通过什么渠道？
