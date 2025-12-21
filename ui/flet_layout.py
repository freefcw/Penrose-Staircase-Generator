"""
Flet UI 布局模块 - 定义 Penrose 楼梯的 Flet 界面

包含：
- StaircaseCanvas: 楼梯绘图区域
- ControlPanel: 侧边栏控制面板
- StepNavigation: 步进导航组件
- MainLayout: 主界面布局
"""
from __future__ import annotations

import logging
from typing import Callable

import flet as ft
import flet.canvas as cv

from rendering.flet_canvas import FletCanvas

logger = logging.getLogger(__name__)


class StaircaseCanvas(ft.Container):
    """
    楼梯绘图区域
    
    封装 Flet Canvas 控件，提供 FletCanvas 适配器接口
    复用 Canvas 实例避免重复创建开销
    """
    
    def __init__(self, width: float = 700, height: float = 500):
        self._width = width
        self._height = height
        self._flet_canvas: FletCanvas | None = None
        
        # 创建可复用的 Canvas 控件
        self._cv_canvas = cv.Canvas(
            shapes=[],
            width=float("inf"),
            height=float("inf"),
        )
        
        super().__init__(
            content=self._cv_canvas,
            bgcolor=ft.Colors.GREY_200,
            border_radius=8,
            expand=True,
        )
    
    def get_canvas_adapter(self, width: float, height: float) -> FletCanvas:
        """获取 FletCanvas 适配器"""
        self._flet_canvas = FletCanvas(width, height)
        return self._flet_canvas
    
    def update_canvas(self) -> None:
        """更新画布显示 - 复用 Canvas 只更新 shapes"""
        if self._flet_canvas:
            # 过滤掉已移除的形状（None）
            shapes = [s for s in self._flet_canvas.get_shapes() if s is not None]
            logger.debug(f"更新画布，形状数量: {len(shapes)}")
            
            # 更新现有 Canvas 的 shapes（不重建）
            self._cv_canvas.shapes = shapes
            
            if self.page:
                self._cv_canvas.update()
    
    def clear_drawing(self) -> None:
        """清除绘图内容"""
        if self._flet_canvas:
            self._flet_canvas.clear()
        # 清空 shapes 但保留 Canvas 实例
        self._cv_canvas.shapes = []
        if self.page:
            self._cv_canvas.update()
        self._flet_canvas = None


