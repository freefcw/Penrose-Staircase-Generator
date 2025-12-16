"""
高亮管理器 - 管理台阶高亮状态和渲染
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from core.geometry import GeometryTransform
from core.theme import RGB
from rendering.canvas import GraphicsCanvas, DrawHandle

if TYPE_CHECKING:
    from graphics import GraphWin
    from core.staircase import StepPosition


class HighlightManager:
    """
    台阶高亮管理器
    
    职责：
    - 管理当前高亮的台阶
    - 清除旧高亮
    - 绘制新高亮
    """
    
    # 默认高亮颜色（亮青色）
    DEFAULT_HIGHLIGHT_COLOR = RGB(0, 255, 255)
    # 默认线宽
    DEFAULT_LINE_WIDTH = 3
    
    def __init__(
        self, 
        win: GraphWin, 
        transform: GeometryTransform,
        highlight_color: RGB | None = None,
        line_width: int = DEFAULT_LINE_WIDTH,
    ):
        """
        初始化高亮管理器
        
        Args:
            win: 图形窗口
            transform: 几何变换器
            highlight_color: 高亮颜色
            line_width: 线宽
        """
        self._win = win
        self._transform = transform
        self._highlight_color = highlight_color or self.DEFAULT_HIGHLIGHT_COLOR
        self._line_width = line_width
        self._current_highlight: DrawHandle | None = None
    
    def highlight(self, step_pos: StepPosition) -> None:
        """
        高亮指定台阶
        
        Args:
            step_pos: 台阶位置信息
        """
        # 清除旧高亮
        self.clear()
        
        # 绘制新高亮
        canvas = GraphicsCanvas(self._win)
        
        # 将模型坐标转换为屏幕坐标（注意 Y 轴翻转）
        screen_points = [
            self._transform.to_screen(p[0], -p[1]) 
            for p in [step_pos.p1, step_pos.p2, step_pos.p3, step_pos.p4]
        ]
        
        self._current_highlight = canvas.draw_polygon_outline(
            screen_points, self._highlight_color, self._line_width
        )
    
    def clear(self) -> None:
        """清除当前高亮"""
        if self._current_highlight:
            try:
                self._current_highlight.undraw()
            except Exception:
                pass
            self._current_highlight = None
    
    def update_transform(self, transform: GeometryTransform) -> None:
        """
        更新几何变换器
        
        在窗口重新渲染后调用
        """
        self._transform = transform
        # 清除旧高亮（因为变换已改变）
        self.clear()
    
    @property
    def has_highlight(self) -> bool:
        """是否有当前高亮"""
        return self._current_highlight is not None
