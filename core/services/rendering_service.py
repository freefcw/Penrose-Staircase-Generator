"""
渲染服务 - 协调渲染流程

遵循单一职责原则，专注于渲染协调。
"""
from __future__ import annotations

import time
from typing import final

from graphics import GraphWin

from core.geometry import GeometryTransform
from core.layout import LayoutConstants
from core.staircase import StaircaseConfig, StaircaseModel
from core.theme import Theme
from export.exporter import ImageExporter
from rendering.canvas import GraphicsCanvas
from rendering.renderer import StaircaseRenderer
from rendering.sequence import SequenceRenderer


@final
class LayoutInfo:
    """窗口布局信息"""

    def __init__(
        self,
        window_width: float,
        window_height: float,
        stair_height: float,
        zoom: float,
        offset_x: float,
        offset_y: float,
    ):
        self.window_width = window_width
        self.window_height = window_height
        self.stair_height = stair_height
        self.zoom = zoom
        self.offset_x = offset_x
        self.offset_y = offset_y


@final
class RenderingService:
    """
    渲染服务
    
    职责：
    - 计算窗口布局
    - 协调楼梯和序列渲染
    - 处理图片导出
    """
    
    @staticmethod
    def calculate_layout(config: StaircaseConfig, scale: float = 1.0) -> LayoutInfo:
        """
        计算窗口布局
        
        Args:
            config: 楼梯配置
            scale: 缩放因子
            
        Returns:
            LayoutInfo 布局信息
        """
        A, B, C, D, L = (
            config.a,
            config.b,
            config.c,
            config.d,
            config.step_length,
        )
        H = GeometryTransform.UNIT_HEIGHT

        # 缩放因子
        zoom = LayoutConstants.ZOOM_BASE / (
            (A + B + C + D + L - 4) * LayoutConstants.ZOOM_DIVISOR
        ) * scale

        # 窗口尺寸
        window_width = (A * L + B * L) * zoom
        stair_height = (A * H * L + B * H * L) * zoom

        # 序列显示区域高度
        total_steps = config.total_steps
        seq_rows = (total_steps // LayoutConstants.SEQUENCE_COLS) + 1
        seq_height = (
            seq_rows * (LayoutConstants.SEQUENCE_ROW_HEIGHT_FACTOR * scale)
            + LayoutConstants.SEQUENCE_AREA_PADDING * scale
        )

        window_height = stair_height + seq_height

        # 偏移量
        offset_x = LayoutConstants.WINDOW_OFFSET_X * scale
        offset_y = (A * L * H * 0.5) * zoom

        return LayoutInfo(
            window_width=window_width,
            window_height=window_height,
            stair_height=stair_height,
            zoom=zoom,
            offset_x=offset_x,
            offset_y=offset_y,
        )
    
    @staticmethod
    def render_to_canvas(
        canvas: GraphicsCanvas,
        transform: GeometryTransform,
        config: StaircaseConfig,
        model: StaircaseModel,
        layout: LayoutInfo,
        theme: Theme,
        n: int,
        scale: float = 1.0,
        show_title: bool = True,
        show_sequence: bool = True,
    ) -> None:
        """
        渲染楼梯和序列到画布
        
        Args:
            canvas: 目标画布
            transform: 几何变换器
            config: 楼梯配置
            model: 楼梯模型
            layout: 布局信息
            theme: 主题
            n: 楼梯序号
            scale: 缩放因子
            show_title: 是否显示标题
            show_sequence: 是否显示序列
        """
        from core.geometry import Point
        
        # 渲染楼梯
        renderer = StaircaseRenderer(canvas, transform, config, model, theme)
        renderer.render(model.start_step_index)

        # 渲染标题
        if show_title and theme.style.show_title:
            title = (
                f"n={n} ratio: {config.a} {config.b} "
                f"{config.c} {config.d} ({config.step_length})"
            )
            canvas.draw_text(
                Point(layout.window_width / 2, 5 * scale),
                title,
                min(int(LayoutConstants.TITLE_FONT_SIZE_FACTOR * scale), 
                    LayoutConstants.FONT_SIZE_MAX),
                theme.colors.text_black,
                face="courier",
            )

        # 渲染颜色序列
        if show_sequence:
            seq_renderer = SequenceRenderer(canvas, config, layout.window_width, theme)
            seq_renderer.render(
                model.color_sequence,
                model.start_step_index,
                layout.stair_height - LayoutConstants.SEQUENCE_VERTICAL_OFFSET * scale,
                scale,
                show_decimal=True,
            )
    
    @staticmethod
    def render_to_window(
        window: GraphWin,
        config: StaircaseConfig,
        model: StaircaseModel,
        layout: LayoutInfo,
        theme: Theme,
        n: int,
        scale: float = 1.0,
    ) -> None:
        """
        渲染楼梯到窗口
        
        Args:
            window: 目标窗口
            config: 楼梯配置
            model: 楼梯模型
            layout: 布局信息
            theme: 主题
            n: 楼梯序号
            scale: 缩放因子
        """
        canvas = GraphicsCanvas(window)
        transform = GeometryTransform(layout.zoom, layout.offset_x, layout.offset_y)
        
        RenderingService.render_to_canvas(
            canvas, transform, config, model, layout, theme, n, scale
        )
    
    @staticmethod
    def export_to_file(
        config: StaircaseConfig,
        model: StaircaseModel,
        theme: Theme,
        n: int,
        scale: float,
        file_path: str,
    ) -> None:
        """
        导出楼梯到图片文件
        
        Args:
            config: 楼梯配置
            model: 楼梯模型
            theme: 主题
            n: 楼梯序号
            scale: 缩放因子
            file_path: 输出文件路径
        """
        layout = RenderingService.calculate_layout(config, scale)
        
        # 创建临时窗口
        export_win = GraphWin(
            "Exporting...",
            int(layout.window_width),
            int(layout.window_height),
        )
        
        # 渲染
        RenderingService.render_to_window(
            export_win, config, model, layout, theme, n, scale
        )
        
        # 确保渲染完成
        export_win.update()
        time.sleep(0.1)
        
        # 导出
        ImageExporter.save_as_png(export_win, file_path)
        
        # 关闭临时窗口
        export_win.close()
