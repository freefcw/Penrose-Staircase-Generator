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


@dataclass(frozen=True)
class LayoutInfo:
    """
    窗口布局信息（统一定义）
    
    包含渲染楼梯所需的所有布局参数
    """
    window_width: float
    window_height: float
    stair_height: float
    zoom: float
    offset_x: float
    offset_y: float


def calculate_layout(
    a: int,
    b: int,
    c: int,
    d: int,
    step_length: float,
    scale: float = 1.0,
) -> LayoutInfo:
    """
    计算窗口布局（统一实现）
    
    Args:
        a: A区台阶数
        b: B区台阶数
        c: C区台阶数
        d: D区台阶数
        step_length: 台阶长度
        scale: 缩放因子
        
    Returns:
        LayoutInfo 布局信息
    """
    # 导入几何常量（避免循环导入）
    from core.geometry import GeometryTransform
    
    H = GeometryTransform.UNIT_HEIGHT
    L = step_length
    total_steps = a + b + c + d - 4

    # 缩放因子
    zoom = LayoutConstants.ZOOM_BASE / (
        (a + b + c + d + L - 4) * LayoutConstants.ZOOM_DIVISOR
    ) * scale

    # 窗口尺寸
    window_width = (a * L + b * L) * zoom
    stair_height = (a * H * L + b * H * L) * zoom

    # 序列显示区域高度
    seq_rows = (total_steps // LayoutConstants.SEQUENCE_COLS) + 1
    seq_height = (
        seq_rows * (LayoutConstants.SEQUENCE_ROW_HEIGHT_FACTOR * scale)
        + LayoutConstants.SEQUENCE_AREA_PADDING * scale
    )

    window_height = stair_height + seq_height

    # 偏移量
    offset_x = LayoutConstants.WINDOW_OFFSET_X * scale
    offset_y = (a * L * H * 0.5) * zoom

    return LayoutInfo(
        window_width=window_width,
        window_height=window_height,
        stair_height=stair_height,
        zoom=zoom,
        offset_x=offset_x,
        offset_y=offset_y,
    )


def calculate_layout_from_config(config, scale: float = 1.0) -> LayoutInfo:
    """
    从 StaircaseConfig 计算布局（便捷方法）
    
    Args:
        config: StaircaseConfig 对象
        scale: 缩放因子
        
    Returns:
        LayoutInfo 布局信息
    """
    return calculate_layout(
        a=config.a,
        b=config.b,
        c=config.c,
        d=config.d,
        step_length=config.step_length,
        scale=scale,
    )
