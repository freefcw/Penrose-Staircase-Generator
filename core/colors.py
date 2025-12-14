"""
颜色管理模块 - 负责配色方案和颜色序列生成
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import ClassVar, final


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


class Theme:
    """主题枚举"""
    CLASSIC = "classic"
    MINIMAL = "minimal"
    PROFESSIONAL = "professional"
    ARTISTIC = "artistic"


@final
class ColorPalette:
    """
    Penrose楼梯配色方案 - 支持主题切换

    定义楼梯各部分的颜色常量
    """

    _current_theme: ClassVar[str] = Theme.MINIMAL

    # 经典主题配色（鲜艳的蓝黄）
    _CLASSIC: ClassVar[dict[str, RGB]] = {
        "STEP_GRAY": RGB(128, 128, 128),
        "STEP_RED": RGB(220, 60, 60),
        "WALL_FRONT": RGB(0, 0, 255),
        "WALL_SIDE": RGB(255, 255, 0),
        "TEXT_BLACK": RGB(0, 0, 0),
        "TEXT_WHITE": RGB(255, 255, 255),
        "TEXT_LIGHT": RGB(0, 0, 0),
        "MARKER_WHITE": RGB(255, 255, 255),
    }

    # 简约主题配色（柔和的蓝灰/米色）
    _MINIMAL: ClassVar[dict[str, RGB]] = {
        "STEP_GRAY": RGB(160, 160, 165),
        "STEP_RED": RGB(200, 80, 80),
        "WALL_FRONT": RGB(70, 100, 140),
        "WALL_SIDE": RGB(245, 220, 160),
        "TEXT_BLACK": RGB(60, 60, 60),
        "TEXT_WHITE": RGB(255, 255, 255),
        "TEXT_LIGHT": RGB(140, 140, 145),
        "MARKER_WHITE": RGB(255, 255, 255),
    }

    # 专业主题配色（深灰/炭黑，低饱和度）
    _PROFESSIONAL: ClassVar[dict[str, RGB]] = {
        "STEP_GRAY": RGB(100, 100, 105),
        "STEP_RED": RGB(180, 70, 70),
        "WALL_FRONT": RGB(45, 55, 72),      # 深蓝灰
        "WALL_SIDE": RGB(200, 200, 195),    # 浅灰
        "TEXT_BLACK": RGB(30, 30, 35),
        "TEXT_WHITE": RGB(250, 250, 250),
        "TEXT_LIGHT": RGB(100, 100, 105),
        "MARKER_WHITE": RGB(255, 255, 255),
    }

    # 艺术主题配色（鲜艳的紫蓝/珊瑚橙）
    _ARTISTIC: ClassVar[dict[str, RGB]] = {
        "STEP_GRAY": RGB(120, 130, 160),    # 淡紫灰
        "STEP_RED": RGB(255, 100, 80),      # 珊瑚红
        "WALL_FRONT": RGB(80, 60, 140),     # 深紫
        "WALL_SIDE": RGB(255, 180, 100),    # 橙黄
        "TEXT_BLACK": RGB(50, 40, 80),
        "TEXT_WHITE": RGB(255, 255, 255),
        "TEXT_LIGHT": RGB(140, 130, 170),
        "MARKER_WHITE": RGB(255, 255, 255),
    }

    # 主题映射
    _THEMES: ClassVar[dict[str, dict[str, RGB]]] = {
        Theme.CLASSIC: _CLASSIC,
        Theme.MINIMAL: _MINIMAL,
        Theme.PROFESSIONAL: _PROFESSIONAL,
        Theme.ARTISTIC: _ARTISTIC,
    }

    @classmethod
    def set_theme(cls, theme: str) -> None:
        """设置当前主题"""
        if theme in cls._THEMES:
            cls._current_theme = theme

    @classmethod
    def get_theme(cls) -> str:
        """获取当前主题"""
        return cls._current_theme

    @classmethod
    def _get_color(cls, name: str) -> RGB:
        """获取当前主题的颜色"""
        colors = cls._THEMES.get(cls._current_theme, cls._MINIMAL)
        return colors[name]

    # 属性访问器
    @classmethod
    @property
    def STEP_GRAY(cls) -> RGB:
        return cls._get_color("STEP_GRAY")

    @classmethod
    @property
    def STEP_RED(cls) -> RGB:
        return cls._get_color("STEP_RED")

    @classmethod
    @property
    def WALL_FRONT(cls) -> RGB:
        return cls._get_color("WALL_FRONT")

    @classmethod
    @property
    def WALL_SIDE(cls) -> RGB:
        return cls._get_color("WALL_SIDE")

    @classmethod
    @property
    def TEXT_BLACK(cls) -> RGB:
        return cls._get_color("TEXT_BLACK")

    @classmethod
    @property
    def TEXT_WHITE(cls) -> RGB:
        return cls._get_color("TEXT_WHITE")

    @classmethod
    @property
    def TEXT_LIGHT(cls) -> RGB:
        return cls._get_color("TEXT_LIGHT")

    @classmethod
    @property
    def MARKER_WHITE(cls) -> RGB:
        return cls._get_color("MARKER_WHITE")

    WALL_GREEN: ClassVar[RGB] = RGB(0, 255, 0)  # 未使用

    @classmethod
    def get_step_color(cls, is_red: bool) -> RGB:
        """获取台阶颜色"""
        return cls._get_color("STEP_RED") if is_red else cls._get_color("STEP_GRAY")


@final
class ColorSequence:
    """
    台阶颜色序列生成器

    负责生成和管理台阶的颜色序列
    """

    count: int

    def __init__(self, count: int, seed: int | None = None):
        """
        初始化颜色序列生成器

        Args:
            count: 台阶总数
            seed: 随机种子（用于可重复性）
        """
        self.count = count
        if seed is not None:
            random.seed(seed)
        self._sequence: list[bool] = []
        self._start_index: int = 0

    def generate(self) -> list[bool]:
        """
        生成随机颜色序列

        Returns:
            颜色序列列表，True=红色，False=灰色
        """
        self._sequence = [random.choice([True, False]) for _ in range(self.count)]
        self._start_index = random.randint(0, max(0, self.count - 1))
        return self._sequence

    @property
    def sequence(self) -> list[bool]:
        """获取颜色序列"""
        return self._sequence

    @property
    def start_index(self) -> int:
        """获取起点索引"""
        return self._start_index

    def get_color_at(self, index: int) -> RGB:
        """获取指定索引的颜色"""
        if 0 <= index < len(self._sequence):
            return ColorPalette.get_step_color(self._sequence[index])
        return ColorPalette.STEP_GRAY
