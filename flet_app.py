"""
Flet 应用主模块 - Penrose 楼梯生成器的 Flet 版本

职责：
- 管理应用生命周期
- 处理 UI 交互事件
- 协调服务调用
"""
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

import flet as ft

from core.config import AppConfig
from core.theme import Theme, RGB
from core.services.state_manager import StateManager
from core.index_converter import IndexConverter
from services.rendering_service import RenderingService
from services.export_service import ExportService
from ui.flet_layout import create_main_layout, ControlPanel, StaircaseCanvas
from rendering.canvas import DrawHandle

if TYPE_CHECKING:
    from core.render_context import RenderContext
    from core.staircase import StaircaseConfig, StaircaseModel

# 配置日志
logger = logging.getLogger(__name__)


class PenroseFletApp:
    """
    Penrose 楼梯生成器 Flet 应用
    
    采用服务分离架构：
    - RenderingService: 楼梯渲染
    - ExportService: 导出功能
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        
        # 初始化状态管理器
        self._state = StateManager(
            n=config.n,
            theme=config.theme,
            export_scale=config.scale,
        )
        
        # 初始化服务
        from core.platform_config import get_platform_config
        platform_config = get_platform_config()
        self._rendering_service = RenderingService(platform_config.preview_scale_factor)
        self._export_service = ExportService()
        
        # UI 引用
        self._page: ft.Page | None = None
        self._control_panel: ControlPanel | None = None
        self._staircase_canvas: StaircaseCanvas | None = None
        
        # 高亮相关状态
        self._current_ctx: RenderContext | None = None
        self._current_highlight: DrawHandle | None = None
        
        # 渲染防抖
        self._last_render_time: float = 0.0
        self._render_debounce_ms: float = 100.0  # 100ms 防抖
    
    def main(self, page: ft.Page) -> None:
        """Flet 应用入口"""
        self._page = page
        
        # 设置页面属性
        page.title = "Penrose Staircase Generator"
        page.window.width = 1000
        page.window.height = 800
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
        self._render_staircase(force=True)  # 首次渲染强制执行
        page.update()
    
    # === 渲染方法 ===
    
    def _render_staircase(self, force: bool = False) -> None:
        """渲染楼梯到画布"""
        if not self._staircase_canvas or not self._page:
            return
        
        # 防抖：跳过短时间内的重复渲染
        current_time = time.time() * 1000  # 转换为毫秒
        if not force and (current_time - self._last_render_time) < self._render_debounce_ms:
            return
        self._last_render_time = current_time
        
        # 获取或计算数据
        data = self._state.get_or_compute()
        if data is None:
            logger.error("无法计算楼梯数据")
            return
        
        config, model = data
        
        # 准备渲染上下文
        ctx = self._rendering_service.prepare_context(
            self._staircase_canvas,
            config,
            self._page.window.width or 1000,
            self._page.window.height or 700,
        )
        if ctx is None:
            return
        
        # 绘制楼梯和序列
        self._rendering_service.render_staircase(ctx, config, model, self._state.theme)
        self._rendering_service.render_sequence(ctx, config, model, self._state.theme)
        
        # 更新画布显示
        self._staircase_canvas.update_canvas()
        
        # 保存渲染上下文用于高亮
        self._current_ctx = ctx
        self._current_highlight = None
        
        # 初始化步进面板
        self._init_step_panel(config, model)
        
        logger.info(
            f"Penrose-Staircase Nr. {self._state.n}: "
            f"{config.a} {config.b} {config.c} {config.d} ({config.step_length}) "
            f"scale={ctx.scale_factor:.2f}"
        )
    
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
    
    # === 事件处理 ===
    
    def _handle_step_change(self, walking_index: int) -> None:
        """处理步进位置变化，高亮当前台阶"""
        model = self._state.cached_model
        config = self._state.cached_config
        
        if not model or not config or not self._current_ctx:
            return
        
        # 清除旧高亮
        if self._current_highlight:
            try:
                self._current_highlight.undraw()
            except Exception:
                pass
            self._current_highlight = None
        
        # 转换索引并获取台阶位置
        draw_index = IndexConverter.walking_to_draw(walking_index, config)
        step_pos = model.get_step_position(draw_index)
        
        if not step_pos:
            logger.warning(f"未找到绘制索引 {draw_index} 的台阶位置")
            return
        
        # 将模型坐标转换为屏幕坐标
        transform = self._current_ctx.transform
        screen_points = [
            transform.to_screen(p[0], -p[1])
            for p in [step_pos.p1, step_pos.p2, step_pos.p3, step_pos.p4]
        ]
        
        # 绘制高亮边框
        highlight_color = RGB(0, 255, 255)
        self._current_highlight = self._current_ctx.canvas.draw_polygon_outline(
            screen_points, highlight_color, width=3
        )
        
        if self._staircase_canvas:
            self._staircase_canvas.update_canvas()
    
    def _handle_generate(self, n: int, theme_name: str, scale: float) -> None:
        """处理生成按钮回调"""
        self._state.update_n(n)
        self._state.update_theme(Theme.get_by_name(theme_name))
        self._state.update_export_scale(scale)
        
        self._state.compute_and_cache()
        self._render_staircase(force=True)
        
        logger.info(f"生成完成: n={n}, theme={theme_name}, scale={scale}")
    
    def _handle_apply(self, theme_name: str, scale: float) -> None:
        """处理Apply按钮回调 - 实时应用主题和缩放"""
        self._state.update_theme(Theme.get_by_name(theme_name))
        self._state.update_export_scale(scale)
        self._render_staircase(force=True)
        logger.info(f"已应用: theme={theme_name}, scale={scale}")
    
    def _handle_export(self, file_path: str) -> None:
        """处理导出按钮回调"""
        model = self._state.cached_model
        config = self._state.cached_config
        
        if model is None or config is None:
            logger.warning("没有可导出的数据")
            if self._control_panel:
                self._control_panel.set_status("导出失败: 请先生成楼梯")
            return
        
        success = self._export_service.export_png(
            config, model, self._state.theme, file_path
        )
        
        if self._control_panel:
            status = f"已导出: {file_path}" if success else "导出失败"
            self._control_panel.set_status(status)
    
    def _handle_export_config(self, file_path: str) -> None:
        """处理导出配置回调"""
        model = self._state.cached_model
        config = self._state.cached_config
        
        if model is None or config is None:
            logger.warning("没有可导出的配置数据")
            return
        
        self._export_service.export_config(
            self._state.n,
            self._state.theme.name.value,
            config,
            model,
            file_path,
        )
    
    def _handle_import_config(self, file_path: str) -> None:
        """处理导入配置回调"""
        session_config = self._export_service.import_config(file_path)
        
        if session_config is None:
            if self._control_panel:
                self._control_panel.set_status("导入失败: 配置文件无效")
            return
        
        # 更新状态并重新渲染
        self._state.update_n(session_config.n)
        self._state.update_theme(Theme.get_by_name(session_config.theme))
        self._state.compute_and_cache()
        self._render_staircase(force=True)


def run_flet_app(config: AppConfig) -> int:
    """运行 Flet 应用"""
    app = PenroseFletApp(config)
    ft.app(target=app.main)
    return 0
