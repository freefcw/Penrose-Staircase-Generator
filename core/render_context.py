"""
渲染上下文 - 封装渲染所需的所有状态

用于在渲染过程中传递布局、变换和画布信息
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.layout import LayoutInfo
    from core.geometry import GeometryTransform
    from rendering.canvas import Canvas


@dataclass
class RenderContext:
    """渲染上下文，封装渲染所需的所有状态"""
    
    layout: LayoutInfo
    scale_factor: float
    transform: GeometryTransform
    canvas: Canvas
    canvas_width: float
    canvas_height: float
    center_offset_x: float
    center_offset_y: float
