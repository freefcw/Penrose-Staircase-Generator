"""
Pillow 画布实现 - 用于导出 PNG 图片

直接渲染到 Pillow Image 对象，然后保存为文件
"""
from __future__ import annotations

from typing import final

from PIL import Image, ImageDraw, ImageFont
from typing_extensions import override

from rendering.canvas import Canvas, DrawHandle
from core.theme import RGB
from core.geometry import Point


class PillowDrawHandle:
    """Pillow 绘图句柄（不支持撤销）"""
    
    def undraw(self) -> None:
        """Pillow 不支持撤销操作"""
        pass


@final
class PillowCanvas(Canvas):
    """
    Pillow 画布实现

    将抽象 Canvas 接口转换为 Pillow 的绘图指令
    用于导出 PNG 图片
    """

    def __init__(self, width: int, height: int, background_color: RGB = RGB(240, 240, 240)):
        """
        初始化 Pillow 画布

        Args:
            width: 画布宽度
            height: 画布高度
            background_color: 背景颜色
        """
        self._width = width
        self._height = height
        self._image = Image.new('RGB', (width, height), self._to_tuple(background_color))
        self._draw = ImageDraw.Draw(self._image)
        
    def _to_tuple(self, rgb: RGB) -> tuple[int, int, int]:
        """将 RGB 转换为元组"""
        return (rgb.r, rgb.g, rgb.b)
    
    def get_image(self) -> Image.Image:
        """获取 Pillow Image 对象"""
        return self._image
    
    def save(self, file_path: str) -> None:
        """保存图片到文件"""
        self._image.save(file_path, 'PNG')
        print(f"[导出] 图片已保存: {file_path}")

    @override
    def draw_polygon(
        self, points: list[Point], fill: RGB, outline: RGB | None = None
    ) -> None:
        """绘制填充多边形"""
        if len(points) < 3:
            return

        xy = [(p.x, p.y) for p in points]
        self._draw.polygon(
            xy,
            fill=self._to_tuple(fill),
            outline=self._to_tuple(outline) if outline else None
        )

    @override
    def draw_line(self, p1: Point, p2: Point, color: RGB, width: int = 1) -> None:
        """绘制直线"""
        self._draw.line(
            [(p1.x, p1.y), (p2.x, p2.y)],
            fill=self._to_tuple(color),
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
        try:
            # 尝试加载中文字体
            from core.fonts import CHINESE_FONT_PATH
            font = ImageFont.truetype(CHINESE_FONT_PATH, size)
        except Exception:
            # 回退到默认字体
            try:
                font = ImageFont.truetype("arial.ttf", size)
            except Exception:
                font = ImageFont.load_default()
        
        # 计算文本居中位置
        bbox = self._draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = position.x - text_width / 2
        y = position.y - text_height / 2
        
        self._draw.text((x, y), text, fill=self._to_tuple(color), font=font)

    @override
    def draw_rectangle(
        self, p1: Point, p2: Point, fill: RGB, outline: RGB, width: int = 1
    ) -> None:
        """绘制矩形"""
        x1, y1 = min(p1.x, p2.x), min(p1.y, p2.y)
        x2, y2 = max(p1.x, p2.x), max(p1.y, p2.y)
        
        self._draw.rectangle(
            [(x1, y1), (x2, y2)],
            fill=self._to_tuple(fill),
            outline=self._to_tuple(outline),
            width=width
        )

    @override
    def draw_polygon_outline(
        self, points: list[Point], color: RGB, width: int = 2
    ) -> DrawHandle:
        """绘制多边形边框（用于高亮）"""
        if len(points) < 3:
            return PillowDrawHandle()

        xy = [(p.x, p.y) for p in points]
        # 闭合多边形
        xy.append(xy[0])
        self._draw.line(xy, fill=self._to_tuple(color), width=width)
        
        return PillowDrawHandle()
