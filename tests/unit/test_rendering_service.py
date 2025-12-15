"""RenderingService 单元测试

注意：RenderingService 依赖 graphics.py（Tkinter），部分测试需要 GUI 环境。
这里只测试不需要 GUI 的功能。
"""
import pytest

from core.staircase import StaircaseConfig


# 检查是否有 GUI 环境
def _has_display() -> bool:
    """检查是否有可用的显示环境"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.destroy()
        return True
    except Exception:
        return False


# 标记需要 GUI 的测试
requires_display = pytest.mark.skipif(
    not _has_display(),
    reason="需要 GUI 环境（Tkinter/Tcl）"
)


class TestLayoutCalculation:
    """测试布局计算（不需要 GUI）"""

    @pytest.fixture
    def config(self) -> StaircaseConfig:
        """创建测试配置"""
        return StaircaseConfig(a=4, b=3, c=2, d=3, step_length=1.0)

    @requires_display
    def test_calculate_layout(self, config: StaircaseConfig) -> None:
        """测试布局计算"""
        from core.services.rendering_service import RenderingService, LayoutInfo
        
        layout = RenderingService.calculate_layout(config)
        
        assert isinstance(layout, LayoutInfo)
        assert layout.window_width > 0
        assert layout.window_height > 0
        assert layout.stair_height > 0
        assert layout.zoom > 0

    @requires_display
    def test_calculate_layout_with_scale(self, config: StaircaseConfig) -> None:
        """测试带缩放的布局计算"""
        from core.services.rendering_service import RenderingService
        
        layout1 = RenderingService.calculate_layout(config, scale=1.0)
        layout2 = RenderingService.calculate_layout(config, scale=2.0)
        
        # 2x 缩放应该产生更大的窗口
        assert layout2.window_width > layout1.window_width
        assert layout2.window_height > layout1.window_height
