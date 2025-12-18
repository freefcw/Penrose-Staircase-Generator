"""
Flet 画布实现 - 将抽象 Canvas 接口映射到 Flet 绘图指令

注意：Flet 坐标系 (0,0) 在左上角，Y轴向下，与原设计一致。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, final

from typing_extensions import override

from rendering.canvas import Canvas, DrawHandle
from core.theme import RGB
from core.geometry import Point

if TYPE_CHECKING:
    import flet as ft
    import flet.canvas as cv


class FletDrawHandle:
    """Flet 绘图句柄，用于撤销操作"""
    
    def __init__(self, shape_index: int, canvas_ref: "FletCanvas"):
        self._shape_index = shape_index
        self._canvas_ref = canvas_ref
    
    def undraw(self) -> None:
        """从画布上移除该图形对象"""
        self._canvas_ref.remove_shape(self._shape_index)


@final
class FletCanvas(Canvas):
    """
    Flet 画布实现

    将抽象 Canvas 接口转换为 Flet 的绘图指令
    """

    def __init__(self, width: float, height: float):
        """
        初始化 Flet 画布

        Args:
            width: 画布宽度
            height: 画布高度
        """
        import flet as ft
        import flet.canvas as cv
        
        self._ft = ft
        self._cv = cv
        self._width = width
        self._height = height
        self._shapes: list = []  # 存储所有绘图形状
        
    def _to_color(self, rgb: RGB) -> str:
        """将 RGB 转换为 Flet 颜色字符串 (#RRGGBB)"""
        return f"#{rgb.r:02x}{rgb.g:02x}{rgb.b:02x}"
    
    def get_shapes(self) -> list:
        """获取所有绘制的形状，用于渲染到 Canvas 控件"""
        return self._shapes
    
    def clear(self) -> None:
        """清除所有形状"""
        self._shapes.clear()
    
    def remove_shape(self, index: int) -> None:
        """移除指定索引的形状"""
        if 0 <= index < len(self._shapes):
            self._shapes[index] = None  # 标记为已移除

    @override
    def draw_polygon(
        self, points: list[Point], fill: RGB, outline: RGB | None = None
    ) -> None:
        """绘制填充多边形"""
        if len(points) < 3:
            return

        # 构建 Path 元素
        elements = [self._cv.Path.MoveTo(points[0].x, points[0].y)]
        for p in points[1:]:
            elements.append(self._cv.Path.LineTo(p.x, p.y))
        elements.append(self._cv.Path.Close())
        
        # 填充多边形
        fill_path = self._cv.Path(
            elements,
            paint=self._ft.Paint(
                color=self._to_color(fill),
                style=self._ft.PaintingStyle.FILL,
            ),
        )
        self._shapes.append(fill_path)
        
        # 绘制边框
        if outline:
            outline_path = self._cv.Path(
                elements,
                paint=self._ft.Paint(
                    color=self._to_color(outline),
                    style=self._ft.PaintingStyle.STROKE,
                    stroke_width=1,
                ),
            )
            self._shapes.append(outline_path)

    @override
    def draw_line(self, p1: Point, p2: Point, color: RGB, width: int = 1) -> None:
        """绘制直线"""
        line = self._cv.Line(
            x1=p1.x, y1=p1.y,
            x2=p2.x, y2=p2.y,
            paint=self._ft.Paint(
                color=self._to_color(color),
                stroke_width=width,
            ),
        )
        self._shapes.append(line)

    @override
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
        text_shape = self._cv.Text(
            x=position.x,
            y=position.y,
            text=text,
            style=self._ft.TextStyle(
                size=size,
                color=self._to_color(color),
            ),
            alignment=self._ft.alignment.center,
        )
        self._shapes.append(text_shape)

    @override
    def draw_rectangle(
        self, p1: Point, p2: Point, fill: RGB, outline: RGB, width: int = 1
    ) -> None:
        """绘制矩形"""
        x = min(p1.x, p2.x)
        y = min(p1.y, p2.y)
        w = abs(p2.x - p1.x)
        h = abs(p2.y - p1.y)
        
        # 填充矩形
        fill_rect = self._cv.Rect(
            x=x, y=y, width=w, height=h,
            paint=self._ft.Paint(
                color=self._to_color(fill),
                style=self._ft.PaintingStyle.FILL,
            ),
        )
        self._shapes.append(fill_rect)
        
        # 边框矩形
        outline_rect = self._cv.Rect(
            x=x, y=y, width=w, height=h,
            paint=self._ft.Paint(
                color=self._to_color(outline),
                style=self._ft.PaintingStyle.STROKE,
                stroke_width=width,
            ),
        )
        self._shapes.append(outline_rect)

    @override
    def draw_polygon_outline(
        self, points: list[Point], color: RGB, width: int = 2
    ) -> DrawHandle:
        """绘制多边形边框（用于高亮）"""
        if len(points) < 3:
            return FletDrawHandle(-1, self)

        # 构建 Path 元素
        elements = [self._cv.Path.MoveTo(points[0].x, points[0].y)]
        for p in points[1:]:
            elements.append(self._cv.Path.LineTo(p.x, p.y))
        elements.append(self._cv.Path.Close())
        
        outline_path = self._cv.Path(
            elements,
            paint=self._ft.Paint(
                color=self._to_color(color),
                style=self._ft.PaintingStyle.STROKE,
                stroke_width=width,
            ),
        )
        
        shape_index = len(self._shapes)
        self._shapes.append(outline_path)
        
        return FletDrawHandle(shape_index, self)
