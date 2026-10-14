把本地文件上传为工单附件，成功后返回 `attachment_id`。单个文件不能超过 10MB，格式限 png、jpg、pdf、log、txt。上传是异步的，返回 id 不代表已经能下载，要等 `status` 变成 `ready`。
