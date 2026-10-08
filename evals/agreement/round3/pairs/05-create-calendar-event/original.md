def create_event(title, start, end, attendees=None, tz="Asia/Shanghai"):
    """
    创建日历事件。`start` / `end` 用 ISO 8601 格式，没带时区就按 `tz` 算。
    如果和已有事件冲突会照常创建，只是返回里多一个 `conflicts` 字段，
    要不要改时间由调用方决定。`attendees` 为空就是只占自己的日历。
    """
