"""
主题模块 - 定义颜色主题和行为配置

遵循开闭原则（OCP），使用多态替代条件判断
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


@dataclass(frozen=True)
class RGB:
    """不可变的RGB颜色"""

    r: int
    g: int
    b: int

    def to_tuple(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)

    def to_hex(self) -> str:
        """转换为十六进制颜色字符串"""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"


class ThemeName(str, Enum):
    """主题名称枚举"""
    CLASSIC = "classic"
    MINIMAL = "minimal"
    PROFESSIONAL = "professional"
    ARTISTIC = "artistic"


@dataclass(frozen=True)
class ThemeColors:
    """主题颜色配置"""
    step_gray: RGB
    step_red: RGB
    wall_front: RGB
    wall_side: RGB
    text_black: RGB
    text_white: RGB
    text_light: RGB
    marker_white: RGB

    def get_step_color(self, is_red: bool) -> RGB:
        """获取台阶颜色"""
        return self.step_red if is_red else self.step_gray


@dataclass(frozen=True)
class ThemeStyle:
    """主题样式行为配置"""
    show_title: bool = False
    show_sequence_border: bool = False
    show_decimal_border: bool = False
    use_light_labels: bool = True
    sequence_hint_simple: bool = True


@dataclass(frozen=True)
class Theme:
    """
    主题对象 - 封装颜色和行为配置

    使用不可变数据类确保线程安全
    """
    name: ThemeName
    colors: ThemeColors
    style: ThemeStyle

    # 预定义主题实例
    CLASSIC: ClassVar[Theme]
    MINIMAL: ClassVar[Theme]
    PROFESSIONAL: ClassVar[Theme]
    ARTISTIC: ClassVar[Theme]

    @classmethod
    def get_by_name(cls, name: str) -> Theme:
        """根据名称获取主题"""
        themes = {
            ThemeName.CLASSIC.value: cls.CLASSIC,
            ThemeName.MINIMAL.value: cls.MINIMAL,
            ThemeName.PROFESSIONAL.value: cls.PROFESSIONAL,
            ThemeName.ARTISTIC.value: cls.ARTISTIC,
        }
        return themes.get(name, cls.MINIMAL)


# === 预定义主题 ===

# 经典主题（鲜艳的蓝黄）
Theme.CLASSIC = Theme(
    name=ThemeName.CLASSIC,
    colors=ThemeColors(
        step_gray=RGB(128, 128, 128),
        step_red=RGB(220, 60, 60),
        wall_front=RGB(0, 0, 255),
        wall_side=RGB(255, 255, 0),
        text_black=RGB(0, 0, 0),
        text_white=RGB(255, 255, 255),
        text_light=RGB(0, 0, 0),
        marker_white=RGB(255, 255, 255),
    ),
    style=ThemeStyle(
        show_title=True,
        show_sequence_border=True,
        show_decimal_border=True,
        use_light_labels=False,
        sequence_hint_simple=False,
    ),
)

# 简约主题（柔和的蓝灰/米色）
Theme.MINIMAL = Theme(
    name=ThemeName.MINIMAL,
    colors=ThemeColors(
        step_gray=RGB(160, 160, 165),
        step_red=RGB(200, 80, 80),
        wall_front=RGB(70, 100, 140),
        wall_side=RGB(245, 220, 160),
        text_black=RGB(60, 60, 60),
        text_white=RGB(255, 255, 255),
        text_light=RGB(140, 140, 145),
        marker_white=RGB(255, 255, 255),
    ),
    style=ThemeStyle(
        show_title=False,
        show_sequence_border=False,
        show_decimal_border=False,
        use_light_labels=True,
        sequence_hint_simple=True,
    ),
)

# 专业主题（深灰/炭黑，低饱和度）
Theme.PROFESSIONAL = Theme(
    name=ThemeName.PROFESSIONAL,
    colors=ThemeColors(
        step_gray=RGB(100, 100, 105),
        step_red=RGB(180, 70, 70),
        wall_front=RGB(45, 55, 72),
        wall_side=RGB(200, 200, 195),
        text_black=RGB(30, 30, 35),
        text_white=RGB(250, 250, 250),
        text_light=RGB(100, 100, 105),
        marker_white=RGB(255, 255, 255),
    ),
    style=ThemeStyle(
        show_title=False,
        show_sequence_border=False,
        show_decimal_border=False,
        use_light_labels=True,
        sequence_hint_simple=True,
    ),
)

# 艺术主题（鲜艳的紫蓝/珊瑚橙）
Theme.ARTISTIC = Theme(
    name=ThemeName.ARTISTIC,
    colors=ThemeColors(
        step_gray=RGB(120, 130, 160),
        step_red=RGB(255, 100, 80),
        wall_front=RGB(80, 60, 140),
        wall_side=RGB(255, 180, 100),
        text_black=RGB(50, 40, 80),
        text_white=RGB(255, 255, 255),
        text_light=RGB(140, 130, 170),
        marker_white=RGB(255, 255, 255),
    ),
    style=ThemeStyle(
        show_title=False,
        show_sequence_border=False,
        show_decimal_border=False,
        use_light_labels=True,
        sequence_hint_simple=True,
    ),
)
