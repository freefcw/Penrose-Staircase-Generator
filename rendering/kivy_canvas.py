"""
Kivy 画布实现 - 将抽象 Canvas 接口映射到 Kivy 绘图指令

注意：Kivy 坐标系 (0,0) 在左下角，Y轴向上。
而原有的 graphics.py 坐标系 (0,0) 在左上角，Y轴向下。
此适配器在绘制时进行 Y 坐标翻转。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, final

from typing_extensions import override

from rendering.canvas import Canvas, DrawHandle
from core.theme import RGB
from core.geometry import Point

if TYPE_CHECKING:
    from kivy.graphics import InstructionGroup
    from kivy.uix.widget import Widget


class KivyDrawHandle:
    """Kivy 绘图句柄，用于撤销操作"""
    
    def __init__(self, instruction_group: InstructionGroup, parent_canvas):
        self._group = instruction_group
        self._parent_canvas = parent_canvas
    
    def undraw(self) -> None:
        """从画布上移除该图形对象"""
        if self._group and self._parent_canvas:
            self._parent_canvas.remove(self._group)


@final
class KivyCanvas(Canvas):
    """
    Kivy 画布实现

    将抽象 Canvas 接口转换为 Kivy 的绘图指令
    """

    def __init__(self, widget: Widget, window_height: float):
        """
        初始化 Kivy 画布

        Args:
            widget: Kivy Widget 对象，用于获取 canvas
            window_height: 窗口高度，用于 Y 坐标翻转
        """
        self._widget = widget
        self._canvas = widget.canvas
        self._window_height = window_height

        # 延迟导入 Kivy 模块
        from kivy.graphics import Color, Line, Mesh, Rectangle, InstructionGroup
        from kivy.core.text import Label as CoreLabel

        self._Color = Color
        self._Line = Line
        self._Mesh = Mesh
        self._Rectangle = Rectangle
        self._InstructionGroup = InstructionGroup
        self._CoreLabel = CoreLabel

    def _flip_y(self, y: float) -> float:
        """将 Y 坐标从 top-left 坐标系翻转到 bottom-left 坐标系"""
        return self._window_height - y
    
    def _transform_x(self, x: float) -> float:
        """将 X 坐标转换为 widget 内的全局坐标"""
        return x + self._widget.x
    
    def _transform_y(self, y: float) -> float:
        """将 Y 坐标翻转并转换为 widget 内的全局坐标"""
        return self._flip_y(y) + self._widget.y

    def _to_rgba(self, rgb: RGB) -> tuple[float, float, float, float]:
        """将 RGB 转换为 Kivy 的 RGBA (0-1 范围)"""
        return (rgb.r / 255.0, rgb.g / 255.0, rgb.b / 255.0, 1.0)

    @override
    def draw_polygon(
        self, points: list[Point], fill: RGB, outline: RGB | None = None
    ) -> None:
        """绘制填充多边形"""
        if len(points) < 3:
            return

        # 转换点坐标（使用 widget 相对坐标）
        transformed_points = [(self._transform_x(p.x), self._transform_y(p.y)) for p in points]

        # 使用 Mesh 绘制填充多边形 (triangle_fan 模式)
        # 构建顶点数据: [x1, y1, u1, v1, x2, y2, u2, v2, ...]
        vertices = []
        for x, y in transformed_points:
            vertices.extend([x, y, 0, 0])  # u, v 设为 0

        # 构建索引 (triangle_fan: 0, 1, 2, 0, 2, 3, 0, 3, 4, ...)
        indices = []
        for i in range(1, len(transformed_points) - 1):
            indices.extend([0, i, i + 1])

        with self._canvas:
            self._Color(*self._to_rgba(fill))
            self._Mesh(vertices=vertices, indices=indices, mode='triangles')

            # 绘制边框
            if outline:
                self._Color(*self._to_rgba(outline))
                flat_points = []
                for x, y in transformed_points:
                    flat_points.extend([x, y])
                self._Line(points=flat_points, close=True, width=1)

    @override
    def draw_line(self, p1: Point, p2: Point, color: RGB, width: int = 1) -> None:
        """绘制直线"""
        with self._canvas:
            self._Color(*self._to_rgba(color))
            self._Line(
                points=[self._transform_x(p1.x), self._transform_y(p1.y), 
                        self._transform_x(p2.x), self._transform_y(p2.y)],
                width=width
            )

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
        from kivy.graphics import Rectangle as KivyRect
        import platform
        import os
        
        # 根据平台获取字体路径列表
        system = platform.system().lower()
        if system == 'darwin':
            # macOS 字体
            font_paths = [
                '/System/Library/Fonts/PingFang.ttc',
                '/System/Library/Fonts/STHeiti Light.ttc',
                '/Library/Fonts/Arial Unicode.ttf',
            ]
        elif system == 'linux':
            # Linux 字体
            font_paths = [
                '/usr/share/fonts/truetype/HarmonyOS_Sans_SC/HarmonyOS_Sans_SC_Regular.ttf',
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/sarasa/sarasa/SarasaGothicSC-Regular.ttf',
                '/usr/share/fonts/truetype/arphic/uming.ttc',
                os.path.expanduser('~/.local/share/fonts/NotoSansCJKsc-Regular.otf'),
            ]
        else:
            # Windows 或其他平台
            font_paths = [
                'C:\\Windows\\Fonts\\msyh.ttc',  # 微软雅黑
                'C:\\Windows\\Fonts\\simsun.ttc',  # 宋体
            ]
        
        font_name = 'Roboto'  # 默认使用 Kivy 内置字体
        for path in font_paths:
            if os.path.exists(path):
                font_name = path
                break
        
        # 创建 CoreLabel 渲染文本
        label = self._CoreLabel(
            text=text,
            font_size=size,
            color=self._to_rgba(color),
            font_name=font_name,
        )
        label.refresh()
        texture = label.texture
        
        if texture:
            # 计算绘制位置 (居中对齐)
            x = self._transform_x(position.x) - texture.width / 2
            y = self._transform_y(position.y) - texture.height / 2
            
            with self._canvas:
                self._Color(1, 1, 1, 1)  # 白色，让纹理颜色显示
                KivyRect(texture=texture, pos=(x, y), size=texture.size)

    @override
    def draw_rectangle(
        self, p1: Point, p2: Point, fill: RGB, outline: RGB, width: int = 1
    ) -> None:
        """绘制矩形"""
        # 计算左下角和尺寸（使用 widget 相对坐标）
        x1, y1 = self._transform_x(p1.x), self._transform_y(p1.y)
        x2, y2 = self._transform_x(p2.x), self._transform_y(p2.y)
        
        left = min(x1, x2)
        bottom = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)

        with self._canvas:
            # 填充
            self._Color(*self._to_rgba(fill))
            self._Rectangle(pos=(left, bottom), size=(w, h))
            
            # 边框
            self._Color(*self._to_rgba(outline))
            self._Line(
                rectangle=[left, bottom, w, h],
                width=width
            )

    @override
    def draw_polygon_outline(
        self, points: list[Point], color: RGB, width: int = 2
    ) -> DrawHandle:
        """绘制多边形边框（用于高亮）"""
        if len(points) < 3:
            return KivyDrawHandle(None, None)  # type: ignore

        # 转换点坐标（使用 widget 相对坐标）
        transformed_points = [(self._transform_x(p.x), self._transform_y(p.y)) for p in points]
        flat_points = []
        for x, y in transformed_points:
            flat_points.extend([x, y])

        group = self._InstructionGroup()
        group.add(self._Color(*self._to_rgba(color)))
        group.add(self._Line(points=flat_points, close=True, width=width))
        
        self._canvas.add(group)
        
        return KivyDrawHandle(group, self._canvas)
