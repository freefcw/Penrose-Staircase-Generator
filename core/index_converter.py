"""
索引转换器 - 统一管理绘制顺序和行走顺序之间的索引转换

绘制顺序: A区(A-1) → D区(D-1) → B区(B-1) → C区(C-1)
行走顺序: D区 → C区(反转) → B区(反转) → A区
"""
from __future__ import annotations

from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from core.staircase import StaircaseConfig


@final
class IndexConverter:
    """
    索引转换器
    
    提供绘制顺序和行走顺序之间的双向索引转换。
    """
    
    @staticmethod
    def draw_to_walking(draw_index: int, config: StaircaseConfig) -> int:
        """
        将绘制顺序索引转换为行走顺序索引
        
        Args:
            draw_index: 绘制顺序中的索引
            config: 楼梯配置
            
        Returns:
            行走顺序中的索引
        """
        a_count = config.a - 1
        d_count = config.d - 1
        b_count = config.b - 1
        c_count = config.c - 1
        
        if draw_index < a_count:
            # A区 → 在行走顺序末尾
            return d_count + c_count + b_count + draw_index
        elif draw_index < a_count + d_count:
            # D区 → 在行走顺序开头
            return draw_index - a_count
        elif draw_index < a_count + d_count + b_count:
            # B区 → 在C区后面，且被反转
            position_in_b = draw_index - a_count - d_count
            return d_count + c_count + (b_count - 1 - position_in_b)
        else:
            # C区 → 在D区后面，且被反转
            position_in_c = draw_index - a_count - d_count - b_count
            return d_count + (c_count - 1 - position_in_c)
    
    @staticmethod
    def walking_to_draw(walking_index: int, config: StaircaseConfig) -> int:
        """
        将行走顺序索引转换为绘制顺序索引
        
        Args:
            walking_index: 行走顺序中的索引
            config: 楼梯配置
            
        Returns:
            绘制顺序中的索引
        """
        a_count = config.a - 1
        d_count = config.d - 1
        b_count = config.b - 1
        c_count = config.c - 1
        
        if walking_index < d_count:
            # D区 → 在绘制顺序中位于 A区后面
            return a_count + walking_index
        elif walking_index < d_count + c_count:
            # C区(反转) → 在绘制顺序末尾，需要反转
            position_in_c = walking_index - d_count
            return a_count + d_count + b_count + (c_count - 1 - position_in_c)
        elif walking_index < d_count + c_count + b_count:
            # B区(反转) → 在绘制顺序中位于 A+D 后面，需要反转
            position_in_b = walking_index - d_count - c_count
            return a_count + d_count + (b_count - 1 - position_in_b)
        else:
            # A区 → 在绘制顺序开头
            position_in_a = walking_index - d_count - c_count - b_count
            return position_in_a
