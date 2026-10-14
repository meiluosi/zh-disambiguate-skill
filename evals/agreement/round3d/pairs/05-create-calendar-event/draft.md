def create_event(title, start, end, attendees=None, tz="Asia/Shanghai"):
    """
    创建日历事件。
    `start` 和 `end` 使用 ISO 8601 格式。
    `start` 或 `end` 没有带时区时，函数按 `tz` 解释这个时间。
    新事件和已有事件冲突时，函数照常创建新事件，并在返回值中多加一个 `conflicts` 字段。
    调用方决定是否修改新事件的时间。
    `attendees` 为空时，新事件只占用自己的日历。
    """
保留未改：（1）「冲突」怎样判断：只看时间是否重叠吗？首尾相接（一个事件的 `end` 等于另一个事件的 `start`）算不算冲突？函数只查自己的日历，还是也查 `attendees` 的日历？（2）「只占自己的日历」中的「自己」指哪个账号：调用方授权的账号，还是别的账号？（3）`attendees` 传空列表 `[]` 和传 `None` 的效果是否相同？
