工具名：send_corp_conversation
描述：企业用户发送消息
参数 userIds（必填）：接收者的 userId 列表。调用方用英文逗号分隔各个 userId。列表最多包含 100 个 userId。
参数 context（必填）：消息内容。消息内容不超过 2048 个字节。
保留未改：「企业用户发送消息」无法确定是「企业用户发出消息」还是「向企业用户发送消息」。send_corp_conversation 和 send_markdown_corp_conversation 的描述一字不差，模型无法据此在两个工具之间选择。请作者写明执行者，并写明两个工具的区别（例如消息格式）。「2048 个字节」没有写明按哪种字符编码计算字节数。
