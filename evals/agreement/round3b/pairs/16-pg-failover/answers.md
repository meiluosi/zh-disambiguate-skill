（1）我当时的想法是 `ping -c 20` 里丢包率超过 50%，或者 `pg_isready` 连续 3 次失败（间隔 10 秒），才算连续丢包。偶尔一两个包丢了不算，这时应继续观察而不是切换。
（2）`/etc/pgbouncer/pgbouncer.ini` 在哪台机器上，我当时没想过这一点。reload 用 `pgbouncer` 的 `RELOAD;` 命令，不是重启进程，否则会断掉现有连接。
（3）我当时没想过这一点。
（4）我写这句的意思是：在 DBA 明确回复前，不要对老主库执行 `systemctl start postgresql`，也不要把它重新挂成从库。DBA 确认之后具体怎么处理，我当时没想过这一点。
