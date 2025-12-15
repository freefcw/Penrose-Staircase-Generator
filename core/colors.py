"""
颜色管理模块 - 负责颜色序列生成

此模块保持向后兼容，从 theme 模块重新导出 RGB 和 Theme
"""
from __future__ import annotations

import random
from typing import final

# 向后兼容导出
from core.theme import RGB, Theme, ThemeColors, ThemeName, ThemeStyle

__all__ = ["RGB", "Theme", "ThemeColors", "ThemeName", "ThemeStyle", "ColorSequence"]


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

    def get_color_at(self, index: int, theme: Theme) -> RGB:
        """获取指定索引的颜色"""
        if 0 <= index < len(self._sequence):
            return theme.colors.get_step_color(self._sequence[index])
        return theme.colors.step_gray
