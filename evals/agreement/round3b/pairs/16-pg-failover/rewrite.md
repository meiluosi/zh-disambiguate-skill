主库故障时，按以下步骤操作：

1. 在跳板机上执行 `ping -c 20 pg-primary`，确认故障不是网络抖动。
2. 满足以下任一条件时，算连续丢包，继续第 3 步：
   - `ping -c 20` 的丢包率超过 50%。
   - `pg_isready` 连续 3 次失败，每次间隔 10 秒。
   没有连续丢包时（例如偶尔丢一两个包），继续观察，不切换主库。
3. 在 `pg-replica-1` 上执行 `pg_ctl promote`。
4. 等待 `pg-replica-1` 启动完成。
5. 把 `/etc/pgbouncer/pgbouncer.ini` 里的 `host` 改成 `pg-replica-1` 的地址。
6. 在 pgbouncer 里执行 `RELOAD;` 命令。不得重启 pgbouncer 进程，重启进程会断开现有连接。

DBA 明确回复数据没有分叉之前：

- 不得对老主库执行 `systemctl start postgresql`。
- 不得把老主库重新挂成从库。

保留未改：（1）`/etc/pgbouncer/pgbouncer.ini` 在哪台机器上？（2）谁负责通知 DBA 检查数据是否分叉？（3）DBA 确认数据没有分叉后，老主库怎么处理：直接启动，还是等进一步指示？
