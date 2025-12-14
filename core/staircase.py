"""
楼梯模型模块 - 定义Penrose楼梯的数据结构
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Zone(Enum):
    """楼梯区域枚举"""

    A = "A"  # 上升区（左上）
    B = "B"  # 水平区（右上）
    C = "C"  # 下降区（右下）
    D = "D"  # 水平区（左下）


@dataclass
class StepPosition:
    """
    单个台阶的几何位置

    存储台阶四个角点的坐标（模型坐标系）
    """

    p1: tuple[float, float]  # 左下角
    p2: tuple[float, float]  # 左上角
    p3: tuple[float, float]  # 右上角
    p4: tuple[float, float]  # 右下角

    @property
    def center(self) -> tuple[float, float]:
        """计算台阶中心点"""
        return (
            (self.p1[0] + self.p2[0] + self.p3[0] + self.p4[0]) / 4,
            (self.p1[1] + self.p2[1] + self.p3[1] + self.p4[1]) / 4,
        )


@dataclass
class StaircaseConfig:
    """
    Penrose楼梯配置

    包含楼梯的所有参数，从 PenroseStaircase 算法计算得出
    """

    a: int  # A区台阶数
    b: int  # B区台阶数
    c: int  # C区台阶数
    d: int  # D区台阶数
    step_length: float  # 台阶长度 (L)

    @property
    def total_steps(self) -> int:
        """总台阶数（不含重复）"""
        return self.a + self.b + self.c + self.d - 4

    @property
    def wall_height(self) -> float:
        """墙体高度"""
        return self.d * 2

    @property
    def zone_step_counts(self) -> dict[Zone, int]:
        """各区域的实际台阶数"""
        return {
            Zone.A: self.a - 1,
            Zone.B: self.b - 1,
            Zone.C: self.c - 1,
            Zone.D: self.d - 1,
        }

    def __post_init__(self):
        """验证配置有效性"""
        if any(v < 2 for v in [self.a, self.b, self.c, self.d]):
            raise ValueError("区域台阶数必须至少为2")
        if self.step_length <= 0:
            raise ValueError("台阶长度必须为正数")


@dataclass
class StaircaseModel:
    """
    Penrose楼梯数据模型

    包含楼梯的配置和运行时状态
    """

    config: StaircaseConfig
    step_positions: list[StepPosition] = field(default_factory=list)
    color_sequence: list[bool] = field(default_factory=list)
    start_step_index: int = 0

    def clear_positions(self):
        """清空位置数据"""
        self.step_positions.clear()

    def add_step_position(self, position: StepPosition):
        """添加台阶位置"""
        self.step_positions.append(position)

    def get_step_position(self, index: int) -> StepPosition | None:
        """获取指定索引的台阶位置"""
        if 0 <= index < len(self.step_positions):
            return self.step_positions[index]
        return None
