（1）我当时的想法是：泛域名证书续期需要 DNS-01 验证，运维同学不要自己改 DNS，直接联系 SRE，也不要尝试执行 `renew.sh`。
（2）我当时没想过这一点。
（3）我当时没想过这一点。我想到的只是：「生效」指 `curl -vI` 输出里 `expire date` 比之前晚，并且没有 `SSL certificate problem`。
