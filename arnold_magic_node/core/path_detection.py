"""Path Detection 的纯文件系统数据准备逻辑。"""

import copy
import os
import pathlib
import re
import time

from .matching import contains_any_substring


def _split_values(values):
    if isinstance(values, str):
        values = re.split(r"[,\uFF0C]", values)
    return [str(value).strip() for value in values or () if str(value).strip()]


def scan_directory(target_directory, exclude_keywords, include_formats=None):
    """返回目录中通过关键词和扩展名过滤的文件路径映射。"""

    filenames = os.listdir(str(target_directory))
    excluded = _split_values(exclude_keywords)
    included = None
    if include_formats:
        included = {
            "." + value.lstrip(".").lower()
            for value in _split_values(include_formats)
        }

    root = pathlib.Path(target_directory)
    result = {}
    for filename in filenames:
        if contains_any_substring(filename, excluded):
            continue
        path = root / filename
        if included is not None and path.suffix.lower() not in included:
            continue
        result[filename] = str(path)
    return result


def collect_file_info(texture_paths, image_dimensions):
    """读取贴图文件的创建时间、扩展名和尺寸。"""

    result = {}
    for filename, file_path in texture_paths.items():
        created_at = os.path.getctime(file_path)
        result[filename] = {
            "creation_time": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(created_at)
            ),
            "file_type": os.path.splitext(file_path)[1],
            "resolution": image_dimensions(file_path),
        }
    return result


def process_file_names(file_info, excluded_words, texture_filters):
    """为文件信息添加用于相似度比较的标准化名称。"""

    result = copy.deepcopy(file_info)
    technical_terms = set()
    for channel, terms in texture_filters.items():
        technical_terms.add(str(channel).upper())
        technical_terms.update(str(term).upper() for term in terms)
    technical_terms.update(str(word).upper() for word in excluded_words)

    for filename, info in result.items():
        normalized = re.sub(r"[_\-.]", " ", filename.upper())
        words = normalized.split()
        words = [word for word in words if word not in technical_terms]
        extension = str(info["file_type"]).upper().replace(".", "")
        info["processed_name"] = " ".join(
            word for word in words if word != extension
        )
    return result


__all__ = ["collect_file_info", "process_file_names", "scan_directory"]
