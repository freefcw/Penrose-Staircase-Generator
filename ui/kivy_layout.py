"""
Kivy UI 布局模块 - 定义 Penrose 楼梯的 Kivy 界面

包含：
- StaircaseWidget: 楼梯绘图区域
- ControlPanelWidget: 侧边栏控制面板
- MainScreen: 主界面布局
"""
from __future__ import annotations

from typing import Callable

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.graphics import Color, Rectangle

from rendering.kivy_canvas import KivyCanvas
from core.platform_config import get_platform_config
from core.fonts import CHINESE_FONT_PATH, register_chinese_font

# 注册字体（保留兼容性）
CHINESE_FONT = register_chinese_font()


class StaircaseWidget(Widget):
    """
    楼梯绘图区域
    
    提供 KivyCanvas 实例用于渲染楼梯
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._kivy_canvas: KivyCanvas | None = None
        
        # 绘制背景
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # 浅灰色背景
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        # 绑定尺寸变化
        self.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, *args):
        """更新背景矩形"""
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
    
    def get_canvas_adapter(self) -> KivyCanvas:
        """获取 KivyCanvas 适配器"""
        if self._kivy_canvas is None:
            self._kivy_canvas = KivyCanvas(self, self.height)
        return self._kivy_canvas
    
    def clear_drawing(self):
        """清除绘图内容"""
        self.canvas.clear()
        # 重新绘制背景
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self._kivy_canvas = None


class ControlPanelWidget(BoxLayout):
    """
    侧边栏控制面板
    
    包含：
    - N 输入框
    - 主题选择器
    - 缩放滑块
    - 生成/导出按钮
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
        **kwargs
    ):
        # 获取平台配置
        platform_config = get_platform_config()
        panel_width = platform_config.control_panel_width
        font_scale = platform_config.font_scale
        
        # 根据font_scale调整尺寸
        base_padding = int(15 * font_scale)
        base_spacing = int(15 * font_scale)
        base_height = int(40 * font_scale)
        base_font_size = int(18 * font_scale)
        
        super().__init__(
            orientation='vertical',
            size_hint=(None, 1),
            width=panel_width,
            padding=base_padding,
            spacing=base_spacing,
            **kwargs
        )
        
        self._on_generate = on_generate
        self._on_apply = on_apply
        self._on_export = on_export
        self._on_export_config = on_export_config
        self._on_import_config = on_import_config
        self._font_scale = font_scale
        self._base_height = base_height
        self._base_font_size = base_font_size
        
        # 背景颜色
        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 1)  # 深灰色背景
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # === 标题 ===
        self.add_widget(Label(
            text='Penrose Control',
            size_hint_y=None,
            height=base_height,
            font_size=base_font_size,
            font_name=CHINESE_FONT_PATH,
            bold=True,
            color=(1, 1, 1, 1)
        ))
        
        # === N 输入区域 ===
        n_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=base_height, spacing=int(5 * font_scale))
        n_box.add_widget(Label(
            text='N =', 
            size_hint_x=0.3, 
            font_name=CHINESE_FONT_PATH,
            font_size=int(14 * font_scale),
            color=(1, 1, 1, 1)
        ))
        self._n_input = TextInput(
            text=str(initial_n),
            multiline=False,
            input_filter='int',
            size_hint_x=0.7,
            font_size=int(14 * font_scale)
        )
        n_box.add_widget(self._n_input)
        self.add_widget(n_box)
        
        # === 主题选择 ===
        theme_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=base_height, spacing=int(5 * font_scale))
        theme_box.add_widget(Label(
            text='Theme', 
            size_hint_x=0.3, 
            font_name=CHINESE_FONT_PATH,
            font_size=int(14 * font_scale),
            color=(1, 1, 1, 1)
        ))
        
        # 自定义Spinner下拉选项样式
        from kivy.uix.spinner import SpinnerOption
        
        # 保存 font_scale 用于闭包
        _fs = font_scale
        
        class LargeSpinnerOption(SpinnerOption):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.font_size = int(18 * _fs)
                self.height = int(50 * _fs)
        
        self._theme_spinner = Spinner(
            text=initial_theme,
            values=self.THEMES,
            size_hint_x=0.7,
            font_size=int(18 * font_scale),
            option_cls=LargeSpinnerOption,
        )
        self._theme_spinner.dropdown_cls.max_height = int(300 * font_scale)
        theme_box.add_widget(self._theme_spinner)
        self.add_widget(theme_box)
        
        # === 缩放滑块 ===
        scale_box = BoxLayout(orientation='vertical', size_hint_y=None, height=int(60 * font_scale))
        scale_label_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=int(30 * font_scale))
        scale_label_box.add_widget(Label(
            text='Scale', 
            size_hint_x=0.5, 
            font_name=CHINESE_FONT_PATH,
            font_size=int(14 * font_scale),
            color=(1, 1, 1, 1)
        ))
        self._scale_label = Label(
            text=f'{initial_scale:.1f}x', 
            size_hint_x=0.5, 
            font_name=CHINESE_FONT_PATH,
            font_size=int(14 * font_scale),
            color=(1, 1, 1, 1)
        )
        scale_label_box.add_widget(self._scale_label)
        scale_box.add_widget(scale_label_box)
        
        self._scale_slider = Slider(min=0.5, max=3.0, value=initial_scale, size_hint_y=None, height=int(30 * font_scale))
        self._scale_slider.bind(value=self._on_scale_change)
        scale_box.add_widget(self._scale_slider)
        self.add_widget(scale_box)
        
        # === 按钮行（Generate + Apply）===
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=int(50 * font_scale), spacing=int(10 * font_scale))
        
        self._generate_btn = Button(
            text='Generate',
            size_hint_x=0.5,
            font_name=CHINESE_FONT_PATH,
            font_size=int(16 * font_scale),
            background_color=(0.2, 0.6, 0.3, 1)
        )
        self._generate_btn.bind(on_press=self._handle_generate)
        btn_row.add_widget(self._generate_btn)
        
        self._apply_btn = Button(
            text='Apply',
            size_hint_x=0.5,
            font_name=CHINESE_FONT_PATH,
            font_size=int(16 * font_scale),
            background_color=(0.5, 0.4, 0.2, 1)
        )
        self._apply_btn.bind(on_press=self._handle_apply)
        btn_row.add_widget(self._apply_btn)
        
        self.add_widget(btn_row)
        
        # === 导出PNG按钮 ===
        self._export_btn = Button(
            text='Export PNG',
            size_hint_y=None,
            height=int(50 * font_scale),
            font_name=CHINESE_FONT_PATH,
            font_size=int(16 * font_scale),
            background_color=(0.3, 0.5, 0.7, 1)
        )
        self._export_btn.bind(on_press=self._handle_export)
        self.add_widget(self._export_btn)
        
        # === 配置管理按钮 ===
        config_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=int(45 * font_scale), spacing=int(10 * font_scale))
        
        self._export_cfg_btn = Button(
            text='导出配置',
            size_hint_x=0.5,
            font_name=CHINESE_FONT_PATH,
            font_size=int(14 * font_scale),
            background_color=(0.4, 0.4, 0.5, 1)
        )
        self._export_cfg_btn.bind(on_press=self._handle_export_config)
        config_row.add_widget(self._export_cfg_btn)
        
        self._import_cfg_btn = Button(
            text='导入配置',
            size_hint_x=0.5,
            font_name=CHINESE_FONT_PATH,
            font_size=int(14 * font_scale),
            background_color=(0.4, 0.4, 0.5, 1)
        )
        self._import_cfg_btn.bind(on_press=self._handle_import_config)
        config_row.add_widget(self._import_cfg_btn)
        
        self.add_widget(config_row)
        
        # === 状态栏 ===
        self._status_label = Label(
            text='Ready',
            size_hint_y=None,
            height=int(30 * font_scale),
            font_name=CHINESE_FONT_PATH,
            color=(0.6, 0.6, 0.6, 1),
            font_size=int(12 * font_scale)
        )
        self.add_widget(self._status_label)
        
        # === 分隔线 ===
        self.add_widget(Widget(size_hint_y=None, height=int(20 * font_scale)))
        
        # === 步进导航组件 ===
        from ui.step_navigation_widget import StepNavigationWidget
        self._step_nav = StepNavigationWidget(font_scale=font_scale)
        self.add_widget(self._step_nav)
        
        # 填充剩余空间
        self.add_widget(Widget())
    
    def _update_bg(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
    
    def _on_scale_change(self, instance, value):
        self._scale_label.text = f'{value:.1f}x'
    
    def _handle_generate(self, instance):
        if self._on_generate:
            try:
                n = int(self._n_input.text)
                theme = self._theme_spinner.text
                scale = self._scale_slider.value
                self._on_generate(n, theme, scale)
                self._status_label.text = f'已生成 N={n}'
            except ValueError:
                self._status_label.text = '错误: N 必须是整数'
    
    def _handle_export(self, instance):
        if self._on_export:
            # 生成带时间戳的文件名
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'penrose_{timestamp}.png'
            self._on_export(filename)
            self._status_label.text = f'Exported: {filename}'
    
    def _handle_apply(self, instance):
        """Apply 按钮 - 实时应用主题和缩放（不重新生成数据）"""
        if self._on_apply:
            theme = self._theme_spinner.text
            scale = self._scale_slider.value
            self._on_apply(theme, scale)
            self._status_label.text = f'已应用: {theme}, {scale:.1f}x'
    
    def _handle_export_config(self, instance):
        """导出配置"""
        if self._on_export_config:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'penrose_config_{timestamp}.json'
            self._on_export_config(filename)
            self._status_label.text = f'配置已导出: {filename}'
    
    def _handle_import_config(self, instance):
        """导入配置 - 显示文件选择弹窗"""
        from kivy.uix.popup import Popup
        from kivy.uix.filechooser import FileChooserListView
        from kivy.uix.boxlayout import BoxLayout as BL
        from kivy.uix.button import Button as Btn
        
        content = BL(orientation='vertical')
        filechooser = FileChooserListView(
            path='.',
            filters=['*.json'],
        )
        content.add_widget(filechooser)
        
        btn_layout = BL(size_hint_y=None, height=50, spacing=10)
        
        def on_select(btn_instance):
            if filechooser.selection and self._on_import_config:
                file_path = filechooser.selection[0]
                self._on_import_config(file_path)
                self._status_label.text = f'配置已导入'
            popup.dismiss()
        
        def on_cancel(btn_instance):
            popup.dismiss()
        
        # 使用中文字体
        select_btn = Btn(text='选择', font_name=CHINESE_FONT_PATH, background_color=(0.2, 0.6, 0.3, 1))
        select_btn.bind(on_press=on_select)
        cancel_btn = Btn(text='取消', font_name=CHINESE_FONT_PATH, background_color=(0.5, 0.3, 0.3, 1))
        cancel_btn.bind(on_press=on_cancel)
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Import Config',  # Popup 标题暂用英文避免乱码
            title_font=CHINESE_FONT_PATH,
            content=content,
            size_hint=(0.9, 0.9),
        )
        popup.open()

    
    def set_status(self, message: str):
        """设置状态栏消息"""
        self._status_label.text = message
    
    # === 步进控制方法（代理到 StepNavigationWidget）===
    
    def set_step_data(
        self,
        total: int,
        start_index: int,
        color_sequence: list[bool],
        on_change: Callable[[int], None] | None = None,
    ) -> None:
        """设置步进数据（代理到 StepNavigationWidget）"""
        self._step_nav.set_data(total, start_index, color_sequence, on_change)
    
    @property
    def current_n(self) -> int:
        try:
            return int(self._n_input.text)
        except ValueError:
            return 190
    
    @property
    def current_theme(self) -> str:
        return self._theme_spinner.text
    
    @property
    def current_scale(self) -> float:
        return self._scale_slider.value


class MainScreen(BoxLayout):
    """
    主界面布局
    
    左侧：控制面板（包含步进控制）
    右侧：楼梯绘图区域
    """
    
    def __init__(
        self,
        on_generate: Callable[[int, str, float], None] | None = None,
        on_apply: Callable[[str, float], None] | None = None,
        on_export: Callable[[str], None] | None = None,
        on_export_config: Callable[[str], None] | None = None,
        on_import_config: Callable[[str], None] | None = None,
        **kwargs
    ):
        super().__init__(orientation='horizontal', **kwargs)
        
        # 控制面板（左侧，包含步进控制）
        self.control_panel = ControlPanelWidget(
            on_generate=on_generate,
            on_apply=on_apply,
            on_export=on_export,
            on_export_config=on_export_config,
            on_import_config=on_import_config,
        )
        self.add_widget(self.control_panel)
        
        # 楼梯绘图区域（右侧）
        self.staircase_widget = StaircaseWidget(size_hint=(1, 1))
        self.add_widget(self.staircase_widget)

