证书一般在到期前 30 天自动续期，但 `certbot` 有时会静默失败，所以每月 1 号手动看一下 `certbot certificates`。如果某张证书剩余天数小于 14，就在 `/opt/ops` 下执行 `./renew.sh <域名>`，然后用 `curl -vI https://<域名>` 确认新证书生效。泛域名证书续期需要改 DNS 记录，这个得找 SRE。
