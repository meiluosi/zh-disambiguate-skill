`certbot` 一般在证书到期前 30 天自动续期。但 `certbot` 有时会静默失败。所以按以下步骤手动检查：

1. 每月 1 号，执行 `certbot certificates`，查看每张证书的剩余天数。
2. 如果某张证书剩余天数小于 14，在 `/opt/ops` 下执行 `./renew.sh <域名>`。
3. 执行 `curl -vI https://<域名>`，确认新证书已生效。

泛域名证书续期需要修改 DNS 记录，这个得找 SRE。

保留未改：（1）`certbot certificates` 和 `./renew.sh` 在哪台机器上执行？（2）泛域名证书剩余天数小于 14 时，是由 SRE 完成整个续期、你不执行 `./renew.sh`，还是你执行 `./renew.sh`、只由 SRE 修改 DNS 记录？（3）`curl -vI` 的输出中看哪个字段，满足什么条件算「新证书已生效」？（4）`./renew.sh` 执行失败或新证书没有生效时，做什么？
