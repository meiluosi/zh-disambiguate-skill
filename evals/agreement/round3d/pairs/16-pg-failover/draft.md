主库挂了时，按以下步骤处理：

1. 在跳板机上 `ping` `pg-primary`，确认故障不是网络抖动。
2. 如果连续丢包，继续第 3 步。
3. 在 `pg-replica-1` 上执行 `pg_ctl promote`。
4. 等待 `pg-replica-1` 起来。
5. 把 `/etc/pgbouncer/pgbouncer.ini` 里的 `host` 改成新主库地址。
6. reload pgbouncer。
7. DBA 确认数据没有分叉之前，不得拉起老主库。

保留未改：（1）`ping` 多少次、连续丢几个包算「连续丢包」？（2）没有连续丢包时（判定为网络抖动），下一步做什么？（3）按什么判断 `pg-replica-1`「起来」了？最多等多久，超时后做什么？（4）「新主库地址」填 `pg-replica-1` 的 IP 还是主机名？（5）修改 `pgbouncer.ini` 和 reload 在哪台机器上执行，reload 用什么命令？（6）谁负责联系 DBA，通过什么渠道？
