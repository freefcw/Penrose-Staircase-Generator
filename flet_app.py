"""
Flet 应用主模块 - Penrose 楼梯生成器的 Flet 版本

使用 Flet 框架替代 Kivy 实现现代化 UI
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

import flet as ft

from core.config import AppConfig
from core.geometry import GeometryTransform
from core.services.state_manager import StateManager
from core.layout import LayoutInfo, calculate_layout_from_config
from core.theme import Theme, RGB
from core.index_converter import IndexConverter
from ui.flet_layout import create_main_layout, ControlPanel, StaircaseCanvas
from rendering.flet_canvas import FletCanvas
from rendering.canvas import DrawHandle

if TYPE_CHECKING:
    from core.staircase import StaircaseConfig, StaircaseModel

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class RenderContext:
    """渲染上下文，封装渲染所需的所有状态"""
    layout: LayoutInfo
    scale_factor: float
    transform: GeometryTransform
    flet_canvas: FletCanvas
    canvas_width: float
    canvas_height: float
    center_offset_x: float
    center_offset_y: float


class PenroseFletApp:
    """
    Penrose 楼梯生成器 Flet 应用
    
    职责：
    - 管理应用生命周期
    - 协调状态管理和渲染
    - 处理 UI 交互
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        
        # 初始化状态管理器
        self._state = StateManager(
            n=config.n,
            theme=config.theme,
            export_scale=config.scale,
        )
        
        # UI 引用
        self._page: ft.Page | None = None
        self._control_panel: ControlPanel | None = None
        self._staircase_canvas: StaircaseCanvas | None = None
        
        # 高亮相关状态
        self._current_transform: GeometryTransform | None = None
        self._current_flet_canvas: FletCanvas | None = None
        self._current_highlight: DrawHandle | None = None
    
    def main(self, page: ft.Page) -> None:
        """Flet 应用入口"""
        self._page = page
        
        # 设置页面属性
        page.title = "Penrose Staircase Generator"
        page.window.width = 1000
        page.window.height = 700
        page.window.min_width = 600
        page.window.min_height = 500
        page.padding = 0
        page.spacing = 0
        
        # 创建主布局
        main_layout, self._control_panel, self._staircase_canvas = create_main_layout(
            on_generate=self._handle_generate,
            on_apply=self._handle_apply,
            on_export=self._handle_export,
            on_export_config=self._handle_export_config,
            on_import_config=self._handle_import_config,
        )
        
        page.add(main_layout)
        
        # 确保布局完成后再渲染
        page.update()
        self._render_staircase()
        page.update()
    
    def _on_page_resize(self, e) -> None:
        """页面尺寸变化时重新渲染"""
        # 可选：实现响应式重渲染
        pass
    
    # === 渲染方法 ===
    
    def _render_staircase(self) -> None:
        """渲染楼梯到画布（协调方法）"""
        if not self._staircase_canvas or not self._page:
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
        
        # 更新画布显示
        self._staircase_canvas.update_canvas()
        
        # 保存高亮所需的状态
        self._current_transform = ctx.transform
        self._current_flet_canvas = ctx.flet_canvas
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
        if not self._staircase_canvas or not self._page:
            return None
        
        self._staircase_canvas.clear_drawing()
        
        # 获取画布尺寸（使用页面尺寸估算）
        canvas_width = (self._page.window.width or 1000) - 280  # 减去控制面板宽度
        canvas_height = (self._page.window.height or 700) - 40  # 减去边距
        
        # 获取平台配置
        from core.platform_config import get_platform_config
        platform_config = get_platform_config()
        # 楼梯缩小 1.5 倍
        scale_factor = platform_config.preview_scale_factor / 1.5
        
        # 计算布局
        layout = calculate_layout_from_config(config, scale_factor)
        
        # 创建 Flet 画布适配器
        flet_canvas = self._staircase_canvas.get_canvas_adapter(canvas_width, canvas_height)
        
        # 估算序列区域高度
        total_steps = config.total_steps
        seq_rows = (total_steps // 10) + 1
        seq_height = seq_rows * 40 * scale_factor
        
        # 计算居中偏移（往右移动 50px）
        total_content_height = layout.stair_height + 50 + seq_height
        center_offset_x = max(0, (canvas_width - layout.window_width) / 2)
        center_offset_y = max(50, (canvas_height - total_content_height) / 2)  # 恢复原位置
        
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
            flet_canvas=flet_canvas,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            center_offset_x=center_offset_x,
            center_offset_y=center_offset_y,
        )
    
    def _draw_staircase(
        self, ctx: RenderContext, config: "StaircaseConfig", model: "StaircaseModel"
    ) -> None:
        """绘制楼梯"""
        from rendering.renderer import StaircaseRenderer
        
        renderer = StaircaseRenderer(
            canvas=ctx.flet_canvas,
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
        
        logger.info(f"开始绘制序列, 形状数量前: {len(ctx.flet_canvas.get_shapes())}")
        
        seq_renderer = SequenceRenderer(
            ctx.flet_canvas,
            config,
            ctx.canvas_width,
            self._state.theme,
            x_offset=0  # 居中显示
        )
        
        # 数列紧接在楼梯下方显示（楼梯缩小后调整位置）
        seq_start_y = ctx.canvas_height * 0.60 + 100 # 调整到 60%（继续下移） 
        # 数列缩放因子也缩小 1.5 倍
        seq_scale = ctx.scale_factor / 1.5
        logger.info(f"序列起始Y: {seq_start_y}, 颜色数量: {len(model.color_sequence)}, 画布高度: {ctx.canvas_height}")
        
        seq_renderer.render(
            model.color_sequence,
            model.start_step_index,
            seq_start_y,
            seq_scale,
            show_decimal=True,
        )
        
        logger.info(f"序列绘制完成, 形状数量后: {len(ctx.flet_canvas.get_shapes())}")
    
    def _init_step_panel(
        self, config: "StaircaseConfig", model: "StaircaseModel"
    ) -> None:
        """初始化步进控制面板"""
        if not self._control_panel:
            return
        
        self._control_panel.set_step_data(
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
        
        if not self._current_transform or not self._current_flet_canvas:
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
        self._current_highlight = self._current_flet_canvas.draw_polygon_outline(
            screen_points, highlight_color, width=3
        )
        
        # 更新画布
        if self._staircase_canvas:
            self._staircase_canvas.update_canvas()
    
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
        """处理导出按钮回调 - 使用 Pillow 渲染并保存 PNG"""
        model = self._state.cached_model
        config = self._state.cached_config
        
        if model is None or config is None:
            logger.warning("没有可导出的数据")
            if self._control_panel:
                self._control_panel.set_status("导出失败: 请先生成楼梯")
            return
        
        from rendering.pillow_canvas import PillowCanvas
        from core.geometry import GeometryTransform
        from core.layout import calculate_layout_from_config
        from rendering.renderer import StaircaseRenderer
        from rendering.sequence import SequenceRenderer
        
        # 使用较大的缩放因子导出高质量图片
        export_scale = 3.0
        layout = calculate_layout_from_config(config, export_scale)
        
        # 创建 Pillow 画布
        canvas_width = int(layout.window_width)
        canvas_height = int(layout.window_height + 200)  # 额外空间给序列
        pillow_canvas = PillowCanvas(canvas_width, canvas_height)
        
        # 创建几何变换器
        transform = GeometryTransform(
            layout.zoom,
            layout.offset_x,
            layout.offset_y
        )
        
        # 渲染楼梯
        renderer = StaircaseRenderer(
            canvas=pillow_canvas,
            transform=transform,
            config=config,
            model=model,
            theme=self._state.theme,
        )
        renderer.render(model.start_step_index)
        
        # 渲染序列
        seq_renderer = SequenceRenderer(
            pillow_canvas,
            config,
            canvas_width,
            self._state.theme,
            x_offset=0
        )
        seq_start_y = layout.stair_height + 30
        seq_renderer.render(
            model.color_sequence,
            model.start_step_index,
            seq_start_y,
            export_scale,
            show_decimal=True,
        )
        
        # 保存图片
        pillow_canvas.save(file_path)
        logger.info(f"导出完成: {file_path}")
        
        if self._control_panel:
            self._control_panel.set_status(f"已导出: {file_path}")
    
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
        
        session_config = ConfigExporter.import_from_file(file_path)
        if session_config is None:
            logger.error(f"导入配置失败: {file_path}")
            if self._control_panel:
                self._control_panel.set_status("导入失败: 配置文件无效")
            return
        
        # 更新状态
        self._state.update_n(session_config.n)
        self._state.update_theme(Theme.get_by_name(session_config.theme))
        
        # 使用导入的配置重新生成楼梯
        self._state.compute_and_cache()
        self._render_staircase()
        
        logger.info(f"配置已导入: {file_path}")


def run_flet_app(config: AppConfig) -> int:
    """运行 Flet 应用"""
    app = PenroseFletApp(config)
    # 使用 Web 模式便于调试
    ft.app(target=app.main, view=ft.AppView.WEB_BROWSER, port=8550)
    return 0
