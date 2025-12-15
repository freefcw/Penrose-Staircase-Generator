"""
楼梯渲染器 - 负责绘制Penrose楼梯的各个部分
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from core.theme import Theme
from core.geometry import GeometryTransform, Point
from core.staircase import StaircaseConfig, StaircaseModel, StepPosition

if TYPE_CHECKING:
    from rendering.canvas import Canvas


class PolygonBuilder:
    """
    多边形构建器

    用于逐步构建多边形的点列表
    """

    def __init__(self, transform: GeometryTransform):
        self.transform = transform
        self._points: list[Point] = []
        self._cursor_x: float = 0
        self._cursor_y: float = 0

    def move_to(self, x: float, y: float) -> "PolygonBuilder":
        """移动画笔到指定位置"""
        self._cursor_x = x
        self._cursor_y = y
        return self

    def move_rel(self, dx: float, dy: float) -> "PolygonBuilder":
        """相对移动画笔"""
        self._cursor_x += dx
        self._cursor_y += dy
        return self

    def line_to(self, x: float, y: float) -> "PolygonBuilder":
        """画线到指定位置"""
        self._points.append(self.transform.to_screen(self._cursor_x, -self._cursor_y))
        self._cursor_x = x
        self._cursor_y = y
        self._points.append(self.transform.to_screen(x, -y))
        return self

    def line_rel(self, dx: float, dy: float) -> "PolygonBuilder":
        """相对画线"""
        self._points.append(self.transform.to_screen(self._cursor_x, -self._cursor_y))
        self._cursor_x += dx
        self._cursor_y += dy
        self._points.append(
            self.transform.to_screen(self._cursor_x, -self._cursor_y)
        )
        return self

    def build(self) -> list[Point]:
        """返回构建的点列表并重置"""
        points = self._points.copy()
        self._points.clear()
        return points

    def clear(self) -> "PolygonBuilder":
        """清空点列表"""
        self._points.clear()
        return self


class StaircaseRenderer:
    """
    Penrose楼梯渲染器
    
    采用组合模式，将渲染职责委托给专注的子渲染器：
    - WallRenderer: 墙体渲染
    - LabelRenderer: 标签渲染
    - DecoratorRenderer: 装饰矩形渲染
    
    本类只负责：
    - 渲染楼梯的四个区域（A、B、C、D）
    - 渲染起点标记
    - 协调渲染顺序（画家算法）
    """

    # 几何常量
    U: float = 1.0  # 单位宽度
    H: float = 0.866025404  # 单位高度 (sqrt(3)/2)

    def __init__(
        self,
        canvas: Canvas,
        transform: GeometryTransform,
        config: StaircaseConfig,
        model: StaircaseModel,
        theme: Theme,
    ):
        """
        初始化渲染器
        
        Args:
            canvas: 画布对象
            transform: 几何变换器
            config: 楼梯配置
            model: 楼梯模型
            theme: 主题对象
        """
        from rendering.wall_renderer import WallRenderer
        from rendering.label_renderer import LabelRenderer
        from rendering.decorator_renderer import DecoratorRenderer
        
        self.canvas = canvas
        self.transform = transform
        self.config = config
        self.model = model
        self.theme = theme
        self.builder = PolygonBuilder(transform)

        # 简化访问
        self.A = config.a
        self.B = config.b
        self.C = config.c
        self.D = config.d
        self.L = config.step_length
        self.WH = config.wall_height
        
        # 子渲染器
        self._wall_renderer = WallRenderer(canvas, transform, config, theme)
        self._label_renderer = LabelRenderer(canvas, transform, config, theme)
        self._decorator_renderer = DecoratorRenderer(canvas, transform, config, theme)

    def render(self, start_index: int) -> None:
        """
        渲染完整楼梯

        按照画家算法顺序渲染：
        1. A区台阶
        2. 内墙、中墙
        3. D区台阶
        4. B区台阶
        5. C区台阶
        6. 装饰矩形
        7. 前墙、右墙
        8. 区域标签
        """
        self.model.clear_positions()
        current_index = 0

        # 渲染A区台阶
        current_index = self._render_zone_a(0, 0, current_index, start_index)

        # 渲染墙体（委托给 WallRenderer）
        self._wall_renderer.render_inner_wall(0, 0)
        self._wall_renderer.render_mid_wall(0, 0)

        # 渲染D区台阶
        current_index = self._render_zone_d(0, 0, current_index, start_index)

        # 渲染B区台阶
        current_index = self._render_zone_b(0, 0, current_index, start_index)

        # 渲染C区台阶
        current_index = self._render_zone_c(0, 0, current_index, start_index)

        # 渲染装饰矩形（委托给 DecoratorRenderer）
        self._decorator_renderer.render_all()

        # 渲染外墙（委托给 WallRenderer）
        self._wall_renderer.render_front_wall(0, 0)
        self._wall_renderer.render_right_wall(0, 0)

        # 渲染区域标签（委托给 LabelRenderer）
        self._label_renderer.render_zone_labels()

    def _render_step(
        self,
        x: float,
        y: float,
        length: float,
        current_index: int,
        start_index: int,
        skip_record: bool = False,
    ) -> int:
        """
        渲染单个台阶

        Args:
            x, y: 台阶起点坐标
            length: 台阶长度
            current_index: 当前台阶索引
            start_index: 起点台阶索引
            skip_record: 是否跳过记录（用于共享台阶）

        Returns:
            更新后的索引
        """
        U, H, L = self.U, self.H, length

        # 计算四个角点
        p1 = (x, y)
        p2 = (x + U * 0.5 * L, y + H * L)
        p3 = (x + U * 0.5 * L + U * L, y + H * L)
        p4 = (x + U * L, y)

        # 构建多边形
        self.builder.clear()
        self.builder.move_to(*p1).line_to(*p2).line_to(*p3).line_to(*p4)
        points = self.builder.build()

        # 确定颜色
        if not skip_record and current_index < len(self.model.color_sequence):
            is_red = self.model.color_sequence[current_index]
            color = self.theme.colors.get_step_color(is_red)
        else:
            color = self.theme.colors.step_gray

        # 绘制多边形
        self.canvas.draw_polygon(points, color)

        # 记录位置
        if not skip_record:
            step_pos = StepPosition(p1, p2, p3, p4)
            self.model.add_step_position(step_pos)

            # 绘制起点标记
            if current_index == start_index:
                self._draw_start_marker(step_pos)

            current_index += 1

        return current_index

    def _draw_start_marker(self, step: StepPosition) -> None:
        """绘制起点对角线标记"""
        sp1 = self.transform.to_screen(step.p1[0], -step.p1[1])
        sp2 = self.transform.to_screen(step.p2[0], -step.p2[1])
        sp3 = self.transform.to_screen(step.p3[0], -step.p3[1])
        sp4 = self.transform.to_screen(step.p4[0], -step.p4[1])

        line_width = max(1, int(self.transform.scale / 8))
        self.canvas.draw_line(sp1, sp3, self.theme.colors.marker_white, line_width)
        self.canvas.draw_line(sp2, sp4, self.theme.colors.marker_white, line_width)

    def _render_zone_a(
        self, x: float, y: float, current_index: int, start_index: int
    ) -> int:
        """渲染A区台阶（上升区）"""
        A, L, U, H = self.A, self.L, self.U, self.H

        for i in range(A - 1, -1, -1):
            step_x = x + (U * 0.5 * L) * i + (U / 2) * i
            step_y = y + (H * L - H) * i
            skip = i == 0  # 第一个台阶是共享的
            current_index = self._render_step(
                step_x, step_y, L, current_index, start_index, skip
            )

        return current_index

    def _render_zone_b(
        self, x: float, y: float, current_index: int, start_index: int
    ) -> int:
        """渲染B区台阶（水平区右）"""
        A, B, L, U, H = self.A, self.B, self.L, self.U, self.H

        for j in range(1, B):
            step_x = x + (U * 0.5 * L) * (A - 1) + (U / 2) * (A - 1) + (L + U / 2) * j
            step_y = y + (H * L - H) * (A - 1) - j * H
            current_index = self._render_step(
                step_x, step_y, L, current_index, start_index
            )

        return current_index

    def _render_zone_c(
        self, x: float, y: float, current_index: int, start_index: int
    ) -> int:
        """渲染C区台阶（下降区）"""
        A, B, C, L, U, H = self.A, self.B, self.C, self.L, self.U, self.H

        xx1 = (U * 0.5 * L) * (A - 1) + (U / 2) * (A - 1) + (L + U / 2) * (B - 1)
        yy1 = (H * L - H) * (A - 1) - (B - 1) * H

        for k in range(1, C):
            step_x = x + xx1 - L * U * 0.5 * k + (U / 2) * k
            step_y = y + yy1 - k * H * (L + 1)
            current_index = self._render_step(
                step_x, step_y, L, current_index, start_index
            )

        return current_index

    def _render_zone_d(
        self, x: float, y: float, current_index: int, start_index: int
    ) -> int:
        """渲染D区台阶（水平区左）"""
        A, B, C, D, L, U, H = self.A, self.B, self.C, self.D, self.L, self.U, self.H

        xx1 = (U * 0.5 * L) * (A - 1) + (U / 2) * (A - 1) + (L + U / 2) * (B - 1)
        yy1 = (H * L - H) * (A - 1) - (B - 1) * H
        xxx1 = xx1 - L * U * 0.5 * (C - 1) + (U / 2) * (C - 1)
        yyy1 = yy1 - (C - 1) * H * (L + 1)

        for m in range(D - 1, 0, -1):
            step_x = x + xxx1 - L * U * m + (U / 2) * m
            step_y = y + yyy1 - H * m
            current_index = self._render_step(
                step_x, step_y, L, current_index, start_index
            )

        return current_index

    def _render_inner_wall(self, x: float, y: float) -> None:
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

    def _render_mid_wall(self, x: float, y: float) -> None:
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

    def _render_front_wall(self, x: float, y: float) -> None:
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

    def _render_right_wall(self, x: float, y: float) -> None:
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

    def _render_stair_rects_c(self, x: float, y: float) -> None:
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

    def _render_stair_rects_d(self, x: float, y: float) -> None:
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

    def _render_zone_labels(self) -> None:
        """渲染区域标签 A、B、C、D，放在每个区域中点外侧"""
        A, B, C, D, L, U, H = self.A, self.B, self.C, self.D, self.L, self.U, self.H

        font_size = max(16, int(self.transform.scale / 1.5))

        # === A区：从 (0,0) 到 A区最高点 ===
        a_start = (0, 0)
        a_end_x = (U * 0.5 * L) * (A - 1) + (U / 2) * (A - 1)
        a_end_y = (H * L - H) * (A - 1)
        a_mid = ((a_start[0] + a_end_x) / 2, (a_start[1] + a_end_y) / 2)
        a_screen = self.transform.to_screen(a_mid[0], -a_mid[1])
        a_label_pos = Point(a_screen.x, a_screen.y - 25)  # 向上偏移25

        # === B区：从 A区终点 到 B区终点 ===
        b_start_x = a_end_x + L * U
        b_start_y = a_end_y + H * L
        b_end_x = b_start_x + (L + U / 2) * (B - 1)
        b_end_y = b_start_y - (B - 1) * H
        b_mid = ((b_start_x + b_end_x) / 2, (b_start_y + b_end_y) / 2)
        b_screen = self.transform.to_screen(b_mid[0], -b_mid[1])
        b_label_pos = Point(b_screen.x, b_screen.y - 25)  # 向上偏移25

        # === C区：从 B区终点 向右下延伸 ===
        c_start_x = b_end_x
        c_start_y = b_end_y
        c_end_x = c_start_x - L * U * 0.5 * (C - 1) + (U / 2) * (C - 1)
        c_end_y = c_start_y - (C - 1) * H * (L + 1)
        c_mid = ((c_start_x + c_end_x) / 2, (c_start_y + c_end_y) / 2)
        c_screen = self.transform.to_screen(c_mid[0], -c_mid[1])
        c_label_pos = Point(c_screen.x + 15, c_screen.y + 35)  # 向右下偏移

        # === D区：前墙底部的台阶 ===
        # D区在前墙（蓝色）前面，从原点(0,0)向左延伸
        d_mid_x = L * (D - 1) / 2  # D区中点X（向右为正）
        d_mid_y = -H * (D - 1) / 2  # D区中点Y（向下为负）
        d_screen = self.transform.to_screen(d_mid_x, -d_mid_y)
        d_label_pos = Point(d_screen.x, d_screen.y + 8)  # 向下偏移8

        labels = [
            (a_label_pos, "A"),
            (b_label_pos, "B"),
            (c_label_pos, "C"),
            (d_label_pos, "D"),
        ]
        # 根据主题样式选择标签颜色
        label_color = (
            self.theme.colors.text_light
            if self.theme.style.use_light_labels
            else self.theme.colors.text_black
        )

        for pos, label in labels:
            self.canvas.draw_text(
                pos, label, font_size, label_color, style="bold"
            )
