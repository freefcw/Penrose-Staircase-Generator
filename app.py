"""
应用程序模块 - Penrose 楼梯生成器的主应用类

遵循单一职责原则，将 CLI 的职责拆分为：
- CLI：参数解析
- PenroseApp：应用程序协调
"""
from __future__ import annotations

import logging

from typing import TYPE_CHECKING  # pyright: ignore[reportUnusedImport]

from graphics import GraphWin, GraphicsError

import pstairs
from core.colors import ColorSequence
from core.config import AppConfig
from core.geometry import GeometryTransform, Point
from core.layout import LayoutConstants
from core.staircase import StaircaseConfig, StaircaseModel
from export.exporter import ImageExporter
from rendering.canvas import GraphicsCanvas
from rendering.renderer import StaircaseRenderer
from rendering.sequence import SequenceRenderer

# 配置日志
logger = logging.getLogger(__name__)


class PenroseApp:
    """
    Penrose 楼梯生成器应用程序

    职责：
    - 协调楼梯计算、渲染和导出
    - 管理窗口生命周期
    """

    def __init__(self, config: AppConfig):
        """
        初始化应用程序

        Args:
            config: 应用程序配置
        """
        self.config = config
        self._win: GraphWin | None = None

    def run(self) -> int:
        """
        运行应用程序

        Returns:
            退出码，0 表示成功
        """
        # 计算楼梯参数
        stair_config, ps_result = self._calculate_staircase()
        if stair_config is None:
            return 1

        # 计算窗口尺寸
        layout = self._calculate_layout(stair_config)

        # 输出信息
        self._print_info(stair_config)

        # 创建窗口和画布
        self._win = self._create_window(layout)
        canvas = GraphicsCanvas(self._win)

        # 创建变换器
        transform = GeometryTransform(layout.zoom, layout.offset_x, layout.offset_y)

        # 创建并渲染模型
        model = self._create_model(stair_config)
        self._render(canvas, transform, stair_config, model, layout)

        # 导出（如果指定了输出路径）
        if self.config.output_path:
            ImageExporter.save_as_png(self._win, self.config.output_path)

        # 等待用户交互
        self._wait_for_close()

        return 0

    def _calculate_staircase(self) -> tuple[StaircaseConfig | None, object]:
        """计算楼梯参数"""
        try:
            ps = pstairs.PenroseStaircase(self.config.n)
            config = StaircaseConfig(ps.a, ps.b, ps.c, ps.d, ps.l)
            return config, ps
        except Exception as e:
            print(f"错误: 无法计算第 {self.config.n} 个Penrose楼梯: {e}")
            return None, None

    def _calculate_layout(self, stair_config: StaircaseConfig) -> LayoutInfo:
        """计算窗口布局"""
        A, B, C, D, L = (
            stair_config.a,
            stair_config.b,
            stair_config.c,
            stair_config.d,
            stair_config.step_length,
        )
        H = GeometryTransform.UNIT_HEIGHT
        scale = self.config.scale

        # 缩放因子
        zoom = LayoutConstants.ZOOM_BASE / (
            (A + B + C + D + L - 4) * LayoutConstants.ZOOM_DIVISOR
        ) * scale

        # 窗口尺寸
        window_width = (A * L + B * L) * zoom
        stair_height = (A * H * L + B * H * L) * zoom

        # 序列显示区域高度
        total_steps = stair_config.total_steps
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

    def _print_info(self, stair_config: StaircaseConfig) -> None:
        """打印楼梯信息"""
        print(
            f"The Penrose-Staircase Nr. {self.config.n} is: "
            f"{stair_config.a} {stair_config.b} {stair_config.c} {stair_config.d} "
            f"({stair_config.step_length}) "
            f"缩放: {self.config.scale}x 主题: {self.config.theme.name.value}"
        )

    def _create_window(self, layout: LayoutInfo) -> GraphWin:
        """创建窗口"""
        return GraphWin(
            "Penrose-Staircase Generator v2.0",
            layout.window_width,
            layout.window_height,
        )

    def _create_model(self, stair_config: StaircaseConfig) -> StaircaseModel:
        """创建楼梯模型"""
        model = StaircaseModel(stair_config)

        # 生成颜色序列
        color_gen = ColorSequence(stair_config.total_steps)
        model.color_sequence = color_gen.generate()
        model.start_step_index = color_gen.start_index

        if self.config.debug:
            logger.debug(
                "总台阶数: %d (A=%d, D=%d, B=%d, C=%d)",
                stair_config.total_steps,
                stair_config.a - 1,
                stair_config.d - 1,
                stair_config.b - 1,
                stair_config.c - 1,
            )
            logger.debug("起点索引(绘制顺序): %d", model.start_step_index)
            logger.debug(
                "颜色序列(绘制顺序): %s",
                [1 if c else 0 for c in model.color_sequence],
            )

        return model

    def _render(
        self,
        canvas: GraphicsCanvas,
        transform: GeometryTransform,
        stair_config: StaircaseConfig,
        model: StaircaseModel,
        layout: LayoutInfo,
    ) -> None:
        """渲染楼梯和序列"""
        theme = self.config.theme
        scale = self.config.scale

        # 渲染楼梯
        renderer = StaircaseRenderer(canvas, transform, stair_config, model, theme)
        renderer.render(model.start_step_index)

        # 渲染标题（根据主题样式）
        if theme.style.show_title:
            title = (
                f"n={self.config.n} ratio: {stair_config.a} {stair_config.b} "
                f"{stair_config.c} {stair_config.d} ({stair_config.step_length})"
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
        seq_renderer = SequenceRenderer(canvas, stair_config, layout.window_width, theme)
        seq_renderer.render(
            model.color_sequence,
            model.start_step_index,
            layout.stair_height - LayoutConstants.SEQUENCE_VERTICAL_OFFSET * scale,
            scale,
            show_decimal=True,
        )

    def _wait_for_close(self) -> None:
        """等待用户关闭窗口"""
        if self._win:
            try:
                self._win.getMouse()
            except GraphicsError:
                pass
            self._win.close()


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
