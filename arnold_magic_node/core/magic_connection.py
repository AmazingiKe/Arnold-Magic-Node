"""Magic Connection 的纯 Python 核心逻辑。

本模块只负责贴图名称解析、通道匹配、处理节点配置解析和执行计划构建。
它不导入 Maya，也不直接修改场景，方便在普通 Python 环境中测试。
"""

import os
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, Tuple

from . import matching as _matching


DEFAULT_CHANNEL_PRIORITY = (
    "base",
    "baseColor",
    "diffuseRoughness",
    "metalness",
    "specular",
    "specularColor",
    "specularRoughness",
    "specularAnisotropy",
    "specularRotation",
    "subsurface",
    "subsurfaceColor",
    "subsurfaceRadius",
    "emission",
    "emissionColor",
    "opacity",
    "normalCamera",
    "ao",
    "bump",
    "displacement",
)

COLOR_CHANNELS = frozenset(
    (
        "baseColor",
        "specularColor",
        "subsurfaceColor",
        "subsurfaceRadius",
        "emissionColor",
        "opacity",
        "normalCamera",
    )
)

GRAY_CHANNELS = frozenset(
    (
        "base",
        "diffuseRoughness",
        "metalness",
        "specular",
        "specularRoughness",
        "specularAnisotropy",
        "specularRotation",
        "subsurface",
        "emission",
        "ao",
        "bump",
        "displacement",
    )
)


class MagicConnectionConfigError(ValueError):
    """Magic Connection 配置无法生成有效计划时抛出的异常。"""


@dataclass(frozen=True)
class ProcessingPlan:
    """单张贴图的处理节点链配置。"""

    node_types: Tuple[str, ...]
    input_port: str
    output_port: str


@dataclass(frozen=True)
class TexturePlan:
    """单张贴图经过通道识别后的执行数据。"""

    node_name: str
    channel: str
    source_output_port: str
    processing: Optional[ProcessingPlan]
    connect_enabled: bool


@dataclass(frozen=True)
class MagicConnectionPlan:
    """一次 Magic Connection 的完整、无 Maya 状态的执行计划。"""

    textures: Tuple[TexturePlan, ...]
    material_name: Optional[str]
    shading_engine_name: Optional[str]


def normalize_texture_name(file_name):
    """按旧版规则标准化贴图文件名，去掉路径、后缀和标点。"""

    name = os.path.splitext(os.path.basename(file_name))[0]
    name = re.sub(r"[^\w\s]", " ", name)
    name = re.sub(r"_+", " ", name)
    name = name.upper()
    return re.sub(r"\s+", " ", name).strip()


def build_keyword_mapping(filter_data):
    """建立关键词到通道的映射，并保留配置字典的通道顺序。"""

    keyword_to_channels = defaultdict(list)
    keywords = []
    seen = set()

    for channel, channel_keywords in filter_data.items():
        for keyword in channel_keywords or ():
            normalized = str(keyword).strip().lower()
            if not normalized or normalized in seen:
                if normalized:
                    keyword_to_channels[normalized].append(channel)
                continue
            keyword_to_channels[normalized].append(channel)
            keywords.append(normalized)
            seen.add(normalized)

    return keyword_to_channels, tuple(keywords)


def match_channel(texture_name, filter_data, keyword_mapping=None):
    """返回贴图文件名最匹配的材质通道，找不到时返回 ``None``。"""

    if keyword_mapping is None:
        keyword_to_channels, keywords = build_keyword_mapping(filter_data)
    else:
        keyword_to_channels, keywords = keyword_mapping

    words = re.split(r"[\s_-]+", normalize_texture_name(texture_name).lower())
    channel_scores = defaultdict(int)

    for word in words:
        if word in keyword_to_channels:
            for channel in keyword_to_channels[word]:
                channel_scores[channel] += 1

    if not channel_scores:
        for word in words:
            for keyword in keywords:
                if _matching.is_edit_distance_at_most_one(word, keyword):
                    for channel in keyword_to_channels[keyword]:
                        channel_scores[channel] += 1

    if not channel_scores:
        return None

    return max(channel_scores.items(), key=lambda item: item[1])[0]


