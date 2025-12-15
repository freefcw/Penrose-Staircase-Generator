"""StaircaseConfig 和 StaircaseModel 单元测试"""
import pytest

from core.staircase import StaircaseConfig, StaircaseModel, StepPosition, Zone


class TestStaircaseConfig:
    """测试 StaircaseConfig 类"""

    def test_init_valid_config(self) -> None:
        """测试有效配置的初始化"""
        config = StaircaseConfig(a=4, b=3, c=2, d=3, step_length=1.0)
        assert config.a == 4
        assert config.b == 3
        assert config.c == 2
        assert config.d == 3

    def test_total_steps_calculation(self) -> None:
        """测试总台阶数计算"""
        config = StaircaseConfig(a=4, b=3, c=2, d=3, step_length=1.0)
        # total = a + b + c + d - 4 = 4 + 3 + 2 + 3 - 4 = 8
        assert config.total_steps == 8

    def test_wall_height(self) -> None:
        """测试墙体高度计算"""
        config = StaircaseConfig(a=4, b=3, c=2, d=5, step_length=1.0)
        assert config.wall_height == 10  # d * 2

    def test_zone_step_counts(self) -> None:
        """测试各区域台阶数"""
        config = StaircaseConfig(a=4, b=3, c=2, d=3, step_length=1.0)
        counts = config.zone_step_counts
        assert counts[Zone.A] == 3  # a - 1
        assert counts[Zone.B] == 2  # b - 1
        assert counts[Zone.C] == 1  # c - 1
        assert counts[Zone.D] == 2  # d - 1

    def test_invalid_zone_values_raises(self) -> None:
        """区域值小于 2 应抛出异常"""
        with pytest.raises(ValueError):
            StaircaseConfig(a=1, b=2, c=2, d=2, step_length=1.0)

    def test_invalid_step_length_raises(self) -> None:
        """台阶长度非正应抛出异常"""
        with pytest.raises(ValueError):
            StaircaseConfig(a=2, b=2, c=2, d=2, step_length=0)
        with pytest.raises(ValueError):
            StaircaseConfig(a=2, b=2, c=2, d=2, step_length=-1.0)


class TestStepPosition:
    """测试 StepPosition 类"""

    def test_center_calculation(self) -> None:
        """测试中心点计算"""
        pos = StepPosition(
            p1=(0.0, 0.0),
            p2=(0.0, 1.0),
            p3=(1.0, 1.0),
            p4=(1.0, 0.0),
        )
        center = pos.center
        assert center == (0.5, 0.5)


class TestStaircaseModel:
    """测试 StaircaseModel 类"""

    @pytest.fixture
    def config(self) -> StaircaseConfig:
        """创建测试配置"""
        return StaircaseConfig(a=4, b=3, c=2, d=3, step_length=1.0)

    def test_init_with_config(self, config: StaircaseConfig) -> None:
        """测试使用配置初始化"""
        model = StaircaseModel(config)
        assert model.config == config
        assert model.step_positions == []
        assert model.color_sequence == []
        assert model.start_step_index == 0

    def test_add_step_position(self, config: StaircaseConfig) -> None:
        """测试添加台阶位置"""
        model = StaircaseModel(config)
        pos = StepPosition(
            p1=(0.0, 0.0),
            p2=(0.0, 1.0),
            p3=(1.0, 1.0),
            p4=(1.0, 0.0),
        )
        model.add_step_position(pos)
        assert len(model.step_positions) == 1
        assert model.step_positions[0] == pos

    def test_get_step_position(self, config: StaircaseConfig) -> None:
        """测试获取台阶位置"""
        model = StaircaseModel(config)
        pos = StepPosition(
            p1=(0.0, 0.0),
            p2=(0.0, 1.0),
            p3=(1.0, 1.0),
            p4=(1.0, 0.0),
        )
        model.add_step_position(pos)
        assert model.get_step_position(0) == pos
        assert model.get_step_position(1) is None
        assert model.get_step_position(-1) is None

    def test_clear_positions(self, config: StaircaseConfig) -> None:
        """测试清空位置数据"""
        model = StaircaseModel(config)
        pos = StepPosition(
            p1=(0.0, 0.0),
            p2=(0.0, 1.0),
            p3=(1.0, 1.0),
            p4=(1.0, 0.0),
        )
        model.add_step_position(pos)
        model.clear_positions()
        assert model.step_positions == []


class TestZone:
    """测试 Zone 枚举"""

    def test_zone_values(self) -> None:
        """测试区域枚举值"""
        assert Zone.A.value == "A"
        assert Zone.B.value == "B"
        assert Zone.C.value == "C"
        assert Zone.D.value == "D"
