"""
配置导出导入模块 - 保存和加载颜色序列配置
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import final


@dataclass
class SessionConfig:
    """会话配置 - 可导出导入的状态"""
    
    n: int
    theme: str
    # 绘制顺序的颜色序列
    color_sequence: list[bool]
    start_step_index: int
    # 行走顺序的颜色序列
    walking_order_colors: list[bool]
    walking_order_start: int
    # 楼梯参数
    a: int
    b: int
    c: int
    d: int
    step_length: float
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> "SessionConfig":
        """从 JSON 字符串加载"""
        data = json.loads(json_str)
        return cls(**data)


@final
class ConfigExporter:
    """配置导出器"""
    
    @staticmethod
    def export_to_file(config: SessionConfig, file_path: str) -> None:
        """导出配置到文件"""
        Path(file_path).write_text(config.to_json(), encoding="utf-8")
        print(f"[导出] 配置已保存到: {file_path}")
    
    @staticmethod
    def import_from_file(file_path: str) -> SessionConfig | None:
        """从文件导入配置"""
        try:
            json_str = Path(file_path).read_text(encoding="utf-8")
            config = SessionConfig.from_json(json_str)
            print(f"[导入] 配置已加载: {file_path}")
            return config
        except Exception as e:
            print(f"[导入] 加载失败: {e}")
            return None