def match_texture_channels(texture_files, filter_data):
    """将 ``{节点名: 文件路径}`` 转为 ``{节点名: 通道或 None}``。"""

    keyword_mapping = build_keyword_mapping(filter_data)
    return {
        node_name: match_channel(file_name, filter_data, keyword_mapping)
        for node_name, file_name in texture_files.items()
    }


def reorder_matches(matches, priority=None):
    """按材质通道优先级排序，并过滤无法识别的通道。"""

    priority = tuple(priority or DEFAULT_CHANNEL_PRIORITY)
    ordered = []
    for channel in priority:
        ordered.extend(
            (node_name, matched_channel)
            for node_name, matched_channel in matches.items()
            if matched_channel == channel
        )
    return ordered


def texture_output_port(channel):
    """返回 file 节点连接到处理链时应使用的输出端口。"""

    if channel in COLOR_CHANNELS:
        return "outColor"
    if channel in GRAY_CHANNELS:
        return "outAlpha"
    raise MagicConnectionConfigError(
        "通道 {!r} 未定义为颜色或灰度通道".format(channel)
    )


def _default_processing_output_port(channel):
    if channel in COLOR_CHANNELS:
        return "outColor"
    return "outColorR"


def _processing_plan(channel, processing_data):
    data = processing_data.get(channel)
    if not data:
        raise MagicConnectionConfigError(
            "通道 {!r} 已开启处理节点，但缺少处理节点配置".format(channel)
        )

    node_types = tuple(data.get("NodeList") or ())
    if not node_types:
        raise MagicConnectionConfigError(
            "通道 {!r} 的 NodeList 不能为空".format(channel)
        )

    input_port = data.get("InputPort") or "input"
    output_port = data.get("OutputPort") or _default_processing_output_port(channel)
    return ProcessingPlan(node_types, input_port, output_port)


def build_magic_connection_plan(
    texture_files,
    filter_data,
    processing_data,
    magic_connection_options,
    processing_options,
    material_name=None,
    shading_engine_name=None,
):
    """根据输入贴图和配置构建一次 Magic Connection 执行计划。

    ``magic_connection_options`` 与 ``processing_options`` 有意保持独立：
    前者决定是否连接材质，后者决定是否创建中间处理节点。
    """

    matches = match_texture_channels(texture_files, filter_data)
    ordered_matches = reorder_matches(matches)
    textures = []

    for node_name, channel in ordered_matches:
        processing = None
        if processing_options.get(channel, False):
            processing = _processing_plan(channel, processing_data)

        textures.append(
            TexturePlan(
                node_name=node_name,
                channel=channel,
                source_output_port=texture_output_port(channel),
                processing=processing,
                connect_enabled=bool(magic_connection_options.get(channel, False)),
            )
        )

    return MagicConnectionPlan(
        textures=tuple(textures),
        material_name=material_name,
        shading_engine_name=shading_engine_name,
    )


def clean_material_name(filename, filter_data):
    """按照贴图过滤词清理材质名称。"""

    professional_terms = [
        str(term).upper()
        for values in filter_data.values()
        for term in values or ()
    ]
    filename = re.sub(r"^\d+_", "", filename)
    for term in professional_terms:
        filename = re.sub(re.escape(term), "", filename, flags=re.IGNORECASE)
    filename = os.path.splitext(filename)[0]
    return re.sub(r"_+", "_", filename).strip("_")


def contains_udim_number(text):
    """识别数字 UDIM 和 Maya 常见的 ``<UDIM>`` 占位符。"""

    return bool(re.search(r"<UDIM>|\b1[0-9]{3}\b", text, flags=re.IGNORECASE))


__all__ = [
    "COLOR_CHANNELS",
    "DEFAULT_CHANNEL_PRIORITY",
    "GRAY_CHANNELS",
    "MagicConnectionConfigError",
    "MagicConnectionPlan",
    "ProcessingPlan",
    "TexturePlan",
    "build_keyword_mapping",
    "build_magic_connection_plan",
    "clean_material_name",
    "contains_udim_number",
    "match_channel",
    "match_texture_channels",
    "normalize_texture_name",
    "reorder_matches",
    "texture_output_port",
]
