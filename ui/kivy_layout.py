"""
Kivy UI 布局模块 - 定义 Penrose 楼梯的 Kivy 界面

包含：
- StaircaseWidget: 楼梯绘图区域
- ControlPanelWidget: 侧边栏控制面板
- MainScreen: 主界面布局
"""
from __future__ import annotations

import os
from typing import Callable

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.graphics import Color, Rectangle
from kivy.core.text import LabelBase

from rendering.kivy_canvas import KivyCanvas


# 注册中文字体 (macOS 系统字体)
def _register_chinese_font():
    """注册支持中文的字体"""
    # macOS 上的中文字体路径
    font_paths = [
        '/System/Library/Fonts/PingFang.ttc',  # PingFang (macOS 10.11+)
        '/System/Library/Fonts/STHeiti Light.ttc',  # 黑体
        '/System/Library/Fonts/Hiragino Sans GB.ttc',  # 冬青黑体
        '/Library/Fonts/Arial Unicode.ttf',  # Arial Unicode
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                LabelBase.register(name='ChineseFont', fn_regular=font_path)
                return 'ChineseFont'
            except Exception:
                continue
    
    # 如果没有找到中文字体，使用默认字体
    return 'Roboto'

# 注册字体
CHINESE_FONT = _register_chinese_font()


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
        on_export: Callable[[str], None] | None = None,
        **kwargs
    ):
        super().__init__(
            orientation='vertical',
            size_hint=(None, 1),
            width=560,
            padding=25,
            spacing=25,
            **kwargs
        )
        
        self._on_generate = on_generate
        self._on_export = on_export
        
        # 背景颜色
        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 1)  # 深灰色背景
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # === 标题 ===
        self.add_widget(Label(
            text='Penrose Control',
            size_hint_y=None,
            height=40,
            font_size=18,
            font_name=CHINESE_FONT,
            bold=True,
            color=(1, 1, 1, 1)
        ))
        
        # === N 输入区域 ===
        n_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        n_box.add_widget(Label(
            text='N =', 
            size_hint_x=0.3, 
            font_name=CHINESE_FONT,
            color=(1, 1, 1, 1)
        ))
        self._n_input = TextInput(
            text=str(initial_n),
            multiline=False,
            input_filter='int',
            size_hint_x=0.7
        )
        n_box.add_widget(self._n_input)
        self.add_widget(n_box)
        
        # === 主题选择 ===
        theme_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        theme_box.add_widget(Label(
            text='Theme', 
            size_hint_x=0.3, 
            font_name=CHINESE_FONT,
            color=(1, 1, 1, 1)
        ))
        self._theme_spinner = Spinner(
            text=initial_theme,
            values=self.THEMES,
            size_hint_x=0.7
        )
        theme_box.add_widget(self._theme_spinner)
        self.add_widget(theme_box)
        
        # === 缩放滑块 ===
        scale_box = BoxLayout(orientation='vertical', size_hint_y=None, height=60)
        scale_label_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        scale_label_box.add_widget(Label(
            text='Scale', 
            size_hint_x=0.5, 
            font_name=CHINESE_FONT,
            color=(1, 1, 1, 1)
        ))
        self._scale_label = Label(
            text=f'{initial_scale:.1f}x', 
            size_hint_x=0.5, 
            font_name=CHINESE_FONT,
            color=(1, 1, 1, 1)
        )
        scale_label_box.add_widget(self._scale_label)
        scale_box.add_widget(scale_label_box)
        
        self._scale_slider = Slider(min=0.5, max=3.0, value=initial_scale, size_hint_y=None, height=30)
        self._scale_slider.bind(value=self._on_scale_change)
        scale_box.add_widget(self._scale_slider)
        self.add_widget(scale_box)
        
        # === 生成按钮 ===
        self._generate_btn = Button(
            text='Generate',
            size_hint_y=None,
            height=50,
            font_name=CHINESE_FONT,
            background_color=(0.2, 0.6, 0.3, 1)
        )
        self._generate_btn.bind(on_press=self._handle_generate)
        self.add_widget(self._generate_btn)
        
        # === 导出按钮 ===
        self._export_btn = Button(
            text='Export PNG',
            size_hint_y=None,
            height=50,
            font_name=CHINESE_FONT,
            background_color=(0.3, 0.5, 0.7, 1)
        )
        self._export_btn.bind(on_press=self._handle_export)
        self.add_widget(self._export_btn)
        
        # === 状态栏 ===
        self._status_label = Label(
            text='Ready',
            size_hint_y=None,
            height=30,
            font_name=CHINESE_FONT,
            color=(0.6, 0.6, 0.6, 1),
            font_size=12
        )
        self.add_widget(self._status_label)
        
        # === 分隔线 ===
        self.add_widget(Widget(size_hint_y=None, height=20))
        
        # === 步进控制面板 ===
        step_frame = BoxLayout(orientation='vertical', size_hint_y=None, height=200, spacing=10)
        
        # 步进标题
        step_frame.add_widget(Label(
            text='Step Navigation',
            size_hint_y=None, height=30,
            font_name=CHINESE_FONT, font_size=16, bold=True,
            color=(1, 1, 1, 1)
        ))
        
        # 状态显示区
        status_box = BoxLayout(orientation='vertical', size_hint_y=None, height=80, spacing=5)
        
        # 位置行
        pos_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        pos_row.add_widget(Label(text='Position:', font_name=CHINESE_FONT, color=(0.7, 0.7, 0.7, 1), size_hint_x=0.4))
        self._step_position_label = Label(text='1 / 24', font_name=CHINESE_FONT, color=(1, 1, 1, 1), font_size=14, bold=True, size_hint_x=0.6)
        pos_row.add_widget(self._step_position_label)
        status_box.add_widget(pos_row)
        
        # 颜色行
        color_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        color_row.add_widget(Label(text='Color:', font_name=CHINESE_FONT, color=(0.7, 0.7, 0.7, 1), size_hint_x=0.4))
        self._step_color_label = Label(text='0', font_name=CHINESE_FONT, color=(0.3, 0.3, 1, 1), font_size=16, bold=True, size_hint_x=0.6)
        color_row.add_widget(self._step_color_label)
        status_box.add_widget(color_row)
        
        # 从起点步数行
        steps_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        steps_row.add_widget(Label(text='From Start:', font_name=CHINESE_FONT, color=(0.7, 0.7, 0.7, 1), size_hint_x=0.4))
        self._steps_from_start_label = Label(text='0', font_name=CHINESE_FONT, color=(1, 1, 1, 1), font_size=14, bold=True, size_hint_x=0.6)
        steps_row.add_widget(self._steps_from_start_label)
        status_box.add_widget(steps_row)
        
        step_frame.add_widget(status_box)
        
        # 步数输入行
        input_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=35, spacing=10)
        input_row.add_widget(Label(text='Steps:', font_name=CHINESE_FONT, color=(0.7, 0.7, 0.7, 1), size_hint_x=0.3))
        self._step_input = TextInput(text='1', size_hint_x=0.3, multiline=False, input_filter='int')
        input_row.add_widget(self._step_input)
        input_row.add_widget(Widget(size_hint_x=0.4))
        step_frame.add_widget(input_row)
        
        # 控制按钮行
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        
        self._step_back_btn = Button(text='<< Back', font_name=CHINESE_FONT, background_color=(0.3, 0.3, 0.5, 1))
        self._step_back_btn.bind(on_press=self._handle_step_back)
        btn_row.add_widget(self._step_back_btn)
        
        self._step_reset_btn = Button(text='Reset', font_name=CHINESE_FONT, background_color=(0.5, 0.3, 0.3, 1))
        self._step_reset_btn.bind(on_press=self._handle_step_reset)
        btn_row.add_widget(self._step_reset_btn)
        
        self._step_next_btn = Button(text='Next >>', font_name=CHINESE_FONT, background_color=(0.3, 0.3, 0.5, 1))
        self._step_next_btn.bind(on_press=self._handle_step_next)
        btn_row.add_widget(self._step_next_btn)
        
        step_frame.add_widget(btn_row)
        self.add_widget(step_frame)
        
        # 步进控制数据
        self._step_total = 24
        self._step_current = 0
        self._step_start_index = 0
        self._step_color_sequence: list[bool] = []
        self._step_accumulated = 0
        self._on_step_change: Callable[[int], None] | None = None
        
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
            # 简化处理：使用固定路径
            self._on_export('penrose_export.png')
            self._status_label.text = 'Exported'

    
    def set_status(self, message: str):
        """设置状态栏消息"""
        self._status_label.text = message
    
    # === 步进控制方法 ===
    def _get_step_count(self) -> int:
        """获取步数输入值"""
        try:
            return max(1, int(self._step_input.text))
        except (ValueError, AttributeError):
            return 1
    
    def _handle_step_back(self, instance):
        """后退"""
        steps = self._get_step_count()
        self._step_current = (self._step_current - steps) % self._step_total
        self._step_accumulated -= steps
        self._update_step_display()
        if self._on_step_change:
            self._on_step_change(self._step_current)
    
    def _handle_step_next(self, instance):
        """前进"""
        steps = self._get_step_count()
        self._step_current = (self._step_current + steps) % self._step_total
        self._step_accumulated += steps
        self._update_step_display()
        if self._on_step_change:
            self._on_step_change(self._step_current)
    
    def _handle_step_reset(self, instance):
        """复位到起点"""
        self._step_current = self._step_start_index
        self._step_accumulated = 0
        self._update_step_display()
        if self._on_step_change:
            self._on_step_change(self._step_current)
    
    def _update_step_display(self):
        """更新步进显示"""
        self._step_position_label.text = f'{self._step_current + 1} / {self._step_total}'
        
        if self._step_color_sequence and 0 <= self._step_current < len(self._step_color_sequence):
            color_val = 1 if self._step_color_sequence[self._step_current] else 0
            self._step_color_label.text = str(color_val)
            self._step_color_label.color = (1, 0.3, 0.3, 1) if color_val == 1 else (0.3, 0.3, 1, 1)
        
        self._steps_from_start_label.text = str(self._step_accumulated)
    
    def set_step_data(self, total: int, start_index: int, color_sequence: list[bool], on_change: Callable[[int], None] | None = None):
        """设置步进数据"""
        self._step_total = total
        self._step_start_index = start_index
        self._step_current = start_index
        self._step_color_sequence = color_sequence
        self._step_accumulated = 0
        self._on_step_change = on_change
        self._update_step_display()
    
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
        on_export: Callable[[str], None] | None = None,
        **kwargs
    ):
        super().__init__(orientation='horizontal', **kwargs)
        
        # 控制面板（左侧，包含步进控制）
        self.control_panel = ControlPanelWidget(
            on_generate=on_generate,
            on_export=on_export
        )
        self.add_widget(self.control_panel)
        
        # 楼梯绘图区域（右侧）
        self.staircase_widget = StaircaseWidget(size_hint=(1, 1))
        self.add_widget(self.staircase_widget)

