def create_event(title, start, end, attendees=None, tz="Asia/Shanghai"):
    """
    函数创建一个日历事件。
    `start` 和 `end` 必须使用 ISO 8601 格式。
    `start` 或 `end` 没有带时区时，函数按 `tz` 的时区解析该值。
    函数只检查当前用户日历里的事件是否和新事件冲突。
    函数不检查其他参会人的日历。
    新事件和已有事件冲突时，函数照常创建新事件。
    这时函数在返回值里多加一个 `conflicts` 字段。
    调用方决定是否修改新事件的时间。
    `attendees` 为空时，新事件只占用当前用户的日历。
    """
保留未改：「为空」原文没有写明所指，正文保留。请作者回答：`attendees` 传空列表 `[]` 和不传（`None`）的效果是否相同？
