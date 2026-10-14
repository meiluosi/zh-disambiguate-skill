证书一般在到期前 30 天自动续期。但 `certbot` 有时会静默失败。所以每月 1 号，手动执行 `certbot certificates`，查看每张证书的剩余天数。

如果某张证书剩余天数小于 14，按证书类型处理。

泛域名证书：续期需要 DNS-01 验证。运维同学不得自己改 DNS 记录，也不得尝试执行 `./renew.sh`。运维同学直接联系 SRE。

其他证书：按以下步骤处理。

1. 在 `/opt/ops` 目录下执行 `./renew.sh <域名>`。
2. 用 `curl -vI https://<域名>` 确认新证书已经生效。`curl -vI` 的输出满足以下全部条件时，新证书已经生效：
   - `expire date` 比续期之前晚。
   - 没有 `SSL certificate problem`。

保留未改：（1）`certbot certificates` 和 `./renew.sh` 在哪台机器上执行？（2）`curl` 显示新证书没有生效时，下一步做什么？
