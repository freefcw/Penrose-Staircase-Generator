"""
标签渲染器 - 负责绘制Penrose楼梯的区域标签

从 StaircaseRenderer 提取的专注组件。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, final

from core.theme import Theme
from core.geometry import GeometryTransform, Point
from core.staircase import StaircaseConfig

if TYPE_CHECKING:
    from rendering.canvas import Canvas


@final
class LabelRenderer:
    """
    区域标签渲染器
    
    职责：
    - 渲染 A、B、C、D 区域标签
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
        初始化标签渲染器
        
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
        
        # 简化访问
        self.A = config.a
        self.B = config.b
        self.C = config.c
        self.D = config.d
        self.L = config.step_length
    
    def render_zone_labels(self) -> None:
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
        d_mid_x = L * (D - 1) / 2
        d_mid_y = -H * (D - 1) / 2
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
