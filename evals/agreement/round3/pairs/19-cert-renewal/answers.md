（1）我当时的想法是整个泛域名证书（形如 `*.example.com`）的续期都交给 SRE，因为续期需要 DNS-01 验证，运维同学不要自己改 DNS。所以不要尝试执行 `./renew.sh`，直接联系 SRE。
（2）新证书没有生效时下一步做什么，我当时没想过这一点。我只定义了生效的标准：`expire date` 比之前晚，并且没有 `SSL certificate problem`。
