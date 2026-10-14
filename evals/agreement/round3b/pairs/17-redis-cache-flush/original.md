缓存数据脏了需要清的时候，不要直接 `FLUSHALL`，会把 session 一起清掉，所有人都得重新登录。用 `redis-cli --scan --pattern 'product:*'` 找出 key 再分批 `UNLINK`，每批 500 个左右。清完观察一下数据库 CPU，如果超过 70% 就先停手，等降下来再继续。
