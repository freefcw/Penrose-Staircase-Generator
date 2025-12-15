"""StateManager 单元测试"""

from core.services.state_manager import StateManager, AppState
from core.theme import Theme


class TestStateManager:
    """测试 StateManager 类"""

    def test_init(self) -> None:
        """测试初始化"""
        manager = StateManager(n=10, theme=Theme.CLASSIC, export_scale=2.0)
        assert manager.n == 10
        assert manager.theme == Theme.CLASSIC
        assert manager.export_scale == 2.0
        assert manager.preview_scale == 1.6

    def test_update_n(self) -> None:
        """测试更新 N 值"""
        manager = StateManager(n=10, theme=Theme.CLASSIC)
        
        # 值改变时返回 True
        assert manager.update_n(20) is True
        assert manager.n == 20
        
        # 值不变时返回 False
        assert manager.update_n(20) is False

    def test_update_n_invalidates_cache(self) -> None:
        """更新 N 应使缓存失效"""
        manager = StateManager(n=10, theme=Theme.CLASSIC)
        manager.compute_and_cache()
        assert manager.has_valid_cache()
        
        manager.update_n(20)
        assert not manager.has_valid_cache()

    def test_update_theme(self) -> None:
        """测试更新主题"""
        manager = StateManager(n=10, theme=Theme.CLASSIC)
        
        assert manager.update_theme(Theme.MINIMAL) is True
        assert manager.theme == Theme.MINIMAL
        
        assert manager.update_theme(Theme.MINIMAL) is False

    def test_update_export_scale(self) -> None:
        """测试更新导出缩放"""
        manager = StateManager(n=10, theme=Theme.CLASSIC)
        manager.update_export_scale(3.0)
        assert manager.export_scale == 3.0

    def test_compute_and_cache(self) -> None:
        """测试计算并缓存"""
        manager = StateManager(n=10, theme=Theme.CLASSIC)
        result = manager.compute_and_cache()
        
        assert result is not None
        config, model = result
        assert config.total_steps > 0
        assert len(model.color_sequence) == config.total_steps
        assert manager.has_valid_cache()

    def test_compute_and_cache_with_invalid_n(self) -> None:
        """无效 N 值应返回 None"""
        manager = StateManager(n=-1, theme=Theme.CLASSIC)
        result = manager.compute_and_cache()
        assert result is None

    def test_get_or_compute_uses_cache(self) -> None:
        """get_or_compute 应使用缓存"""
        manager = StateManager(n=10, theme=Theme.CLASSIC)
        
        # 第一次调用会计算
        result1 = manager.get_or_compute()
        assert result1 is not None
        
        # 第二次调用应返回相同的缓存对象
        result2 = manager.get_or_compute()
        assert result2 is not None
        assert result1[0] is result2[0]  # 同一个 config 对象
        assert result1[1] is result2[1]  # 同一个 model 对象

    def test_invalidate_cache(self) -> None:
        """测试缓存失效"""
        manager = StateManager(n=10, theme=Theme.CLASSIC)
        manager.compute_and_cache()
        assert manager.has_valid_cache()
        
        manager.invalidate_cache()
        assert not manager.has_valid_cache()

    def test_get_state(self) -> None:
        """测试获取状态快照"""
        manager = StateManager(n=10, theme=Theme.CLASSIC, export_scale=2.0)
        state = manager.get_state()
        
        assert isinstance(state, AppState)
        assert state.n == 10
        assert state.theme == Theme.CLASSIC
        assert state.export_scale == 2.0
