"""
绘图上下文模块 - 封装绘图相关的参数对象

遵循参数对象模式，减少长参数列表
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SequenceDrawContext:
    """
    序列绘制上下文

    封装绘制颜色序列所需的所有参数
    """
    start_y: float
    scale: float
    row_height: float
    start_x: float
    box_size: float
    margin: float
    num_rows: int


@dataclass(frozen=True)
class RenderContext:
    """
    渲染上下文

    封装渲染过程中共享的参数
    """
    scale: float
    zoom: float
    window_width: float
    window_height: float
    stair_height: float
