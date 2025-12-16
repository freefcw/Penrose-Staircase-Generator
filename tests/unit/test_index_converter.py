"""IndexConverter 单元测试"""
import pytest
from core.index_converter import IndexConverter
from core.staircase import StaircaseConfig


class TestIndexConverter:
    """测试 IndexConverter 索引转换器"""

    @pytest.fixture
    def config(self) -> StaircaseConfig:
        """创建测试用的楼梯配置 (A=9, B=5, C=5, D=9)"""
        return StaircaseConfig(a=9, b=5, c=5, d=9, step_length=6.0)
    
    @pytest.fixture
    def small_config(self) -> StaircaseConfig:
        """创建小型测试配置 (A=3, B=2, C=2, D=3)"""
        return StaircaseConfig(a=3, b=2, c=2, d=3, step_length=2.0)

    def test_draw_to_walking_zone_a(self, config: StaircaseConfig) -> None:
        """测试 A 区绘制索引转换为行走索引"""
        # A 区绘制索引 0-7 (共 8 个，即 A-1=8)
        # A 区在行走顺序的末尾
        a_count = config.a - 1  # 8
        d_count = config.d - 1  # 8
        b_count = config.b - 1  # 4
        c_count = config.c - 1  # 4
        expected_offset = d_count + c_count + b_count  # 16
        
        for draw_idx in range(a_count):
            walking_idx = IndexConverter.draw_to_walking(draw_idx, config)
            assert walking_idx == expected_offset + draw_idx

    def test_draw_to_walking_zone_d(self, config: StaircaseConfig) -> None:
        """测试 D 区绘制索引转换为行走索引"""
        # D 区绘制索引 8-15 (在 A 区后，共 8 个，即 D-1=8)
        # D 区在行走顺序的开头
        a_count = config.a - 1  # 8
        d_count = config.d - 1  # 8
        
        for i in range(d_count):
            draw_idx = a_count + i
            walking_idx = IndexConverter.draw_to_walking(draw_idx, config)
            assert walking_idx == i

    def test_draw_to_walking_zone_b(self, config: StaircaseConfig) -> None:
        """测试 B 区绘制索引转换为行走索引（反转）"""
        # B 区绘制索引 16-19 (在 A+D 后，共 4 个，即 B-1=4)
        # B 区在行走顺序的 C 区后面，且被反转
        a_count = config.a - 1  # 8
        d_count = config.d - 1  # 8
        b_count = config.b - 1  # 4
        c_count = config.c - 1  # 4
        
        # 绘制顺序的 B 区最后一个 -> 行走顺序 B 区的第一个
        draw_idx = a_count + d_count + b_count - 1  # 19
        walking_idx = IndexConverter.draw_to_walking(draw_idx, config)
        assert walking_idx == d_count + c_count  # 12

    def test_draw_to_walking_zone_c(self, config: StaircaseConfig) -> None:
        """测试 C 区绘制索引转换为行走索引（反转）"""
        # C 区绘制索引 20-23 (在 A+D+B 后，共 4 个，即 C-1=4)
        # C 区在行走顺序的 D 区后面，且被反转
        a_count = config.a - 1  # 8
        d_count = config.d - 1  # 8
        b_count = config.b - 1  # 4
        c_count = config.c - 1  # 4
        
        # 绘制顺序的 C 区最后一个 -> 行走顺序 C 区的第一个
        draw_idx = a_count + d_count + b_count + c_count - 1  # 23
        walking_idx = IndexConverter.draw_to_walking(draw_idx, config)
        assert walking_idx == d_count  # 8

    def test_walking_to_draw_zone_d(self, config: StaircaseConfig) -> None:
        """测试 D 区行走索引转换为绘制索引"""
        a_count = config.a - 1
        d_count = config.d - 1
        
        for walking_idx in range(d_count):
            draw_idx = IndexConverter.walking_to_draw(walking_idx, config)
            assert draw_idx == a_count + walking_idx

    def test_walking_to_draw_zone_a(self, config: StaircaseConfig) -> None:
        """测试 A 区行走索引转换为绘制索引"""
        a_count = config.a - 1
        d_count = config.d - 1
        b_count = config.b - 1
        c_count = config.c - 1
        total = a_count + d_count + b_count + c_count
        
        # A 区在行走顺序末尾
        for i in range(a_count):
            walking_idx = d_count + c_count + b_count + i
            draw_idx = IndexConverter.walking_to_draw(walking_idx, config)
            assert draw_idx == i

    def test_roundtrip_conversion(self, config: StaircaseConfig) -> None:
        """测试双向转换的一致性：draw -> walking -> draw"""
        total = config.total_steps
        
        for draw_idx in range(total):
            walking_idx = IndexConverter.draw_to_walking(draw_idx, config)
            restored_draw_idx = IndexConverter.walking_to_draw(walking_idx, config)
            assert restored_draw_idx == draw_idx, \
                f"Roundtrip failed: {draw_idx} -> {walking_idx} -> {restored_draw_idx}"

    def test_roundtrip_conversion_reverse(self, config: StaircaseConfig) -> None:
        """测试双向转换的一致性：walking -> draw -> walking"""
        total = config.total_steps
        
        for walking_idx in range(total):
            draw_idx = IndexConverter.walking_to_draw(walking_idx, config)
            restored_walking_idx = IndexConverter.draw_to_walking(draw_idx, config)
            assert restored_walking_idx == walking_idx, \
                f"Roundtrip failed: {walking_idx} -> {draw_idx} -> {restored_walking_idx}"

    def test_small_config(self, small_config: StaircaseConfig) -> None:
        """测试小型配置的索引转换"""
        total = small_config.total_steps  # 6
        
        # 验证双向转换
        for i in range(total):
            walking = IndexConverter.draw_to_walking(i, small_config)
            draw = IndexConverter.walking_to_draw(walking, small_config)
            assert draw == i
