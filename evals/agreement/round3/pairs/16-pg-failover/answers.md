（1）连续丢包指 `ping -c 20` 里丢包率超过 50%，或者 `pg_isready` 连续 3 次失败，间隔 10 秒。偶尔一两个包丢了不算，应该继续观察而不是切换。
（2）`pg_is_in_recovery()` 返回 `false` 就算起来了，通常 10 秒内。
（3）`pgbouncer.ini` 在哪台机器上，我当时没想过这一点。reload 用 `pgbouncer` 的 `RELOAD;` 命令，不是重启进程，否则会断掉现有连接。
（4）由谁联系 DBA，我当时没想过这一点。我只想到在 DBA 明确回复前，不要对老主库执行 `systemctl start postgresql`，也不要把它重新挂成从库。
