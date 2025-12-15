"""pstairs 核心算法单元测试"""
import pytest

from pstairs import PenroseStaircase


class TestPenroseStaircaseInit:
    """测试 PenroseStaircase 初始化"""

    def test_init_with_valid_n(self) -> None:
        """测试有效 n 值的初始化"""
        ps = PenroseStaircase(10)
        assert ps.valid is True
        assert ps.a > 0
        assert ps.b > 0
        assert ps.c > 0
        assert ps.d > 0

    def test_init_with_n_one(self) -> None:
        """测试 n=1 的边界情况"""
        ps = PenroseStaircase(1)
        assert ps.valid is True
        # n=1 的实际值（根据算法计算）
        assert ps.a == 3
        assert ps.b == 2
        assert int(ps.c) == 2
        assert ps.d == 3

    def test_init_with_n_190(self) -> None:
        """测试 n=190 的已知结果"""
        ps = PenroseStaircase(190)
        assert ps.valid is True
        # 实际算法输出
        assert ps.a == 9
        assert ps.b == 5
        assert int(ps.c) == 5
        assert ps.d == 9

    @pytest.mark.parametrize("n", [0, -1, -100])
    def test_init_with_invalid_n(self, n: int) -> None:
        """测试无效 n 值"""
        ps = PenroseStaircase(n)
        assert ps.valid is False


class TestPenroseStaircaseDirectFormula:
    """测试直接公式方法"""

    def test_direct_a_matches_iterative(self) -> None:
        """验证 DIRECT_A 与迭代算法结果一致"""
        ps = PenroseStaircase(100)
        assert ps.DIRECT_A(100) == ps.A_of_NP(100)

    def test_direct_b_matches_iterative(self) -> None:
        """验证 DIRECT_B 与迭代算法结果一致"""
        ps = PenroseStaircase(100)
        assert ps.DIRECT_B(100) == ps.B_of_NP(100)

    def test_direct_c_matches_iterative(self) -> None:
        """验证 DIRECT_C 与迭代算法结果一致"""
        ps = PenroseStaircase(100)
        assert int(ps.DIRECT_C(100)) == ps.C_of_NP(100)

    def test_direct_d_returns_valid_value(self) -> None:
        """验证 DIRECT_D 返回有效值"""
        ps = PenroseStaircase(100)
        d_value = ps.DIRECT_D(100)
        # D 应该是正数
        assert d_value > 0
        # D 应该与初始化时计算的值接近
        assert abs(round(d_value) - ps.d) <= 1  # 允许微小差异


class TestPenroseStaircaseConstraints:
    """测试楼梯约束条件"""

    @pytest.mark.parametrize("n", [1, 10, 50, 100, 190, 500])
    def test_stairsum_is_even(self, n: int) -> None:
        """楼梯和必须是偶数"""
        ps = PenroseStaircase(n)
        assert ps.g % 2 == 0

    @pytest.mark.parametrize("n", [1, 10, 50, 100, 190])
    def test_d_equals_a_plus_b_minus_c(self, n: int) -> None:
        """D = A + B - C 约束"""
        ps = PenroseStaircase(n)
        assert ps.d == ps.a + ps.b - int(ps.c)

    @pytest.mark.parametrize("n", [1, 10, 50, 100, 190])
    def test_all_zones_at_least_2(self, n: int) -> None:
        """所有区域至少有 2 个台阶"""
        ps = PenroseStaircase(n)
        assert ps.a >= 2
        assert ps.b >= 2
        assert int(ps.c) >= 2
        assert ps.d >= 2


class TestPenroseStaircaseSequence:
    """测试楼梯序列属性"""

    def test_sequence_is_monotonic(self) -> None:
        """楼梯和序列是单调递增的"""
        prev_g = 0
        for n in range(1, 51):
            ps = PenroseStaircase(n)
            assert ps.g >= prev_g
            prev_g = ps.g

    def test_step_length_positive(self) -> None:
        """台阶长度必须为正"""
        for n in [1, 10, 100, 500]:
            ps = PenroseStaircase(n)
            assert ps.l > 0
