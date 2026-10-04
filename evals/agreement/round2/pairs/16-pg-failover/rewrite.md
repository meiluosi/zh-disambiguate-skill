主库故障时，按以下步骤切换：

1. 在跳板机上检查 `pg-primary`，排除网络抖动。满足以下任一条件时，才继续第 2 步：
   - `ping -c 20 pg-primary` 的丢包率超过 50%。
   - `pg_isready` 连续 3 次失败，每次间隔 10 秒。
2. 如果两个条件都不满足（例如只丢了 1 到 2 个包），不得切换。继续观察 `pg-primary`。
3. 在 `pg-replica-1` 上执行 `pg_ctl promote`。
4. 等待 `pg-replica-1` 上的 `pg_is_in_recovery()` 返回 `false`。通常在 10 秒内返回。
5. 把 `/etc/pgbouncer/pgbouncer.ini` 里的 `host` 改成新主库的地址。
6. 执行 `pgbouncer` 的 `RELOAD;` 命令。
7. 不得重启 `pgbouncer` 进程。重启进程会断开现有连接。
8. DBA 明确回复老主库数据没有分叉之前，不得对老主库执行 `systemctl start postgresql`。
9. DBA 明确回复老主库数据没有分叉之前，不得把老主库重新挂成从库。
