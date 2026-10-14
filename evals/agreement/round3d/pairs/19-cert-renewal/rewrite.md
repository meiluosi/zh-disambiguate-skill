`certbot` 一般在证书到期前 30 天自动续期。但 `certbot` 有时会静默失败。所以按以下步骤手动检查：

1. 每月 1 号，执行 `certbot certificates`，查看每张证书的剩余天数。
2. 如果某张证书剩余天数小于 14，按证书类型处理：
   - 泛域名证书（形如 `*.example.com`）：你直接联系 SRE。你不得自己修改 DNS 记录。你不得执行 `./renew.sh`。泛域名证书续期需要 DNS-01 验证，需要修改 DNS 记录。
   - 其他证书：在 `/opt/ops` 下执行 `./renew.sh <域名>`。
3. 执行 `./renew.sh` 后，执行 `curl -vI https://<域名>`。满足以下全部条件时，算新证书已生效：
   1. 输出里的 `expire date` 比续期前晚。
   2. 输出里没有 `SSL certificate problem`。

保留未改：（1）`certbot certificates` 和 `./renew.sh` 在哪台机器上执行？（2）`./renew.sh` 执行失败或新证书没有生效时，做什么？
