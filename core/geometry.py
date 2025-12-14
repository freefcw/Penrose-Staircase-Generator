"""
几何变换模块 - 负责坐标转换和2D变换
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import ClassVar, final


@dataclass(frozen=True)
class Point:
    """不可变的2D点"""

    x: float
    y: float

    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point) -> Point:
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Point:
        return Point(self.x * scalar, self.y * scalar)

    def to_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)


@final
class GeometryTransform:
    """
    几何变换器

    职责：
    - 2D旋转变换
    - 模型坐标到屏幕坐标的转换
    """

    UNIT_WIDTH: ClassVar[float] = 1.0
    UNIT_HEIGHT: ClassVar[float] = 0.866025404  # sqrt(3)/2，等边三角形高度比

    scale: float
    offset_x: float
    offset_y: float

    def __init__(self, scale: float, offset_x: float, offset_y: float):
        """
        初始化几何变换器

        Args:
            scale: 缩放因子
            offset_x: X轴偏移量
            offset_y: Y轴偏移量
        """
        self.scale = scale
        self.offset_x = offset_x
        self.offset_y = offset_y

    def rotate_2d(self, x: float, y: float, degrees: float) -> Point:
        """
        2D旋转变换

        Args:
            x: X坐标
            y: Y坐标
            degrees: 旋转角度（度）

        Returns:
            旋转后的点
        """
        radians = math.radians(degrees)
        cos_r = math.cos(radians)
        sin_r = math.sin(radians)
        return Point(x * cos_r - y * sin_r, x * sin_r + y * cos_r)

    def to_screen(self, x: float, y: float) -> Point:
        """
        将模型坐标转换为屏幕坐标

        应用30度旋转和0.8纵向压缩以产生等角透视效果

        注意：调用者需要在传入前对 Y 坐标取反

        Args:
            x: 模型X坐标
            y: 模型Y坐标（已取反）

        Returns:
            屏幕坐标点
        """
        rotated = self.rotate_2d(x, y, 30)
        return Point(
            rotated.x * self.scale + self.offset_x,
            rotated.y * self.scale * 0.8 + self.offset_y,
        )

    def to_screen_point(self, point: Point) -> Point:
        """将Point对象转换为屏幕坐标"""
        return self.to_screen(point.x, point.y)
