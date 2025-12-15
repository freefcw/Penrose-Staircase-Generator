"""
UI 面板基类 - 提取公共逻辑

遵循 DRY 原则，统一 UI 面板的公共行为。
"""
from __future__ import annotations

import tkinter as tk
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final


@dataclass
class PanelConfig:
    """面板配置"""
    
    title: str
    width: int
    height: int
    x: int = 50
    y: int = 50
    resizable: bool = False
    padding: int = 15


class BasePanel(ABC):
    """
    UI 面板基类
    
    提供公共功能：
    - 窗口创建和管理
    - 关闭状态跟踪
    - UI 更新机制
    """
    
    def __init__(self, config: PanelConfig):
        """
        初始化面板
        
        Args:
            config: 面板配置
        """
        self._config = config
        self._root: tk.Toplevel | None = None
        self._is_closed = False
    
    @property
    def is_visible(self) -> bool:
        """面板是否可见"""
        return self._root is not None and not self._is_closed
    
    def show(self, parent: tk.Tk | None = None) -> None:
        """
        显示面板
        
        Args:
            parent: 父窗口
        """
        if parent:
            self._root = tk.Toplevel(parent)
        else:
            self._root = tk.Toplevel()
        
        self._root.title(self._config.title)
        self._root.geometry(
            f"{self._config.width}x{self._config.height}"
            f"+{self._config.x}+{self._config.y}"
        )
        self._root.resizable(self._config.resizable, self._config.resizable)
        self._root.protocol("WM_DELETE_WINDOW", self._handle_close)
        
        self._build_ui()
    
    @abstractmethod
    def _build_ui(self) -> None:
        """构建 UI 组件（子类实现）"""
        pass
    
    def _handle_close(self) -> None:
        """处理窗口关闭"""
        self._is_closed = True
        if self._root:
            self._root.destroy()
    
    def update(self) -> None:
        """更新 UI，处理事件队列"""
        if self._root and not self._is_closed:
            try:
                self._root.update()
            except tk.TclError:
                self._is_closed = True
    
    @final
    def is_closed(self) -> bool:
        """检查面板是否已关闭"""
        return self._is_closed
    
    @final
    def close(self) -> None:
        """关闭面板"""
        self._handle_close()
