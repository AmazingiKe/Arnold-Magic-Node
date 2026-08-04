"""Arnold Magic Node 贴图名称匹配所需的轻量算法。"""


def contains_any_substring(text, keywords):
    """判断文本是否包含任一非空关键字，匹配时忽略大小写。"""
    normalized_text = text.lower()

    for keyword in keywords:
        normalized_keyword = keyword.strip().lower()
        if normalized_keyword and normalized_keyword in normalized_text:
            return True

    return False


def is_edit_distance_at_most_one(left, right):
    """判断两个字符串是否只需至多一次插入、删除或替换即可相同。"""
    if left == right:
        return True

    if abs(len(left) - len(right)) > 1:
        return False

    if len(left) == len(right):
        mismatch_count = 0
        for left_char, right_char in zip(left, right):
            if left_char != right_char:
                mismatch_count += 1
                if mismatch_count > 1:
                    return False
        return True

    if len(left) > len(right):
        left, right = right, left

    left_index = 0
    right_index = 0
    skipped_character = False

    while left_index < len(left):
        if left[left_index] == right[right_index]:
            left_index += 1
            right_index += 1
            continue

        if skipped_character:
            return False

        skipped_character = True
        right_index += 1

    return True
