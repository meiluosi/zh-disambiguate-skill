def create_event(title, start, end, attendees=None, tz="Asia/Shanghai"):
    """
    创建日历事件。
    `start` 和 `end` 必须使用 ISO 8601 格式。
    `start` 或 `end` 没有带时区时，函数按 `tz` 指定的时区解释该时间。
    新事件和已有事件冲突时，函数照常创建新事件。
    这时返回值里多一个 `conflicts` 字段。
    调用方决定是否修改新事件的时间。
    `attendees` 为空时，新事件只占用自己的日历。
    """

保留未改：（1）「和已有事件冲突」是指和谁的已有事件时间重叠：只算自己日历上的事件，还是也算 `attendees` 日历上的事件？
