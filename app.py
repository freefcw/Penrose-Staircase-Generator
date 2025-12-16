"""
应用程序模块 - Penrose 楼梯生成器的主应用类

重构后的版本，将职责拆分为多个服务类：
- StateManager: 状态管理
- RenderingService: 渲染协调
- EventProcessor: 事件处理
"""
from __future__ import annotations

import logging

from graphics import GraphWin

from core.config import AppConfig
from core.geometry import GeometryTransform
from core.index_converter import IndexConverter
from core.platform_config import get_platform_config
from core.services.state_manager import StateManager
from core.services.rendering_service import RenderingService, LayoutInfo
from core.services.event_processor import EventProcessor
from core.theme import Theme
from export.exporter import ImageExporter
from ui.control_panel import ControlPanel, PanelState
from ui.highlight_manager import HighlightManager
from ui.step_panel import StepControlPanel

# 配置日志
logger = logging.getLogger(__name__)


class PenroseApp:
    """
    Penrose 楼梯生成器应用程序
    
    职责（重构后）：
    - 协调各服务完成功能
    - 管理 UI 面板的创建和回调
    - 管理窗口的创建和关闭
    
    已拆分的职责：
    - 状态管理 → StateManager
    - 渲染协调 → RenderingService
    - 事件处理 → EventProcessor
    """

    def __init__(self, config: AppConfig):
        """
        初始化应用程序
        
        Args:
            config: 应用程序配置
        """
        self.config = config
        
        # 初始化服务
        self._state = StateManager(
            n=config.n,
            theme=config.theme,
            export_scale=config.scale,
        )
        self._events = EventProcessor(on_close=self._cleanup)
        
        # UI 组件
        self._win: GraphWin | None = None
        self._control_panel: ControlPanel | None = None
        self._step_panel: StepControlPanel | None = None
        
        # 高亮管理器
        self._highlight_manager: HighlightManager | None = None

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
        
        # 进入事件循环
        self._run_event_loop()

        # 清理
        self._cleanup()
        return 0

    # === 初始化方法 ===

    def _initial_render(self) -> bool:
        """执行初始渲染"""
        data = self._state.compute_and_cache()
        if data is None:
            return False
        
        config, model = data
        layout = RenderingService.calculate_layout(config, self._state.preview_scale)
        self._print_info(config)

        # 创建窗口和渲染
        self._win = self._create_window(layout)
        RenderingService.render_to_window(
            self._win, config, model, layout,
            self._state.theme, self._state.n, self._state.preview_scale
        )
        
        # 创建高亮管理器
        transform = GeometryTransform(layout.zoom, layout.offset_x, layout.offset_y)
        self._highlight_manager = HighlightManager(self._win, transform)
        
        return True

    def _create_control_panel(self) -> None:
        """创建控制面板"""
        initial_state = PanelState(
            n=self._state.n,
            theme=self._state.theme.name.value,
            scale=self._state.export_scale,
        )

        self._control_panel = ControlPanel(
            initial_state=initial_state,
            on_save=self._handle_save,
            on_generate=self._handle_generate,
            on_export=self._handle_export,
            on_close=self._handle_close,
            on_export_config=self._handle_export_config,
            on_import_config=self._handle_import_config,
        )
        self._control_panel.show()

    # === 事件循环 ===

    def _run_event_loop(self) -> None:
        """运行事件循环"""
        updatables = []
        if self._control_panel:
            updatables.append(self._control_panel)
        
        self._events.run_loop(self._win, updatables)

    # === 回调处理 ===

    def _handle_save(self, state: PanelState) -> None:
        """处理保存按钮回调 - 仅保存设置，不刷新数据"""
        new_theme = Theme.get_by_name(state.theme)
        self._state.update_theme(new_theme)
        self._state.update_export_scale(state.scale)
        
        print(f"[DEBUG] 保存: theme={state.theme}, export_scale={state.scale}")

        # 如果已有窗口，使用新主题重新渲染
        if self._win and not self._win.isClosed():
            self._refresh_display()

    def _handle_generate(self, state: PanelState) -> None:
        """处理生成按钮回调 - 重新生成数据"""
        new_theme = Theme.get_by_name(state.theme)
        self._state.update_n(state.n)
        self._state.update_theme(new_theme)
        self._state.update_export_scale(state.scale)
        
        print(f"[DEBUG] 生成: n={state.n}, theme={state.theme}, export_scale={state.scale}")

        # 重新计算并渲染
        self._redraw()
        
        # 重新生成后，高亮会被清除
        if self._highlight_manager:
            self._highlight_manager.clear()
        
        # 创建/更新步进控制面板
        self._create_step_panel()

    def _handle_export(self, file_path: str) -> None:
        """处理导出按钮回调"""
        data = self._state.get_or_compute()
        if data is None:
            return
        
        config, model = data
        RenderingService.export_to_file(
            config, model, self._state.theme,
            self._state.n, self._state.export_scale, file_path
        )
        print(f"导出完成: {file_path} (缩放: {self._state.export_scale}x)")

    def _handle_close(self) -> None:
        """处理关闭按钮回调"""
        self._events.request_close()
    
    def _handle_export_config(self, file_path: str) -> None:
        """处理导出配置回调"""
        model = self._state.cached_model
        config = self._state.cached_config
        if model is None or config is None:
            print("[导出配置] 没有可导出的数据")
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
    
    def _handle_import_config(self, file_path: str) -> None:
        """处理导入配置回调"""
        from core.config_io import ConfigExporter
        from core.staircase import StaircaseConfig, StaircaseModel
        
        session_config = ConfigExporter.import_from_file(file_path)
        if session_config is None:
            return
        
        # 更新状态
        self._state.update_n(session_config.n)
        new_theme = Theme.get_by_name(session_config.theme)
        self._state.update_theme(new_theme)
        
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
        
        # 直接设置缓存
        self._state._cached_config = config
        self._state._cached_model = model
        
        # 重新渲染
        self._refresh_display()
        self._create_step_panel()
        
        print(f"[导入配置] 已加载: n={session_config.n}, 主题={session_config.theme}")

    # === 渲染方法 ===

    def _redraw(self) -> None:
        """重新计算并渲染"""
        data = self._state.compute_and_cache()
        if data is None:
            return

        config, model = data
        layout = RenderingService.calculate_layout(config, self._state.preview_scale)
        
        # 关闭旧窗口，创建新窗口
        if self._win and not self._win.isClosed():
            self._win.close()

        self._win = self._create_window(layout)
        RenderingService.render_to_window(
            self._win, config, model, layout,
            self._state.theme, self._state.n, self._state.preview_scale
        )
        self._print_info(config)
        
        # 创建/更新高亮管理器
        transform = GeometryTransform(layout.zoom, layout.offset_x, layout.offset_y)
        self._highlight_manager = HighlightManager(self._win, transform)
        
        # 恢复高亮状态
        self._restore_highlight()

    def _refresh_display(self) -> None:
        """仅刷新显示，不重新计算数据"""
        if not self._state.has_valid_cache():
            self._redraw()
            return
        
        config = self._state.cached_config
        model = self._state.cached_model
        if config is None or model is None:
            return
        
        layout = RenderingService.calculate_layout(config, self._state.preview_scale)

        # 关闭旧窗口，创建新窗口
        if self._win and not self._win.isClosed():
            self._win.close()

        self._win = self._create_window(layout)
        RenderingService.render_to_window(
            self._win, config, model, layout,
            self._state.theme, self._state.n, self._state.preview_scale
        )
        self._print_info(config)
        
        # 创建/更新高亮管理器
        transform = GeometryTransform(layout.zoom, layout.offset_x, layout.offset_y)
        self._highlight_manager = HighlightManager(self._win, transform)
        
        # 恢复高亮状态
        self._restore_highlight()

    # === 步进面板 ===

    def _create_step_panel(self) -> None:
        """创建步进控制面板"""
        model = self._state.cached_model
        if model is None:
            return
        
        parent = None
        if self._control_panel and hasattr(self._control_panel, '_root'):
            parent = self._control_panel._root
        
        self._step_panel = StepControlPanel(
            total_steps=model.config.total_steps,
            start_index=model.walking_order_start,  # 使用行走顺序的起点
            color_sequence=model.walking_order_colors,  # 使用行走顺序的颜色
            on_step_change=self._handle_step_change,
        )
        self._step_panel.show(parent)

    def _handle_step_change(self, new_index: int) -> None:
        """处理步进位置变化，并高亮当前台阶"""
        model = self._state.cached_model
        config = self._state.cached_config
        if not model or not config:
            return
        
        color = 1 if model.walking_order_colors[new_index] else 0
        print(f"[步进] 位置: {new_index + 1}/{model.config.total_steps}, 颜色: {color}")
        
        # 高亮当前台阶
        if self._highlight_manager:
            # 转换索引（行走顺序 -> 绘制顺序）
            draw_index = IndexConverter.walking_to_draw(new_index, config)
            step_pos = model.get_step_position(draw_index)
            if step_pos:
                self._highlight_manager.highlight(step_pos)

    def _restore_highlight(self) -> None:
        """恢复高亮状态
        
        在窗口刷新后调用，根据步进面板的当前索引重新应用高亮
        """
        if self._step_panel and not self._step_panel.is_closed():
            current_index = self._step_panel.current_index
            self._handle_step_change(current_index)

    # === 辅助方法 ===

    def _create_window(self, layout: LayoutInfo) -> GraphWin:
        """创建窗口并居中显示，支持平台适配
        
        注意：窗口尺寸直接使用 layout 中的尺寸（已在计算时应用了平台缩放），
        不再单独缩放窗口，避免窗口尺寸和渲染内容不匹配。
        """
        # 获取平台配置
        config = get_platform_config()

        # 直接使用布局尺寸（已包含平台缩放）
        win_width = int(layout.window_width)
        win_height = int(layout.window_height)

        win = GraphWin(
            f"Penrose-Staircase N={self._state.n}",
            win_width,
            win_height,
        )

        try:
            master = win.master
            master.update_idletasks()

            # 让窗口可以调整大小
            master.resizable(True, True)

            # 设置最小窗口大小
            master.minsize(config.min_window_width, config.min_window_height)

            screen_width = master.winfo_screenwidth()
            screen_height = master.winfo_screenheight()

            # 使用平台相关的偏移量
            x = (screen_width - win_width) // 2 + config.offset_x
            y = (screen_height - win_height) // 2 + config.offset_y

            x = max(0, min(x, screen_width - win_width))
            y = max(0, min(y, screen_height - win_height))

            master.geometry(f"{win_width}x{win_height}+{x}+{y}")

            # 打印平台信息用于调试
            print(f"[平台检测] 预览缩放因子: {config.preview_scale_factor}, "
                  f"字体缩放: {config.font_scale}")

        except Exception as e:
            print(f"[窗口创建] 设置窗口参数时出错: {e}")
            pass

        return win

    def _print_info(self, config) -> None:
        """打印楼梯信息"""
        print(
            f"The Penrose-Staircase Nr. {self._state.n} is: "
            f"{config.a} {config.b} {config.c} {config.d} "
            f"({config.step_length}) "
            f"导出缩放: {self._state.export_scale}x 主题: {self._state.theme.name.value}"
        )

    def _cleanup(self) -> None:
        """清理资源"""
        if self._win and not self._win.isClosed():
            self._win.close()
