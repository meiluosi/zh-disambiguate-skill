主库挂了的话，先确认不是网络抖动，在跳板机上 `ping` 一下 `pg-primary`，连续丢包再往下走。然后在 `pg-replica-1` 上执行 `pg_ctl promote`，等它起来后把 `/etc/pgbouncer/pgbouncer.ini` 里的 `host` 改成新主库地址并 reload。老主库先别急着拉起来，等 DBA 确认数据没分叉再说。
