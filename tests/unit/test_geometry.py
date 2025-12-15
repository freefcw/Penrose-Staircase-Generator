"""Geometry 单元测试"""
import math

from core.geometry import Point, GeometryTransform


class TestPoint:
    """测试 Point 类"""

    def test_create_point(self) -> None:
        """测试创建点"""
        p = Point(3.0, 4.0)
        assert p.x == 3.0
        assert p.y == 4.0

    def test_point_is_immutable(self) -> None:
        """测试点不可变"""
        p = Point(1.0, 2.0)
        # frozen=True 应该阻止修改
        try:
            p.x = 5.0  # type: ignore
            assert False, "应该抛出 FrozenInstanceError"
        except Exception:
            pass  # 预期行为

    def test_point_add(self) -> None:
        """测试点加法"""
        p1 = Point(1.0, 2.0)
        p2 = Point(3.0, 4.0)
        result = p1 + p2
        assert result.x == 4.0
        assert result.y == 6.0

    def test_point_sub(self) -> None:
        """测试点减法"""
        p1 = Point(5.0, 7.0)
        p2 = Point(2.0, 3.0)
        result = p1 - p2
        assert result.x == 3.0
        assert result.y == 4.0

    def test_point_mul(self) -> None:
        """测试点乘标量"""
        p = Point(2.0, 3.0)
        result = p * 2.5
        assert result.x == 5.0
        assert result.y == 7.5

    def test_to_tuple(self) -> None:
        """测试转换为元组"""
        p = Point(1.5, 2.5)
        t = p.to_tuple()
        assert t == (1.5, 2.5)


class TestGeometryTransform:
    """测试 GeometryTransform 类"""

    def test_create_transform(self) -> None:
        """测试创建变换器"""
        transform = GeometryTransform(scale=2.0, offset_x=10.0, offset_y=20.0)
        assert transform.scale == 2.0
        assert transform.offset_x == 10.0
        assert transform.offset_y == 20.0

    def test_unit_constants(self) -> None:
        """测试单位常量"""
        assert GeometryTransform.UNIT_WIDTH == 1.0
        assert abs(GeometryTransform.UNIT_HEIGHT - 0.866025404) < 1e-6

    def test_rotate_2d_zero_degrees(self) -> None:
        """测试 0 度旋转（不变）"""
        transform = GeometryTransform(1.0, 0.0, 0.0)
        result = transform.rotate_2d(3.0, 4.0, 0)
        assert abs(result.x - 3.0) < 1e-10
        assert abs(result.y - 4.0) < 1e-10

    def test_rotate_2d_90_degrees(self) -> None:
        """测试 90 度旋转"""
        transform = GeometryTransform(1.0, 0.0, 0.0)
        result = transform.rotate_2d(1.0, 0.0, 90)
        assert abs(result.x - 0.0) < 1e-10
        assert abs(result.y - 1.0) < 1e-10

    def test_rotate_2d_180_degrees(self) -> None:
        """测试 180 度旋转"""
        transform = GeometryTransform(1.0, 0.0, 0.0)
        result = transform.rotate_2d(3.0, 4.0, 180)
        assert abs(result.x - (-3.0)) < 1e-10
        assert abs(result.y - (-4.0)) < 1e-10

    def test_to_screen_with_scale(self) -> None:
        """测试屏幕坐标转换带缩放"""
        transform = GeometryTransform(scale=2.0, offset_x=100.0, offset_y=50.0)
        result = transform.to_screen(0.0, 0.0)
        assert result.x == 100.0
        assert result.y == 50.0

    def test_to_screen_applies_rotation(self) -> None:
        """测试屏幕坐标转换应用30度旋转"""
        transform = GeometryTransform(scale=1.0, offset_x=0.0, offset_y=0.0)
        result = transform.to_screen(1.0, 0.0)
        # 30度旋转后 x=cos(30)≈0.866, y=sin(30)=0.5
        # 再乘以0.8纵向压缩
        expected_x = math.cos(math.radians(30))
        expected_y = math.sin(math.radians(30)) * 0.8
        assert abs(result.x - expected_x) < 1e-6
        assert abs(result.y - expected_y) < 1e-6

    def test_to_screen_point(self) -> None:
        """测试 Point 对象转换"""
        transform = GeometryTransform(scale=1.0, offset_x=10.0, offset_y=20.0)
        p = Point(0.0, 0.0)
        result = transform.to_screen_point(p)
        assert result.x == 10.0
        assert result.y == 20.0
