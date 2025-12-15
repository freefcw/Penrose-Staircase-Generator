"""PenroseCalculator 单元测试"""
import pytest

from core.calculator import PenroseCalculator, PenroseResult
from core.staircase import StaircaseConfig


class TestPenroseCalculator:
    """测试 PenroseCalculator 计算器"""

    def test_calculate_returns_penrose_result(self) -> None:
        """calculate 应返回 PenroseResult 实例"""
        result = PenroseCalculator.calculate(10)
        assert isinstance(result, PenroseResult)

    def test_calculate_preserves_n(self) -> None:
        """结果中应保留原始 n 值"""
        for n in [1, 10, 100, 190]:
            result = PenroseCalculator.calculate(n)
            assert result.n == n

    def test_calculate_known_values(self) -> None:
        """测试 n=190 的结果"""
        result = PenroseCalculator.calculate(190)
        # 实际算法输出
        assert result.a == 9
        assert result.b == 5
        assert result.c == 5
        assert result.d == 9

    @pytest.mark.parametrize("invalid_n", [0, -1, -100])
    def test_calculate_invalid_n_raises(self, invalid_n: int) -> None:
        """无效 n 值应抛出 ValueError"""
        with pytest.raises(ValueError):
            PenroseCalculator.calculate(invalid_n)

    def test_calculate_non_integer_raises(self) -> None:
        """非整数 n 值应抛出 ValueError"""
        with pytest.raises(ValueError):
            PenroseCalculator.calculate(3.14)  # type: ignore


class TestPenroseResult:
    """测试 PenroseResult 数据类"""

    def test_to_config_returns_staircase_config(self) -> None:
        """to_config 应返回 StaircaseConfig 实例"""
        result = PenroseCalculator.calculate(10)
        config = result.to_config()
        assert isinstance(config, StaircaseConfig)

    def test_to_config_preserves_values(self) -> None:
        """to_config 应保留所有参数值"""
        result = PenroseCalculator.calculate(100)
        config = result.to_config()
        assert config.a == result.a
        assert config.b == result.b
        assert config.c == result.c
        assert config.d == result.d
        assert config.step_length == result.step_length

    def test_result_is_immutable(self) -> None:
        """PenroseResult 应该是不可变的"""
        result = PenroseCalculator.calculate(10)
        with pytest.raises(AttributeError):
            result.a = 999  # type: ignore


class TestPenroseCalculatorIsValid:
    """测试 is_valid 方法"""

    @pytest.mark.parametrize("valid_n", [1, 10, 100, 1000])
    def test_is_valid_positive_integers(self, valid_n: int) -> None:
        """正整数应该是有效的"""
        assert PenroseCalculator.is_valid(valid_n) is True

    @pytest.mark.parametrize("invalid_n", [0, -1, -100])
    def test_is_valid_non_positive_integers(self, invalid_n: int) -> None:
        """非正整数应该是无效的"""
        assert PenroseCalculator.is_valid(invalid_n) is False

    def test_is_valid_non_integer(self) -> None:
        """非整数应该是无效的"""
        assert PenroseCalculator.is_valid(3.14) is False  # type: ignore
        assert PenroseCalculator.is_valid("10") is False  # type: ignore
