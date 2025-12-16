"""控制面板模块 - 基于 Tkinter 的交互式控制面板"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from core.platform_config import get_platform_config


class PanelAction(str, Enum):
    """控制面板动作枚举"""
    NONE = "none"
    REDRAW = "redraw"
    EXPORT = "export"
    CLOSE = "close"


@dataclass
class PanelState:
    """控制面板状态"""
    n: int
    theme: str
    scale: float
    
    def copy(self) -> PanelState:
        return PanelState(n=self.n, theme=self.theme, scale=self.scale)


class ControlPanel:
    """控制面板窗口
    
    基于 Tkinter，提供以下功能：
    - 设置楼梯序号 N
    - 选择主题样式  
    - 调整缩放比例
    - 导出图片
    - 关闭应用
    
    Example:
        >>> panel = ControlPanel(initial_state=PanelState(n=190, theme="minimal", scale=1.0))
        >>> panel.show()
    """
    
    # 可用主题列表
    THEMES = ["minimal", "classic", "professional", "artistic"]
    
    # 窗口配置（默认值，实际使用平台配置）
    WINDOW_WIDTH = 300
    WINDOW_HEIGHT = 420
    PADDING = 10

    @staticmethod
    def get_platform_size():
        """获取平台相关的窗口大小"""
        config = get_platform_config()
        return {
            "width": config.control_panel_width,
            "height": config.control_panel_height,
            "font_scale": config.font_scale
        }
    
    def __init__(
        self, 
        initial_state: PanelState,
        on_save: Callable[[PanelState], None] | None = None,
        on_generate: Callable[[PanelState], None] | None = None,
        on_export: Callable[[str], None] | None = None,
        on_close: Callable[[], None] | None = None,
        on_export_config: Callable[[str], None] | None = None,
        on_import_config: Callable[[str], None] | None = None,
    ):
        """初始化控制面板
        
        Args:
            initial_state: 初始状态
            on_save: 保存按钮回调（仅保存设置，不刷新数据）
            on_generate: 生成按钮回调（重新生成数据）
            on_export: 导出按钮回调
            on_close: 关闭按钮回调
            on_export_config: 导出配置回调
            on_import_config: 导入配置回调
        """
        self._state = initial_state.copy()
        self._on_save = on_save
        self._on_generate = on_generate
        self._on_export = on_export
        self._on_close = on_close
        self._on_export_config = on_export_config
        self._on_import_config = on_import_config
        
        self._root: tk.Tk | None = None
        self._pending_action = PanelAction.NONE
        self._is_closed = False
        
        # UI 组件引用
        self._n_entry: ttk.Entry | None = None
        self._theme_combo: ttk.Combobox | None = None
        self._scale_slider: ttk.Scale | None = None  # 直接引用 Scale
        self._scale_label: ttk.Label | None = None
        self._status_label: ttk.Label | None = None
    
    def show(self) -> None:
        """显示控制面板"""
        self._root = tk.Tk()
        self._root.title("Penrose 控制面板")

        # 使用平台相关的尺寸
        platform_size = self.get_platform_size()
        self._root.geometry(f"{platform_size['width']}x{platform_size['height']}")
        self._root.resizable(False, False)

        # 设置关闭事件
        self._root.protocol("WM_DELETE_WINDOW", self._handle_close)

        self._build_ui()
    
    def _build_ui(self) -> None:
        """构建 UI 组件"""
        if not self._root:
            return
            
        # 主容器
        main_frame = ttk.Frame(self._root, padding=self.PADDING)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === 楼梯序号 N ===
        n_frame = ttk.LabelFrame(main_frame, text="楼梯序号", padding=5)
        n_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(n_frame, text="N =").pack(side=tk.LEFT, padx=(0, 5))
        self._n_entry = ttk.Entry(n_frame, width=10)
        self._n_entry.insert(0, str(self._state.n))
        self._n_entry.pack(side=tk.LEFT)
        
        # 绑定回车键到生成功能
        self._n_entry.bind("<Return>", lambda e: self._handle_generate())
        
        # === 主题选择 ===
        theme_frame = ttk.LabelFrame(main_frame, text="主题样式", padding=5)
        theme_frame.pack(fill=tk.X, pady=(0, 10))
        
        self._theme_combo = ttk.Combobox(
            theme_frame,
            values=self.THEMES,
            state="readonly",
            width=15
        )
        self._theme_combo.pack(side=tk.LEFT)
        
        # 设置初始选中项索引
        try:
            initial_index = self.THEMES.index(self._state.theme)
            self._theme_combo.current(initial_index)
        except ValueError:
            self._theme_combo.current(0)  # 默认选择第一个
        
        # === 缩放比例 ===
        scale_frame = ttk.LabelFrame(main_frame, text="缩放比例", padding=5)
        scale_frame.pack(fill=tk.X, pady=(0, 10))
        
        self._scale_slider = ttk.Scale(
            scale_frame,
            from_=0.5,
            to=3.0,
            value=self._state.scale,
            orient=tk.HORIZONTAL,
            length=200,
            command=self._on_scale_change,  # 实时更新标签
        )
        self._scale_slider.pack(side=tk.LEFT, padx=(0, 10))
        
        self._scale_label = ttk.Label(scale_frame, text=f"{self._state.scale:.1f}x")
        self._scale_label.pack(side=tk.LEFT)
        
        # === 操作按钮区域 ===
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 生成按钮（主要操作）
        generate_btn = ttk.Button(
            action_frame, 
            text="🎲 生成", 
            command=self._handle_generate,
            width=10
        )
        generate_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 保存按钮（仅保存设置）
        save_btn = ttk.Button(
            action_frame, 
            text="💾 保存", 
            command=self._handle_save,
            width=10
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # === 导出按钮区域 ===
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 导出按钮
        export_btn = ttk.Button(
            export_frame, 
            text="📷 导出PNG", 
            command=self._handle_export,
            width=12
        )
        export_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 关闭按钮
        close_btn = ttk.Button(
            export_frame, 
            text="❌ 关闭", 
            command=self._handle_close,
            width=8
        )
        close_btn.pack(side=tk.RIGHT)
        
        # === 配置导出/导入区域 ===
        config_frame = ttk.LabelFrame(main_frame, text="配置管理", padding=5)
        config_frame.pack(fill=tk.X, pady=(10, 0))
        
        export_cfg_btn = ttk.Button(
            config_frame,
            text="📤 导出配置",
            command=self._handle_export_config,
            width=12
        )
        export_cfg_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        import_cfg_btn = ttk.Button(
            config_frame,
            text="📥 导入配置",
            command=self._handle_import_config,
            width=12
        )
        import_cfg_btn.pack(side=tk.LEFT)
        
        # === 状态栏 ===
        self._status_label = ttk.Label(
            main_frame, 
            text="就绪", 
            foreground="gray"
        )
        self._status_label.pack(fill=tk.X, pady=(10, 0))
    
    def _on_scale_change(self, value: str) -> None:
        """缩放滑块值变化时更新标签"""
        if self._scale_label:
            self._scale_label.config(text=f"{float(value):.1f}x")

    def _update_state_from_ui(self) -> bool:
        """从 UI 读取并更新状态，返回是否成功"""
        try:
            # 读取并验证 N 值
            n_text = self._n_entry.get() if self._n_entry else ""
            n = int(n_text)
            if n < 1:
                self._set_status("错误: N 必须为正整数", error=True)
                return False
            
            # 更新状态
            self._state.n = n
            # 直接从 Combobox 获取当前选中的值
            theme_value = self._theme_combo.get() if self._theme_combo else "minimal"
            self._state.theme = theme_value
            # 直接从 Scale 获取当前值
            scale_value = self._scale_slider.get() if self._scale_slider else 1.0
            self._state.scale = scale_value
            return True
        except ValueError:
            self._set_status("错误: N 必须为整数", error=True)
            return False
    
    def _handle_save(self) -> None:
        """处理保存按钮点击 - 仅保存设置，不刷新数据"""
        if not self._update_state_from_ui():
            return
            
        self._set_status("正在保存设置...")
        
        # 触发回调
        if self._on_save:
            self._on_save(self._state)
        
        self._set_status(f"已保存: 主题={self._state.theme}, 缩放={self._state.scale:.1f}x")
    
    def _handle_generate(self) -> None:
        """处理生成按钮点击 - 重新生成数据"""
        if not self._update_state_from_ui():
            return
            
        self._set_status(f"正在生成 N={self._state.n}...")
        
        # 触发回调
        if self._on_generate:
            self._on_generate(self._state)
        
        self._set_status(f"已生成: N={self._state.n}, 主题={self._state.theme}")
    
    def _handle_export(self) -> None:
        """处理导出按钮点击"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG 图片", "*.png"), ("所有文件", "*.*")],
            title="导出为 PNG"
        )
        
        if file_path:
            self._set_status("正在导出...")
            if self._on_export:
                self._on_export(file_path)
            self._set_status(f"已导出: {file_path}")
    
    def _handle_close(self) -> None:
        """处理关闭按钮点击"""
        self._is_closed = True
        if self._on_close:
            self._on_close()
        if self._root:
            self._root.destroy()
    
    def _handle_export_config(self) -> None:
        """处理导出配置按钮点击"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON 配置", "*.json"), ("所有文件", "*.*")],
            title="导出配置"
        )
        
        if file_path:
            self._set_status("正在导出配置...")
            if self._on_export_config:
                self._on_export_config(file_path)
            self._set_status(f"配置已导出: {file_path}")
    
    def _handle_import_config(self) -> None:
        """处理导入配置按钮点击"""
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON 配置", "*.json"), ("所有文件", "*.*")],
            title="导入配置"
        )
        
        if file_path:
            self._set_status("正在导入配置...")
            if self._on_import_config:
                self._on_import_config(file_path)
            self._set_status(f"配置已导入: {file_path}")
    
    def _set_status(self, message: str, error: bool = False) -> None:
        """设置状态栏消息"""
        if self._status_label and self._root:
            self._status_label.config(
                text=message,
                foreground="red" if error else "gray"
            )
            self._root.update()
    
    def update(self) -> None:
        """更新 UI，处理事件队列"""
        if self._root and not self._is_closed:
            try:
                self._root.update()
            except tk.TclError:
                self._is_closed = True
    
    def is_closed(self) -> bool:
        """检查窗口是否已关闭"""
        return self._is_closed
    
    @property
    def state(self) -> PanelState:
        """获取当前状态"""
        return self._state.copy()
