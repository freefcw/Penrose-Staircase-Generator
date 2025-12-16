"""HighlightManager 单元测试"""
import pytest
from unittest.mock import MagicMock, patch

from core.geometry import GeometryTransform
from core.staircase import StepPosition
from core.theme import RGB
from ui.highlight_manager import HighlightManager


class TestHighlightManager:
    """测试 HighlightManager 高亮管理器"""

    @pytest.fixture
    def mock_win(self) -> MagicMock:
        """创建模拟的 GraphWin"""
        win = MagicMock()
        win.isClosed.return_value = False
        return win

    @pytest.fixture
    def transform(self) -> GeometryTransform:
        """创建测试用的几何变换器"""
        return GeometryTransform(scale=50.0, offset_x=100.0, offset_y=200.0)

    @pytest.fixture
    def step_pos(self) -> StepPosition:
        """创建测试用的台阶位置"""
        return StepPosition(
            p1=(0.0, 0.0),
            p2=(0.5, 0.866),
            p3=(1.5, 0.866),
            p4=(1.0, 0.0),
        )

    @pytest.fixture
    def manager(self, mock_win: MagicMock, transform: GeometryTransform) -> HighlightManager:
        """创建 HighlightManager 实例"""
        return HighlightManager(mock_win, transform)

    def test_init(self, manager: HighlightManager, mock_win: MagicMock) -> None:
        """测试初始化"""
        assert manager._win == mock_win
        assert manager._current_highlight is None
        assert not manager.has_highlight

    def test_default_highlight_color(self, manager: HighlightManager) -> None:
        """测试默认高亮颜色"""
        assert manager._highlight_color == RGB(0, 255, 255)

    def test_custom_highlight_color(self, mock_win: MagicMock, transform: GeometryTransform) -> None:
        """测试自定义高亮颜色"""
        custom_color = RGB(255, 0, 255)
        manager = HighlightManager(mock_win, transform, highlight_color=custom_color)
        assert manager._highlight_color == custom_color

    @patch('ui.highlight_manager.GraphicsCanvas')
    def test_highlight_creates_polygon(
        self, 
        mock_canvas_class: MagicMock,
        manager: HighlightManager, 
        step_pos: StepPosition
    ) -> None:
        """测试高亮会创建多边形边框"""
        mock_canvas = MagicMock()
        mock_handle = MagicMock()
        mock_canvas.draw_polygon_outline.return_value = mock_handle
        mock_canvas_class.return_value = mock_canvas
        
        manager.highlight(step_pos)
        
        # 验证调用了 draw_polygon_outline
        mock_canvas.draw_polygon_outline.assert_called_once()
        
        # 验证保存了高亮句柄
        assert manager._current_highlight == mock_handle
        assert manager.has_highlight

    @patch('ui.highlight_manager.GraphicsCanvas')
    def test_highlight_clears_previous(
        self, 
        mock_canvas_class: MagicMock,
        manager: HighlightManager, 
        step_pos: StepPosition
    ) -> None:
        """测试高亮新台阶时会清除旧高亮"""
        mock_canvas = MagicMock()
        mock_handle1 = MagicMock()
        mock_handle2 = MagicMock()
        mock_canvas.draw_polygon_outline.side_effect = [mock_handle1, mock_handle2]
        mock_canvas_class.return_value = mock_canvas
        
        # 第一次高亮
        manager.highlight(step_pos)
        assert manager._current_highlight == mock_handle1
        
        # 第二次高亮应该清除第一个
        manager.highlight(step_pos)
        mock_handle1.undraw.assert_called_once()
        assert manager._current_highlight == mock_handle2

    def test_clear(self, manager: HighlightManager) -> None:
        """测试清除高亮"""
        mock_handle = MagicMock()
        manager._current_highlight = mock_handle
        
        manager.clear()
        
        mock_handle.undraw.assert_called_once()
        assert manager._current_highlight is None
        assert not manager.has_highlight

    def test_clear_handles_exception(self, manager: HighlightManager) -> None:
        """测试清除时的异常处理"""
        mock_handle = MagicMock()
        mock_handle.undraw.side_effect = Exception("Canvas error")
        manager._current_highlight = mock_handle
        
        # 不应该抛出异常
        manager.clear()
        
        assert manager._current_highlight is None

    def test_update_transform(self, manager: HighlightManager) -> None:
        """测试更新变换器"""
        mock_handle = MagicMock()
        manager._current_highlight = mock_handle
        
        new_transform = GeometryTransform(scale=100.0, offset_x=200.0, offset_y=300.0)
        manager.update_transform(new_transform)
        
        # 验证变换器已更新
        assert manager._transform == new_transform
        
        # 验证旧高亮已清除
        mock_handle.undraw.assert_called_once()
        assert manager._current_highlight is None

    def test_has_highlight_property(self, manager: HighlightManager) -> None:
        """测试 has_highlight 属性"""
        assert not manager.has_highlight
        
        manager._current_highlight = MagicMock()
        assert manager.has_highlight
        
        manager._current_highlight = None
        assert not manager.has_highlight
