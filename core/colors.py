"""
颜色管理模块 - 负责配色方案和颜色序列生成
"""
from __future__ import annotations

import random
from dataclasses import dataclass


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


class ColorPalette:
    """
    Penrose楼梯配色方案

    定义楼梯各部分的颜色常量
    """

    # 台阶颜色
    STEP_GRAY = RGB(128, 128, 128)
    STEP_RED = RGB(220, 60, 60)

    # 墙体颜色
    WALL_FRONT = RGB(0, 0, 255)  # 前墙（蓝色）
    WALL_SIDE = RGB(255, 255, 0)  # 侧墙（黄色）
    WALL_GREEN = RGB(0, 255, 0)  # 绿色（未使用）

    # UI颜色
    TEXT_BLACK = RGB(0, 0, 0)
    TEXT_WHITE = RGB(255, 255, 255)
    MARKER_WHITE = RGB(255, 255, 255)

    @classmethod
    def get_step_color(cls, is_red: bool) -> RGB:
        """获取台阶颜色"""
        return cls.STEP_RED if is_red else cls.STEP_GRAY


class ColorSequence:
    """
    台阶颜色序列生成器

    负责生成和管理台阶的颜色序列
    """

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