class StepNavigation(ft.Container):
    """
    步进导航组件
    
    功能：
    - 前进/后退按钮
    - 当前位置显示
    - 颜色状态显示
    """
    
    def __init__(self, on_change: Callable[[int], None] | None = None):
        self._on_change = on_change
        self._total = 0
        self._start_index = 0
        self._current_index = 0
        self._steps_from_start = 0
        self._color_sequence: list[bool] = []
        
        # UI 组件
        self._position_text = ft.Text("--/--", size=14, weight=ft.FontWeight.BOLD)
        self._color_text = ft.Text("--", size=18, weight=ft.FontWeight.BOLD)
        self._steps_text = ft.Text("0", size=14, weight=ft.FontWeight.BOLD)
        self._step_input = ft.TextField(
            value="1", 
            width=60, 
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            bgcolor=ft.Colors.GREY_100,
            color=ft.Colors.BLACK,
            border_color=ft.Colors.GREY_400,
        )
        
        super().__init__(
            content=self._build_ui(),
            padding=10,
            visible=False,  # 初始隐藏，等待数据设置
        )
    
    def _build_ui(self) -> ft.Column:
        """构建 UI"""
        return ft.Column([
            # 标题
            ft.Text("步进控制", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Divider(height=1, color=ft.Colors.GREY_600),
            
            # 状态显示
            ft.Row([
                ft.Text("位置:", size=12, color=ft.Colors.GREY_400),
                self._position_text,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                ft.Text("颜色:", size=12, color=ft.Colors.GREY_400),
                self._color_text,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                ft.Text("累计步数:", size=12, color=ft.Colors.GREY_400),
                self._steps_text,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Divider(height=1, color=ft.Colors.GREY_600),
            
            # 步进控制
            ft.Row([
                ft.Text("步数:", size=12, color=ft.Colors.GREY_400),
                self._step_input,
            ]),
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="后退",
                    on_click=self._step_backward,
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="复位",
                    on_click=self._reset_to_start,
                ),
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    tooltip="前进",
                    on_click=self._step_forward,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=8)
    
    def set_data(
        self,
        total: int,
        start_index: int,
        color_sequence: list[bool],
        on_change: Callable[[int], None] | None = None,
    ) -> None:
        """设置步进数据"""
        self._total = total
        self._start_index = start_index
        self._current_index = start_index
        self._steps_from_start = 0
        self._color_sequence = color_sequence
        self._on_change = on_change
        self.visible = True
        self._update_display()
    
    def _get_step_count(self) -> int:
        """获取步数输入值"""
        try:
            return max(1, int(self._step_input.value or "1"))
        except ValueError:
            return 1
    
    def _step_forward(self, e) -> None:
        """前进"""
        steps = self._get_step_count()
        self._current_index = (self._current_index + steps) % self._total
        self._steps_from_start += steps
        self._update_display()
        self._notify_change()
    
    def _step_backward(self, e) -> None:
        """后退"""
        steps = self._get_step_count()
        self._current_index = (self._current_index - steps) % self._total
        self._steps_from_start -= steps
        self._update_display()
        self._notify_change()
    
    def _reset_to_start(self, e) -> None:
        """复位到起点"""
        self._current_index = self._start_index
        self._steps_from_start = 0
        self._update_display()
        self._notify_change()
    
    def _update_display(self) -> None:
        """更新显示"""
        self._position_text.value = f"{self._current_index + 1}/{self._total}"
        self._position_text.color = ft.Colors.WHITE
        
        if self._color_sequence:
            color = 1 if self._color_sequence[self._current_index] else 0
            self._color_text.value = str(color)
            self._color_text.color = ft.Colors.RED if color == 1 else ft.Colors.BLUE
        
        self._steps_text.value = str(self._steps_from_start)
        self._steps_text.color = ft.Colors.WHITE
        
        if self.page:
            self.update()
    
    def _notify_change(self) -> None:
        """通知位置变化"""
        if self._on_change:
            self._on_change(self._current_index)


class ControlPanel(ft.Container):
    """
    侧边栏控制面板
    
    包含：
    - N 输入框
    - 主题选择器
    - 缩放滑块
    - 生成/导出按钮
    - 步进导航
    """
    
    THEMES = ["minimal", "classic", "professional", "artistic"]
    
    def __init__(
        self,
        initial_n: int = 190,
        initial_theme: str = "minimal",
        initial_scale: float = 1.0,
        on_generate: Callable[[int, str, float], None] | None = None,
        on_apply: Callable[[str, float], None] | None = None,
        on_export: Callable[[str], None] | None = None,
        on_export_config: Callable[[str], None] | None = None,
        on_import_config: Callable[[str], None] | None = None,
    ):
        self._on_generate = on_generate
        self._on_apply = on_apply
        self._on_export = on_export
        self._on_export_config = on_export_config
        self._on_import_config = on_import_config
        
        # UI 组件
        self._n_input = ft.TextField(
            value=str(initial_n),
            width=100,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.CENTER,
            bgcolor=ft.Colors.GREY_100,
            color=ft.Colors.BLACK,
            border_color=ft.Colors.GREY_500,
        )
        
        self._theme_dropdown = ft.Dropdown(
            value=initial_theme,
            options=[ft.dropdown.Option(t) for t in self.THEMES],
            width=150,
            bgcolor=ft.Colors.GREY_100,
            color=ft.Colors.BLACK,
            border_color=ft.Colors.GREY_500,
            filled=True,
            fill_color=ft.Colors.GREY_100,
        )
        
        self._scale_slider = ft.Slider(
            min=0.5, max=3.0, value=initial_scale,
            divisions=25,
            label="{value}x",
            on_change=self._on_scale_change,
        )
        self._scale_text = ft.Text(f"{initial_scale:.1f}x", size=14, color=ft.Colors.WHITE)
        
        self._status_text = ft.Text("Ready", size=12, color=ft.Colors.GREY_400)
        
        # 文件选择器（用于导入配置）
        self._file_picker = ft.FilePicker(
            on_result=self._on_file_picked,
        )
        
        # 步进导航组件
        self._step_nav = StepNavigation()
        
        super().__init__(
            content=self._build_ui(),
            width=280,
            bgcolor=ft.Colors.GREY_900,
            padding=20,
        )
    
    def did_mount(self):
        """控件挂载后添加 FilePicker 到 overlay"""
        if self.page and self._file_picker not in self.page.overlay:
            self.page.overlay.append(self._file_picker)
            self.page.update()
    
    def _build_ui(self) -> ft.Column:
        """构建 UI"""
        return ft.Column([
            # 标题
            ft.Text(
                "Penrose Control",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            ft.Divider(height=1, color=ft.Colors.GREY_700),
            
            # N 输入
            ft.Row([
                ft.Text("N =", size=14, color=ft.Colors.WHITE),
                self._n_input,
            ]),
            
            # 主题选择
            ft.Row([
                ft.Text("Theme", size=14, color=ft.Colors.WHITE),
                self._theme_dropdown,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            # 缩放滑块
            ft.Column([
                ft.Row([
                    ft.Text("Scale", size=14, color=ft.Colors.WHITE),
                    self._scale_text,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self._scale_slider,
            ]),
            
            # 按钮行
            ft.Row([
                ft.ElevatedButton(
                    "Generate",
                    bgcolor=ft.Colors.GREEN_700,
                    color=ft.Colors.WHITE,
                    on_click=self._handle_generate,
                    expand=True,
                ),
                ft.ElevatedButton(
                    "Apply",
                    bgcolor=ft.Colors.AMBER_700,
                    color=ft.Colors.WHITE,
                    on_click=self._handle_apply,
                    expand=True,
                ),
            ], spacing=10),
            
            # 导出按钮
            ft.ElevatedButton(
                "Export PNG",
                icon=ft.Icons.IMAGE,
                bgcolor=ft.Colors.BLUE_700,
                color=ft.Colors.WHITE,
                on_click=self._handle_export,
                width=240,
            ),
            
            # 配置管理按钮
            ft.Row([
                ft.OutlinedButton(
                    "导出配置",
                    on_click=self._handle_export_config,
                    expand=True,
                ),
                ft.OutlinedButton(
                    "导入配置",
                    on_click=self._handle_import_config,
                    expand=True,
                ),
            ], spacing=10),
            
            # 状态栏
            self._status_text,
            
            ft.Divider(height=1, color=ft.Colors.GREY_700),
            
            # 步进导航
            self._step_nav,
            
        ], spacing=15, expand=True)
    
    def _on_scale_change(self, e) -> None:
        """缩放滑块变化"""
        self._scale_text.value = f"{e.control.value:.1f}x"
        self._scale_text.update()
    
    def _handle_generate(self, e) -> None:
        """生成按钮"""
        if self._on_generate:
            try:
                n = int(self._n_input.value or "190")
                theme = self._theme_dropdown.value or "minimal"
                scale = self._scale_slider.value
                self._on_generate(n, theme, scale)
                self.set_status(f"已生成 N={n}")
            except ValueError:
                self.set_status("错误: N 必须是整数")
    
    def _handle_apply(self, e) -> None:
        """Apply 按钮"""
        if self._on_apply:
            theme = self._theme_dropdown.value or "minimal"
            scale = self._scale_slider.value
            self._on_apply(theme, scale)
            self.set_status(f"已应用: {theme}, {scale:.1f}x")
    
    def _handle_export(self, e) -> None:
        """导出按钮"""
        if self._on_export:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'penrose_{timestamp}.png'
            self._on_export(filename)
            self.set_status(f"Exported: {filename}")
    
    def _handle_export_config(self, e) -> None:
        """导出配置"""
        if self._on_export_config:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'penrose_config_{timestamp}.json'
            self._on_export_config(filename)
            self.set_status(f"配置已导出: {filename}")
    
    def _handle_import_config(self, e) -> None:
        """导入配置 - 打开文件选择对话框"""
        self._file_picker.pick_files(
            allowed_extensions=["json"],
            dialog_title="选择配置文件",
        )
        self.set_status("请选择配置文件...")
    
    def _on_file_picked(self, e: ft.FilePickerResultEvent) -> None:
        """文件选择完成回调"""
        if not e.files:
            self.set_status("已取消选择文件")
            return
        
        file_path = e.files[0].path
        if file_path and self._on_import_config:
            self._on_import_config(file_path)
            self.set_status(f"配置已导入: {file_path.split('/')[-1]}")
    
    def set_status(self, message: str) -> None:
        """设置状态栏消息"""
        self._status_text.value = message
        if self.page:
            self._status_text.update()
    
    def set_step_data(
        self,
        total: int,
        start_index: int,
        color_sequence: list[bool],
        on_change: Callable[[int], None] | None = None,
    ) -> None:
        """设置步进数据"""
        self._step_nav.set_data(total, start_index, color_sequence, on_change)
        if self.page:
            self._step_nav.update()
    
    @property
    def current_n(self) -> int:
        try:
            return int(self._n_input.value or "190")
        except ValueError:
            return 190
    
    @property
    def current_theme(self) -> str:
        return self._theme_dropdown.value or "minimal"
    
    @property
    def current_scale(self) -> float:
        return self._scale_slider.value


class ResponsiveLayout(ft.Container):
    """
    响应式布局容器
    
    - 桌面端 (宽度 >= 600): 左右分栏布局
    - 移动端 (宽度 < 600): AppBar + 抽屉菜单
    """
    
    MOBILE_BREAKPOINT = 600
    
    def __init__(
        self,
        control_panel: ControlPanel,
        staircase_canvas: StaircaseCanvas,
    ):
        self._control_panel = control_panel
        self._staircase_canvas = staircase_canvas
        self._is_mobile = False
        
        # 移动端抽屉菜单
        self._drawer = ft.NavigationDrawer(
            controls=[
                ft.Container(
                    content=self._create_drawer_content(),
                    padding=0,
                )
            ],
            bgcolor=ft.Colors.GREY_900,
        )
        
        # 移动端 AppBar
        self._app_bar = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.MENU,
                on_click=self._toggle_drawer,
                icon_color=ft.Colors.WHITE,
            ),
            title=ft.Text("Penrose Staircase", weight=ft.FontWeight.BOLD),
            bgcolor=ft.Colors.GREY_900,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.IMAGE,
                    tooltip="导出 PNG",
                    on_click=self._handle_mobile_export,
                    icon_color=ft.Colors.WHITE,
                ),
            ],
        )
        
        # 桌面端布局
        self._desktop_layout = ft.Row([
            control_panel,
            staircase_canvas,
        ], expand=True, spacing=0)
        
        # 移动端布局（仅画布）
        self._mobile_layout = ft.Container(
            content=staircase_canvas,
            expand=True,
        )
        
        super().__init__(
            content=self._desktop_layout,
            expand=True,
        )
    
    def _create_drawer_content(self) -> ft.Column:
        """创建抽屉内容 - 复制控制面板的核心 UI"""
        return ft.Column([
            ft.Container(
                content=ft.Text(
                    "Penrose Control",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                padding=ft.padding.only(left=20, top=20, bottom=10),
            ),
            ft.Divider(height=1, color=ft.Colors.GREY_700),
            
            # N 输入
            ft.Container(
                content=ft.Row([
                    ft.Text("N =", size=14, color=ft.Colors.WHITE),
                    self._control_panel._n_input,
                ]),
                padding=ft.padding.symmetric(horizontal=20, vertical=5),
            ),
            
            # 主题选择
            ft.Container(
                content=ft.Row([
                    ft.Text("Theme", size=14, color=ft.Colors.WHITE),
                    self._control_panel._theme_dropdown,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.symmetric(horizontal=20, vertical=5),
            ),
            
            # 缩放滑块
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Scale", size=14, color=ft.Colors.WHITE),
                        self._control_panel._scale_text,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    self._control_panel._scale_slider,
                ]),
                padding=ft.padding.symmetric(horizontal=20, vertical=5),
            ),
            
            # 按钮
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(
                        "Generate",
                        bgcolor=ft.Colors.GREEN_700,
                        color=ft.Colors.WHITE,
                        on_click=self._handle_generate_and_close,
                        expand=True,
                    ),
                    ft.ElevatedButton(
                        "Apply",
                        bgcolor=ft.Colors.AMBER_700,
                        color=ft.Colors.WHITE,
                        on_click=self._handle_apply_and_close,
                        expand=True,
                    ),
                ], spacing=10),
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ),
            
            # 状态栏
            ft.Container(
                content=self._control_panel._status_text,
                padding=ft.padding.symmetric(horizontal=20),
            ),
            
            ft.Divider(height=1, color=ft.Colors.GREY_700),
            
            # 步进导航
            ft.Container(
                content=self._control_panel._step_nav,
                padding=ft.padding.symmetric(horizontal=20),
            ),
        ], spacing=5, scroll=ft.ScrollMode.AUTO)
    
    def _toggle_drawer(self, e) -> None:
        """切换抽屉显示"""
        if self.page:
            self.page.open(self._drawer)
    
    def _close_drawer(self) -> None:
        """关闭抽屉"""
        if self.page:
            self.page.close(self._drawer)
    
    def _handle_generate_and_close(self, e) -> None:
        """生成并关闭抽屉"""
        self._control_panel._handle_generate(e)
        self._close_drawer()
    
    def _handle_apply_and_close(self, e) -> None:
        """应用并关闭抽屉"""
        self._control_panel._handle_apply(e)
        self._close_drawer()
    
    def _handle_mobile_export(self, e) -> None:
        """移动端导出"""
        self._control_panel._handle_export(e)
    
    def did_mount(self) -> None:
        """挂载后检测屏幕尺寸"""
        self._check_layout()
        if self.page:
            self.page.on_resized = self._on_resize
    
    def _on_resize(self, e) -> None:
        """窗口大小变化时重新检测布局"""
        self._check_layout()
    
    def _check_layout(self) -> None:
        """检测并切换布局模式"""
        if not self.page:
            return
        
        width = self.page.window.width or 800
        is_mobile = width < self.MOBILE_BREAKPOINT
        
        if is_mobile != self._is_mobile:
            self._is_mobile = is_mobile
            self._apply_layout()
    
    def _apply_layout(self) -> None:
        """应用布局"""
        if not self.page:
            return
        
        if self._is_mobile:
            # 移动端：显示 AppBar，隐藏侧边栏
            self.page.appbar = self._app_bar
            self._control_panel.visible = False
            self.content = self._staircase_canvas
            logger.info("切换到移动端布局")
        else:
            # 桌面端：隐藏 AppBar，显示侧边栏
            self.page.appbar = None
            self._control_panel.visible = True
            self.content = self._desktop_layout
            logger.info("切换到桌面端布局")
        
        self.page.update()


def create_main_layout(
    on_generate: Callable[[int, str, float], None] | None = None,
    on_apply: Callable[[str, float], None] | None = None,
    on_export: Callable[[str], None] | None = None,
    on_export_config: Callable[[str], None] | None = None,
    on_import_config: Callable[[str], None] | None = None,
) -> tuple[ResponsiveLayout, ControlPanel, StaircaseCanvas]:
    """
    创建主界面布局（响应式）
    
    Returns:
        (主布局, 控制面板, 楼梯画布)
    """
    control_panel = ControlPanel(
        on_generate=on_generate,
        on_apply=on_apply,
        on_export=on_export,
        on_export_config=on_export_config,
        on_import_config=on_import_config,
    )
    
    staircase_canvas = StaircaseCanvas()
    
    main_layout = ResponsiveLayout(control_panel, staircase_canvas)
    
    return main_layout, control_panel, staircase_canvas
