"""
装饰矩形渲染器 - 负责绘制Penrose楼梯的装饰矩形

从 StaircaseRenderer 提取的专注组件。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, final

from core.theme import Theme
from core.geometry import GeometryTransform
from core.staircase import StaircaseConfig
from rendering.renderer import PolygonBuilder

if TYPE_CHECKING:
    from rendering.canvas import Canvas


@final
class DecoratorRenderer:
    """
    装饰矩形渲染器
    
    职责：
    - 渲染C区装饰矩形
    - 渲染D区装饰矩形
    """
    
    # 几何常量
    U: float = 1.0  # 单位宽度
    H: float = 0.866025404  # 单位高度 (sqrt(3)/2)
    
    def __init__(
        self,
        canvas: "Canvas",
        transform: GeometryTransform,
        config: StaircaseConfig,
        theme: Theme,
    ):
        """
        初始化装饰矩形渲染器
        
        Args:
            canvas: 画布对象
            transform: 几何变换器
            config: 楼梯配置
            theme: 主题对象
        """
        self.canvas = canvas
        self.transform = transform
        self.config = config
        self.theme = theme
        self.builder = PolygonBuilder(transform)
        
        # 简化访问
        self.A = config.a
        self.B = config.b
        self.C = config.c
        self.D = config.d
        self.L = config.step_length
    
    def render_all(self, x: float = 0, y: float = 0) -> None:
        """渲染所有装饰矩形"""
        self.render_stair_rects_d(x, y)
        self.render_stair_rects_c(x, y)
    
    def render_stair_rects_c(self, x: float, y: float) -> None:
        """渲染C区装饰矩形"""
        A, B, L, U, H = self.A, self.B, self.L, self.U, self.H

        for n in range(2, B):
            px = (U * 0.5 * L) * (A - 1) + (U / 2) * (A - 1) + L * U * n + (n - 1) * (U / 2)
            py = (H * L - H) * (A - 1) - H * (n - 1)
            self._render_stair_rect_c(x + px, y + py)

    def _render_stair_rect_c(self, x: float, y: float) -> None:
        """渲染单个C区装饰矩形"""
        L, U, H = self.L, self.U, self.H

        self.builder.clear()
        self.builder.move_to(x, y)
        self.builder.line_to(x + U * L * 0.5, y + H * L)
        self.builder.line_rel(U / 2, -H)
        self.builder.line_rel(-U * L * 0.5, -H * L)

        self.canvas.draw_polygon(self.builder.build(), self.theme.colors.wall_side)

    def render_stair_rects_d(self, x: float, y: float) -> None:
        """渲染D区装饰矩形"""
        A, B, C, L, U, H = self.A, self.B, self.C, self.L, self.U, self.H

        px = (U * 0.5 * L) * (A - 1) + (U / 2) * (A - 1) + L * U * B + (B - 1) * (U / 2) - L * U
        py = (H * L - H) * (A - 1) - H * (B - 1)

        for o in range(1, C - 1):
            self._render_stair_rect_d(
                x + px - L * U * 0.5 * o + (U / 2) * o,
                y + py - (L + 1) * H * o
            )

    def _render_stair_rect_d(self, x: float, y: float) -> None:
        """渲染单个D区装饰矩形"""
        L, U, H = self.L, self.U, self.H

        self.builder.clear()
        self.builder.move_to(x, y)
        self.builder.line_to(x + U * L, y)
        self.builder.line_rel(U / 2, -H)
        self.builder.line_rel(-U * L, 0)

        self.canvas.draw_polygon(self.builder.build(), self.theme.colors.wall_front)
