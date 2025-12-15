"""Penrose 楼梯计算器 - 包装层

封装 pstairs.PenroseStaircase，提供语义化 API。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import final

import pstairs
from core.staircase import StaircaseConfig


@final
@dataclass(frozen=True)
class PenroseResult:
    """Penrose 楼梯计算结果

    不可变数据类，包含楼梯的所有参数。

    Attributes:
        n: 楼梯序号
        a: A区台阶数（左上，上升）
        b: B区台阶数（右上，水平）
        c: C区台阶数（右下，下降）
        d: D区台阶数（左下，水平）
        step_length: 台阶长度 (L)
        stairsum: 楼梯和 (g)
    """

    n: int
    a: int
    b: int
    c: int
    d: int
    step_length: float
    stairsum: int

    def to_config(self) -> StaircaseConfig:
        """转换为 StaircaseConfig

        Returns:
            StaircaseConfig 实例
        """
        return StaircaseConfig(
            a=self.a,
            b=self.b,
            c=self.c,
            d=self.d,
            step_length=self.step_length,
        )


@final
class PenroseCalculator:
    """Penrose 楼梯计算器

    提供语义化 API，内部委托给 pstairs.PenroseStaircase。
    这是推荐的公有 API，隐藏了底层实现细节。

    Example:
        >>> result = PenroseCalculator.calculate(190)
        >>> print(result.a, result.b, result.c, result.d)
        8 5 2 7
    """

    @staticmethod
    def calculate(n: int) -> PenroseResult:
        """计算第 n 个 Penrose 楼梯

        Args:
            n: 楼梯序号（必须为正整数）

        Returns:
            PenroseResult 包含计算结果

        Raises:
            ValueError: 当 n 不是正整数时
        """
        if not isinstance(n, int) or n < 1:
            raise ValueError(f"n 必须为正整数，收到: {n}")

        ps = pstairs.PenroseStaircase(n)

        if not ps.valid:
            raise ValueError(f"无法计算第 {n} 个 Penrose 楼梯")

        return PenroseResult(
            n=n,
            a=ps.a,
            b=ps.b,
            c=int(ps.c),  # DIRECT_C 返回 float，需要转为 int
            d=ps.d,
            step_length=ps.l,
            stairsum=ps.g,
        )

    @staticmethod
    def is_valid(n: int) -> bool:
        """检查 n 是否为有效的楼梯序号

        Args:
            n: 待检查的序号

        Returns:
            True 如果 n 是有效的正整数
        """
        return isinstance(n, int) and n > 0
