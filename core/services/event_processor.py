"""
事件处理器 - 处理应用事件循环

遵循单一职责原则，专注于事件处理。
"""
from __future__ import annotations

import time
from typing import TYPE_CHECKING, Protocol, final

from graphics import GraphicsError

if TYPE_CHECKING:
    from graphics import GraphWin


class Updatable(Protocol):
    """可更新的对象协议"""
    
    def update(self) -> None:
        """更新状态"""
        ...
    
    def is_closed(self) -> bool:
        """检查是否已关闭"""
        ...


@final
class EventProcessor:
    """
    事件处理器
    
    职责：
    - 运行事件循环
    - 检测窗口关闭和键盘事件
    - 更新 UI 面板
    """
    
    # 事件循环间隔（毫秒）
    LOOP_INTERVAL_MS = 50
    
    def __init__(self, on_close: callable | None = None):  # type: ignore
        """
        初始化事件处理器
        
        Args:
            on_close: 关闭回调函数
        """
        self._should_close = False
        self._on_close = on_close
    
    @property
    def should_close(self) -> bool:
        """是否应该关闭"""
        return self._should_close
    
    def request_close(self) -> None:
        """请求关闭"""
        self._should_close = True
    
    def run_loop(
        self,
        window: GraphWin | None,
        updatables: list[Updatable],
    ) -> None:
        """
        运行事件循环
        
        Args:
            window: 主窗口（可选）
            updatables: 需要更新的对象列表
        """
        while not self._should_close:
            # 检查主窗口
            if window is not None:
                if window.isClosed():
                    break
                
                try:
                    key = window.checkKey()
                    if key and key.lower() == 'q':
                        break
                except GraphicsError:
                    break
            
            # 更新所有可更新对象
            for obj in updatables:
                obj.update()
                if obj.is_closed():
                    self._should_close = True
                    break
            
            # 避免 CPU 占用过高
            time.sleep(self.LOOP_INTERVAL_MS / 1000.0)
        
        if self._on_close:
            self._on_close()
