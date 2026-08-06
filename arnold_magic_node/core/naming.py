"""不依赖 Maya 的节点名称处理规则。"""

import re


def replacement_name(
    node_name,
    target,
    replacement,
    enabled=True,
    ignore_case=False,
):
    """返回替换后的节点名；禁用或未匹配时返回 ``None``。"""

    if not enabled:
        return None
    flags = re.IGNORECASE if ignore_case else 0
    pattern = re.compile(re.escape(target), flags)
    if not pattern.search(node_name):
        return None
    return pattern.sub(replacement, node_name)


__all__ = ["replacement_name"]
