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
from core.theme import Theme, RGB
from core.index_converter import IndexConverter
from ui.kivy_layout import MainScreen
from rendering.canvas import DrawHandle

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
        
        # 高亮相关状态
        self._current_transform: GeometryTransform | None = None
        self._current_kivy_canvas = None  # KivyCanvas
        self._current_highlight: DrawHandle | None = None
    
    def build(self):
        """构建应用 UI"""
        # 设置窗口大小（放大2倍）
        Window.size = (2000, 1400)
        Window.minimum_width = 1200
        Window.minimum_height = 1000
        
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
        
        # 获取平台配置
        from core.platform_config import get_platform_config
        platform_config = get_platform_config()
        
        # 计算基础布局
        base_layout = calculate_layout(config, 1.0)
        
        # 使用平台配置的缩放因子
        scale_factor = platform_config.preview_scale_factor
        
        # 使用缩放重新计算布局
        layout = calculate_layout(config, scale_factor)
        
        # 获取 Kivy 画布适配器
        from rendering.kivy_canvas import KivyCanvas
        kivy_canvas = KivyCanvas(staircase_widget, widget_height)
        
        # 估算数列区域高度（根据总步数）
        total_steps = config.total_steps
        seq_rows = (total_steps // 10) + 1  # 每行约10个
        seq_height = seq_rows * 40 * scale_factor  # 每行高度约40px
        
        # 楼梯和数列的总高度（作为整体）
        total_content_height = layout.stair_height + 50 + seq_height  # 50是间距
        
        # 计算偏移：将楼梯+数列整体在widget中居中
        center_offset_x = (widget_width - layout.window_width) / 2
        center_offset_y = (widget_height - total_content_height) / 2
        
        # 确保偏移不为负，至少距离顶部50px，并整体左移50px
        center_offset_x = max(0, center_offset_x) - 50
        center_offset_y = max(50, center_offset_y)
        
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
        
        # 渲染数列 - 在楼梯下方，水平居中后左移100px
        from rendering.sequence import SequenceRenderer
        seq_renderer = SequenceRenderer(
            kivy_canvas, config, widget_width, self._state.theme, x_offset=center_offset_x - 100
        )
        # 数列起始 Y 坐标（楼梯下方，上移100px）
        seq_start_y = layout.stair_height + center_offset_y + 50 - 100
        seq_renderer.render(
            model.color_sequence,
            model.start_step_index,
            seq_start_y,
            scale_factor,
            show_decimal=True,
        )
        
        # 保存高亮所需的状态
        self._current_transform = transform
        self._current_kivy_canvas = kivy_canvas
        self._current_highlight = None  # 清除旧高亮
        
        # 初始化步进控制面板数据
        self._main_screen.control_panel.set_step_data(
            total=config.total_steps,
            start_index=model.walking_order_start,
            color_sequence=model.walking_order_colors,
            on_change=self._handle_step_change,
        )
        
        # 打印信息
        logger.info(
            f"Penrose-Staircase Nr. {self._state.n}: "
            f"{config.a} {config.b} {config.c} {config.d} ({config.step_length}) "
            f"scale={scale_factor:.2f}"
        )
    
    def _handle_step_change(self, walking_index: int) -> None:
        """处理步进位置变化，高亮当前台阶"""
        model = self._state.cached_model
        config = self._state.cached_config
        
        if not model or not config:
            return
        
        if not self._current_transform or not self._current_kivy_canvas:
            return
        
        # 打印步进信息
        color = 1 if model.walking_order_colors[walking_index] else 0
        logger.info(f"[步进] 位置: {walking_index + 1}/{config.total_steps}, 颜色: {color}")
        
        # 清除旧高亮
        if self._current_highlight:
            try:
                self._current_highlight.undraw()
            except Exception:
                pass
            self._current_highlight = None
        
        # 转换索引（行走顺序 -> 绘制顺序）
        draw_index = IndexConverter.walking_to_draw(walking_index, config)
        step_pos = model.get_step_position(draw_index)
        
        if not step_pos:
            logger.warning(f"未找到绘制索引 {draw_index} 的台阶位置")
            return
        
        # 将模型坐标转换为屏幕坐标
        screen_points = [
            self._current_transform.to_screen(p[0], -p[1])
            for p in [step_pos.p1, step_pos.p2, step_pos.p3, step_pos.p4]
        ]
        
        # 绘制高亮边框（亮青色）
        highlight_color = RGB(0, 255, 255)
        self._current_highlight = self._current_kivy_canvas.draw_polygon_outline(
            screen_points, highlight_color, width=3
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
