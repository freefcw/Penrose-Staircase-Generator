"""
颜色序列可视化模块 - 显示台阶颜色序列
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from core.theme import RGB, Theme
from core.geometry import Point
from core.layout import LayoutConstants
from core.staircase import StaircaseConfig
from rendering.context import SequenceDrawContext

if TYPE_CHECKING:
    from rendering.canvas import Canvas


class SequenceRenderer:
    """
    颜色序列可视化渲染器

    职责：
    - 将台阶颜色序列按行走顺序重排
    - 以网格形式显示颜色序列
    - 显示二进制到十进制的转换
    """

    COLS = LayoutConstants.SEQUENCE_COLS  # 每行显示的台阶数

    def __init__(
        self,
        canvas: Canvas,
        config: StaircaseConfig,
        window_width: float,
        theme: Theme,
    ):
        """
        初始化序列渲染器

        Args:
            canvas: 画布对象
            config: 楼梯配置
            window_width: 窗口宽度
            theme: 主题对象
        """
        self.canvas = canvas
        self.config = config
        self.window_width = window_width
        self.theme = theme

    def render(
        self,
        colors: list[bool],
        start_index: int,
        start_y: float,
        scale: float = 1.0,
        show_decimal: bool = False,
    ) -> None:
        """
        渲染颜色序列

        Args:
            colors: 颜色序列（绘制顺序）
            start_index: 起点索引（绘制顺序中的索引）
            start_y: 起始Y坐标
            scale: 缩放因子
            show_decimal: 是否显示十进制转换
        """
        if not colors:
            return

        # 转换为行走顺序
        walking_order = self._reorder_to_walking(colors)
        walking_start = self._convert_start_index(start_index)

        # 从起点开始循环排列
        if 0 <= walking_start < len(walking_order):
            ordered = walking_order[walking_start:] + walking_order[:walking_start]
        else:
            ordered = walking_order[:]

        # 绘制
        self._draw_sequence(ordered, start_y, scale, show_decimal)

    def _reorder_to_walking(self, colors: list[bool]) -> list[bool]:
        """
        将绘制顺序转换为行走顺序

        绘制顺序: A区(A-1) → D区(D-1) → B区(B-1) → C区(C-1)
        行走顺序: D区 → C区(反转) → B区(反转) → A区
        """
        a_count = self.config.a - 1
        d_count = self.config.d - 1
        b_count = self.config.b - 1

        walking_order: list[bool] = []

        # D区
        walking_order.extend(colors[a_count : a_count + d_count])
        # C区 (反转)
        walking_order.extend(list(reversed(colors[a_count + d_count + b_count :])))
        # B区 (反转)
        walking_order.extend(
            list(reversed(colors[a_count + d_count : a_count + d_count + b_count]))
        )
        # A区
        walking_order.extend(colors[0:a_count])

        return walking_order

    def _convert_start_index(self, draw_index: int) -> int:
        """
        将绘制顺序索引转换为行走顺序索引

        Args:
            draw_index: 绘制顺序中的索引

        Returns:
            行走顺序中的索引
        """
        a_count = self.config.a - 1
        d_count = self.config.d - 1
        b_count = self.config.b - 1
        c_count = self.config.c - 1

        if draw_index < a_count:
            # A区 → 在行走顺序末尾
            return d_count + c_count + b_count + draw_index
        elif draw_index < a_count + d_count:
            # D区 → 在行走顺序开头
            return draw_index - a_count
        elif draw_index < a_count + d_count + b_count:
            # B区 → 在C区后面，且被反转
            position_in_b = draw_index - a_count - d_count
            return d_count + c_count + (b_count - 1 - position_in_b)
        else:
            # C区 → 在D区后面，且被反转
            position_in_c = draw_index - a_count - d_count - b_count
            return d_count + (c_count - 1 - position_in_c)

    def _draw_sequence(
        self,
        ordered: list[bool],
        start_y: float,
        scale: float,
        show_decimal: bool,
    ) -> None:
        """绘制颜色序列网格"""
        box_size = LayoutConstants.SEQUENCE_BOX_SIZE * scale
        margin = LayoutConstants.SEQUENCE_MARGIN * scale
        start_x = (self.window_width - (self.COLS * (box_size + margin))) / 2

        # 计算行高
        row_height = box_size + margin
        if show_decimal:
            row_height = box_size + margin + LayoutConstants.SEQUENCE_DECIMAL_HEIGHT * scale

        # 根据主题样式决定样式
        is_simple_style = not self.theme.style.show_sequence_border

        # 绘制标题
        hint_pos = Point(
            self.window_width / 2, 
            start_y - LayoutConstants.SEQUENCE_TITLE_OFFSET * scale
        )
        if self.theme.style.sequence_hint_simple:
            hint_text = f"台阶序列 (共{len(ordered)}级)"
            title_color = self.theme.colors.text_light
        else:
            hint_text = f"台阶序列 (共{len(ordered)}级, 从★开始)"
            title_color = self.theme.colors.text_black
        self.canvas.draw_text(
            hint_pos, hint_text, min(int(12 * scale), 30), title_color
        )

        num_rows = (len(ordered) + self.COLS - 1) // self.COLS

        # 绘制方块
        for i, is_red in enumerate(ordered):
            row = i // self.COLS
            col = i % self.COLS
            x = start_x + col * (box_size + margin)
            y = start_y + row * row_height

            # 绘制方块
            color = self.theme.colors.get_step_color(is_red)
            p1 = Point(x, y)
            p2 = Point(x + box_size, y + box_size)
            if is_simple_style:
                self.canvas.draw_rectangle(p1, p2, color, color, 0)  # 无边框
            else:
                self.canvas.draw_rectangle(
                    p1, p2, color, self.theme.colors.text_black, max(1, int(scale))
                )

            # 绘制数字 (0或1)
            text_pos = Point(x + box_size / 2, y + box_size / 2)
            self.canvas.draw_text(
                text_pos,
                "1" if is_red else "0",
                min(int(12 * scale), 36),
                self.theme.colors.text_white,
            )

        # 绘制十进制转换
        if show_decimal:
            ctx = SequenceDrawContext(
                start_y=start_y,
                scale=scale,
                row_height=row_height,
                start_x=start_x,
                box_size=box_size,
                margin=margin,
                num_rows=num_rows,
            )
            self._draw_decimal_values(ordered, ctx)

    def _draw_decimal_values(
        self,
        ordered: list[bool],
        ctx: SequenceDrawContext,
    ) -> None:
        """绘制十进制转换值"""
        is_simple_style = not self.theme.style.show_decimal_border

        for row in range(ctx.num_rows):
            row_start = row * self.COLS
            row_end = min(row_start + self.COLS, len(ordered))
            row_data = ordered[row_start:row_end]

            if len(row_data) >= 6:
                # 前3位转十进制
                first_3 = row_data[0:3]
                first_decimal = (
                    (1 if first_3[0] else 0) * 4
                    + (1 if first_3[1] else 0) * 2
                    + (1 if first_3[2] else 0)
                )

                # 后3位转十进制
                last_3 = row_data[3:6]
                last_decimal = (
                    (1 if last_3[0] else 0) * 4
                    + (1 if last_3[1] else 0) * 2
                    + (1 if last_3[2] else 0)
                )

                decimal_y = (
                    ctx.start_y + row * ctx.row_height + ctx.box_size 
                    + LayoutConstants.DECIMAL_Y_OFFSET * ctx.scale
                )
                decimal_box_height = LayoutConstants.DECIMAL_BOX_HEIGHT_FACTOR * ctx.scale

                # 前3位
                first_box_x1 = ctx.start_x
                first_box_x2 = ctx.start_x + 3 * (ctx.box_size + ctx.margin) - ctx.margin
                first_center_x = (first_box_x1 + first_box_x2) / 2

                if not is_simple_style:
                    self.canvas.draw_rectangle(
                        Point(first_box_x1, decimal_y),
                        Point(first_box_x2, decimal_y + decimal_box_height),
                        RGB(255, 255, 255),
                        self.theme.colors.text_black,
                    )
                text_color = (
                    self.theme.colors.text_light
                    if is_simple_style
                    else self.theme.colors.text_black
                )
                self.canvas.draw_text(
                    Point(first_center_x, decimal_y + decimal_box_height / 2),
                    str(first_decimal),
                    min(int(LayoutConstants.DECIMAL_FONT_SIZE_FACTOR * ctx.scale), 24),
                    text_color,
                )

                # 后3位
                last_box_x1 = ctx.start_x + 3 * (ctx.box_size + ctx.margin)
                last_box_x2 = ctx.start_x + 6 * (ctx.box_size + ctx.margin) - ctx.margin
                last_center_x = (last_box_x1 + last_box_x2) / 2

                if not is_simple_style:
                    self.canvas.draw_rectangle(
                        Point(last_box_x1, decimal_y),
                        Point(last_box_x2, decimal_y + decimal_box_height),
                        RGB(255, 255, 255),
                        self.theme.colors.text_black,
                    )
                self.canvas.draw_text(
                    Point(last_center_x, decimal_y + decimal_box_height / 2),
                    str(last_decimal),
                    min(int(LayoutConstants.DECIMAL_FONT_SIZE_FACTOR * ctx.scale), 24),
                    text_color,
                )
