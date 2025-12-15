"""
应用配置模块 - 定义应用程序配置数据结构
"""
from __future__ import annotations

from dataclasses import dataclass

from core.theme import Theme


@dataclass(frozen=True)
class AppConfig:
    """
    应用程序配置

    包含运行 Penrose 楼梯生成器所需的所有配置
    """
    n: int  # Penrose楼梯编号
    scale: int  # 缩放因子
    theme: Theme  # 主题对象
    output_path: str | None = None  # 输出文件路径
    debug: bool = True  # 是否输出调试信息

    def __post_init__(self) -> None:
        """验证配置"""
        if self.n < 1:
            raise ValueError("Penrose楼梯编号必须 >= 1")
        if self.scale < 1:
            raise ValueError("缩放因子必须 >= 1")
