"""
平台配置模块 - 集中管理平台相关的配置

提供统一的接口获取不同平台的配置参数。
"""
from __future__ import annotations

import platform
from dataclasses import dataclass
from typing import ClassVar, final


@dataclass(frozen=True)
class PlatformConfig:
    """平台配置
    
    封装所有平台相关的配置参数，包括：
    - 窗口位置偏移
    - 字体缩放
    - 预览缩放因子
    - 控制面板尺寸
    - 步进面板尺寸
    - 最小窗口尺寸
    """
    
    # === 主窗口配置 ===
    offset_x: int = 0
    offset_y: int = 0
    font_scale: float = 1.0
    preview_scale_factor: float = 1.0
    min_window_width: int = 400
    min_window_height: int = 300
    
    # === 控制面板配置 ===
    control_panel_width: int = 300
    control_panel_height: int = 420
    
    # === 步进面板配置 ===
    step_panel_width: int = 320
    step_panel_height: int = 280


# === 平台特定配置 ===

DARWIN_CONFIG = PlatformConfig(
    # 主窗口 - 较小窗口但保持组件大小
    offset_x=0,
    offset_y=0,
    font_scale=2.0,  # 保持组件原有大小
    preview_scale_factor=3.0,  # 楼梯预览缩放（与 Linux 一致）
    min_window_width=800,
    min_window_height=600,
    # 控制面板 - 保持原有大小
    control_panel_width=640,
    control_panel_height=1000,
    # 步进面板 - 保持原有大小
    step_panel_width=640,
    step_panel_height=600,
)

LINUX_CONFIG = PlatformConfig(
    # 主窗口 - 放大2倍
    offset_x=0,
    offset_y=0,
    font_scale=2.0,  # 字体放大2倍
    preview_scale_factor=3.0,  # 缩放因子放大2倍
    min_window_width=1600,
    min_window_height=1200,
    # 控制面板 - 放大2倍
    control_panel_width=640,
    control_panel_height=1000,
    # 步进面板 - 放大2倍
    step_panel_width=640,
    step_panel_height=600,
)

WINDOWS_CONFIG = PlatformConfig(
    # 主窗口
    offset_x=150,
    offset_y=-50,
    font_scale=1.0,
    preview_scale_factor=1.0,
    min_window_width=400,
    min_window_height=300,
    # 控制面板
    control_panel_width=300,
    control_panel_height=420,
    # 步进面板
    step_panel_width=320,
    step_panel_height=280,
)


# === 平台配置映射 ===

_PLATFORM_CONFIGS: dict[str, PlatformConfig] = {
    "darwin": DARWIN_CONFIG,
    "linux": LINUX_CONFIG,
    "windows": WINDOWS_CONFIG,
}


@final
class PlatformConfigProvider:
    """平台配置提供器
    
    根据当前操作系统自动选择对应的配置。
    """
    
    _cached_config: ClassVar[PlatformConfig | None] = None
    _cached_system: ClassVar[str | None] = None
    
    @classmethod
    def get_config(cls) -> PlatformConfig:
        """获取当前平台的配置
        
        Returns:
            当前平台的配置对象
        """
        system = platform.system().lower()
        
        # 使用缓存避免重复检测
        if cls._cached_config is not None and cls._cached_system == system:
            return cls._cached_config
        
        cls._cached_system = system
        cls._cached_config = _PLATFORM_CONFIGS.get(system, DARWIN_CONFIG)
        
        return cls._cached_config
    
    @classmethod
    def get_preview_scale_factor(cls) -> float:
        """获取预览缩放因子"""
        return cls.get_config().preview_scale_factor
    
    @classmethod
    def get_font_scale(cls) -> float:
        """获取字体缩放因子"""
        return cls.get_config().font_scale


# === 便捷函数 ===

def get_platform_config() -> PlatformConfig:
    """获取当前平台的配置（便捷函数）"""
    return PlatformConfigProvider.get_config()
