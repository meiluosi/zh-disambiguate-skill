def create_event(title, start, end, attendees=None, tz="Asia/Shanghai"):
    """
    创建日历事件。
    `start` 和 `end` 必须使用 ISO 8601 格式。
    `start` 或 `end` 没有带时区时，函数按 `tz` 指定的时区解释该时间。
    冲突指新事件和当前用户自己日历里 `status != cancelled` 的事件时间重叠。
    只要时间有重叠就算冲突，只重叠 1 分钟也算。
    函数不检查其他参会人的日历。
    新事件和已有事件冲突时，函数照常创建新事件。
    这时返回值里多一个 `conflicts` 字段。
    调用方决定是否修改新事件的时间。
    `attendees` 为空时，新事件只占用自己的日历。
    """
