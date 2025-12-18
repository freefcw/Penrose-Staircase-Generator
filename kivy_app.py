"""
Kivy 应用主模块 - Penrose 楼梯生成器的 Kivy 版本

使用 Kivy 框架替代 Tkinter/graphics.py 实现 UI

注意：此模块完全避免导入任何 Tkinter/graphics.py 相关模块，
以防止 Kivy (SDL2) 与 Tkinter 在 macOS 上的冲突。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock

from core.config import AppConfig
from core.geometry import GeometryTransform
from core.services.state_manager import StateManager
from core.layout import LayoutInfo, calculate_layout_from_config
from core.theme import Theme, RGB
from core.index_converter import IndexConverter
from ui.kivy_layout import MainScreen
from rendering.canvas import DrawHandle

if TYPE_CHECKING:
    from core.staircase import StaircaseConfig, StaircaseModel
    from rendering.kivy_canvas import KivyCanvas

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class RenderContext:
    """渲染上下文，封装渲染所需的所有状态"""
    layout: LayoutInfo
    scale_factor: float
    transform: GeometryTransform
    kivy_canvas: "KivyCanvas"
    widget_width: float
    widget_height: float
    center_offset_x: float
    center_offset_y: float


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
        self._current_kivy_canvas: "KivyCanvas | None" = None
        self._current_highlight: DrawHandle | None = None
    
    def build(self):
        """构建应用 UI"""
        # 设置窗口大小（原来的一半）
        Window.size = (1000, 700)
        Window.minimum_width = 600
        Window.minimum_height = 500
        
        # 创建主界面
        self._main_screen = MainScreen(
            on_generate=self._handle_generate,
            on_apply=self._handle_apply,
            on_export=self._handle_export,
            on_export_config=self._handle_export_config,
            on_import_config=self._handle_import_config,
        )
        
        # 延迟渲染，等待 widget 尺寸确定
        Clock.schedule_once(lambda dt: self._render_staircase(), 0.1)
        
        return self._main_screen
    
    # === 渲染方法 ===
    
    def _render_staircase(self) -> None:
        """渲染楼梯到画布（协调方法）"""
        if not self._main_screen:
            return
        
        # 获取或计算数据
        data = self._state.get_or_compute()
        if data is None:
            logger.error("无法计算楼梯数据")
            return
        
        config, model = data
        
        # 准备渲染上下文
        ctx = self._prepare_render_context(config)
        if ctx is None:
            return
        
        # 绘制楼梯
        self._draw_staircase(ctx, config, model)
        
        # 绘制序列
        self._draw_sequence(ctx, config, model)
        
        # 保存高亮所需的状态
        self._current_transform = ctx.transform
        self._current_kivy_canvas = ctx.kivy_canvas
        self._current_highlight = None
        
        # 初始化步进面板
        self._init_step_panel(config, model)
        
        # 打印信息
        logger.info(
            f"Penrose-Staircase Nr. {self._state.n}: "
            f"{config.a} {config.b} {config.c} {config.d} ({config.step_length}) "
            f"scale={ctx.scale_factor:.2f}"
        )
    
    def _prepare_render_context(self, config: "StaircaseConfig") -> RenderContext | None:
        """准备渲染上下文：计算布局和创建画布"""
        if not self._main_screen:
            return None
        
        staircase_widget = self._main_screen.staircase_widget
        staircase_widget.clear_drawing()
        
        # 获取 widget 尺寸
        widget_width = staircase_widget.width
        widget_height = staircase_widget.height
        
        # 获取平台配置
        from core.platform_config import get_platform_config
        platform_config = get_platform_config()
        scale_factor = platform_config.preview_scale_factor
        
        # 计算布局
        layout = calculate_layout_from_config(config, scale_factor)
        
        # 创建 Kivy 画布适配器
        from rendering.kivy_canvas import KivyCanvas
        kivy_canvas = KivyCanvas(staircase_widget, widget_height)
        
        # 估算序列区域高度
        total_steps = config.total_steps
        seq_rows = (total_steps // 10) + 1
        seq_height = seq_rows * 40 * scale_factor
        
        # 计算居中偏移
        total_content_height = layout.stair_height + 50 + seq_height
        center_offset_x = max(0, (widget_width - layout.window_width) / 2) - 50
        center_offset_y = max(50, (widget_height - total_content_height) / 2)
        
        # 创建几何变换器
        transform = GeometryTransform(
            layout.zoom,
            layout.offset_x + center_offset_x,
            layout.offset_y + center_offset_y
        )
        
        return RenderContext(
            layout=layout,
            scale_factor=scale_factor,
            transform=transform,
            kivy_canvas=kivy_canvas,
            widget_width=widget_width,
            widget_height=widget_height,
            center_offset_x=center_offset_x,
            center_offset_y=center_offset_y,
        )
    
    def _draw_staircase(
        self, ctx: RenderContext, config: "StaircaseConfig", model: "StaircaseModel"
    ) -> None:
        """绘制楼梯"""
        from rendering.renderer import StaircaseRenderer
        
        renderer = StaircaseRenderer(
            canvas=ctx.kivy_canvas,
            transform=ctx.transform,
            config=config,
            model=model,
            theme=self._state.theme,
        )
        renderer.render(model.start_step_index)
    
    def _draw_sequence(
        self, ctx: RenderContext, config: "StaircaseConfig", model: "StaircaseModel"
    ) -> None:
        """绘制颜色序列"""
        from rendering.sequence import SequenceRenderer
        
        seq_renderer = SequenceRenderer(
            ctx.kivy_canvas,
            config,
            ctx.widget_width,
            self._state.theme,
            x_offset=ctx.center_offset_x - 100
        )
        
        seq_start_y = ctx.layout.stair_height + ctx.center_offset_y
        seq_renderer.render(
            model.color_sequence,
            model.start_step_index,
            seq_start_y,
            ctx.scale_factor,
            show_decimal=True,
        )
    
    def _init_step_panel(
        self, config: "StaircaseConfig", model: "StaircaseModel"
    ) -> None:
        """初始化步进控制面板"""
        if not self._main_screen:
            return
        
        self._main_screen.control_panel.set_step_data(
            total=config.total_steps,
            start_index=model.walking_order_start,
            color_sequence=model.walking_order_colors,
            on_change=self._handle_step_change,
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
    
    def _handle_apply(self, theme_name: str, scale: float) -> None:
        """处理Apply按钮回调 - 实时应用主题和缩放（不重新生成数据）"""
        self._state.update_theme(Theme.get_by_name(theme_name))
        self._state.update_export_scale(scale)
        
        # 重新渲染（使用缓存数据）
        self._render_staircase()
        
        logger.info(f"已应用: theme={theme_name}, scale={scale}")
    
    def _handle_export_config(self, file_path: str) -> None:
        """处理导出配置回调"""
        model = self._state.cached_model
        config = self._state.cached_config
        if model is None or config is None:
            logger.warning("没有可导出的配置数据")
            return
        
        from core.config_io import SessionConfig, ConfigExporter
        
        session_config = SessionConfig(
            n=self._state.n,
            theme=self._state.theme.name.value,
            color_sequence=model.color_sequence,
            start_step_index=model.start_step_index,
            walking_order_colors=model.walking_order_colors,
            walking_order_start=model.walking_order_start,
            a=config.a,
            b=config.b,
            c=config.c,
            d=config.d,
            step_length=config.step_length,
        )
        ConfigExporter.export_to_file(session_config, file_path)
        logger.info(f"配置已导出: {file_path}")
    
    def _handle_import_config(self, file_path: str) -> None:
        """处理导入配置回调"""
        from core.config_io import ConfigExporter
        from core.staircase import StaircaseConfig, StaircaseModel
        
        session_config = ConfigExporter.import_from_file(file_path)
        if session_config is None:
            logger.warning(f"无法导入配置: {file_path}")
            return
        
        # 更新状态
        self._state.update_n(session_config.n)
        self._state.update_theme(Theme.get_by_name(session_config.theme))
        
        # 创建配置和模型
        config = StaircaseConfig(
            a=session_config.a,
            b=session_config.b,
            c=session_config.c,
            d=session_config.d,
            step_length=session_config.step_length,
        )
        model = StaircaseModel(config)
        model.color_sequence = session_config.color_sequence
        model.start_step_index = session_config.start_step_index
        model.walking_order_colors = session_config.walking_order_colors
        model.walking_order_start = session_config.walking_order_start
        
        # 设置缓存
        self._state._cached_config = config
        self._state._cached_model = model
        
        # 重新渲染
        self._render_staircase()
        
        logger.info(f"配置已导入: {file_path}")


def run_kivy_app(config: AppConfig) -> int:
    """运行 Kivy 应用"""
    app = PenroseKivyApp(config)
    app.run()
    return 0
