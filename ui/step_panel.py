"""步进控制面板 - 用于在楼梯序列上导航"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Callable


@dataclass
class StepInfo:
    """步进信息"""
    current_index: int  # 当前位置索引（在颜色序列中）
    total_steps: int  # 总台阶数
    color_value: int  # 当前颜色值（0或1）
    steps_from_start: int  # 从起点（X）开始的步数
    
    @property
    def position_display(self) -> str:
        """显示位置信息"""
        return f"{self.current_index + 1}/{self.total_steps}"


class StepControlPanel:
    """步进控制面板
    
    功能：
    - 前进/后退指定步数
    - 显示当前位置颜色（1/0）
    - 显示从起点（X）开始的累计步数
    """
    
    WINDOW_WIDTH = 320
    WINDOW_HEIGHT = 280
    PADDING = 15
    
    def __init__(
        self,
        total_steps: int,
        start_index: int,
        color_sequence: list[bool],
        on_step_change: Callable[[int], None] | None = None,
    ):
        """初始化步进控制面板
        
        Args:
            total_steps: 总台阶数
            start_index: 起点索引（X标记位置）
            color_sequence: 颜色序列
            on_step_change: 步进变化回调
        """
        self._total_steps = total_steps
        self._start_index = start_index
        self._color_sequence = color_sequence
        self._on_step_change = on_step_change
        
        # 当前位置（从起点开始）
        self._current_index = start_index
        self._steps_from_start = 0
        
        self._root: tk.Toplevel | None = None
        self._is_closed = False
        
        # UI 组件
        self._position_label: ttk.Label | None = None
        self._color_label: ttk.Label | None = None
        self._steps_label: ttk.Label | None = None
        self._step_entry: ttk.Entry | None = None
    
    def show(self, parent: tk.Tk | None = None) -> None:
        """显示面板"""
        if parent:
            self._root = tk.Toplevel(parent)
        else:
            self._root = tk.Toplevel()
        
        self._root.title("步进控制")
        self._root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+50+450")
        self._root.resizable(False, False)
        self._root.protocol("WM_DELETE_WINDOW", self._handle_close)
        
        self._build_ui()
        self._update_display()
    
    def _build_ui(self) -> None:
        """构建 UI"""
        if not self._root:
            return
        
        main_frame = ttk.Frame(self._root, padding=self.PADDING)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === 状态显示区 ===
        status_frame = ttk.LabelFrame(main_frame, text="当前状态", padding=5)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 位置
        pos_row = ttk.Frame(status_frame)
        pos_row.pack(fill=tk.X, pady=2)
        ttk.Label(pos_row, text="位置:").pack(side=tk.LEFT)
        self._position_label = ttk.Label(pos_row, text="--", font=("Courier", 12, "bold"))
        self._position_label.pack(side=tk.RIGHT)
        
        # 颜色
        color_row = ttk.Frame(status_frame)
        color_row.pack(fill=tk.X, pady=2)
        ttk.Label(color_row, text="颜色:").pack(side=tk.LEFT)
        self._color_label = ttk.Label(color_row, text="--", font=("Courier", 14, "bold"))
        self._color_label.pack(side=tk.RIGHT)
        
        # 累计步数
        steps_row = ttk.Frame(status_frame)
        steps_row.pack(fill=tk.X, pady=2)
        ttk.Label(steps_row, text="从起点步数:").pack(side=tk.LEFT)
        self._steps_label = ttk.Label(steps_row, text="0", font=("Courier", 12, "bold"))
        self._steps_label.pack(side=tk.RIGHT)
        
        # === 步进控制区 ===
        control_frame = ttk.LabelFrame(main_frame, text="步进控制", padding=5)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 步数输入
        input_row = ttk.Frame(control_frame)
        input_row.pack(fill=tk.X, pady=5)
        ttk.Label(input_row, text="步数:").pack(side=tk.LEFT)
        self._step_entry = ttk.Entry(input_row, width=8)
        self._step_entry.insert(0, "1")
        self._step_entry.pack(side=tk.LEFT, padx=5)
        
        # 按钮
        btn_row = ttk.Frame(control_frame)
        btn_row.pack(fill=tk.X, pady=5)
        
        back_btn = ttk.Button(btn_row, text="<< 后退", command=self._step_backward, width=7)
        back_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        forward_btn = ttk.Button(btn_row, text="前进 >>", command=self._step_forward, width=7)
        forward_btn.pack(side=tk.LEFT)
        
        reset_btn = ttk.Button(btn_row, text="复位", command=self._reset_to_start, width=6)
        reset_btn.pack(side=tk.RIGHT)
    
    def _get_step_count(self) -> int:
        """获取步数输入值"""
        try:
            return max(1, int(self._step_entry.get() if self._step_entry else "1"))
        except ValueError:
            return 1
    
    def _step_forward(self) -> None:
        """前进"""
        steps = self._get_step_count()
        new_index = (self._current_index + steps) % self._total_steps
        self._current_index = new_index
        self._steps_from_start += steps
        self._update_display()
        self._notify_change()
    
    def _step_backward(self) -> None:
        """后退"""
        steps = self._get_step_count()
        new_index = (self._current_index - steps) % self._total_steps
        self._current_index = new_index
        self._steps_from_start -= steps
        self._update_display()
        self._notify_change()
    
    def _reset_to_start(self) -> None:
        """复位到起点"""
        self._current_index = self._start_index
        self._steps_from_start = 0
        self._update_display()
        self._notify_change()
    
    def _update_display(self) -> None:
        """更新显示"""
        if not self._root:
            return
        
        # 位置
        if self._position_label:
            self._position_label.config(text=f"{self._current_index + 1}/{self._total_steps}")
        
        # 颜色
        if self._color_label:
            color = 1 if self._color_sequence[self._current_index] else 0
            self._color_label.config(
                text=str(color),
                foreground="red" if color == 1 else "blue"
            )
        
        # 累计步数
        if self._steps_label:
            self._steps_label.config(text=str(self._steps_from_start))
    
    def _notify_change(self) -> None:
        """通知位置变化"""
        if self._on_step_change:
            self._on_step_change(self._current_index)
    
    def _handle_close(self) -> None:
        """关闭面板"""
        self._is_closed = True
        if self._root:
            self._root.destroy()
    
    def update(self) -> None:
        """更新 UI"""
        if self._root and not self._is_closed:
            try:
                self._root.update()
            except tk.TclError:
                self._is_closed = True
    
    def is_closed(self) -> bool:
        """检查是否已关闭"""
        return self._is_closed
    
    @property
    def current_index(self) -> int:
        """当前位置索引"""
        return self._current_index
