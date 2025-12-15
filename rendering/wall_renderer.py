"""
墙体渲染器 - 负责绘制Penrose楼梯的墙体结构

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
class WallRenderer:
    """
    墙体渲染器
    
    职责：
    - 渲染内墙
    - 渲染中墙
    - 渲染前墙
    - 渲染右墙
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
        初始化墙体渲染器
        
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
        self.WH = config.wall_height
    
    def render_all(self, x: float = 0, y: float = 0) -> None:
        """渲染所有墙体"""
        self.render_inner_wall(x, y)
        self.render_mid_wall(x, y)
        self.render_front_wall(x, y)
        self.render_right_wall(x, y)
    
    def render_inner_wall(self, x: float, y: float) -> None:
        """渲染内墙"""
        A, B, L, U, H, WH = self.A, self.B, self.L, self.U, self.H, self.WH

        self.builder.clear()
        self.builder.move_to(x, y)
        self.builder.move_rel(L * U + L * U * 0.5 + U / 2, H * L - H)

        for _ in range(1, A):
            self.builder.move_rel(L * U * 0.5, H * L)
            self.builder.move_rel(U * 0.5, -H)

        self.builder.move_rel(-L * 0.5 * U, -H * L)

        for _ in range(1, B - 1):
            self.builder.line_rel(L * U, 0)
            self.builder.line_rel(U * 0.5, -H)

        self.builder.line_rel(L, 0)
        self.builder.line_rel(U * 0.5, -H)
        self.builder.line_rel(-L, 0)
        self.builder.line_rel(U * WH * 0.5 - B * U * 0.5, -H * WH + H * B)
        self.builder.line_rel(-L * U * (B - 2) + U * 0.5, -H)

        self.canvas.draw_polygon(self.builder.build(), self.theme.colors.wall_front)

    def render_mid_wall(self, x: float, y: float) -> None:
        """渲染中墙"""
        A, C, L, U, H, WH = self.A, self.C, self.L, self.U, self.H, self.WH

        self.builder.clear()
        self.builder.move_to(x, y)
        self.builder.move_rel(L * U + L * U * 0.5 + U / 2, H * L - H)

        for _ in range(1, A):
            self.builder.line_rel(L * U * 0.5, H * L)
            self.builder.line_rel(U * 0.5, -H)

        self.builder.line_rel(-L * 0.5 * U, -H * L)
        self.builder.line_rel(U * WH * 0.5, -H * WH)
        self.builder.line_rel(-U * 0.5 * L * (C - 1), -H * L * (C - 1))

        self.canvas.draw_polygon(self.builder.build(), self.theme.colors.wall_side)

    def render_front_wall(self, x: float, y: float) -> None:
        """渲染前墙"""
        D, L, U, H, WH = self.D, self.L, self.U, self.H, self.WH

        self.builder.clear()
        self.builder.move_to(x, y)

        for _ in range(1, D):
            self.builder.line_rel(L, 0)
            self.builder.line_rel(-U * 0.5, H)

        self.builder.line_rel(L, 0)
        self.builder.line_rel(U * WH * 0.5, -H * WH)
        self.builder.line_rel(-U * D * L, 0)

        self.canvas.draw_polygon(self.builder.build(), self.theme.colors.wall_front)

    def render_right_wall(self, x: float, y: float) -> None:
        """渲染右墙"""
        C, D, L, U, H, WH = self.C, self.D, self.L, self.U, self.H, self.WH

        self.builder.clear()
        self.builder.move_to(x, y)

        for _ in range(1, D):
            self.builder.move_rel(L, 0)
            self.builder.move_rel(-U * 0.5, H)

        self.builder.move_rel(L, 0)

        for _ in range(1, C):
            self.builder.line_rel(L * U * 0.5, H * L)
            self.builder.line_rel(-U * 0.5, H)

        self.builder.line_rel(L * U * 0.5, H * L)

        for _ in range(1, C):
            self.builder.line_rel(U * 0.5, -H)

        self.builder.line_rel(U * WH * 0.5, -H * WH)
        self.builder.line_rel(-U * 0.5 * L * C, -H * L * C)

        self.canvas.draw_polygon(self.builder.build(), self.theme.colors.wall_side)
