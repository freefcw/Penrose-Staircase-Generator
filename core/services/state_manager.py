"""
状态管理器 - 管理应用程序状态和缓存

遵循单一职责原则，专注于状态管理。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import final

from core.calculator import PenroseCalculator
from core.colors import ColorSequence
from core.index_converter import IndexConverter
from core.platform_config import PlatformConfigProvider
from core.staircase import StaircaseConfig, StaircaseModel
from core.theme import Theme


# 基础预览缩放
_BASE_PREVIEW_SCALE = 1.6


@dataclass
class AppState:
    """应用程序状态快照"""
    
    n: int
    theme: Theme
    export_scale: float
    preview_scale: float = 1.6
    
    # 缓存数据
    cached_config: StaircaseConfig | None = field(default=None, repr=False)
    cached_model: StaircaseModel | None = field(default=None, repr=False)


@final
class StateManager:
    """
    状态管理器
    
    职责：
    - 管理应用状态（N值、主题、缩放）
    - 管理楼梯配置和模型的缓存
    - 提供状态查询接口
    """
    
    def __init__(self, n: int, theme: Theme, export_scale: float = 1.0):
        """
        初始化状态管理器
        
        Args:
            n: 初始楼梯序号
            theme: 初始主题
            export_scale: 导出缩放比例
        """
        self._n = n
        self._theme = theme
        self._export_scale = export_scale
        # 应用平台相关的预览缩放因子
        scale_factor = PlatformConfigProvider.get_preview_scale_factor()
        self._preview_scale = _BASE_PREVIEW_SCALE * scale_factor
        
        # 缓存
        self._cached_config: StaircaseConfig | None = None
        self._cached_model: StaircaseModel | None = None
    
    # === 属性访问器 ===
    
    @property
    def n(self) -> int:
        """当前楼梯序号"""
        return self._n
    
    @property
    def theme(self) -> Theme:
        """当前主题"""
        return self._theme
    
    @property
    def export_scale(self) -> float:
        """导出缩放比例"""
        return self._export_scale
    
    @property
    def preview_scale(self) -> float:
        """预览缩放比例"""
        return self._preview_scale
    
    @property
    def cached_config(self) -> StaircaseConfig | None:
        """缓存的楼梯配置"""
        return self._cached_config
    
    @property
    def cached_model(self) -> StaircaseModel | None:
        """缓存的楼梯模型"""
        return self._cached_model
    
    # === 状态更新方法 ===
    
    def update_n(self, n: int) -> bool:
        """
        更新楼梯序号
        
        Args:
            n: 新的楼梯序号
            
        Returns:
            True 如果值发生变化
        """
        if self._n != n:
            self._n = n
            self.invalidate_cache()
            return True
        return False
    
    def update_theme(self, theme: Theme) -> bool:
        """
        更新主题
        
        Args:
            theme: 新的主题
            
        Returns:
            True 如果值发生变化
        """
        if self._theme != theme:
            self._theme = theme
            return True
        return False
    
    def update_export_scale(self, scale: float) -> None:
        """更新导出缩放比例"""
        self._export_scale = scale
    
    # === 缓存管理 ===
    
    def invalidate_cache(self) -> None:
        """使缓存失效"""
        self._cached_config = None
        self._cached_model = None
    
    def has_valid_cache(self) -> bool:
        """检查是否有有效的缓存"""
        return self._cached_config is not None and self._cached_model is not None
    
    def compute_and_cache(self) -> tuple[StaircaseConfig, StaircaseModel] | None:
        """
        计算楼梯配置和模型，并缓存结果
        
        Returns:
            (config, model) 元组，如果计算失败则返回 None
        """
        try:
            result = PenroseCalculator.calculate(self._n)
            config = result.to_config()
            model = self._create_model(config)
            
            self._cached_config = config
            self._cached_model = model
            
            return config, model
        except ValueError:
            return None
    
    def get_or_compute(self) -> tuple[StaircaseConfig, StaircaseModel] | None:
        """
        获取缓存的配置和模型，如果没有则计算
        
        Returns:
            (config, model) 元组，如果计算失败则返回 None
        """
        if self.has_valid_cache():
            return self._cached_config, self._cached_model  # type: ignore
        return self.compute_and_cache()
    
    def _create_model(self, config: StaircaseConfig) -> StaircaseModel:
        """创建楼梯模型"""
        model = StaircaseModel(config)
        color_gen = ColorSequence(config.total_steps)
        draw_order_colors = color_gen.generate()
        draw_order_start = color_gen.start_index
        
        # 保存绘制顺序（用于渲染）
        model.color_sequence = draw_order_colors
        model.start_step_index = draw_order_start
        
        # 转换为行走顺序（用于步进面板）
        model.walking_order_colors = self._convert_to_walking_order(
            draw_order_colors, config
        )
        model.walking_order_start = IndexConverter.draw_to_walking(
            draw_order_start, config
        )
        
        return model
    
    def _convert_to_walking_order(
        self, colors: list[bool], config: StaircaseConfig
    ) -> list[bool]:
        """
        将绘制顺序转换为行走顺序
        
        绘制顺序: A区(A-1) → D区(D-1) → B区(B-1) → C区(C-1)
        行走顺序: D区 → C区(反转) → B区(反转) → A区
        """
        a_count = config.a - 1
        d_count = config.d - 1
        b_count = config.b - 1
        
        walking_order: list[bool] = []
        
        # D区
        walking_order.extend(colors[a_count : a_count + d_count])
        # C区 (反转)
        walking_order.extend(list(reversed(colors[a_count + d_count + b_count :])))
        # B区 (反转)
        walking_order.extend(
            list(reversed(colors[a_count + d_count : a_count + d_count + b_count]))
        )
        # A区
        walking_order.extend(colors[0:a_count])
        
        return walking_order
    
    # === 状态快照 ===
    
    def get_state(self) -> AppState:
        """获取当前状态快照"""
        return AppState(
            n=self._n,
            theme=self._theme,
            export_scale=self._export_scale,
            preview_scale=self._preview_scale,
            cached_config=self._cached_config,
            cached_model=self._cached_model,
        )
