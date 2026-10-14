def create_event(title, start, end, attendees=None, tz="Asia/Shanghai"):
    """
    创建日历事件。
    `start` 和 `end` 使用 ISO 8601 格式。
    `start` 或 `end` 没有带时区时，函数按 `tz` 解释这个时间。
    新事件的时间段和当前用户日历中任一 `status != cancelled` 的事件重叠时，算作冲突。
    任何重叠都算冲突，哪怕只重叠 1 分钟。
    函数不检查其他参会人的日历。
    新事件和已有事件冲突时，函数照常创建新事件，并在返回值中多加一个 `conflicts` 字段。
    调用方决定是否修改新事件的时间。
    `attendees` 是邮箱字符串列表。调用方传入 `attendees` 时，函数向列表中的邮箱发送邀请邮件。
    `attendees` 为空时，新事件只占用当前用户的日历。
    """
保留未改：（1）首尾相接（一个事件的 `end` 等于另一个事件的 `start`）算不算冲突？（2）「当前用户」具体指哪个授权账号？（3）`attendees` 传空列表 `[]` 和传 `None` 的效果是否相同？
