"""Layout 单元测试"""
from core.layout import LayoutConstants, LabelOffset, LABEL_OFFSETS


class TestLayoutConstants:
    """测试 LayoutConstants 类"""

    def test_zoom_constants(self) -> None:
        """测试缩放常量"""
        assert LayoutConstants.ZOOM_BASE == 11.0
        assert LayoutConstants.ZOOM_DIVISOR == 0.1

    def test_sequence_constants(self) -> None:
        """测试序列区域常量"""
        assert LayoutConstants.SEQUENCE_COLS == 6
        assert LayoutConstants.SEQUENCE_BOX_SIZE == 20.0
        assert LayoutConstants.SEQUENCE_MARGIN == 5.0

    def test_font_constants(self) -> None:
        """测试字体常量"""
        assert LayoutConstants.FONT_SIZE_MIN == 5
        assert LayoutConstants.FONT_SIZE_MAX == 36
        assert LayoutConstants.LABEL_FONT_SIZE_MIN == 16

    def test_label_offset_constants(self) -> None:
        """测试标签偏移常量"""
        assert LayoutConstants.LABEL_OFFSET_A_Y == -25.0
        assert LayoutConstants.LABEL_OFFSET_B_Y == -25.0
        assert LayoutConstants.LABEL_OFFSET_C_X == 15.0
        assert LayoutConstants.LABEL_OFFSET_C_Y == 35.0
        assert LayoutConstants.LABEL_OFFSET_D_Y == 8.0


class TestLabelOffset:
    """测试 LabelOffset 类"""

    def test_create_offset(self) -> None:
        """测试创建偏移"""
        offset = LabelOffset(x=10.0, y=20.0)
        assert offset.x == 10.0
        assert offset.y == 20.0

    def test_default_values(self) -> None:
        """测试默认值"""
        offset = LabelOffset()
        assert offset.x == 0.0
        assert offset.y == 0.0

    def test_is_immutable(self) -> None:
        """测试不可变"""
        offset = LabelOffset(x=1.0, y=2.0)
        try:
            offset.x = 5.0  # type: ignore
            assert False, "应该抛出 FrozenInstanceError"
        except Exception:
            pass  # 预期行为


class TestLabelOffsets:
    """测试预定义的标签偏移"""

    def test_all_zones_defined(self) -> None:
        """测试所有区域都有定义"""
        assert "A" in LABEL_OFFSETS
        assert "B" in LABEL_OFFSETS
        assert "C" in LABEL_OFFSETS
        assert "D" in LABEL_OFFSETS

    def test_zone_a_offset(self) -> None:
        """测试A区偏移"""
        offset = LABEL_OFFSETS["A"]
        assert offset.x == 0.0
        assert offset.y == LayoutConstants.LABEL_OFFSET_A_Y

    def test_zone_c_offset(self) -> None:
        """测试C区偏移（有X偏移）"""
        offset = LABEL_OFFSETS["C"]
        assert offset.x == LayoutConstants.LABEL_OFFSET_C_X
        assert offset.y == LayoutConstants.LABEL_OFFSET_C_Y
