"""
应用程序模块 - Penrose 楼梯生成器的主应用类

遵循单一职责原则，将 CLI 的职责拆分为：
- CLI：参数解析
- PenroseApp：应用程序协调
"""
from __future__ import annotations

import logging
import time

from graphics import GraphWin, GraphicsError

from core.calculator import PenroseCalculator, PenroseResult
from core.colors import ColorSequence
from core.config import AppConfig
from core.geometry import GeometryTransform, Point
from core.layout import LayoutConstants
from core.staircase import StaircaseConfig, StaircaseModel
from core.theme import Theme
from export.exporter import ImageExporter
from rendering.canvas import GraphicsCanvas
from rendering.renderer import StaircaseRenderer
from rendering.sequence import SequenceRenderer
from ui.control_panel import ControlPanel, PanelState

# 配置日志
logger = logging.getLogger(__name__)


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


class PenroseApp:
    """
    Penrose 楼梯生成器应用程序

    职责：
    - 协调楼梯计算、渲染和导出
    - 管理窗口生命周期
    - 集成控制面板实现交互式操作
    """

    # 事件循环间隔（毫秒）
    EVENT_LOOP_INTERVAL = 50

    def __init__(self, config: AppConfig):
        """
        初始化应用程序

        Args:
            config: 应用程序配置
        """
        self.config = config
        self._win: GraphWin | None = None
        self._control_panel: ControlPanel | None = None
        self._should_close = False
        
        # 当前状态
        self._current_n = config.n
        self._current_theme = config.theme
        self._current_scale = config.scale

    def run(self) -> int:
        """
        运行应用程序

        Returns:
            退出码，0 表示成功
        """
        # 非交互模式：直接渲染并导出
        if self.config.output_path:
            if not self._initial_render():
                return 1
            ImageExporter.save_as_png(self._win, self.config.output_path)
            self._cleanup()
            return 0

        # 交互模式：先弹出控制面板
        self._create_control_panel()
        
        # 进入事件循环（主窗口会在点击应用后创建）
        self._event_loop()

        # 清理
        self._cleanup()
        return 0

    def _initial_render(self) -> bool:
        """执行初始渲染"""
        stair_config = self._calculate_staircase()
        if stair_config is None:
            return False

        layout = self._calculate_layout(stair_config)
        self._print_info(stair_config)

        # 创建窗口和画布
        self._win = self._create_window(layout)

        # 渲染
        self._do_render(stair_config, layout)
        return True

    def _create_control_panel(self) -> None:
        """创建控制面板"""
        initial_state = PanelState(
            n=self._current_n,
            theme=self._current_theme.name.value,
            scale=self._current_scale,
        )

        self._control_panel = ControlPanel(
            initial_state=initial_state,
            on_apply=self._handle_apply,
            on_export=self._handle_export,
            on_close=self._handle_close,
        )
        self._control_panel.show()

    def _event_loop(self) -> None:
        """事件循环 - 处理用户交互"""
        while not self._should_close:
            # 检查主窗口是否关闭（只在窗口存在时检查）
            if self._win is not None and self._win.isClosed():
                break

            # 检查键盘事件（只在窗口存在时检查）
            if self._win is not None:
                try:
                    key = self._win.checkKey()
                    if key and key.lower() == 'q':
                        break
                except GraphicsError:
                    break

            # 更新控制面板
            if self._control_panel:
                self._control_panel.update()
                if self._control_panel.is_closed():
                    break

            # 避免 CPU 占用过高
            time.sleep(self.EVENT_LOOP_INTERVAL / 1000.0)

    def _handle_apply(self, state: PanelState) -> None:
        """处理应用按钮回调"""
        # 更新状态
        self._current_n = state.n
        self._current_theme = Theme.get_by_name(state.theme)
        self._current_scale = state.scale
        
        # 调试输出
        print(f"[DEBUG] 应用: n={state.n}, theme={state.theme}, scale={state.scale} -> {self._current_theme.name.value}")

        # 重新渲染
        self._redraw()

    def _handle_export(self, file_path: str) -> None:
        """处理导出按钮回调"""
        if self._win:
            ImageExporter.save_as_png(self._win, file_path)

    def _handle_close(self) -> None:
        """处理关闭按钮回调"""
        self._should_close = True

    def _redraw(self) -> None:
        """重新计算并渲染"""
        stair_config = self._calculate_staircase()
        if stair_config is None:
            return

        layout = self._calculate_layout(stair_config)

        # 关闭旧窗口，创建新窗口
        if self._win and not self._win.isClosed():
            self._win.close()

        self._win = self._create_window(layout)
        self._do_render(stair_config, layout)
        self._print_info(stair_config)

    def _do_render(self, stair_config: StaircaseConfig, layout: LayoutInfo) -> None:
        """执行实际渲染"""
        if not self._win:
            return

        canvas = GraphicsCanvas(self._win)
        transform = GeometryTransform(layout.zoom, layout.offset_x, layout.offset_y)
        model = self._create_model(stair_config)

        self._render(canvas, transform, stair_config, model, layout)

    def _cleanup(self) -> None:
        """清理资源"""
        if self._win and not self._win.isClosed():
            self._win.close()

    def _calculate_staircase(self) -> StaircaseConfig | None:
        """计算楼梯参数"""
        try:
            result = PenroseCalculator.calculate(self._current_n)
            return result.to_config()
        except ValueError as e:
            print(f"错误: {e}")
            return None

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
        scale = self._current_scale

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
            f"The Penrose-Staircase Nr. {self._current_n} is: "
            f"{stair_config.a} {stair_config.b} {stair_config.c} {stair_config.d} "
            f"({stair_config.step_length}) "
            f"缩放: {self._current_scale}x 主题: {self._current_theme.name.value}"
        )

    def _create_window(self, layout: LayoutInfo) -> GraphWin:
        """创建窗口"""
        return GraphWin(
            f"Penrose-Staircase N={self._current_n}",
            int(layout.window_width),
            int(layout.window_height),
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
        theme = self._current_theme
        scale = self._current_scale

        # 渲染楼梯
        renderer = StaircaseRenderer(canvas, transform, stair_config, model, theme)
        renderer.render(model.start_step_index)

        # 渲染标题（根据主题样式）
        if theme.style.show_title:
            title = (
                f"n={self._current_n} ratio: {stair_config.a} {stair_config.b} "
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
