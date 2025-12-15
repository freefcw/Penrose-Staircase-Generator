"""
布局常量模块 - 定义所有布局相关的魔法数字

遵循 DRY 原则，将散落在代码各处的魔法数字集中管理
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, final


@final
class LayoutConstants:
    """
    布局常量

    集中管理所有布局相关的数值常量
    """

    # === 缩放 ===
    ZOOM_BASE: ClassVar[float] = 11.0
    ZOOM_DIVISOR: ClassVar[float] = 0.1

    # === 序列区域 ===
    SEQUENCE_COLS: ClassVar[int] = 6
    SEQUENCE_BOX_SIZE: ClassVar[float] = 20.0
    SEQUENCE_MARGIN: ClassVar[float] = 5.0
    SEQUENCE_ROW_HEIGHT_FACTOR: ClassVar[float] = 30.0
    SEQUENCE_DECIMAL_HEIGHT: ClassVar[float] = 15.0
    SEQUENCE_TITLE_OFFSET: ClassVar[float] = 15.0
    SEQUENCE_VERTICAL_OFFSET: ClassVar[float] = 30.0
    SEQUENCE_AREA_PADDING: ClassVar[float] = 5.0

    # === 标签偏移 ===
    LABEL_OFFSET_A_Y: ClassVar[float] = -25.0
    LABEL_OFFSET_B_Y: ClassVar[float] = -25.0
    LABEL_OFFSET_C_X: ClassVar[float] = 15.0
    LABEL_OFFSET_C_Y: ClassVar[float] = 35.0
    LABEL_OFFSET_D_Y: ClassVar[float] = 8.0

    # === 字体 ===
    FONT_SIZE_MIN: ClassVar[int] = 5
    FONT_SIZE_MAX: ClassVar[int] = 36
    LABEL_FONT_SIZE_MIN: ClassVar[int] = 16
    TITLE_FONT_SIZE_FACTOR: ClassVar[float] = 10.0
    SEQUENCE_FONT_SIZE_FACTOR: ClassVar[float] = 12.0
    DECIMAL_FONT_SIZE_FACTOR: ClassVar[float] = 10.0

    # === 线宽 ===
    LINE_WIDTH_DIVISOR: ClassVar[float] = 8.0

    # === 窗口偏移 ===
    WINDOW_OFFSET_X: ClassVar[float] = 10.0

    # === 十进制区域 ===
    DECIMAL_BOX_HEIGHT_FACTOR: ClassVar[float] = 12.0
    DECIMAL_Y_OFFSET: ClassVar[float] = 2.0


@dataclass(frozen=True)
class LabelOffset:
    """标签偏移配置"""
    x: float = 0.0
    y: float = 0.0


# 预定义的标签偏移
LABEL_OFFSETS = {
    "A": LabelOffset(0, LayoutConstants.LABEL_OFFSET_A_Y),
    "B": LabelOffset(0, LayoutConstants.LABEL_OFFSET_B_Y),
    "C": LabelOffset(LayoutConstants.LABEL_OFFSET_C_X, LayoutConstants.LABEL_OFFSET_C_Y),
    "D": LabelOffset(0, LayoutConstants.LABEL_OFFSET_D_Y),
}
