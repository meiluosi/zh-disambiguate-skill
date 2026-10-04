def create_event(title, start, end, attendees=None, tz="Asia/Shanghai"):
    """
    创建日历事件。

    `start` 和 `end` 使用 ISO 8601 格式。
    如果 `start` 或 `end` 不带时区，函数按 `tz` 指定的时区解析这个时间。

    冲突的定义：新事件的时间段和当前用户日历中任一 `status != cancelled` 的事件重叠。
    重叠 1 分钟也算冲突。函数不检查其他参会人的日历。

    发生冲突时，函数照常创建事件，并在返回值中加入 `conflicts` 字段。
    如果 `conflicts` 非空，调用方必须执行以下步骤：
    1. 告诉用户新事件和已有事件冲突。
    2. 询问用户是否修改时间。
    3. 如果用户要求保持原样，调用方不再处理冲突。
    调用方不得把 `conflicts` 非空的结果当作普通的创建成功直接结束。

    `attendees` 是邮箱字符串列表。
    - 如果 `attendees` 非空，函数向列表中的每个邮箱发送邀请邮件。
    - 如果 `attendees` 为空，事件只占用当前用户自己的日历。
    """
