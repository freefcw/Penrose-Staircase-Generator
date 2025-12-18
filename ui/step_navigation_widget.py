"""
步进导航组件 - 独立的步进控制 Widget

从 ControlPanelWidget 提取的职责单一组件
"""
from __future__ import annotations

from typing import Callable

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from core.fonts import CHINESE_FONT_PATH


class StepNavigationWidget(BoxLayout):
    """
    步进导航组件
    
    职责：
    - 显示当前步进位置、颜色、累计步数
    - 提供前进/后退/复位按钮
    - 触发步进变化回调
    """
    
    def __init__(
        self,
        font_scale: float = 1.0,
        on_change: Callable[[int], None] | None = None,
        **kwargs
    ):
        super().__init__(
            orientation='vertical',
            size_hint_y=None,
            height=int(200 * font_scale),
            spacing=int(10 * font_scale),
            **kwargs
        )
        
        self._font_scale = font_scale
        self._on_change = on_change
        
        # 状态数据
        self._total = 24
        self._current = 0
        self._start_index = 0
        self._color_sequence: list[bool] = []
        self._accumulated = 0
        
        self._build_ui()
    
    def _build_ui(self) -> None:
        """构建 UI"""
        fs = self._font_scale
        
        # 标题
        self.add_widget(Label(
            text='Step Navigation',
            size_hint_y=None, height=int(30 * fs),
            font_name=CHINESE_FONT_PATH,
            font_size=int(16 * fs),
            bold=True,
            color=(1, 1, 1, 1)
        ))
        
        # 状态显示区
        status_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=int(80 * fs),
            spacing=int(5 * fs)
        )
        
        # 位置行
        pos_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=int(25 * fs))
        pos_row.add_widget(Label(
            text='Position:',
            font_name=CHINESE_FONT_PATH,
            font_size=int(12 * fs),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_x=0.4
        ))
        self._position_label = Label(
            text='1 / 24',
            font_name=CHINESE_FONT_PATH,
            color=(1, 1, 1, 1),
            font_size=int(14 * fs),
            bold=True,
            size_hint_x=0.6
        )
        pos_row.add_widget(self._position_label)
        status_box.add_widget(pos_row)
        
        # 颜色行
        color_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=int(25 * fs))
        color_row.add_widget(Label(
            text='Color:',
            font_name=CHINESE_FONT_PATH,
            font_size=int(12 * fs),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_x=0.4
        ))
        self._color_label = Label(
            text='0',
            font_name=CHINESE_FONT_PATH,
            color=(0.3, 0.3, 1, 1),
            font_size=int(16 * fs),
            bold=True,
            size_hint_x=0.6
        )
        color_row.add_widget(self._color_label)
        status_box.add_widget(color_row)
        
        # 从起点步数行
        steps_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=int(25 * fs))
        steps_row.add_widget(Label(
            text='From Start:',
            font_name=CHINESE_FONT_PATH,
            font_size=int(12 * fs),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_x=0.4
        ))
        self._from_start_label = Label(
            text='0',
            font_name=CHINESE_FONT_PATH,
            color=(1, 1, 1, 1),
            font_size=int(14 * fs),
            bold=True,
            size_hint_x=0.6
        )
        steps_row.add_widget(self._from_start_label)
        status_box.add_widget(steps_row)
        
        self.add_widget(status_box)
        
        # 步数输入行
        input_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=int(35 * fs),
            spacing=int(10 * fs)
        )
        input_row.add_widget(Label(
            text='Steps:',
            font_name=CHINESE_FONT_PATH,
            font_size=int(12 * fs),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_x=0.3
        ))
        self._step_input = TextInput(
            text='1',
            size_hint_x=0.3,
            multiline=False,
            input_filter='int',
            font_size=int(14 * fs)
        )
        input_row.add_widget(self._step_input)
        input_row.add_widget(Widget(size_hint_x=0.4))
        self.add_widget(input_row)
        
        # 控制按钮行
        btn_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=int(45 * fs),
            spacing=int(10 * fs)
        )
        
        back_btn = Button(
            text='<< Back',
            font_name=CHINESE_FONT_PATH,
            font_size=int(18 * fs),
            background_color=(0.3, 0.3, 0.5, 1)
        )
        back_btn.bind(on_press=self._handle_back)
        btn_row.add_widget(back_btn)
        
        reset_btn = Button(
            text='Reset',
            font_name=CHINESE_FONT_PATH,
            font_size=int(18 * fs),
            background_color=(0.5, 0.3, 0.3, 1)
        )
        reset_btn.bind(on_press=self._handle_reset)
        btn_row.add_widget(reset_btn)
        
        next_btn = Button(
            text='Next >>',
            font_name=CHINESE_FONT_PATH,
            font_size=int(18 * fs),
            background_color=(0.3, 0.3, 0.5, 1)
        )
        next_btn.bind(on_press=self._handle_next)
        btn_row.add_widget(next_btn)
        
        self.add_widget(btn_row)
    
    # === 事件处理 ===
    
    def _get_step_count(self) -> int:
        """获取步数输入值"""
        try:
            return max(1, int(self._step_input.text))
        except (ValueError, AttributeError):
            return 1
    
    def _handle_back(self, instance) -> None:
        """后退"""
        steps = self._get_step_count()
        self._current = (self._current - steps) % self._total
        self._accumulated -= steps
        self._update_display()
        if self._on_change:
            self._on_change(self._current)
    
    def _handle_next(self, instance) -> None:
        """前进"""
        steps = self._get_step_count()
        self._current = (self._current + steps) % self._total
        self._accumulated += steps
        self._update_display()
        if self._on_change:
            self._on_change(self._current)
    
    def _handle_reset(self, instance) -> None:
        """复位到起点"""
        self._current = self._start_index
        self._accumulated = 0
        self._update_display()
        if self._on_change:
            self._on_change(self._current)
    
    def _update_display(self) -> None:
        """更新显示"""
        self._position_label.text = f'{self._current + 1} / {self._total}'
        
        if self._color_sequence and 0 <= self._current < len(self._color_sequence):
            color_val = 1 if self._color_sequence[self._current] else 0
            self._color_label.text = str(color_val)
            self._color_label.color = (1, 0.3, 0.3, 1) if color_val == 1 else (0.3, 0.3, 1, 1)
        
        self._from_start_label.text = str(self._accumulated)
    
    # === 公共接口 ===
    
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
        self._current = start_index
        self._color_sequence = color_sequence
        self._accumulated = 0
        self._on_change = on_change
        self._update_display()
    
    @property
    def current_index(self) -> int:
        """当前步进索引"""
        return self._current
