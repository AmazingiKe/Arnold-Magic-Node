"""Path Detection 使用的纯相似度算法。"""

import difflib
from datetime import datetime


def processed_name_similarity(left, right):
    if not left or not right:
        return 0.0
    return difflib.SequenceMatcher(None, left.lower(), right.lower()).ratio()


def resolution_similarity(left, right):
    values = (left, right)
    if any(not value or len(value) != 2 for value in values):
        return 0.0
    if any(dimension <= 0 for value in values for dimension in value):
        return 0.0
    if left == right:
        return 1.0
    left_area = left[0] * left[1]
    right_area = right[0] * right[1]
    return 1 - abs(left_area - right_area) / max(left_area, right_area)


def file_type_similarity(left, right):
    return 1.0 if left.lower() == right.lower() else 0.0


def creation_time_similarity(left, right, day_tolerance):
    maximum_difference = 3600 * 24 * day_tolerance
    date_format = "%Y-%m-%d %H:%M:%S"
    left_time = datetime.strptime(left, date_format)
    right_time = datetime.strptime(right, date_format)
    difference = abs((left_time - right_time).total_seconds())
    return 1 - min(difference / maximum_difference, 1.0)


def calculate_similarity(target_info, candidates, weights, max_diff=30):
    """按旧版权重规则计算每个候选文件的综合相似度。"""

    target = next(iter(target_info.values()))
    results = {}
    for filename, candidate in candidates.items():
        results[filename] = (
            weights["name_weight"]
            * processed_name_similarity(
                target["processed_name"], candidate["processed_name"]
            )
            + weights["resolution_weight"]
            * resolution_similarity(target["resolution"], candidate["resolution"])
            + weights["format_weight"]
            * file_type_similarity(target["file_type"], candidate["file_type"])
            + weights["creation_time_weight"]
            * creation_time_similarity(
                target["creation_time"], candidate["creation_time"], max_diff
            )
        )
    return results


def select_matches(
    similarities,
    auto_max_value,
    similarity_max,
    similarity_range,
):
    """选择阈值范围内的候选项，并按相似度降序返回。"""

    threshold = max(similarities.values()) if auto_max_value else similarity_max
    minimum = max(threshold - similarity_range, 0.0)
    maximum = min(threshold + similarity_range, 1.0)
    matches = [
        (target, similarity)
        for target, similarity in similarities.items()
        if minimum <= similarity <= maximum
    ]
    matches.sort(key=lambda item: item[1], reverse=True)
    return matches


__all__ = [
    "calculate_similarity",
    "creation_time_similarity",
    "file_type_similarity",
    "processed_name_similarity",
    "resolution_similarity",
    "select_matches",
]
