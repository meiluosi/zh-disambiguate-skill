导出任务还在处理中（`status=running`），目前没有可下载的文件。
请至少等待 15 秒，再调用 `get_export(job_id)` 查询任务状态。普通导出一般在 1 到 3 分钟内完成。
同一个 `job_id` 还在 `running` 时，调用方不得调用 `create_export` 重复创建这个导出任务。
重复创建会产生重复文件，并占用导出配额。导出配额是每天 5 个。

保留未改：「重复创建」：只禁止用相同参数调用 `create_export`，还是在这个 `job_id` 完成前，用任何参数调用 `create_export` 都不允许？
