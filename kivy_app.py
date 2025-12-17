"""
Kivy 应用主模块 - Penrose 楼梯生成器的 Kivy 版本

使用 Kivy 框架替代 Tkinter/graphics.py 实现 UI

注意：此模块完全避免导入任何 Tkinter/graphics.py 相关模块，
以防止 Kivy (SDL2) 与 Tkinter 在 macOS 上的冲突。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock

from core.config import AppConfig
from core.geometry import GeometryTransform
from core.services.state_manager import StateManager
from core.layout import LayoutConstants
from core.staircase import StaircaseConfig
from core.theme import Theme
from ui.kivy_layout import MainScreen

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class LayoutInfo:
    """窗口布局信息（本地定义，避免导入 RenderingService）"""
    window_width: float
    window_height: float
    stair_height: float
    zoom: float
    offset_x: float
    offset_y: float


def calculate_layout(config: StaircaseConfig, scale: float = 1.0) -> LayoutInfo:
    """
    计算窗口布局（本地实现，避免导入 RenderingService）
    """
    A, B, C, D, L = config.a, config.b, config.c, config.d, config.step_length
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


class PenroseKivyApp(App):
    """
    Penrose 楼梯生成器 Kivy 应用
    
    职责：
    - 管理应用生命周期
    - 协调状态管理和渲染
    - 处理 UI 交互
    """
    
    title = 'Penrose Staircase Generator'
    
    def __init__(self, config: AppConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        
        # 初始化状态管理器
        self._state = StateManager(
            n=config.n,
            theme=config.theme,
            export_scale=config.scale,
        )
        
        # UI 引用
        self._main_screen: MainScreen | None = None
    
    def build(self):
        """构建应用 UI"""
        # 设置窗口大小
        Window.size = (1000, 700)
        Window.minimum_width = 600
        Window.minimum_height = 500
        
        # 创建主界面
        self._main_screen = MainScreen(
            on_generate=self._handle_generate,
            on_export=self._handle_export,
        )
        
        # 延迟渲染，等待 widget 尺寸确定
        Clock.schedule_once(lambda dt: self._render_staircase(), 0.1)
        
        return self._main_screen
    
    def _render_staircase(self) -> None:
        """渲染楼梯到画布"""
        if not self._main_screen:
            return
        
        # 获取或计算数据
        data = self._state.get_or_compute()
        if data is None:
            logger.error("无法计算楼梯数据")
            return
        
        config, model = data
        
        # 清除旧绘图
        staircase_widget = self._main_screen.staircase_widget
        staircase_widget.clear_drawing()
        
        # 获取实际 widget 尺寸
        widget_width = staircase_widget.width
        widget_height = staircase_widget.height
        
        # 计算基础布局
        base_layout = calculate_layout(config, 1.0)
        
        # 固定缩放因子为 3
        scale_factor = 3.0
        
        # 使用固定缩放重新计算布局
        layout = calculate_layout(config, scale_factor)
        
        # 获取 Kivy 画布适配器
        from rendering.kivy_canvas import KivyCanvas
        kivy_canvas = KivyCanvas(staircase_widget, widget_height)
        
        # 计算偏移：楼梯右移 250px，上移减少留白
        center_offset_x = (widget_width - layout.window_width) / 2 + 400  # 右移 250px
        center_offset_y = 10  # 减少顶部留白
        
        # 创建几何变换器（添加偏移）
        transform = GeometryTransform(
            layout.zoom, 
            layout.offset_x + center_offset_x, 
            layout.offset_y + center_offset_y
        )
        
        # 使用渲染器绘制楼梯
        from rendering.renderer import StaircaseRenderer
        renderer = StaircaseRenderer(
            canvas=kivy_canvas,
            transform=transform,
            config=config,
            model=model,
            theme=self._state.theme,
        )
        renderer.render(model.start_step_index)
        
        # 渲染数列
        from rendering.sequence import SequenceRenderer
        seq_renderer = SequenceRenderer(
            kivy_canvas, config, widget_width, self._state.theme, x_offset=400
        )
        # 数列起始 Y 坐标（楼梯下方，减少间距）
        seq_start_y = layout.stair_height + center_offset_y + 10  # 从 30 改为 10
        seq_renderer.render(
            model.color_sequence,
            model.start_step_index,
            seq_start_y,
            scale_factor,
            show_decimal=True,
        )
        
        # 打印信息
        logger.info(
            f"Penrose-Staircase Nr. {self._state.n}: "
            f"{config.a} {config.b} {config.c} {config.d} ({config.step_length}) "
            f"scale={scale_factor:.2f}"
        )
    
    def _handle_generate(self, n: int, theme_name: str, scale: float) -> None:
        """处理生成按钮回调"""
        # 更新状态
        self._state.update_n(n)
        self._state.update_theme(Theme.get_by_name(theme_name))
        self._state.update_export_scale(scale)
        
        # 重新计算并渲染
        self._state.compute_and_cache()
        self._render_staircase()
        
        logger.info(f"生成完成: n={n}, theme={theme_name}, scale={scale}")
    
    def _handle_export(self, file_path: str) -> None:
        """处理导出按钮回调"""
        if not self._main_screen:
            return
        
        # 使用 Kivy 的截图功能
        staircase_widget = self._main_screen.staircase_widget
        staircase_widget.export_to_png(file_path)
        
        logger.info(f"导出完成: {file_path}")


def run_kivy_app(config: AppConfig) -> int:
    """运行 Kivy 应用"""
    app = PenroseKivyApp(config)
    app.run()
    return 0
