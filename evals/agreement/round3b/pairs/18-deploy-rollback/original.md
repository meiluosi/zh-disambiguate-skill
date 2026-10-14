发版后如果错误率明显上升，先回滚再排查。在 `deploy-cli` 里执行 `deploy rollback --service=order-api --to=previous`，回滚完成后看 5 分钟监控，恢复了再在群里同步。数据库迁移已经跑过的话不要自己回滚 schema，找后端负责人。
