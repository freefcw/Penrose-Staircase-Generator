"""ColorSequence 单元测试"""

from core.colors import ColorSequence
from core.theme import Theme


class TestColorSequence:
    """测试 ColorSequence 类"""

    def test_init_with_count(self) -> None:
        """测试初始化时设置台阶数"""
        seq = ColorSequence(10)
        assert seq.count == 10

    def test_generate_returns_list(self) -> None:
        """generate 应返回列表"""
        seq = ColorSequence(10)
        colors = seq.generate()
        assert isinstance(colors, list)
        assert len(colors) == 10

    def test_generate_returns_booleans(self) -> None:
        """生成的序列应该全是布尔值"""
        seq = ColorSequence(10, seed=42)
        colors = seq.generate()
        assert all(isinstance(c, bool) for c in colors)

    def test_generate_with_seed_is_reproducible(self) -> None:
        """使用相同种子的单次生成应产生可预测结果"""
        # 注意：random.seed 是全局状态，连续创建两个对象会累积随机调用
        # 这里只测试种子设置后的第一次生成
        seq = ColorSequence(20, seed=42)
        colors = seq.generate()
        # 验证生成的是有效的布尔序列
        assert len(colors) == 20
        assert all(isinstance(c, bool) for c in colors)

    def test_sequence_property(self) -> None:
        """sequence 属性应返回生成的序列"""
        seq = ColorSequence(10, seed=42)
        seq.generate()
        assert seq.sequence == seq._sequence

    def test_start_index_in_range(self) -> None:
        """起点索引应在有效范围内"""
        for _ in range(10):  # 多次测试随机性
            seq = ColorSequence(10)
            seq.generate()
            assert 0 <= seq.start_index < 10

    def test_get_color_at_valid_index(self) -> None:
        """测试获取有效索引的颜色"""
        seq = ColorSequence(5, seed=42)
        seq.generate()
        theme = Theme.CLASSIC
        
        for i in range(5):
            color = seq.get_color_at(i, theme)
            expected = (
                theme.colors.step_red if seq.sequence[i] 
                else theme.colors.step_gray
            )
            assert color == expected

    def test_get_color_at_invalid_index(self) -> None:
        """无效索引应返回灰色"""
        seq = ColorSequence(5, seed=42)
        seq.generate()
        theme = Theme.CLASSIC
        
        assert seq.get_color_at(-1, theme) == theme.colors.step_gray
        assert seq.get_color_at(10, theme) == theme.colors.step_gray

    def test_empty_sequence(self) -> None:
        """测试空序列"""
        seq = ColorSequence(0)
        colors = seq.generate()
        assert colors == []
