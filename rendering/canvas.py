"""
画布抽象层 - 解耦渲染与具体图形库

遵循依赖倒置原则（DIP），定义抽象画布接口
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.colors import RGB
from core.geometry import Point

if TYPE_CHECKING:
    from graphics import GraphWin


class Canvas(ABC):
    """
    画布抽象接口

    定义绑定图形库的抽象方法，具体实现由子类完成
    """

    @abstractmethod
    def draw_polygon(
        self, points: list[Point], fill: RGB, outline: RGB | None = None
    ) -> None:
        """绘制多边形"""
        ...

    @abstractmethod
    def draw_line(self, p1: Point, p2: Point, color: RGB, width: int = 1) -> None:
        """绘制直线"""
        ...

    @abstractmethod
    def draw_text(
        self,
        position: Point,
        text: str,
        size: int,
        color: RGB,
        face: str = "helvetica",
        style: str = "normal",
    ) -> None:
        """绘制文本"""
        ...

    @abstractmethod
    def draw_rectangle(
        self, p1: Point, p2: Point, fill: RGB, outline: RGB, width: int = 1
    ) -> None:
        """绘制矩形"""
        ...


class GraphicsCanvas(Canvas):
    """
    graphics.py 库的具体实现

    将抽象Canvas接口转换为graphics.py的具体调用
    """

    def __init__(self, win: GraphWin):
        """
        初始化画布

        Args:
            win: graphics.py 的窗口对象
        """
        self.win = win
        # 延迟导入以避免循环依赖
        from graphics import Line, Polygon, Rectangle, Text
        from graphics import Point as GPoint
        from graphics import color_rgb

        self._Line = Line
        self._Polygon = Polygon
        self._Rectangle = Rectangle
        self._Text = Text
        self._GPoint = GPoint
        self._color_rgb = color_rgb

    def _to_gpoint(self, point: Point):
        """将Point转换为graphics.Point"""
        return self._GPoint(point.x, point.y)

    def _to_color(self, rgb: RGB) -> str:
        """将RGB转换为graphics颜色"""
        return self._color_rgb(rgb.r, rgb.g, rgb.b)

    def draw_polygon(
        self, points: list[Point], fill: RGB, outline: RGB | None = None
    ) -> None:
        gpoints = [self._to_gpoint(p) for p in points]
        poly = self._Polygon(gpoints)
        poly.setFill(self._to_color(fill))
        if outline:
            poly.setOutline(self._to_color(outline))
        poly.draw(self.win)

    def draw_line(self, p1: Point, p2: Point, color: RGB, width: int = 1) -> None:
        line = self._Line(self._to_gpoint(p1), self._to_gpoint(p2))
        line.setOutline(self._to_color(color))
        line.setWidth(width)
        line.draw(self.win)

    def draw_text(
        self,
        position: Point,
        text: str,
        size: int,
        color: RGB,
        face: str = "helvetica",
        style: str = "normal",
    ) -> None:
        text_obj = self._Text(self._to_gpoint(position), text)
        # graphics.py 限制字体大小5-36
        clamped_size = max(5, min(size, 36))
        text_obj.setSize(clamped_size)
        text_obj.setTextColor(self._to_color(color))
        text_obj.setFace(face)
        if style != "normal":
            text_obj.setStyle(style)
        text_obj.draw(self.win)

    def draw_rectangle(
        self, p1: Point, p2: Point, fill: RGB, outline: RGB, width: int = 1
    ) -> None:
        rect = self._Rectangle(self._to_gpoint(p1), self._to_gpoint(p2))
        rect.setFill(self._to_color(fill))
        rect.setOutline(self._to_color(outline))
        rect.setWidth(width)
        rect.draw(self.win)
