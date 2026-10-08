工具名：send_markdown_corp_conversation
描述：企业用户发送消息
参数 userIds（必填）：接收者的 userId 列表。调用方用英文逗号分隔各个 userId。列表最多包含 100 个 userId。
参数 content（必填）：Markdown 格式的消息。消息不超过 5000 个字符。
参数 title（必填）：消息标题。标题不超过 128 个字节。
保留未改：「企业用户发送消息」无法确定是「企业用户发出消息」还是「向企业用户发送消息」。send_markdown_corp_conversation 和 send_corp_conversation 的描述一字不差，模型无法据此在两个工具之间选择。请作者写明执行者，并写明两个工具的区别（例如消息格式）。content 按字符计长度，title 按字节计长度，原文没有写明 title 按哪种字符编码计算字节数。
